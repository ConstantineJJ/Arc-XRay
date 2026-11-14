import _paths
import copy
from pathlib import Path
import tempfile
import unittest

from arc_xray.assess import assess, require_complete
from arc_xray.model import enrich
from arc_xray.scan import scan


class CompletionTests(unittest.TestCase):
    def test_survey_cannot_be_misreported_as_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("def main():\n    return 1\n")
            data = scan(root)
            self.assertEqual(assess(data)["status"], "survey")
            with self.assertRaises(ValueError):
                require_complete(data)
            self.assertEqual(assess(enrich(data, {}, root))["status"], "survey")

    def test_complete_requires_five_areas_files_and_execution_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "main.py").write_text("def main():\n    return 1\n")
            data = scan(root)
            node = data["nodes"][0]
            ref = node["evidence"][0]
            patch = {"node_updates": [{"id": node["id"], "purpose": "Entrypoint", "inputs": "No arguments", "outputs": "Returns integer 1", "evidence": [ref]}],
                "assessment": {area: {"status": "reviewed", "summary": "Inspected this boundary in the single-module fixture.", "evidence": [ref]}
                    for area in ("architecture", "dependencies", "data", "execution", "review")}}
            patch["assessment"]["execution"]["paths"] = {key: {"status": "reviewed" if key == "success" else "not_applicable", "summary": "Returns 1; no error handler/retry/cancellation exists in this function.", "evidence": [ref]} for key in ("success", "error", "retry_or_cancellation")}
            result = enrich(data, patch, root)
            self.assertEqual(require_complete(result)["status"], "complete")
            partial = copy.deepcopy(result)
            partial["assessment"]["data"]["status"] = "partial"
            with self.assertRaises(ValueError):
                require_complete(partial)
            result["coverage"]["truncated"] = True
            with self.assertRaises(ValueError):
                require_complete(result)
