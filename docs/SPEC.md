# Arc-XRay 0.1 — implementation contract

Approved scope: reusable, read-only architecture audit; autonomous index.html;
embedded ChatGPT/Codex viewer; source-backed architecture review; shareable plugin;
Bash installation; supplied icon; English and Russian UI and guides.

| Module | Responsibility | Dependencies |
|---|---|---|
| scanner | Bounded source discovery, Python AST, lexical import adapters | Python standard library |
| model | Portable graph, evidence, coverage and enrichment validation | scanner |
| review | Structural observations and qualified risks | model |
| renderer | Offline HTML, JSON, Markdown, draw.io and Mermaid | model, viewer |
| mcp | Local stdio tools and embedded MCP App resource | scanner, renderer |
| distribution | Manifests, marketplace, Bash installer, archive | all |

Build order: scanner/model/review → renderer/viewer → MCP → distribution.
The agent performs semantic investigation and adds reviewed evidence-backed
components, connections, workflows and findings. Static extraction is a starting
point, not a promise of whole-program analysis or runtime correctness.

## Acceptance

- A Python service and a separate TypeScript project produce browsable atlases.
- Every extracted connection has a source anchor; inferred calls remain qualified.
- Python branches/loops/error handlers have a bounded execution view. Lexical
  adapters do not claim complete control-flow analysis.
- Findings separate observation, possible impact and follow-up. No severity means
  a demonstrated exploit; efficiency observations have no invented benchmarks.
- Source bytes are unchanged, excluded secrets/symlinks are not read, traversal and
  rendering have explicit bounds, unsupported languages and omissions are visible.
- HTML works from file:// without a server, CDN or adjacent files. Content is
  rendered as text and embedded JSON cannot terminate a script element.
- Viewer supports map/tree, pan/zoom, search, groups, relationship/confidence
  filters, source inspection, fullscreen/focus mode and single/bulk finding logs.
- Same viewer accepts MCP tool results using the official MCP Apps bridge SDK.
- MCP initialization, tool calls and UI resource reads pass protocol tests;
  actual host installation/rendering is reported separately from harness tests.
- Bash installer uses supported marketplace/plugin CLI commands. Test in isolated
  configuration; do not overwrite the user's settings or existing plugin.
- Archive contains one usable portable plugin, no source projects, secrets,
  dependency directories, tests, local reports or marketplace wrappers.

## Commands and boundaries

Runtime: Python 3.10+; no third-party Python packages. Build/GUI tests: Node 22+,
npm ci. `python -B -m unittest discover -s tests -v`, `npm run build:bridge`,
`npm run test:ui`, `python -B scripts/package.py`.

Use small Python modules, explicit dictionaries matching the versioned schema,
stdlib unittest, plain HTML/CSS/JS. No mandatory hosted service or API key.
Never execute/import project code, follow symlinks, automatically clone arbitrary
URLs, fix audited sources, auto-publish their evidence or conceal incomplete scans.
Remote ChatGPT needs accessible sources and a supported remote runtime or a host
code environment; a local stdio install alone cannot provide access on web/mobile.

Public directory submission and a hosted MCP service are separate deployment
tasks. This version supports repository distribution and local MCP Apps.
