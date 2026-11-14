# Using Arc-XRay

## Host setup

1. Install Python 3.10+ and check `python3 --version` in the same environment used
   by the desktop client. On Windows, Git Bash can run the Bash commands; if your
   interpreter is only named `python`, expose `python3` or adjust the local MCP
   command in your own checkout. Do not modify an installed cache.
2. Run the marketplace/install command in the README. Select Arc-XRay in a new
   local chat. If tools have not refreshed, restart the client and retry once.
3. Select a project folder or the current workspace. The plugin does not need
   account credentials or a separately hosted service for local operation.

For another MCP Apps client, configure a stdio server:

```json
{
  "command": "python3",
  "args": ["-B", "/absolute/path/to/Arc-XRay/arc-xray.py", "mcp", "--data-dir", "/absolute/path/to/atlas-output", "--allow-root", "/absolute/path/to/projects"]
}
```

`--allow-root` is optional and repeatable. Without it, each audit's explicit
project_path is the read scope. Drive/home roots are rejected. The server has no
generic arbitrary-file reader and no network listener. Artifacts are written only
under its own data directory. Absolute source-root mappings are kept privately
there in sessions.json, not included in exported atlas.json.

Local stdio installation does not make a service reachable from web/mobile
ChatGPT. In those environments, use a host code environment with supplied sources
and HTML preview, or deploy/connect a separate supported remote runtime. No
endpoint, tunnel or account binding is invented or provisioned by this repository.

Official references: [plugin packaging and marketplaces](https://developers.openai.com/plugins/build/plugins),
[MCP Apps](https://github.com/modelcontextprotocol/ext-apps),
[OpenAI host support](https://github.com/openai/mcp-extensions/blob/main/docs/spec.md#platform-support).

## Ask the agent

Specify the project and desired depth. For example:

> Audit this repository read-only. Map entrypoints, modules, dependencies and
> storage. Trace a successful request, an error and a retry/cancellation path.
> Review contradictions, redundancy, coupling and possible bottlenecks. Attach
> source evidence and list unknowns. Open the atlas in-app and give me index.html.

The skill requires an initial scan **and** semantic investigation. Automatically
extracted imports and source inventories are not a complete audit. Agents can add
reviewed descriptions, boundaries, relationships and focused workflows through
`arc_xray_enrich` or `--enrichment`; the [contract](../skills/arc-xray/references/enrichment.md)
explains IDs and evidence. Rescan when source hashes change.

## Explore the atlas

- Select a view on the left. Click components and arrows to open descriptions,
  inputs/outputs, relationships and expandable source excerpts on the right.
- Search covers the complete atlas, including workflow steps. Selecting a result
  opens the view containing it and reveals its group.
- Drag empty canvas to pan; use the mouse wheel or +/− to zoom. **Fit** restores
  the full visible graph. Component titles have full hover descriptions.
- **Map** groups components. Group headings and **View → Collapse/Expand** control
  group detail. **Tree** builds directed main branches; cycles/cross connections
  remain present and can be hidden through **View**. Tree root is configurable.
- Solid arrows carry data, long dashes show control, short dots show dependencies.
  Color is selectable per connection, source component or relationship type.
- **View** also controls evidence filters and independent text size. The first
  120 matching components are drawn for usability; **Show more** reveals more.
  Exports retain the complete graph. The count bar identifies the displayed subset.
- **Canvas only** or **F** hides auxiliary panels. **Esc**/the exit button restores
  them. In an embedded host this is an internal focus layout; the host supplies its
  own outer fullscreen controls. On narrow screens panels stack vertically.

## Review and logs

Open **Risks & inconsistencies**. Each finding distinguishes observation,
potential impact and investigation; click its components or inspect source
anchors. High severity is a review priority, not proof of exploitability.

Use a row's ↓ button or **Create log** for one finding, or **Log all observations**
for a batch. Adjust the selection, filename, Markdown/JSON format and optional
comment. Preview the contents before saving. Save As opens a folder/file dialog
where supported. Otherwise the browser download setting chooses the destination;
enable “Ask where to save each file” to select a folder. Host sandboxes may restrict
downloads. Picker cancellation preserves the dialog; write errors offer a retry
or explicit browser download. Logging never marks findings fixed.

## Files and verification

`index.html` is a self-contained interactive viewer. Keep `atlas.json` for graph
interchange, `REPORT.md` for the review and coverage, `COMPONENTS.md` for component
documentation, `architecture.drawio` for editing in diagrams.net, and `flows.md`
for Mermaid. Mermaid views are limited to 80 components with an explicit omission
notice; draw.io and atlas JSON contain the complete views. Mermaid uses solid
arrows for data, thick arrows for control and dotted arrows for dependencies.

```bash
python3 -B arc-xray.py validate /path/to/atlas/atlas.json --project /path/to/project
```

This checks graph references and source hashes. It does not prove that an agent's
interpretation is correct. Review important links manually and report untested
runtime behavior. Before sharing an audit, inspect its source excerpts: filename
exclusions and best-effort secret redaction are not a guarantee of confidentiality.

## Output and scope controls

CLI output must be a new/empty folder or a folder marked `.arc-xray-output`.
Existing unrelated reports are refused, not replaced. Keep custom enrichment JSON
in the output area; generated files are replaced on rebuild, unrelated files are
retained. No backups or duplicate numbered atlases are created.

Default CLI bounds: 2,000 files, 256 KB/file, 24 MB total. MCP defaults to 500 files
and allows up to 2,000. Traversal stops after 30,000 directory entries. Unsupported,
excluded, unreadable and unresolved areas are reported. Embedded payloads over
8 MB use the offline file; choose a narrower scope for the app. Built-in filters
skip VCS, dependencies, build directories, symlinks/junctions and common secret
filenames. `.gitignore` semantics are not implemented; add repeated `--exclude`
project-relative glob patterns when using the CLI.
