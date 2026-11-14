# Verification — Arc-XRay 0.2.0

2026-11-15, Europe/Riga. Evidence is scoped to the checks performed.

- PASS: 20 Python unit/integration checks cover source edges, read-only behavior,
  evidence freshness, report/localization/exports and survey/completion gates.
- PASS: 41 browser checks exercise the canonical blue file, map/tree/search/filter,
  source inspectors, pan/zoom, logs and save-cancellation, focus mode, responsive
  widths 320–3840, and rendering the exact same HTML/model in an iframe preview.
- PASS: a 180-component graph retains all 180 components and can expand them all;
  no first-120 truncation. No browser script errors or runtime network requests.
- PASS: package/install: scripts/package.py and scripts/verify-install.py verify a
  standalone skill installed through the CLI. No MCP manifests/server/SDK are
  bundled. The skill-only copy must produce a completion-gated fixture atlas.
- Windows PowerShell 5.1 and Git Bash installers have non-mutating dry runs.
- Native Chat/Work model invocation remains a separate acceptance item; browser
  parity does not prove an agent actually followed every instruction. If host
  source/Python/preview capabilities are absent, report them instead of improvising.
- Source correctness/performance/security are not certified by structural tests.

Version 0.1 showed a blank MCP panel in user screenshots and alternative agent-
written simplified HTML. Version 0.2 removes that dependency and packages one
renderer; it does not claim an inaccessible host can execute code automatically.

Русский: проверки архива и браузера не подменяют фактический вызов агентом в
обычном Chat. Полнота означает исследованную статическую область с доказательствами,
а не гарантию отсутствия ошибок. Исходники Tools_C не изменялись.

- PASS: actual Git Bash install in the user environment; installed 0.2.0 doctor reports mcp_required=false. Shell regression tests verify Windows exe/native Unix selection.
