"""Bounded, source-level execution sketches, explicitly not runtime traces."""
import ast

from .model import add_evidence, identity


def build_flow(data, path, raw, entry, add_edge):
    title = getattr(entry, "name", "__main__ guard")
    view_id = identity("flow", f"{path}:{entry.lineno}")
    members, before = [], len(data["edges"])
    counter = 0
    truncated = False

    def add(label, kind, statement):
        nonlocal counter, truncated
        if counter >= 60:
            truncated = True
            return None
        counter += 1
        ref = add_evidence(data, path, raw, statement.lineno, getattr(statement, "end_lineno", statement.lineno))
        key = identity("step", f"{view_id}:{counter}")
        data["nodes"].append({"id": key, "label": label[:160], "path": path, "group": "flow", "kind": kind,
            "status": "verified", "purpose": "Source-level execution step. Connections show possible syntactic paths, not observed execution.",
            "inputs": "See source condition/arguments.", "outputs": "Possible next step; runtime values unknown.", "evidence": [ref]})
        members.append(key)
        return key

    def connect(sources, target, label="next"):
        if not target:
            return
        ref = next(n["evidence"][0] for n in reversed(data["nodes"]) if n["id"] == target)
        for source, pending_label in sources:
            add_edge(source, target, "control", pending_label or label, ref, "inference")

    start = add(title + " · start", "entry", entry)
    finish = add("return / end", "exit", entry)

    def sequence(statements, incoming, loop=None):
        current = incoming
        for statement in statements:
            if not current or truncated:
                break
            try:
                label = ast.unparse(statement).split("\n")[0]
            except RecursionError:
                label = type(statement).__name__
            kind = "decision" if isinstance(statement, ast.If) else "loop" if isinstance(statement, (ast.For, ast.While, ast.AsyncFor)) else "error" if isinstance(statement, (ast.Try, ast.Raise)) else "step"
            node = add(label, kind, statement)
            if node is None:
                break
            connect(current, node)
            if isinstance(statement, ast.If):
                yes = sequence(statement.body, [(node, "condition true")], loop)
                no = sequence(statement.orelse, [(node, "condition false")], loop) if statement.orelse else [(node, "condition false")]
                current = yes + no
            elif isinstance(statement, (ast.For, ast.While, ast.AsyncFor)):
                breaks = []
                body = sequence(statement.body, [(node, "iterate / true")], (node, breaks))
                connect(body, node, "loop back")
                current = sequence(statement.orelse, [(node, "exhausted / false")], loop) + breaks
            elif isinstance(statement, ast.Break) and loop:
                loop[1].append((node, "break"))
                current = []
            elif isinstance(statement, ast.Continue) and loop:
                connect([(node, "continue")], loop[0])
                current = []
            elif isinstance(statement, ast.Try):
                normal = sequence(statement.body, [(node, "try")], loop)
                normal = sequence(statement.orelse, normal, loop)
                handled = []
                for handler in statement.handlers:
                    handled += sequence(handler.body, [(node, "possible exception → handler")], loop)
                current = sequence(statement.finalbody, normal + handled, loop) if statement.finalbody else normal + handled
            elif isinstance(statement, (ast.Return, ast.Raise)):
                connect([(node, "return" if isinstance(statement, ast.Return) else "raise / propagation")], finish)
                current = []
            elif isinstance(statement, (ast.With, ast.AsyncWith)):
                current = sequence(statement.body, [(node, "enter context")], loop)
            else:
                current = [(node, "")]
        return current

    exits = sequence(entry.body, [(start, "")])
    connect(exits, finish)
    if truncated:
        data["coverage"]["limitations"].append(f"Execution sketch {path}:{entry.lineno} capped at 60 nodes.")
    data["views"].append({"id": view_id, "title": f"{path} · {title}", "category": "workflow",
        "description": "Possible source-level paths: branches, loops and exception handlers. Calls are not expanded; exceptions, finally/unwinding and async scheduling are approximated.",
        "nodes": members, "edges": [e["id"] for e in data["edges"][before:]]})
