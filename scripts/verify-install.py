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
sys.path.insert(0, str(ROOT / "skills/arc-xray/scripts"))
from arc_xray import __version__


def main():
    codex = shutil.which("codex")
    if not codex:
        print(json.dumps({"status": "SKIP", "reason": "Codex CLI not installed"}))
        return
    archive = ROOT / f"dist/arc-xray-{__version__}.zip"
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
        # Copy only the skill, as in a Chat code environment exposing skill resources.
        standalone = base / "standalone-skill"
        shutil.copytree(installed / "skills/arc-xray", standalone)
        output_atlas = base / "standalone-output"
        run = subprocess.run([sys.executable, "-B", str(standalone / "scripts/arc-xray.py"), "audit", str(ROOT / "examples/python-service"), "--out", str(output_atlas), "--enrichment", str(ROOT / "examples/python-review.json"), "--finalize"], capture_output=True, text=True, timeout=30)
        assert run.returncode == 0, run.stderr
        graph = json.loads((output_atlas / "atlas.json").read_text(encoding="utf-8"))
        assert graph["completion"]["status"] == "complete"
        assert graph["project"]["viewer_id"] == "arc-xray-blue-v1"
        assert not (installed / "mcp.json").exists() and not (installed / ".mcp.json").exists()
        result = {"status": "PASS", "steps": ["marketplace registered", "plugin installed", "installed launcher executed", "skill-only runtime created complete audit without MCP"],
                  "native_chat_invocation": "not exercised by CLI install", "results": logs, "doctor": json.loads(doctor.stdout)}
        output = ROOT / ".test-output/install-verification.json"
        output.parent.mkdir(exist_ok=True)
        output.write_text(json.dumps(result, indent=2), encoding="utf-8")
        print(json.dumps({key: value for key, value in result.items() if key != "results"}))


if __name__ == "__main__":
    main()
