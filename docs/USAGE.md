# Arc-XRay 0.2 guide

Install the ZIP through Plugins or use the shell-specific commands in README.
No MCP setup is involved. All runtime/viewer files are under skills/arc-xray/.
Source-access and Python execution are provided by the host, independently of
plugin installation. Upload sources if a Chat cannot read your local project.

When a terminal prompt starts with `PS`, use the one-line PowerShell installer in
README. Bash syntax will not work there. The installer detects the desktop CLI;
users do not need to enter path variables or change PATH.

Start with the [host execution check](../skills/arc-xray/references/host-environments.md).
Chat's Python environment and local source may be separate; transfer the actual
source snapshot and complete skill when possible. If execution is unavailable,
report the blocker and stop rather than creating substitute HTML or a CMD launcher.

## Workflow

1. The agent loads the full SKILL.md and supporting references, locates its bundled
   scripts/arc-xray.py, and establishes actual source/output paths.
2. `audit` inventories sources and produces a survey in the canonical blue UI.
3. The agent reads implementation modules, traces relationships and success/error/
   retry-or-cancellation paths, and records semantic review plus five assessment areas.
4. `review --project ... --review-file ... --finalize` rebuilds the same atlas.
5. `validate --project ... --require-complete` checks references, source hashes and
   recorded completeness. Never claim source interpretation is independently proven.
6. Open/download that exact index.html. Never hand-write a different Chat interface.

Use the actual bundled launcher's --help; example symbols with ellipses above are
argument explanations, not commands to paste. A copyable repository example is
in README. Review JSON format: [contract](../skills/arc-xray/references/enrichment.md).

## Explore

Choose views on the left. Click a component/arrow for purpose, inputs/outputs,
relationships and source excerpts/hashes. Search spans the full graph. Drag empty
canvas to pan, wheel or +/− to zoom, Fit to restore. View changes text size,
confidence/type filters, arrow coloring, tree root and cross-link display.

Map groups components; Tree projects directed branches while retaining cycles and
cross connections. Large graphs initially collapse groups while preserving every
component. Expand a group or all groups to inspect detail. No first-120 sampling.
Canvas only/F hides panels; Esc restores them. The same HTML also works in an
iframe preview; outer display controls depend on the host.

Review findings individually or export all. Choose Markdown/JSON, selection,
filename and comment; preview before saving. Save As works where available;
otherwise download location follows browser settings. Logging does not fix risks.

## Coverage

Survey, partial and complete statuses are explicit. Complete means all recorded
static-source areas/modules/paths in scope passed the gate. Runtime, correctness,
security and performance remain separate. Exclusions and unknown references remain
visible. Never narrow source scope silently to satisfy completion.

Bounds: 2,000 files, 256 KB/file, 24 MB total, 30,000 directory entries. Python AST
and lexical adapters are partial program analysis. Unsupported semantics need
agent investigation. VCS/dependency/build directories, links and common secret
filenames are skipped; .gitignore is not interpreted, use explicit --exclude.

Output must be new/empty or owned by .arc-xray-output. Rebuilds replace only known
generated files. Keep review.json there for resuming after interruptions. Review
source excerpts before sharing: filename filters/redaction cannot guarantee secrecy.

Draw.io/JSON retain all views. Mermaid shows up to 80 nodes per view with explicit
omission notices. CLI/graph/hash checks do not establish native Chat acceptance.
