# Capabilities and boundaries / Возможности и границы

| Area | Implemented | Boundary |
|---|---|---|
| Python | AST imports, symbols, candidate imported calls, I/O candidates; bounded branch/loop/error sketches | Does not resolve arbitrary aliasing, reflection, finally/unwinding or async scheduling |
| JavaScript / TypeScript | Lexical static import/export, require and literal dynamic-import references; relative extension/index lookup | Comments/aliases may mislead; no AST type/call/control-flow analysis |
| GDScript | Literal preload/load references including res:// | No scene/engine execution or signal graph |
| Go / Rust / C# | Lexical import/namespace candidates | Workspace/package/namespace resolution is partial; qualified references can be external-or-unknown |
| C/C++, Java, Ruby, PHP, Shell, SQL, HTML/CSS, docs/config | File inventory, source anchors | Semantic relationships require agent enrichment |
| Architecture review | Cycles, coupling, large modules, parse failures, dynamic execution, swallowed exceptions, omitted explicit HTTP timeout, queue capacity and blocking-async candidates | Qualified heuristics, not measured defects or a security certification |
| Agent workflow | Source investigation of all five audit areas; descriptions, boundaries, relationships, workflow views and review enrichment | Requires an agent with actual source access; interpretation is not automatically proven |
| Offline atlas | Self-contained HTML, map/tree, search, filters, pan/zoom, inspection, focus layout, log exports | Initial graph display capped at 120 matching nodes; explicit Show more; exports remain complete |
| Embedded viewer | Standard MCP App resource and official App SDK bridge | Requires a compatible client and running local server; payload limit 8 MB |
| Formats | JSON, Markdown docs/report, editable draw.io pages, Mermaid | Mermaid caps each view at 80 nodes and labels omitted coverage |
| Distribution | Agent Plugins portable manifest, Codex compatibility manifest, repo marketplace, Bash installer, standalone ZIP | No hosted endpoint or public OpenAI directory listing is provisioned |

Русский: автоматический граф — исходная заготовка для исследования агента.
Подтверждение исходника, документация, инженерный вывод и неизвестное разделены.
Статические проверки не подтверждают runtime, безопасность, измеренную эффективность
или отсутствие ошибок. Проверки и фактические ограничения перечислены в
[VERIFICATION.md](VERIFICATION.md).
