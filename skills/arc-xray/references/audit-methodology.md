# Source-backed architecture investigation

Read source, not just filenames. A useful atlas answers what each component does,
what it receives, what it changes/returns, what invokes it and what it depends on.

## Investigation sequence

1. Inventory boundaries: runtime/language, packages, startup commands, client/server,
   routers, services, adapters, bridges, skills/prompts, MCP/tools and storage.
2. Trace two or more representative requests end to end. Show input validation,
   transformations, dispatch, state writes, return values and error propagation.
3. Inspect failure branches: retries, bounds, timeouts, cancellation, queues,
   idempotency and partial completion. Separate configured intent from code behavior.
4. Compare contracts/config/docs with implementations. Record contradictions and
   which side was inspected. Check duplication, cycles, excessive coordination,
   hidden mutable state, data retention and dependency/environment assumptions.
5. For efficiency, identify the actual source pattern (e.g. synchronous disk I/O
   in an event handler or unbounded queue draining). Describe a possible impact;
   record measured performance only if an authorized measurement exists.

## Evidence rules

- `verified`: source property directly observed at attached anchors; not runtime
  verification. State the narrow claim that the source actually supports.
- `documented`: a declared interface, instruction or dependency, not observed behavior.
- `inference`: engineering interpretation, lexical match, ambiguous call, potential
  risk or possible execution path. Explain the assumption.
- `unknown`: not established with available evidence. Do not fill gaps with invented
  certainty or treat docs as an implementation.

Every important node, edge and finding needs evidence. Source paths are relative
to the selected project; line ranges are short and include a SHA-256 of the
inspected bytes. Recheck the files after enrichment. Keep source excerpts verbatim
except best-effort secret redaction. Do not publish a user's audit without consent.

## Readability and coverage

Use distinct system, dependency, data/storage and execution views. Keep subsystem
boundaries explicit and add focused workflow views rather than one enormous graph.
The tree is a spanning forest; cross and cycle edges remain graph relationships.

List analyzed source files, exclusions, unsupported languages, unresolved references,
generated/dynamic areas and paths not reviewed. Counts, import graphs and a parsed
diagram are structural evidence. They do not demonstrate workflow correctness,
runtime behavior, exploitability, business validity or measured performance.

## Finding format

Write a concise title and qualified severity, then three separate paragraphs:
what the source establishes, what could result under stated conditions, and what
the owner should investigate. Record risks without fixing production code.
Do not label a cycle, large file or high dependency count as a defect by itself.
