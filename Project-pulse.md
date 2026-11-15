# Arc-XRay — current state

## 0.2.1 — 2026-11-15

User screenshots showed Bash syntax pasted into PowerShell and a separate Chat
agent replacing the renderer after failing to execute local Python. Added simple
one-line commands by shell and automatic Windows desktop CLI discovery outside
PATH. No PATH, execution-policy or unrelated plugin changes are made.

The skill now requires packaged doctor execution and source access before an
atlas promise; documents source/skill transfer to a separate Python environment
and explicitly stops instead of inventing HTML or unsolicited CMD launchers.
This is an instruction improvement, not a grant of missing host capabilities.

Checks: 26 Python checks and 41 browser checks PASS. Real PowerShell 5.1 desktop
discovery with the ordinary PATH passes without installation. New regressions
cover missing PATH, missing CLI, registration failure and check-only behavior.
Package validation and isolated CLI install of 0.2.1 PASS, including a skill-only
completed fixture atlas. Both PowerShell and Git Bash check-only discovery pass
with the ordinary user/machine PATH. Release and native Chat acceptance are
separate gates. Native
Chat generation has not been re-tested by the agent; the user's screenshot of
the previous substitute HTML is not an accepted canonical atlas.

Publication verified: main CI on da4f36c passes Windows/Linux/macOS and viewer
checks. The exact remote `irm .../install.ps1 | iex` command run in PowerShell 5.1
with the ordinary PATH installed 0.2.1 into the user environment; the installed
doctor confirms version, blue viewer and no MCP requirement. Remote Bash check
also passes. GitHub release v0.2.1 is published; all 38 downloaded ZIP members
match the tagged Git source byte-for-byte. Original icon is retained. The only
native Chat acceptance still outstanding is a fresh agent invocation following
the new preflight and canonical generation path.

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
