<p align="center"><img src="assets/arc-xray.png" width="112" alt="Arc-XRay"></p>
<h1 align="center">Arc-XRay</h1>
<p align="center">Explore your architecture. Follow the evidence.</p>

[Русская документация](README.ru.md) · [User guide](docs/USAGE.md) · [Capabilities and limits](docs/CAPABILITIES.md)

Arc-XRay turns a user-selected source project into an interactive architecture
atlas and an evidence-based architectural review. An agent investigates the
source; the bundled scanner supplies a reproducible starting graph and the
renderer creates a standalone **index.html**. The same viewer is available as a
local **MCP App** in compatible ChatGPT/Codex desktop clients.

## Install the plugin

Prerequisites: **Python 3.10+ available as `python3`**, Git, and a recent Codex CLI
with `codex plugin marketplace add` and `codex plugin add` support.

```bash
codex plugin marketplace add ConstantineJJ/Arc-XRay && codex plugin add arc-xray@arc-xray
```

Or clone this repository, inspect the installer, then run `bash install.sh`.
The installer uses the same supported commands, checks prerequisites and preserves
other plugins. `bash install.sh --dry-run` prints the commands without installing.
Open a new local chat, select **Arc-XRay**, and ask:

> Create a read-only architecture atlas for this project. Trace important workflows,
> review architectural risks, and provide both index.html and the in-app viewer.

Installation adds tools and an audit skill; it does not grant access to another
user's sources. Select a project the agent can actually read.

## What you get

- Map and directed tree, zoom/pan, global search, group expansion, filters,
  colored arrows, source inspectors, adjustable text and canvas-only mode.
- Separate system, dependency, data/I/O, execution and coverage views.
- Architectural observations: errors, contradictions, coupling, redundancy,
  possible efficiency problems and risks, each qualified and linked to source.
- Single/bulk finding logs in Markdown or JSON, with Save As where the browser
  supports it and a clearly labeled download fallback.
- `index.html`, `atlas.json`, `REPORT.md`, `COMPONENTS.md`, editable
  `architecture.drawio`, and `flows.md` with Mermaid diagrams.
- English/Russian controls and documentation; the agent writes project-specific
  analysis in the requested language. Source excerpts and identifiers are retained.

No mandatory server subscription, API key, pip install or npm install is needed
to **run** the shipped plugin. The viewer has no CDN/runtime network dependencies.

![Arc-XRay architecture atlas](docs/atlas-preview.png)

## Run without a plugin host

```bash
git clone https://github.com/ConstantineJJ/Arc-XRay.git
cd Arc-XRay
python3 -B arc-xray.py audit /path/to/project --out /path/to/new-atlas --language en
python3 -B arc-xray.py validate /path/to/new-atlas/atlas.json --project /path/to/project
```

Open the generated **index.html** in a browser. It works directly from `file://`
and does not need a local web server or adjacent files for interactive exploration.
`viewer/index.html` in this repository is a build template, not a generated atlas.

Try the synthetic example (it is read, never executed):

```bash
python3 -B arc-xray.py audit examples/python-service --out .test-output/demo --enrichment examples/python-review.json
```

## In-app viewing and honest limits

The plugin provides a local stdio MCP server and the standard MCP Apps
`ui://arc-xray/atlas` resource. `arc_xray_audit`, `arc_xray_enrich` and
`arc_xray_open` deliver the interactive viewer to supporting clients.

**Plain web/mobile ChatGPT cannot start a local stdio process or read your disk.**
It needs accessible sources and a separately reachable runtime, or a host code
environment that can generate and preview HTML. This repository does not deploy
a hosted MCP endpoint. A repository install is also distinct from approval in the
public OpenAI plugin directory. See [host setup](docs/USAGE.md#host-setup).

Automatic analysis is not a complete architecture audit. Python imports use AST;
JavaScript/TypeScript, GDScript, Go, Rust and C# imports use **lexical adapters**.
Other supported source extensions receive inventory coverage. Python execution
views are bounded syntactic sketches; runtime dispatch, aliases, generated code,
finally/unwinding and async scheduling are incomplete. Agent source investigation
and semantic enrichment are part of the plugin workflow.

Source observations, documentation, inference and unknowns are labeled separately.
Heuristics do not prove defects, exploitability or measured bottlenecks. No automatic
findings does not mean a clean architecture. Project code is never executed or fixed.

## Development

```bash
python3 -B -m unittest discover -s tests -v
npm ci
npm run build:bridge
npx playwright install chromium
npm run test:ui
python3 -B scripts/package.py
```

Python runtime uses only the standard library. Node/npm are for development;
the official MCP Apps bridge is already bundled, with licenses in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md). Packaging produces
`dist/arc-xray-0.1.0.zip`, containing one portable plugin and its compatibility
manifest. No marketplace wrapper, test projects or dependency directories are included.

[Verification record](docs/VERIFICATION.md) · [Design contract](docs/SPEC.md) · [MIT license](LICENSE)
