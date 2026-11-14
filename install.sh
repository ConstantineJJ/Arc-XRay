#!/usr/bin/env bash
# Uses supported Codex commands; does not edit config.toml or install Python.
set -euo pipefail

if [[ "${1:-}" == "--help" ]]; then
  printf '%s\n' 'Usage: bash install.sh [--dry-run]' 'Requires Git and a Codex CLI with plugin marketplace/add support. Runtime uses host Python 3.10+.'
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
arc_codex_bin=codex
case "$(uname -s 2>/dev/null || true)" in
  MINGW*|MSYS*|CYGWIN*)
    # The desktop distribution can contain both a foreign-platform `codex`
    # binary and the Windows executable. Git Bash resolves the bare name first.
    if command -v codex.exe >/dev/null; then arc_codex_bin=codex.exe; fi
    ;;
esac
command -v "$arc_codex_bin" >/dev/null || { printf '%s\n' 'Install/update the Codex CLI first: https://developers.openai.com/codex/cli' >&2; exit 1; }
command -v git >/dev/null || { printf '%s\n' 'Git is required for the repository marketplace.' >&2; exit 1; }
"$arc_codex_bin" plugin marketplace add --help >/dev/null
"$arc_codex_bin" plugin add --help >/dev/null
"$arc_codex_bin" plugin marketplace add ConstantineJJ/Arc-XRay
"$arc_codex_bin" plugin add arc-xray@arc-xray
printf '%s\n' 'Arc-XRay installed. Open a new chat and select Arc-XRay. No MCP server is required.' 'Audit needs readable sources and a Python/file environment supplied by the host.'
