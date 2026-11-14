"""Build one portable plugin ZIP using an explicit, inspected runtime allowlist."""
import ast
import hashlib
import json
from pathlib import Path
import shutil
import struct
import sys
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills/arc-xray/scripts"))
from arc_xray import __version__

FILES = ["plugin.json", ".codex-plugin/plugin.json", "arc-xray.py", "LICENSE", "README.md", "README.ru.md", "CHANGELOG.md", "install.sh", "install.ps1"]
DIRECTORIES = ["skills", "docs"]


def package():
    manifest = json.loads((ROOT / "plugin.json").read_text(encoding="utf-8"))
    compat = json.loads((ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))
    assert manifest["$schema"] == "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
    assert manifest["name"] == compat["name"] == "arc-xray"
    assert manifest["version"] == compat["version"] == __version__
    interface = manifest["extensions"]["com.openai"]["interface"]
    assert len(interface["shortDescription"]) <= 30
    assert interface["category"] == compat["interface"]["category"] == "Developer Tools"
    assert compat["interface"]["defaultPrompt"] == interface["defaultPrompt"]
    assert not compat.get("mcpServers") and not (ROOT / "mcp.json").exists() and not (ROOT / ".mcp.json").exists()
    assert not manifest.get("apps") and not manifest["extensions"]["com.openai"].get("apps") and not compat.get("apps")
    for field in ("logo", "composerIcon"):
        path = (ROOT / interface[field]).resolve()
        assert path.is_relative_to(ROOT) and path.is_file() and path.stat().st_size <= 5 * 1024**2
        raw = path.read_bytes()
        assert raw[:8] == b"\x89PNG\r\n\x1a\n"
        width, height = struct.unpack(">II", raw[16:24])
        assert 48 <= width == height <= 4096
    files = [ROOT / name for name in FILES]
    for directory in DIRECTORIES:
        files.extend(p for p in (ROOT / directory).rglob("*") if p.is_file() and "__pycache__" not in p.parts)
    files = sorted(set(files))
    for path in files:
        assert not path.is_symlink()
        assert path.suffix not in {".pyc", ".pyo"}
        assert not any(p in {"node_modules", ".git", "sources", "tests"} for p in path.relative_to(ROOT).parts)
        if path.suffix == ".json":
            json.loads(path.read_text(encoding="utf-8"))
        elif path.suffix == ".py":
            ast.parse(path.read_text(encoding="utf-8"))
    destination = ROOT / "dist" / f"arc-xray-{__version__}.zip"
    destination.parent.mkdir(exist_ok=True)
    # ZIP lives outside this temporary plugin directory; no archive can include itself.
    with tempfile.TemporaryDirectory(prefix="arc-xray-package-") as tmp:
        stage = Path(tmp) / "arc-xray"
        for path in files:
            target = stage / path.relative_to(ROOT)
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(path, target)
        with zipfile.ZipFile(destination, "w", compression=zipfile.ZIP_DEFLATED) as archive:
            for path in files:
                relative = path.relative_to(ROOT)
                archive.write(stage / relative, "arc-xray/" + relative.as_posix())
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        names = archive.namelist()
        assert all(name.startswith("arc-xray/") for name in names)
        assert "arc-xray/skills/arc-xray/SKILL.md" in names
        assert "arc-xray/skills/arc-xray/scripts/viewer/app.js" in names
        assert "arc-xray/skills/arc-xray/scripts/arc_xray/scan.py" in names
        assert not any(name.endswith(("mcp.json", "server.py", "bridge.bundle.js")) for name in names)
        assert not any("marketplace" in name or ".app.json" in name for name in names)
        archived = json.loads(archive.read("arc-xray/plugin.json"))
        assert archived == manifest
    result = {"status": "PASS", "archive": str(destination), "version": __version__, "files": len(files),
              "sha256": hashlib.sha256(destination.read_bytes()).hexdigest(), "public_directory": "not submitted"}
    print(json.dumps(result))
    return destination


if __name__ == "__main__":
    package()
