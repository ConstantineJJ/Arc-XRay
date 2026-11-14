"""Exercise real local plugin installation in disposable child-process settings."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent


def main():
    codex = shutil.which("codex")
    if not codex:
        print(json.dumps({"status": "SKIP", "reason": "Codex CLI not installed"}))
        return
    archive = ROOT / "dist/arc-xray-0.1.0.zip"
    with tempfile.TemporaryDirectory(prefix="arc-xray-install-") as tmp:
        base = Path(tmp)
        market = base / "marketplace"
        plugins = market / "plugins"
        plugins.mkdir(parents=True)
        with zipfile.ZipFile(archive) as bundle:
            bundle.extractall(plugins)
        catalog = market / ".agents/plugins/marketplace.json"
        catalog.parent.mkdir(parents=True)
        catalog.write_text(json.dumps({"name": "arc-xray-test", "interface": {"displayName": "Arc-XRay isolated verification"},
            "plugins": [{"name": "arc-xray", "source": {"source": "local", "path": "./plugins/arc-xray"},
                "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"}, "category": "Developer Tools"}]}), encoding="utf-8")
        # Configure only the spawned CLI, never the running agent/client or user's settings.
        child_environment = os.environ.copy()
        child_environment["CODEX_HOME"] = str(base / "isolated-settings")
        (base / "isolated-settings").mkdir()
        logs = []
        for args in (["plugin", "marketplace", "add", str(market), "--json"],
                     ["plugin", "add", "arc-xray@arc-xray-test", "--json"],
                     ["plugin", "list", "--json"]):
            completed = subprocess.run([codex, *args], env=child_environment, capture_output=True, text=True, timeout=60)
            if completed.returncode:
                raise RuntimeError(completed.stderr or completed.stdout)
            logs.append(json.loads(completed.stdout))
        installed = Path(logs[1]["installedPath"])
        doctor = subprocess.run([sys.executable, "-B", str(installed / "arc-xray.py"), "doctor"], capture_output=True, text=True, timeout=15)
        assert doctor.returncode == 0, doctor.stderr
        requests = [{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}},
                    {"jsonrpc": "2.0", "id": 2, "method": "tools/list"},
                    {"jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": {"uri": "ui://arc-xray/atlas"}}]
        startup = subprocess.run([sys.executable, "-B", str(installed / "arc-xray.py"), "mcp", "--data-dir", str(base / "data")],
                                 input="\n".join(json.dumps(r) for r in requests) + "\n", capture_output=True, text=True, timeout=15)
        responses = [json.loads(line) for line in startup.stdout.splitlines()]
        assert startup.returncode == 0 and len(responses) == 3, startup.stderr
        assert len(responses[1]["result"]["tools"]) == 4
        assert "ontoolresult" in responses[2]["result"]["contents"][0]["text"]
        result = {"status": "PASS", "steps": ["marketplace registered", "plugin installed", "plugin listed", "installed launcher executed", "installed MCP discovered four tools and UI resource"],
                  "native_client_render": "not exercised by CLI install", "results": logs, "doctor": json.loads(doctor.stdout)}
        output = ROOT / ".test-output/install-verification.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps({key: value for key, value in result.items() if key != "results"}))


if __name__ == "__main__":
    main()
