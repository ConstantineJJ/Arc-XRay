# Host execution check — use the same real runtime

This is a skills plugin. The host supplies file access and Python execution;
Arc-XRay supplies the analyzer, review contract and canonical renderer. No tool
named `arc_xray_*` is expected. Do not diagnose missing MCP tools as plugin failure.

## Prove capabilities before building a result

1. Read the installed skill, locate `scripts/arc-xray.py` and its adjacent
   `arc_xray/`, `viewer/` and `../assets/` resources. Do not only read SKILL.md.
2. Identify an actual Python 3.10+ execution environment. Run the packaged
   launcher's `doctor` there using real paths. It must report
   `viewer_id: arc-xray-blue-v1` and `mcp_required: false`. Report the version.
3. Confirm that this execution environment can read the intended source bytes.
   A cloud Python environment usually cannot resolve a user's `E:\...` path.
4. Confirm a writable, agreed output directory and separately identify whether
   the host can preview HTML. A missing preview does not block downloadable HTML.

Do not claim any of these passed from plugin discovery, installation, directory
names, screenshots, source metadata or a successful unrelated tool call.

## When Chat execution and local sources are in different environments

Use an available host file-transfer/archive capability or uploaded source archive
to put the actual source snapshot into the Python environment. If authorized
source reading is already available, do not ask the user to send those sources
again until you have checked whether the host can transfer them. The core plugin
does not require any particular connector or MCP service.

Copy the complete installed `skills/arc-xray/` directory into that same
environment. Alternatively obtain the corresponding version from the public
Arc-XRay repository using available host retrieval tools; retain the complete
runtime/viewer/assets structure and record its version. Do not reconstruct the
renderer or analyzer from memory. Reject unsafe archive paths and symlinks when
unpacking input; do not execute project code.

Preserve project-relative paths and exact source bytes, including encodings and
line endings. Declare snapshot scope and omitted/unreadable files. Audit/review
and hash validation then refer to this snapshot, not to live Windows files.
Do not fabricate freshness proof for files outside this environment. If possible,
compare the recorded hashes with the source provider at the end.

Run `doctor`, `audit`, source investigation, `review --finalize` and
`validate --require-complete` with the same packaged runtime. Open/attach that
exact generated index.html. None of these steps can be replaced by an agent's
own HTML, file tree or Mermaid diagram.

## If a required capability remains missing

State which check failed and why. Offer one concrete route: provide the source
archive to an available Python environment, or continue in a Work/Codex chat
whose environment can read the project and run Python. Do not promise that
switching modes always supplies those capabilities; check them there.

Do not produce a substitute index.html, claim completion, silently switch to
metadata, ask the user to install an unrelated MCP, or create a launcher without
being asked. This preserves a consistent UI but cannot grant a host new powers.
