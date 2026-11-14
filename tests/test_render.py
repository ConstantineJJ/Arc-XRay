import _paths
import json
import re
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from arc_xray.scan import scan
from arc_xray.render import render, html_document


class RenderTests(unittest.TestCase):
    def test_source_template_tokens_are_not_interpreted_during_rendering(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text('"""Contains /*__APP__*/ and __LANG__ as source evidence."""\n', encoding="utf-8")
            data = scan(root)
            html = html_document(data, "ru")
            embedded = re.search(r'<script id="atlas-data" type="application/json">(.*?)</script>', html, re.S).group(1)
            self.assertEqual(json.loads(embedded), data)

    def test_artifacts_are_self_contained_and_xml_edges_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "project"
            root.mkdir()
            (root / "main.py").write_text("import service\n", encoding="utf-8")
            (root / "service.py").write_text("pass\n", encoding="utf-8")
            data = scan(root, name="Fixture </script><script>window.pwned=1</script>")
            output = Path(tmp) / "atlas"
            render(data, output, language="ru")
            html = (output / "index.html").read_text(encoding="utf-8")
            self.assertNotIn("<script>window.pwned", html)
            self.assertNotIn('src="http', html)
            self.assertIn("data:image/png;base64,", html)
            xml = ET.parse(output / "architecture.drawio")
            self.assertEqual(len(xml.findall("diagram")), len(data["views"]))
            diagram = xml.find("diagram/mxGraphModel/root")
            cells = {c.attrib["id"]: c for c in diagram}
            edges = [c for c in cells.values() if c.attrib.get("edge") == "1"]
            self.assertEqual(len(edges), len(data["views"][0]["edges"]))
            for edge in edges:
                self.assertIn(edge.attrib["source"], cells)
                self.assertIn(edge.attrib["target"], cells)
            self.assertEqual(json.loads((output / "atlas.json").read_text(encoding="utf-8"))["schema_version"], 1)

    def test_render_refuses_overwriting_unowned_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "index.html").write_text("Owner file", encoding="utf-8")
            data = scan(root)
            with self.assertRaises(ValueError):
                render(data, root)
            self.assertEqual((root / "index.html").read_text(), "Owner file")

    def test_preview_uses_same_data_document_without_server(self):
        html = html_document(None, "en")
        self.assertIn("Arc-XRay", html)
        self.assertIn("ArcXRay", html)
        self.assertNotIn("mcp-app", html)
        self.assertNotIn("/*__DATA__*/", html)

    def test_output_resolves_parent_alias_without_replacing_link_destination(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp).resolve()
            target = base / "real"
            target.mkdir()
            alias = base / "alias"
            try:
                alias.symlink_to(target, target_is_directory=True)
            except OSError:
                self.skipTest("Creating directory symlinks is not permitted on this host")
            root = base / "source"
            root.mkdir()
            (root / "main.py").write_text("pass\n")
            render(scan(root), alias / "atlas")
            self.assertTrue((target / "atlas/index.html").exists())
            with self.assertRaises(ValueError):
                render(scan(root), alias)

    def test_russian_report_translates_generated_findings(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source"
            root.mkdir()
            (root / "main.py").write_text('eval("1")\n', encoding="utf-8")
            output = Path(tmp) / "atlas"
            render(scan(root), output, language="ru")
            report = (output / "REPORT.md").read_text(encoding="utf-8")
            self.assertIn("Вызов динамического выполнения кода", report)
            self.assertIn("содержит вызов eval", report)
            self.assertNotIn("Dynamic code execution call", report)


if __name__ == "__main__":
    unittest.main()
