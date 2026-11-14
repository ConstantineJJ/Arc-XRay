#!/usr/bin/env bash
# Uses supported Codex commands; does not edit config.toml or install Python.
set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  printf '%s\n' 'Usage: bash install.sh [--dry-run]' 'Requires Python 3.10+, Git and a Codex CLI with plugin marketplace/add support.'
  exit 0
fi
if [[ "${1:-}" == "--dry-run" ]]; then
  printf '%s\n' 'codex plugin marketplace add ConstantineJJ/Arc-XRay' 'codex plugin add arc-xray@arc-xray'
  exit 0
fi
if [[ $# -gt 0 ]]; then
  printf '%s\n' 'Unknown argument. Use --help.' >&2
  exit 2
fi
command -v codex >/dev/null || { printf '%s\n' 'Install/update the Codex CLI first: https://developers.openai.com/codex/cli' >&2; exit 1; }
command -v git >/dev/null || { printf '%s\n' 'Git is required for the repository marketplace.' >&2; exit 1; }
command -v python3 >/dev/null || { printf '%s\n' 'Python 3.10+ must be available as python3 (including to the desktop app).' >&2; exit 1; }
python3 -c 'import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)' || { printf '%s\n' 'Python 3.10 or newer is required.' >&2; exit 1; }
codex plugin marketplace add --help >/dev/null
codex plugin add --help >/dev/null
codex plugin marketplace add ConstantineJJ/Arc-XRay
codex plugin add arc-xray@arc-xray
printf '%s\n' 'Arc-XRay installed. Open a new local chat and select Arc-XRay.' 'The web/mobile app needs an accessible runtime; local installation alone does not provide one.'
