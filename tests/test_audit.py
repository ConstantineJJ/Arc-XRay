import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from arc_xray.scan import scan
from arc_xray.model import validate, enrich


class AuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def put(self, name, text):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        return path

    def test_python_edges_cycles_flow_evidence_and_read_only(self):
        self.put("main.py", 'from service import run\n\nif __name__ == "__main__":\n    run()\n')
        self.put("service.py", 'import store\n\ndef run():\n    for item in [1, 2]:\n        if item:\n            store.save(item)\n    try:\n        exec("pass")\n    except Exception:\n        pass\n')
        self.put("store.py", 'import service\n\ndef save(value):\n    return value\n')
        before = {p.name: p.read_bytes() for p in self.root.iterdir()}
        data = scan(self.root)
        validate(data)
        self.assertEqual(before, {p.name: p.read_bytes() for p in self.root.iterdir()})
        modules = {n["path"]: n["id"] for n in data["nodes"] if n["kind"] == "module"}
        self.assertTrue(any(e["source"] == modules["main.py"] and e["target"] == modules["service.py"] and e["kind"] == "dependency" for e in data["edges"]))
        self.assertTrue(any(e["kind"] == "control" for e in data["edges"]))
        self.assertTrue(any(n["kind"] == "decision" for n in data["nodes"]))
        self.assertTrue(any(n["kind"] == "loop" for n in data["nodes"]))
        self.assertTrue(any(f["rule"] == "dependency-cycle" for f in data["findings"]))
        self.assertTrue(any(f["rule"] == "dynamic-execution" for f in data["findings"]))
        for e in data["edges"]:
            self.assertTrue(e["evidence"])
            for ref in e["evidence"]:
                anchor = data["evidence"][ref]
                self.assertEqual(anchor["sha256"], hashlib.sha256((self.root / anchor["path"]).read_bytes()).hexdigest())
        self.assertNotIn(str(self.root), json.dumps(data))

    def test_typescript_relative_and_external_imports(self):
        self.put("src/main.ts", "import {run} from './service';\nimport express from 'express';\nrun();\n")
        self.put("src/service.ts", "export function run() { return 1; }\n")
        data = scan(self.root)
        validate(data)
        self.assertTrue(any(n["kind"] == "external" and n["label"] == "express" for n in data["nodes"]))
        self.assertTrue(any(e["kind"] == "dependency" and e["status"] == "inference" for e in data["edges"]))
        self.assertTrue(any("lexical" in str(x).lower() for x in data["coverage"]["limitations"]))

    def test_excluded_secrets_ignored_output_bounds_and_bad_syntax(self):
        self.put(".env", "SECRET=do-not-include")
        self.put("credentials.json", '{"password":"do-not-include"}')
        self.put("node_modules/lib/index.js", "SECRET=do-not-include")
        self.put("docs/architecture-review/index.html", "do-not-include")
        self.put("a.py", "def broken(:\n")
        self.put("b.py", "pass\n")
        data = scan(self.root, max_files=1)
        self.assertNotIn("do-not-include", json.dumps(data))
        self.assertTrue(data["coverage"]["truncated"])
        self.assertTrue(any(f["rule"] == "parse-error" for f in data["findings"]))

    def test_import_resolution_does_not_invent_symbols_as_modules(self):
        self.put("pkg/__init__.py", "from .worker import run\n")
        self.put("pkg/worker.py", "def run():\n    pass\n")
        self.put("main.py", "from pkg.worker import run\n")
        data = scan(self.root)
        self.assertFalse(any(n["label"] == "pkg.worker.run" for n in data["nodes"]))

    def test_unresolved_relative_import_is_unknown_not_external_package(self):
        self.put("main.ts", "import x from './missing';\n")
        data = scan(self.root)
        self.assertFalse(any(n["kind"] == "external" for n in data["nodes"]))
        self.assertTrue(data["coverage"]["unresolved"])

    def test_enrichment_requires_real_evidence(self):
        self.put("main.py", "pass\n")
        data = scan(self.root)
        invalid = {"findings": [{"id": "A1", "title": "Invented", "evidence": ["missing"]}]}
        with self.assertRaises(ValueError):
            enrich(data, invalid, self.root)


if __name__ == "__main__":
    unittest.main()
