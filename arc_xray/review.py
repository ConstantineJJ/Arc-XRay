"""Conservative static observations; potential consequences are not runtime proof."""
from .model import identity


def finding(data, rule, title, observation, impact, proposal, nodes, evidence, severity="medium", status="inference"):
    data["findings"].append({"id": identity("risk", rule + ":" + ":".join(nodes) + ":" + ":".join(evidence)),
        "rule": rule, "title": title, "severity": severity, "status": status,
        "observation": observation, "impact": impact, "proposal": proposal,
        "nodes": nodes, "evidence": evidence})


def review_graph(data):
    modules = {n["id"]: n for n in data["nodes"] if n["kind"] == "module"}
    graph = {key: set() for key in modules}
    edges = [e for e in data["edges"] if e["kind"] == "dependency" and e["source"] in modules and e["target"] in modules]
    for edge in edges:
        graph[edge["source"]].add(edge["target"])
    # Iterative Kosaraju avoids recursion failure on deep repository graphs.
    visited, order = set(), []
    for root in graph:
        stack = [(root, False)]
        while stack:
            node, done = stack.pop()
            if done:
                order.append(node)
            elif node not in visited:
                visited.add(node)
                stack.append((node, True))
                stack.extend((n, False) for n in sorted(graph[node], reverse=True) if n not in visited)
    reverse = {n: set() for n in graph}
    for a, targets in graph.items():
        for b in targets:
            reverse[b].add(a)
    visited.clear()
    for root in reversed(order):
        if root in visited:
            continue
        component, stack = [], [root]
        while stack:
            node = stack.pop()
            if node in visited:
                continue
            visited.add(node)
            component.append(node)
            stack.extend(reverse[node] - visited)
        if len(component) > 1 or root in graph[root]:
            selected = sorted(component)
            refs = sorted({ref for e in edges if e["source"] in selected and e["target"] in selected for ref in e["evidence"]})
            finding(data, "dependency-cycle", "Cyclic module dependencies",
                    "Static dependency cycle: " + " → ".join(modules[n]["path"] for n in selected) + ".",
                    "May complicate initialization, testing and independent changes. Deferred imports can be intentional; this is not an import-failure claim.",
                    "Inspect initialization order and dependency direction before proposing a change.", selected, refs)
    for node, targets in graph.items():
        if len(targets) >= 12:
            finding(data, "high-coupling", "Module depends on many local components",
                    f"{modules[node]['path']} references {len(targets)} local modules.",
                    "Changes may have a wider coordination cost. This threshold is a review heuristic, not a defect or measured bottleneck.",
                    "Review responsibility boundaries and which dependencies are intentional.", [node], modules[node]["evidence"], "low")
    for node in modules.values():
        if node.get("lines", 0) >= 800:
            finding(data, "large-module", "Large source module",
                    f"{node['path']} has {node['lines']} lines.",
                    "May increase navigation and review cost; line count does not prove poor design or slow execution.",
                    "Inspect responsibility cohesion and actual change patterns.", [node["id"]], node["evidence"], "low")
