"""Portable evidence model. No absolute machine paths in distributed atlases."""
import copy
import hashlib
from pathlib import Path, PurePosixPath
import re

STATUSES = {"verified", "documented", "inference", "unknown"}
KINDS = {"dependency", "control", "data"}


def identity(prefix, value):
    return prefix + "-" + hashlib.sha256(value.encode()).hexdigest()[:16]


def safe_relative(root, name):
    if not isinstance(name, str) or not name or "\\" in name or ":" in name:
        raise ValueError("Expected a portable project-relative path")
    rel = PurePosixPath(name)
    if rel.is_absolute() or ".." in rel.parts:
        raise ValueError("Path escapes project")
    path = Path(root) / name
    current = Path(root)
    for part in rel.parts:
        current /= part
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError("Symbolic links are not source evidence")
    if not path.resolve().is_relative_to(Path(root).resolve()):
        raise ValueError("Path escapes project")
    return path


def redact(text):
    # Best effort only: source excerpts still require review before publication.
    text = re.sub(r'(?i)((?:password|api[_-]?key|access[_-]?token|secret)\s*[:=]\s*)[\'\"][^\'\"\n]*[\'\"]', r'\1"[REDACTED]"', text)
    return re.sub(r'(?i)(https?://)[^\s/@:]+:[^\s/@]+@', r'\1[REDACTED]@', text)


def add_evidence(data, path, raw, line=1, end=None):
    lines = raw.decode("utf-8-sig", errors="replace").splitlines() or [""]
    line = max(1, min(int(line), len(lines)))
    end = max(line, min(int(end or line + 3), len(lines), line + 11))
    digest = hashlib.sha256(raw).hexdigest()
    ref = identity("ev", f"{path}:{line}:{end}:{digest}")
    excerpt = redact("\n".join(lines[line - 1:end]))[:1800]
    data["evidence"][ref] = {"path": path, "line": line, "end": end,
                             "sha256": digest, "excerpt": excerpt}
    return ref


def validate(data):
    if data.get("schema_version") != 1:
        raise ValueError("Unsupported atlas schema")
    for anchor in data["evidence"].values():
        name = anchor["path"]
        if not isinstance(name, str) or PurePosixPath(name).is_absolute() or ".." in PurePosixPath(name).parts or ":" in name or "\\" in name:
            raise ValueError("Evidence path must be project-relative")
        if not re.fullmatch(r"[0-9a-f]{64}", anchor["sha256"]) or type(anchor["line"]) is not int or type(anchor["end"]) is not int or not 1 <= anchor["line"] <= anchor["end"]:
            raise ValueError("Invalid source evidence anchor")
    ids = set()
    for bucket in ("nodes", "edges", "findings", "views"):
        local = set()
        for item in data[bucket]:
            if not re.fullmatch(r"[A-Za-z0-9_.:-]{1,160}", item["id"]) or item["id"] in local:
                raise ValueError(f"Invalid/duplicate {bucket} id: {item['id']}")
            local.add(item["id"])
            required = {"nodes": {"label", "group", "kind", "purpose", "inputs", "outputs"}, "edges": {"source", "target", "kind", "label"},
                        "findings": {"rule", "title", "severity", "observation", "impact", "proposal", "nodes"}, "views": {"title", "description", "nodes", "edges"}}[bucket]
            if required - set(item):
                raise ValueError(f"Missing {bucket} fields: {sorted(required - set(item))}")
            if bucket in {"nodes", "edges", "findings"}:
                if item["status"] not in STATUSES:
                    raise ValueError("Unknown evidence status")
                if not item.get("evidence") or any(r not in data["evidence"] for r in item["evidence"]):
                    raise ValueError(f"Missing evidence: {item['id']}")
        if bucket == "nodes":
            ids = local
    for node in data["nodes"]:
        if node["group"] not in data["groups"]:
            raise ValueError("Unknown component group")
    for edge in data["edges"]:
        if edge["kind"] not in KINDS or edge["source"] not in ids or edge["target"] not in ids:
            raise ValueError("Invalid relationship")
    edge_ids = {e["id"] for e in data["edges"]}
    for finding in data["findings"]:
        if finding["severity"] not in {"high", "medium", "low", "info"}:
            raise ValueError("Invalid severity")
        if any(n not in ids for n in finding["nodes"]):
            raise ValueError("Unknown finding component")
    for view in data["views"]:
        if any(n not in ids for n in view["nodes"]) or any(e not in edge_ids for e in view["edges"]):
            raise ValueError("Unknown view element")
        members = set(view["nodes"])
        if any(e["id"] in view["edges"] and (e["source"] not in members or e["target"] not in members) for e in data["edges"]):
            raise ValueError("View relationship leaves its components")
    return data


def enrich(data, patch, root):
    """Merge agent-authored semantic review, validating evidence against source bytes."""
    result = copy.deepcopy(data)
    known = {n["id"]: n for n in result["nodes"]}
    original_hashes = {e["path"]: e["sha256"] for e in result["evidence"].values()}
    for path, digest in original_hashes.items():
        if hashlib.sha256(safe_relative(root, path).read_bytes()).hexdigest() != digest:
            raise ValueError("Source changed since scan; rescan before enriching")

    def refs(value):
        found = []
        for ref in value:
            if isinstance(ref, str):
                if ref not in result["evidence"]:
                    raise ValueError("Unknown evidence reference")
                anchor = result["evidence"][ref]
                raw = safe_relative(root, anchor["path"]).read_bytes()
                if hashlib.sha256(raw).hexdigest() != anchor["sha256"]:
                    raise ValueError("Source changed since scan; rescan before enriching")
                found.append(ref)
            else:
                path = safe_relative(root, ref["path"])
                # Enrichment may only quote already inventoried source files.
                allowed = {e["path"] for e in result["evidence"].values()}
                if ref["path"] not in allowed or path.stat().st_size > 256_000:
                    raise ValueError("Evidence outside scanned source inventory")
                raw = path.read_bytes()
                count = len(raw.decode("utf-8-sig").splitlines()) or 1
                start, end = ref["line"], ref.get("end", ref["line"])
                if type(start) is not int or type(end) is not int or not 1 <= start <= end <= count:
                    raise ValueError("Evidence line range is outside the source file")
                found.append(add_evidence(result, ref["path"], raw, start, end))
        if not found:
            raise ValueError("Enrichment requires evidence")
        return found

    for update in patch.get("node_updates", []):
        target = known[update["id"]]
        target["evidence"] = list(dict.fromkeys(target["evidence"] + refs(update.get("evidence", []))))
        for field in ("purpose", "inputs", "outputs", "label"):
            if field in update:
                target[field] = str(update[field])
        target["semantic_review"] = True
    for bucket in ("nodes", "edges", "findings"):
        for item in patch.get(bucket, []):
            item = copy.deepcopy(item)
            item["evidence"] = refs(item.get("evidence", []))
            item.setdefault("status", "inference")
            result[bucket].append(item)
    for view in patch.get("views", []):
        if any(v["id"] == view["id"] for v in result["views"]):
            raise ValueError("Enrichment view id already exists")
        result["views"].append(copy.deepcopy(view))
    result["project"]["agent_review"] = True
    # Include manually added components/edges in the global graph.
    for view in result["views"]:
        if view["id"] == "system":
            view["nodes"] = [n["id"] for n in result["nodes"] if n["group"] != "flow"]
            members = set(view["nodes"])
            view["edges"] = [e["id"] for e in result["edges"] if e["source"] in members and e["target"] in members]
    return validate(result)
