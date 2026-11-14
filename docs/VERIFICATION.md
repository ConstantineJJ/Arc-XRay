# Verification record — 0.1.0

Date: 2026-11-15 (Europe/Riga). Run the commands below to reproduce the checks.

| Check | Evidence / acceptance boundary |
|---|---|
| Python unit/integration — PASS | 18 tests. `python3 -B -m unittest discover -s tests -v`: source import resolution, cycles, qualified efficiency findings, source preservation, secret-name exclusion, stale/nonexistent evidence rejection, Russian review, rendering, XML parity, output ownership, MCP protocol/scope/session tests |
| Browser — PASS | 37 checks. `npm run test:ui`: offline rendering, map/tree, color distinctions, single-parent tree projection, filters, search, source inspection, pan/zoom, text size, finding selection, actual JSON download, save-writer/cancellation, focus layout, 320/375/768/1440/1920/3840 widths; no script errors or runtime remote requests |
| Embedded UI | Official MCP Apps AppBridge ↔ App handshake and tool-result delivery in a browser test host, including source inspection. This is not actual account/client installation acceptance. |
| Source fixtures | Separate synthetic Python and TypeScript services; fixture code is read, not executed. Source hashes checked; the Python example also demonstrates semantic enrichment. |
| Editable exports | draw.io XML page/edge/endpoint checks. Mermaid generated with valid references and explicit per-view bounds. Actual diagrams.net import/edit/save is separate from XML validation. |
| Package | `python3 -B scripts/package.py`: runtime allowlist, manifests/version, icon dimensions/paths, JSON/Python syntax, one-plugin ZIP structure, excluded marketplace/dependency/test files and archive CRC. |
| Local installation — PASS | `python3 -B scripts/verify-install.py`: actual Codex CLI marketplace registration, plugin install/list, execution from the installed cache, four MCP tools and UI resource. Uses temporary child-process settings; the user's configuration is untouched. |
| Native client rendering — WARN | The optional attempt to open the generated file in the controlled in-app browser was rejected by the tool's file:// URL policy. No workaround was used. Actual native ChatGPT/Codex MCP App rendering remains unverified, independently of the successful standard SDK test host. |
| Artwork — PASS | Supplied PNG copied without modification; source and packaged icon SHA-256 match. |

Machine-specific browser output, profiles and logs stay under ignored .test-output/.
The shipped viewer/bridge.bundle.js is the intentional prebuilt runtime asset;
its dependency versions and license notices are recorded in package-lock.json and
THIRD_PARTY_NOTICES.md. Python runtime has no third-party dependencies.

PASS/WARN/SKIP is scoped: source-backed relationships and structural checks are not
runtime, exploitability, performance or complete semantic acceptance. No audited
production project, Blender scene or engine is modified or launched. No cloud
endpoint/public plugin directory submission is part of this repository release.

Русский: проверки подтверждают перечисленные свойства, а не безошибочность всего
проекта. Встроенный просмотр проверяется отдельно от установки в реальный клиент.
Интерпретации агента надо сверять с исходниками; отсутствие находок не равно
сертификации качества архитектуры. Архив не означает одобрение публичного каталога.
