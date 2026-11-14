"""Bounded source scanner. Never imports or executes audited project code."""
import ast
from collections import Counter
from datetime import datetime, timezone
import fnmatch
import os
from pathlib import Path
import re

from .model import add_evidence, identity, validate
from .review import finding, review_graph
from . import __version__

EXTENSIONS = {".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript", ".cjs": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".gd": "GDScript", ".go": "Go", ".rs": "Rust", ".cs": "C#",
    ".c": "C", ".h": "C/C++", ".cpp": "C++", ".hpp": "C++", ".java": "Java", ".rb": "Ruby", ".php": "PHP",
    ".sh": "Shell", ".ps1": "PowerShell", ".md": "Markdown", ".json": "JSON", ".toml": "TOML",
    ".yaml": "YAML", ".yml": "YAML", ".sql": "SQL", ".html": "HTML", ".css": "CSS"}
SKIP_DIRS = {".git", ".svn", ".hg", "node_modules", "__pycache__", ".venv", "venv", "env", "dist", "build",
    ".next", ".cache", ".local", "coverage", "vendor", "target", ".idea", ".vscode", ".test-output"}
SENSITIVE = (".env*", "*credentials*", "*secret*", "*.pem", "*.key", "*token*", "*lock.json", "*.lock")


def linked(path):
    return path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction())


def call_name(node, depth=0):
    """Describe call syntax without copying argument values into component labels."""
    if depth > 40:
        return "<expression>"
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return call_name(node.value, depth + 1) + "." + node.attr
    if isinstance(node, ast.Call):
        return call_name(node.func, depth + 1) + "(…)"
    if isinstance(node, ast.Subscript):
        return call_name(node.value, depth + 1) + "[…]"
    return "<expression>"


def scan(root, *, name=None, max_files=2000, max_bytes=256_000, max_total=24_000_000, exclude=(), output=None):
    root = Path(root).resolve()
    if not root.is_dir():
        raise ValueError("Project root must be an existing directory")
    if not 1 <= max_files <= 5000 or not 1 <= max_bytes <= 256_000 or not 1 <= max_total <= 48_000_000:
        raise ValueError("Scan bounds exceed supported limits")
    data = {"schema_version": 1, "project": {"name": name or root.name, "created_at": datetime.now(timezone.utc).isoformat(),
        "agent_review": False, "source_root": ".", "mode": "static-read-only", "generator_version": __version__, "viewer_id": "arc-xray-blue-v1"},
        "groups": {"entry": "Entrypoints", "modules": "Implementation", "tests": "Tests", "config": "Configuration",
                   "docs": "Documentation", "external": "External dependencies", "storage": "Data / I/O", "flow": "Execution steps"},
        "nodes": [], "edges": [], "evidence": {}, "findings": [], "views": [],
        "coverage": {"analyzed_files": 0, "discovered_files": 0, "excluded_files": 0, "skipped": [], "unresolved": [],
            "languages": {}, "truncated": False, "limitations": [
                "Static evidence confirms source syntax, not runtime execution, reachability, security or performance.",
                "Python imports use AST; calls and execution paths are conservative syntactic candidates. Aliasing, monkey patching and reflection are incomplete.",
                "JavaScript/TypeScript, GDScript, Go, Rust and C# import adapters are lexical: comments, aliases and generated code can cause omissions or false matches.",
                "Other file types have inventory coverage only. Gitignore rules are not evaluated; explicit excludes and built-in filters apply.",
                "No dependency installation, project code execution, engine launch, benchmarks or automatic fixes are performed.",
                "Secrets are excluded by filename and excerpts receive best-effort redaction; review artifacts before sharing."]}}
    coverage, files, total = data["coverage"], {}, 0
    out = Path(output).resolve() if output else None
    enumerated, stop = 0, False
    for directory, dirs, names in os.walk(root, followlinks=False):
        enumerated += len(dirs) + len(names)
        if enumerated > 30_000:
            coverage["truncated"] = True
            coverage["limitations"].append("Directory enumeration stopped after 30,000 entries; discovered-file counts cover only the visited prefix.")
            break
        dirs[:] = sorted(d for d in dirs if d not in SKIP_DIRS and not linked(Path(directory) / d)
                         and not (out and (Path(directory) / d).resolve() == out)
                         and not any(fnmatch.fnmatch((Path(directory) / d).relative_to(root).as_posix(), p) for p in exclude))
        for filename in sorted(names):
            path = Path(directory) / filename
            relative = path.relative_to(root).as_posix()
            if path.suffix.lower() not in EXTENSIONS:
                continue
            coverage["discovered_files"] += 1
            if (linked(path) or any(fnmatch.fnmatch(filename.lower(), p) for p in SENSITIVE)
                or relative.startswith("docs/architecture-review/") or any(fnmatch.fnmatch(relative, p) for p in exclude)):
                coverage["excluded_files"] += 1
                continue
            if len(files) >= max_files:
                coverage["truncated"] = True
                coverage["skipped"].append({"path": relative, "reason": "file-count-limit"})
                coverage["limitations"].append("File count reached; remaining directories were not traversed. Discovered-file counts cover only the visited prefix.")
                stop = True
                break
            try:
                size = path.stat().st_size
                if size > max_bytes or total + size > max_total:
                    coverage["truncated"] = True
                    coverage["skipped"].append({"path": relative, "reason": "byte-limit"})
                    continue
                raw = path.read_bytes()
                if len(raw) > max_bytes or total + len(raw) > max_total:
                    coverage["truncated"] = True
                    coverage["skipped"].append({"path": relative, "reason": "changed-size-limit"})
                    continue
                text = raw.decode("utf-8-sig")
                if "\x00" in text:
                    raise ValueError("binary content")
            except (OSError, UnicodeError, ValueError) as error:
                coverage["skipped"].append({"path": relative, "reason": type(error).__name__})
                continue
            total += len(raw)
            files[relative] = (raw, text)
        if stop:
            break
    coverage["analyzed_files"] = len(files)
    coverage["languages"] = dict(Counter(EXTENSIONS[Path(p).suffix.lower()] for p in files))
    coverage["bytes_read"] = total
    modules, asts = {}, {}
    for path, (raw, text) in files.items():
        suffix = Path(path).suffix.lower()
        group = "tests" if any(s.startswith("test") or s in {"spec", "specs", "__tests__"} for s in Path(path).parts) else "docs" if suffix == ".md" else "config" if suffix in {".json", ".toml", ".yaml", ".yml"} else "entry" if Path(path).stem.lower() in {"main", "app", "server", "index", "cli", "__main__"} else "modules"
        kind = "document" if group == "docs" else "config" if group == "config" else "module"
        ref = add_evidence(data, path, raw)
        node = {"id": identity("file", path), "label": path, "path": path, "group": group, "kind": kind,
                "language": EXTENSIONS[suffix], "lines": len(text.splitlines()), "status": "verified", "evidence": [ref],
                "purpose": "Source file inventoried; semantic purpose requires agent review.",
                "inputs": "Not established by static inventory.", "outputs": "Not established by static inventory.", "symbols": []}
        modules[path] = node
        data["nodes"].append(node)
        if suffix == ".py":
            try:
                tree = ast.parse(text, filename=path)
                asts[path] = tree
                node["purpose"] = ast.get_docstring(tree) or "Python module; inspect symbols and relationships for responsibilities."
                node["symbols"] = [{"name": n.name, "line": n.lineno, "end": n.end_lineno, "kind": type(n).__name__,
                    "doc": ast.get_docstring(n) or ""} for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))][:200]
            except (SyntaxError, RecursionError, MemoryError) as error:
                line = getattr(error, "lineno", 1) or 1
                ev = add_evidence(data, path, raw, line)
                finding(data, "parse-error", "Python source could not be parsed", f"{path}:{line}: {type(error).__name__}.",
                    "AST dependencies and execution flow for this file are incomplete. The interpreter version may differ from the project's target.",
                    "Inspect the source and target Python version before calling this a project defect.", [node["id"]], [ev], "medium", "verified")
    edge_keys = set()

    def edge(source, target, kind, label, ref, status="verified"):
        key = (source, target, kind, label, ref)
        if key in edge_keys:
            return
        edge_keys.add(key)
        data["edges"].append({"id": identity("edge", "|".join(key)), "source": source, "target": target,
            "kind": kind, "label": label, "status": status, "evidence": [ref]})

    def external(name, ref):
        key = identity("ext", name)
        existing = next((n for n in data["nodes"] if n["id"] == key), None)
        if existing:
            return key
        data["nodes"].append({"id": key, "label": name, "group": "external", "kind": "external", "status": "documented",
            "purpose": "Referenced import; installation, version and behavior are unverified.", "inputs": "Import reference.",
            "outputs": "External module API (not inspected).", "evidence": [ref]})
        return key

    def py_resolve(name):
        base = name.replace(".", "/")
        for prefix in ("", "src/"):
            for candidate in (prefix + base + ".py", prefix + base + "/__init__.py"):
                if candidate in modules:
                    return modules[candidate]["id"]
        return None

    for path, tree in asts.items():
        raw, text = files[path]
        source, aliases = modules[path]["id"], {}
        for statement in ast.walk(tree):
            if not isinstance(statement, (ast.Import, ast.ImportFrom)):
                continue
            ev = add_evidence(data, path, raw, statement.lineno, statement.end_lineno)
            if isinstance(statement, ast.Import):
                items = [(a.name, a.asname or a.name.split(".")[0], 0) for a in statement.names]
            else:
                package = Path(path).parent.parts
                if package and package[0] == "src":
                    package = package[1:]
                base = list(package[:len(package) - statement.level + 1]) if statement.level else []
                if statement.module:
                    base += statement.module.split(".")
                module = ".".join(base)
                items = []
                for alias in statement.names:
                    full = ".".join(filter(None, [module, alias.name]))
                    items.append((full if py_resolve(full) else module, alias.asname or alias.name, statement.level))
            for name, alias, relative in items:
                target = py_resolve(name)
                if not target and relative:
                    coverage["unresolved"].append({"path": path, "line": statement.lineno, "reference": name})
                    continue
                target = target or external(name or "unknown import", ev)
                aliases[alias] = target
                edge(source, target, "dependency", "import " + name, ev)
        for call in (n for n in ast.walk(tree) if isinstance(n, ast.Call)):
            try:
                called = call_name(call.func)
            except RecursionError:
                continue
            ev = add_evidence(data, path, raw, call.lineno, call.end_lineno)
            base = called.split(".")[0]
            if base in aliases:
                edge(source, aliases[base], "control", "call candidate: " + called, ev, "inference")
            if called in {"eval", "exec", "builtins.eval", "builtins.exec"}:
                finding(data, "dynamic-execution", "Dynamic code execution call", f"{path}:{call.lineno} contains a call named {called}.",
                    "If untrusted input reaches this call it can cross a trust boundary. Name shadowing and input provenance have not been resolved.",
                    "Trace the input, caller authorization and process permissions; do not infer exploitability from syntax alone.", [source], [ev], "high")
            if called in {"requests.get", "requests.post", "requests.put", "requests.delete", "requests.patch", "requests.request", "urllib.request.urlopen"} and not any(k.arg == "timeout" for k in call.keywords):
                finding(data, "network-timeout", "Network call omits an explicit timeout", f"{path}:{call.lineno} calls {called} without a timeout keyword.",
                    "If no timeout is imposed elsewhere, waiting can be unbounded. Wrapper behavior, global defaults and runtime reachability are unverified.",
                    "Trace client configuration and outer deadlines before deciding whether a timeout is missing.", [source], [ev])
            if called in {"queue.Queue", "asyncio.Queue"} and not call.args and not any(k.arg == "maxsize" for k in call.keywords):
                finding(data, "unbounded-queue", "Queue construction has no explicit capacity", f"{path}:{call.lineno} constructs {called} without a maxsize argument.",
                    "If producers outpace consumers and no outer bound exists, pending work may grow. The queue may also be intentionally bounded by its caller.",
                    "Review producer rate, backpressure, cancellation and memory limits. No load benchmark was performed.", [source], [ev])
            if called == "open" or called.endswith((".read_text", ".write_text", ".read_bytes", ".write_bytes", ".execute", ".fetch", ".fetchall")):
                label = "I/O: " + called
                literal = call.args[0].value if call.args and isinstance(call.args[0], ast.Constant) and isinstance(call.args[0].value, str) else None
                if literal and len(literal) < 100 and not re.search(r"[\\:]|password|secret|token|key", literal, re.I):
                    label += " · " + literal
                target = identity("io", label)
                if not any(n["id"] == target for n in data["nodes"]):
                    data["nodes"].append({"id": target, "label": label, "kind": "resource", "group": "storage", "status": "inference",
                        "purpose": "Syntactic I/O candidate; actual resource and operation semantics require review.", "inputs": "Call arguments (see source).",
                        "outputs": "File/database/path result; not executed.", "evidence": [ev]})
                reading = called.endswith((".read_text", ".read_bytes", ".fetch", ".fetchall"))
                edge(target if reading else source, source if reading else target, "data", "I/O candidate: " + called, ev, "inference")
        for handler in (n for n in ast.walk(tree) if isinstance(n, ast.ExceptHandler)):
            if handler.type is None or (isinstance(handler.type, ast.Name) and handler.type.id in {"Exception", "BaseException"}):
                if all(isinstance(n, ast.Pass) for n in handler.body):
                    ev = add_evidence(data, path, raw, handler.lineno, handler.end_lineno)
                    finding(data, "swallowed-error", "Broad exception is silently discarded", f"{path}:{handler.lineno} has a broad except handler containing only pass.",
                        "Failures may become difficult to observe; the surrounding context may still make this intentional.",
                        "Review failure visibility, return values and the intended recovery behavior.", [source], [ev])
        for function in (n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef)):
            blocking = [n for n in ast.walk(function) if isinstance(n, ast.Call) and
                        (call_name(n.func) in {"time.sleep", "requests.get", "requests.post"} or call_name(n.func).endswith((".read_text", ".write_text", ".read_bytes", ".write_bytes")))]
            for call in blocking[:10]:
                ev = add_evidence(data, path, raw, call.lineno, call.end_lineno)
                finding(data, "blocking-async", "Synchronous operation inside an async function", f"{path}:{call.lineno}: {call_name(call.func)} appears in async function {function.name}.",
                    "If executed on the event-loop thread, synchronous waiting or I/O can delay other tasks. Name binding, nested scopes and scheduling are not resolved.",
                    "Verify the actual call path and execution thread, then measure latency before changing the design.", [source], [ev])
        # Keep the first view bounded; deeper functions remain listed in component cards.
        candidates = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name in {"main", "run", "handler", "serve"}]
        candidates += [n for n in tree.body if isinstance(n, ast.If) and any(isinstance(x, ast.Name) and x.id == "__name__" for x in ast.walk(n.test))]
        for entry in candidates[:2]:
            if sum(v.get("category") == "workflow" for v in data["views"]) >= 8:
                coverage["limitations"].append("Execution views capped at eight entry functions/guards; deeper paths require agent review.")
                break
            from .workflows import build_flow
            build_flow(data, path, raw, entry, edge)
    for path, (raw, text) in files.items():
        suffix = Path(path).suffix.lower()
        patterns = []
        if suffix in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}:
            patterns = [r'''(?:import|export)\s+(?:[^;\n]*?\s+from\s*)?["']([^"']+)["']''', r'''(?:require|import)\s*\(\s*["']([^"']+)["']\s*\)''']
        elif suffix == ".gd":
            patterns = [r'''(?:preload|load)\s*\(\s*["']([^"']+)["']\s*\)''']
        elif suffix == ".go":
            patterns = [r'''(?:import\s+|^\s*)["']([^"']+)["']''']
        elif suffix == ".rs":
            patterns = [r"\buse\s+([\w:]+)", r"\bmod\s+(\w+)\s*;"]
        elif suffix == ".cs":
            patterns = [r"\busing\s+([\w.]+)\s*;"]
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.M):
                name = match.group(1)
                line = text.count("\n", 0, match.start()) + 1
                ev = add_evidence(data, path, raw, line)
                target = None
                if name.startswith((".", "res://")):
                    base = name[6:] if name.startswith("res://") else (Path(path).parent / name).as_posix()
                    # Normalize dot segments lexically; no filesystem traversal.
                    base = os.path.normpath(base).replace("\\", "/")
                    options = [base] + [base + e for e in (".ts", ".tsx", ".js", ".jsx", ".mjs", ".gd")] + [base + "/index" + e for e in (".ts", ".js", ".tsx")]
                    if Path(base).suffix in {".js", ".jsx"}:
                        options += [str(Path(base).with_suffix(e)).replace("\\", "/") for e in (".ts", ".tsx")]
                    target = next((modules[p]["id"] for p in options if p in modules), None)
                    if not target:
                        coverage["unresolved"].append({"path": path, "line": line, "reference": name})
                        continue
                else:
                    target = external(name, ev)
                edge(modules[path]["id"], target, "dependency", "lexical import: " + name, ev, "inference")
    review_graph(data)
    base = [n["id"] for n in data["nodes"] if n["group"] != "flow"]
    def view(key, title, description, members):
        ids = set(members)
        return {"id": key, "title": title, "description": description, "nodes": members,
                "edges": [e["id"] for e in data["edges"] if e["source"] in ids and e["target"] in ids]}
    data["views"] = [view("system", "System architecture", "Source components and statically observed relationships. Semantic review may add boundaries and workflows.", base),
        view("dependencies", "Dependencies", "Imports point from consumer to referenced component. External versions and installation are not verified.", [n["id"] for n in data["nodes"] if n["kind"] in {"module", "external"}]),
        view("data", "Data flow / I/O", "Syntactic resource operations; input provenance and complete storage behavior require agent review.", [n["id"] for n in data["nodes"] if n["kind"] in {"module", "resource"}]),
        *data["views"], view("coverage", "Source coverage", "All inventoried files. Inventory does not imply semantic or runtime verification.", base)]
    if not base:
        coverage["limitations"].append("No supported readable source files found. Select another root or adjust explicit limits/excludes.")
    return validate(data)
