# Arc-XRay contributor instructions

- The audited project is read-only. Do not import/execute its code or install its
  dependencies to inspect architecture. Generated artifacts belong only in an
  explicitly selected output folder, owned through `.arc-xray-output`.
- Preserve unknowns. AST observations, lexical matches, agent interpretation and
  runtime acceptance are different evidence levels. No invented performance claims.
- Keep exported paths project-relative. No personal projects, Tools_C-specific
  findings, private logs, credentials or machine state in this repository/package.
- Python runtime must stay standard-library only. Viewer must work offline from
  file://. The official MCP Apps bridge is prebuilt; update its lockfile and notices
  together using `npm run build:bridge`.
- Verify: `python -B -m unittest discover -s tests -v`, `npm run test:ui`,
  `python -B scripts/package.py`. Keep native-client acceptance separate from the
  standard SDK test host. Do not claim public directory approval from a valid ZIP.
- Preserve the supplied assets/arc-xray.png; do not regenerate the user's artwork.
