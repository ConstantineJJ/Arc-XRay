# Arc-XRay — current state

## 0.2.0 — 2026-11-15

User-requested direction: independent skill plugin, no MCP dependency, one blue
renderer and completion-gated source analysis in all host modes.

Runtime, viewer, translations and original icon now live inside skills/arc-xray/;
root launcher remains a convenience. Removed stdio server/configuration/SDK and
introduced five-area, implementation-module and execution-path review validation.
Large graphs retain every node with expandable grouping. Added PowerShell 5.1
installer and copyable shell-specific commands. Docs include upgrade guidance,
host capability limits and a Russian Discord description.

Checks: 20 Python unit/integration tests and 41 browser parity checks PASS locally.
Archive, isolated CLI install and standalone skill-only completed-fixture execution
PASS. Actual Windows PowerShell 5.1 and Bash dry runs PASS. Cross-platform CI is
a separate gate. Read-only Tools_C inventory produced 713 components/4,283
relationships; it is explicitly a survey, not a claimed semantic Tools_C audit.
Actual Git Bash installation from GitHub into the user environment PASS; the
installed 0.2.0 skill launcher starts and no MCP configuration is present. Git Bash
selects codex.exe on Windows, guarded by two platform-selection regression tests.
No native Chat model invocation is claimed by the automated browser harness.
Tools_C sources and installed private plugin caches remain unchanged. No .tooling
profile existed in this repository; no unrelated project integration was added.

Next owner-facing action after verification: replace 0.1.0 with the new ZIP in the
application, open a fresh chat and request the source-backed full audit. Do not
reuse an old MCP connection or a hand-authored simplified renderer.
