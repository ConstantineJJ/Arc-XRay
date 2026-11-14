from pathlib import Path
import shutil
import subprocess
import unittest


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
        self.assertNotIn(("UNIX-CLI" if expected == "WINDOWS-CLI" else "WINDOWS-CLI"), result.stdout)

    def test_git_bash_selects_windows_executable(self):
        self.run_platform("MINGW64_NT-10.0", "WINDOWS-CLI")

    def test_linux_bash_selects_native_command(self):
        self.run_platform("Linux", "UNIX-CLI")
