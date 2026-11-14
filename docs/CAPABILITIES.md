# Arc-XRay 0.2 capabilities

| Area | Implemented | Honest boundary |
|---|---|---|
| Plugin | Self-contained skill with Python, viewer and icon | No MCP dependency; host must expose files, source and code execution |
| Analysis | Architecture, dependencies, data, execution, review | Agent source investigation is required; a scanner survey is not a full audit |
| Completion | Evidence-backed five-area/module/path gate | Checks recorded coverage, not truth of arbitrary agent reasoning |
| Python | AST imports, symbols, call/I/O candidates, bounded execution sketches | Reflection, runtime dispatch, async/finally semantics remain partial |
| JS/TS, GDScript, Go, Rust, C# | Lexical import candidates | No whole-program semantic/type resolution; false matches/omissions possible |
| Other files | Inventory and source anchors | Agent interpretation needed |
| Interface | One canonical blue HTML renderer for all previews/downloads | Native host preview controls/access vary; no invented replacement UI |
| Large graphs | Entire matching graph retained, groups initially collapsed | User can expand every group; very large expanded diagrams can be expensive |
| Review | Errors, contradictions, redundancy, coupling, potential efficiency/trust/retention risks | Qualify assumptions; no invented benchmark, exploit or runtime proof |
| Exports | HTML, JSON, Markdown, draw.io, Mermaid, individual/bulk logs | Mermaid has explicit per-view bounds; Save As depends on browser |

Русский: независимость от MCP не отменяет необходимость доступа к исходникам и
Python в окружении приложения. Полный аудит требует исследования агентом, а
проверка полноты не является сертификацией правильности архитектуры.
