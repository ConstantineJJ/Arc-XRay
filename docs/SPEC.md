# Arc-XRay 0.2 implementation contract

User scope: independent plugin; no MCP requirement; one canonical blue interface
in Chat, Work and browsers; full source review rather than a silently reduced
metadata graph; working PowerShell/Bash installation and a Russian Discord post.

Runtime and assets are canonical under skills/arc-xray/. Root arc-xray.py is a
convenience launcher. No copied runtimes, MCP manifests, servers or bridge SDK.

Acceptance:
- Same index.html/model in a browser and host-style HTML preview. Keep identity
  arc-xray-blue-v1; agents must not hand-author another UI.
- Large graphs retain all nodes, initially grouped; every group expands.
- Survey/partial/complete are distinct. Finalization requires all five review
  areas, implementation modules and success/error/retry-or-cancellation paths,
  real evidence and a complete source inventory within explicit scope.
- Source is read-only and never executed by auditing. Unknowns remain explicit.
- A copy containing only the skill can generate the complete fixture atlas.
- Archive has no MCP registration or server. Installed source passes the same tests.
- Commands parse in Windows PowerShell 5.1; Bash commands are labeled as Bash.
- Native Chat invocation/HTML preview is distinct from a browser harness or ZIP check.

Commands: python -B -m unittest discover -s tests -v; npm ci; npm run test:ui;
python -B scripts/package.py; python -B scripts/verify-install.py.
All writes are confined to Arc-XRay and scoped test/artifact folders; Tools_C is
reference-only for this product change. Do not edit installed plugin caches.
