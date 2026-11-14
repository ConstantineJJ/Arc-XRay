"""Offline and embedded renderers for the same versioned atlas model."""
import base64
import html
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from .model import validate

PACKAGE_ROOT = Path(__file__).resolve().parent.parent
OWNED_FILES = {"index.html", "atlas.json", "REPORT.md", "COMPONENTS.md", "architecture.drawio", "flows.md", ".arc-xray-output"}
MARKER = "Arc-XRay generated output v1\n"


def html_document(data, language="en", embedded=False):
    if language not in {"en", "ru"}:
        raise ValueError("Language must be en or ru")
    if data is not None:
        validate(data)
    template = (PACKAGE_ROOT / "viewer/index.html").read_text(encoding="utf-8")
    style = (PACKAGE_ROOT / "viewer/style.css").read_text(encoding="utf-8")
    app = (PACKAGE_ROOT / "viewer/app.js").read_text(encoding="utf-8")
    bridge = (PACKAGE_ROOT / "viewer/bridge.bundle.js").read_text(encoding="utf-8") if embedded else ""
    icon = base64.b64encode((PACKAGE_ROOT / "assets/arc-xray.png").read_bytes()).decode("ascii")
    payload = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    return template.replace("__ICON__", icon).replace("/*__STYLE__*/", style).replace("/*__DATA__*/", payload).replace("__LANG__", language).replace("__EMBEDDED__", str(embedded).lower()).replace("/*__APP__*/", app.replace("</script", "<\\/script")).replace("/*__BRIDGE__*/", bridge.replace("</script", "<\\/script"))


def drawio_document(data):
    root = ET.Element("mxfile", {"host": "Arc-XRay", "version": "0.1.0"})
    nodes = {n["id"]: n for n in data["nodes"]}
    edges = {e["id"]: e for e in data["edges"]}
    for view in data["views"]:
        diagram = ET.SubElement(root, "diagram", {"id": view["id"], "name": view["title"]})
        graph = ET.SubElement(diagram, "mxGraphModel", {"dx": "1200", "dy": "800", "grid": "1", "gridSize": "10", "page": "0"})
        cells = ET.SubElement(graph, "root")
        ET.SubElement(cells, "mxCell", {"id": "0"})
        ET.SubElement(cells, "mxCell", {"id": "1", "parent": "0"})
        for index, key in enumerate(view["nodes"]):
            node = nodes[key]
            attrs = {"id": key, "value": node["label"], "vertex": "1", "parent": "1",
                     "style": "rounded=1;whiteSpace=wrap;html=0;fillColor=#26383e;strokeColor=#59e1cf;fontColor=#e1edf0;fontSize=16;",
                     "tooltip": node["purpose"] + "\n" + ", ".join(f"{data['evidence'][r]['path']}:{data['evidence'][r]['line']}" for r in node["evidence"])}
            cell = ET.SubElement(cells, "mxCell", attrs)
            ET.SubElement(cell, "mxGeometry", {"x": str(40 + index % 4 * 330), "y": str(40 + index // 4 * 170), "width": "280", "height": "115", "as": "geometry"})
        for index, key in enumerate(view["edges"]):
            edge = edges[key]
            color = ["#78d5f7", "#f2bc70", "#bb9cff", "#7dd6aa", "#f491b7", "#d6d782"][index % 6]
            pattern = "" if edge["kind"] == "data" else "dashed=1;dashPattern=" + ("9 5;" if edge["kind"] == "control" else "2 5;")
            cell = ET.SubElement(cells, "mxCell", {"id": key, "value": edge["label"], "edge": "1", "parent": "1", "source": edge["source"], "target": edge["target"],
                "style": f"edgeStyle=orthogonalEdgeStyle;rounded=1;html=0;endArrow=block;strokeColor={color};fontSize=12;{pattern}"})
            ET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
    return ET.tostring(root, encoding="unicode", xml_declaration=True)


def mermaid_document(data):
    nodes, edges = {n["id"]: n for n in data["nodes"]}, {e["id"]: e for e in data["edges"]}
    out = ["# Arc-XRay — architecture views", "", "Arrow key: solid = data, dashed = control, dotted = dependency. Source evidence is in atlas.json.", ""]
    for view in data["views"]:
        selected = view["nodes"][:80]
        names = {key: "n" + str(i) for i, key in enumerate(selected)}
        out += ["## " + view["title"], "", view["description"], ""]
        if len(selected) < len(view["nodes"]):
            out += [f"Showing {len(selected)} of {len(view['nodes'])} components. The interactive atlas and draw.io retain the complete view.", ""]
        out += ["```mermaid", "flowchart TD"]
        for key in selected:
            label = html.escape(nodes[key]["label"], quote=True).replace("`", "&#96;").replace("\n", " ")
            out.append(f'  {names[key]}["{label}"]')
        for key in view["edges"]:
            e = edges[key]
            if e["source"] in names and e["target"] in names:
                arrow = "-->" if e["kind"] == "data" else "-.->"
                out.append(f"  {names[e['source']]} {arrow}|{e['kind']}| {names[e['target']]}")
        out += ["```", ""]
    return "\n".join(out)


def markdown_report(data, language):
    ru = language == "ru"
    title = "Отчёт об архитектуре" if ru else "Architecture review"
    out = [f"# {data['project']['name']} — {title}", "", data["project"]["created_at"], "",
        "Аудит исходников без запуска и изменений кода." if ru else "Read-only source audit. Project code was not executed.", "",
        f"{data['coverage']['analyzed_files']} files · {len(data['nodes'])} components · {len(data['edges'])} relationships · {len(data['findings'])} observations.", "",
        ("Смысловое ревью агента добавлено." if ru else "Includes agent semantic review.") if data["project"]["agent_review"] else
        ("Это автоматическое исследование; смысловое ревью агента ещё не добавлено." if ru else "Automatic survey only; semantic agent review has not been added."), "",
        "## Покрытие и ограничения" if ru else "## Coverage and limitations", "",
        "File/byte limit reached: " + str(data["coverage"]["truncated"]), ""]
    out += ["- " + limit for limit in data["coverage"]["limitations"]]
    out += ["", "## Риски и несоответствия" if ru else "## Risks and inconsistencies", ""]
    if not data["findings"]:
        out += ["Автоматические правила не выявили наблюдений; это не гарантия отсутствия проблем." if ru else "No automatic observations; this is not a guarantee that problems are absent.", ""]
    for f in data["findings"]:
        out += ["### " + f["title"], "", f"{f['id']} · {f['severity']} · {f['status']} · {f['rule']}", ""]
        for key, en, russian in [("observation", "Observation", "Наблюдение"), ("impact", "Potential impact", "Возможное последствие"), ("proposal", "Follow-up", "Предлагаемая проверка")]:
            out += ["**" + (russian if ru else en) + ".** " + f[key], ""]
        for ref in f["evidence"]:
            e = data["evidence"][ref]
            out += [f"- `{e['path']}:{e['line']}–{e['end']}` · SHA-256 `{e['sha256']}`"]
        out += [""]
    out += ["## Неразрешённые ссылки" if ru else "## Unresolved references", ""]
    out += [f"- `{x['path']}:{x['line']}` → `{x['reference']}`" for x in data["coverage"]["unresolved"]]
    out += ["", "## Пропущенные файлы" if ru else "## Skipped files", ""]
    out += [f"- `{x['path']}`: {x['reason']}" for x in data["coverage"]["skipped"]]
    return "\n".join(out) + "\n"


def component_document(data, language):
    out = ["# " + ("Компоненты" if language == "ru" else "Components"), ""]
    for n in data["nodes"]:
        out += ["## " + n["label"], "", f"`{n['id']}` · {n['kind']} · {n['status']}", "", n["purpose"], "", "Input: " + n["inputs"], "", "Output: " + n["outputs"], ""]
        for ref in n["evidence"]:
            e = data["evidence"][ref]
            out.append(f"- `{e['path']}:{e['line']}–{e['end']}`")
        out += [""]
    return "\n".join(out)


def render(data, output, *, language="en"):
    validate(data)
    output = Path(output)
    # Do not replace a symlinked path or overwrite an unrelated documentation folder.
    current = output.absolute()
    while current != current.parent:
        if current.is_symlink() or (hasattr(current, "is_junction") and current.is_junction()):
            raise ValueError("Output cannot contain symbolic links")
        current = current.parent
    output = output.resolve()
    marker = output / ".arc-xray-output"
    if output.exists() and any(output.iterdir()):
        if not marker.is_file() or marker.read_text(encoding="utf-8") != MARKER:
            raise ValueError("Output directory is not owned by Arc-XRay; choose an empty/new directory")
    for name in OWNED_FILES:
        if (output / name).is_symlink():
            raise ValueError("Generated files cannot be symbolic links")
    # Build before touching the output, so a missing bundled viewer cannot leave a partial run.
    content = {"index.html": html_document(data, language), "atlas.json": json.dumps(data, ensure_ascii=False, indent=2) + "\n",
        "REPORT.md": markdown_report(data, language), "COMPONENTS.md": component_document(data, language),
        "architecture.drawio": drawio_document(data), "flows.md": mermaid_document(data), ".arc-xray-output": MARKER}
    output.mkdir(parents=True, exist_ok=True)
    for name, value in content.items():
        path = output / name
        temporary = path.with_name(path.name + ".arc-tmp")
        if temporary.exists() or temporary.is_symlink():
            raise ValueError("Temporary output name already exists")
        try:
            temporary.write_text(value, encoding="utf-8", newline="\n")
            temporary.replace(path)
        finally:
            if temporary.exists():
                temporary.unlink()
    return {"index": str(output / "index.html"), "output": str(output), "files": sorted(content)}
