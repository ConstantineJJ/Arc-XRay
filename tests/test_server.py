import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from arc_xray.server import Server


class ServerTests(unittest.TestCase):
    def test_protocol_and_resource(self):
        with tempfile.TemporaryDirectory() as tmp:
            server = Server(Path(tmp))
            initialized = server.handle("initialize", {"protocolVersion": "2025-11-25"})
            self.assertIn("tools", initialized["capabilities"])
            tools = server.handle("tools/list", {})["tools"]
            self.assertIn("arc_xray_audit", [t["name"] for t in tools])
            resource = server.handle("resources/read", {"uri": "ui://arc-xray/atlas"})["contents"][0]
            self.assertEqual(resource["mimeType"], "text/html;profile=mcp-app")
            self.assertIn("ontoolresult", resource["text"])
            self.assertIn("openai/ui", resource["_meta"])

    def test_audit_opens_same_atlas_and_restricts_scope(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "fixture"
            root.mkdir()
            (root / "main.py").write_text("pass\n")
            server = Server(Path(tmp) / "data", [root])
            result = server.handle("tools/call", {"name": "arc_xray_audit", "arguments": {"project_path": str(root)}})
            self.assertFalse(result.get("isError", False))
            atlas_id = result["structuredContent"]["atlas_id"]
            opened = server.handle("tools/call", {"name": "arc_xray_open", "arguments": {"atlas_id": atlas_id}})
            self.assertEqual(opened["_meta"]["atlas"]["project"]["name"], "fixture")
            denied = server.handle("tools/call", {"name": "arc_xray_audit", "arguments": {"project_path": str(Path(tmp))}})
            self.assertTrue(denied["isError"])
            invalid = server.handle("tools/call", {"name": "arc_xray_open", "arguments": {"atlas_id": "../../outside"}})
            self.assertTrue(invalid["isError"])

    def test_stdio_is_json_lines_and_errors_do_not_crash(self):
        requests = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
                    {"jsonrpc": "2.0", "method": "notifications/initialized"},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                    {"jsonrpc": "2.0", "id": 3, "method": "unknown"}]
        with tempfile.TemporaryDirectory() as tmp:
            result = subprocess.run([sys.executable, "-B", "arc-xray.py", "mcp", "--data-dir", tmp],
                input="\n".join(json.dumps(r) for r in requests) + "\n", text=True, capture_output=True, timeout=15)
            self.assertEqual(result.returncode, 0, result.stderr)
            responses = [json.loads(line) for line in result.stdout.splitlines()]
            self.assertEqual([r["id"] for r in responses], [1, 2, 3])
            self.assertEqual(responses[-1]["error"]["code"], -32601)

    def test_sessions_survive_a_new_server_and_another_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            first, second = base / "first", base / "second"
            for path in (first, second):
                path.mkdir()
                (path / "main.py").write_text("pass\n")
            one = Server(base / "data").handle("tools/call", {"name": "arc_xray_audit", "arguments": {"project_path": str(first)}})
            two = Server(base / "data")
            two.handle("tools/call", {"name": "arc_xray_audit", "arguments": {"project_path": str(second)}})
            again = Server(base / "data")
            self.assertIn(one["structuredContent"]["atlas_id"], again.sessions)


if __name__ == "__main__":
    unittest.main()
