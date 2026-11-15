from pathlib import Path
import shutil
import subprocess
import unittest
import json
import tempfile


class InstallerTests(unittest.TestCase):
    def run_platform(self, platform, expected):
        git_bash = Path("C:/Program Files/Git/bin/bash.exe")
        bash = str(git_bash) if git_bash.exists() else shutil.which("bash")
        if not bash:
            self.skipTest("Bash unavailable")
        script = r'''
uname() { printf '%s\n' PLATFORM; }
codex() { printf 'UNIX-CLI %s\n' "$*"; }
codex.exe() { printf 'WINDOWS-CLI %s\n' "$*"; }
source ./install.sh
'''.replace("PLATFORM", platform)
        result = subprocess.run([bash, "-c", script], capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn(expected + " plugin marketplace add ConstantineJJ/Arc-XRay", result.stdout)
        self.assertIn(expected + " plugin add arc-xray@arc-xray", result.stdout)
        self.assertIn(expected + " plugin marketplace upgrade arc-xray", result.stdout)
        self.assertNotIn(("UNIX-CLI" if expected == "WINDOWS-CLI" else "WINDOWS-CLI"), result.stdout)

    def test_git_bash_selects_windows_executable(self):
        self.run_platform("MINGW64_NT-10.0", "WINDOWS-CLI")

    def test_linux_bash_selects_native_command(self):
        self.run_platform("Linux", "UNIX-CLI")

    def test_git_bash_finds_desktop_outside_path(self):
        git_bash = Path("C:/Program Files/Git/bin/bash.exe")
        bash = str(git_bash) if git_bash.exists() else shutil.which("bash")
        if not bash:
            self.skipTest("Bash unavailable")
        with tempfile.TemporaryDirectory(prefix="arc-desktop-cli-") as tmp:
            root = Path(tmp)
            cli = root / "app/resources/codex.exe"
            cli.parent.mkdir(parents=True)
            cli.write_text('#!/usr/bin/env bash\nprintf "DESKTOP-CLI %s\\n" "$*"\n', encoding="utf-8")
            cli.chmod(0o755)
            script = r'''
uname() { printf '%s\n' MINGW64_NT; }
command() {
  if [[ "$1" == -v && ( "$2" == codex.exe || "$2" == codex ) ]]; then return 1; fi
  builtin command "$@"
}
powershell.exe() { printf '%s\n' DESKTOP; }
cygpath() { printf '%s\n' DESKTOP; }
source ./install.sh
'''.replace("DESKTOP;", "'" + root.as_posix().replace("'", "'\\''") + "';")
            result = subprocess.run([bash, "-c", script], capture_output=True, text=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("DESKTOP-CLI plugin add arc-xray@arc-xray", result.stdout)


class PowerShellInstallerTests(unittest.TestCase):
    def run_installer(self, *, desktop=False, missing=False, fail=False, check=False):
        windows_ps = Path("C:/Windows/System32/WindowsPowerShell/v1.0/powershell.exe")
        shell = str(windows_ps) if windows_ps.exists() else shutil.which("pwsh")
        if not shell:
            self.skipTest("PowerShell unavailable")
        installer = Path("install.ps1").read_text(encoding="utf-8")
        script = r'''
$ErrorActionPreference = 'Stop'
$script:arcCalls = [System.Collections.Generic.List[string]]::new()
function Invoke-ArcFakeCli {
    $script:arcCalls.Add(($args -join ' '))
    $global:LASTEXITCODE = 0
    if (FAIL -and ($args -join ' ') -eq 'plugin marketplace add ConstantineJJ/Arc-XRay') { $global:LASTEXITCODE = 7 }
}
function Get-Command {
    param($Name, $ErrorAction)
    if ($Name -eq 'Get-AppxPackage') { return [pscustomobject]@{ Source = 'Get-AppxPackage' } }
    if (DESKTOP -or MISSING) { return $null }
    return [pscustomobject]@{ Source = 'Invoke-ArcFakeCli' }
}
function Get-AppxPackage {
    param($Name, $ErrorAction)
    if (MISSING) { return $null }
    return [pscustomobject]@{ InstallLocation = 'desktop-root' }
}
function Join-Path { param($Path, $ChildPath) return 'Invoke-ArcFakeCli' }
function Test-Path { param($LiteralPath, $PathType) return (-not MISSING) }
$arcScript = [scriptblock]::Create(INSTALLER)
try {
    & $arcScript CHECK | Out-Null
    @{ calls = @($script:arcCalls); error = $null } | ConvertTo-Json -Compress
} catch {
    @{ calls = @($script:arcCalls); error = $_.Exception.Message } | ConvertTo-Json -Compress
}
'''
        for key, value in (("DESKTOP", desktop), ("MISSING", missing), ("FAIL", fail)):
            script = script.replace(key, "$true" if value else "$false")
        script = script.replace("INSTALLER", "'" + installer.replace("'", "''") + "'")
        script = script.replace("CHECK", "-CheckOnly" if check else "")
        result = subprocess.run([shell, "-NoProfile", "-Command", script], capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_path_cli_install(self):
        result = self.run_installer()
        self.assertIsNone(result["error"])
        self.assertIn("plugin add arc-xray@arc-xray", result["calls"])
        self.assertIn("plugin marketplace upgrade arc-xray", result["calls"])

    def test_desktop_cli_without_path(self):
        result = self.run_installer(desktop=True)
        self.assertIsNone(result["error"])
        self.assertIn("plugin add arc-xray@arc-xray", result["calls"])

    def test_missing_cli_explained(self):
        result = self.run_installer(missing=True)
        self.assertIn("Codex", result["error"])
        self.assertEqual(result["calls"], [])

    def test_failure_stops_before_plugin_install(self):
        result = self.run_installer(fail=True)
        self.assertIn("Marketplace registration failed", result["error"])
        self.assertNotIn("plugin add arc-xray@arc-xray", result["calls"])

    def test_check_only_does_not_install(self):
        result = self.run_installer(desktop=True, check=True)
        self.assertIsNone(result["error"])
        self.assertIn("plugin add --help", result["calls"])
        self.assertNotIn("plugin add arc-xray@arc-xray", result["calls"])
