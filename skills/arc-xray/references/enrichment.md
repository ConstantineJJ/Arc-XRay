# Semantic enrichment contract (schema v1)

The initial `audit` writes atlas.json. Inspect it with host file tools to find
node/evidence IDs. All execution uses scripts/arc-xray.py inside this skill.

Supply a review JSON to the CLI's `review --review-file` or `audit --enrichment`.
Existing nodes/edges/findings are retained. New IDs must be
unique. Enrichment views must include both endpoints of every listed edge.

```json
{
  "node_updates": [
    {
      "id": "<existing file node id>",
      "purpose": "Describe the responsibility observed in source.",
      "inputs": "Request fields / arguments and their provenance.",
      "outputs": "Return value, state changes, files or external calls.",
      "evidence": [{"path": "src/service.py", "line": 10, "end": 16}]
    }
  ],
  "nodes": [],
  "edges": [],
  "findings": [],
  "views": []
}
```

Evidence entries may be existing evidence IDs or `{path,line,end}` objects. Source
files must already be in the scan inventory. Paths must remain within the project;
symlinks and absolute paths are rejected. Existing evidence hashes are checked
against the current source bytes. Do not run enrichment on a stale source snapshot.

New components require `id,label,group,kind,status,purpose,inputs,outputs,evidence`;
optional `path,language,symbols`. Use one of the existing groups in atlas.json.
New connections require `id,source,target,kind,label,status,evidence`, with kind
`data`, `control` or `dependency`. Direction is explicit: data producer → consumer,
control caller/decision → invoked/next step, dependency consumer → provider.

New findings require `id,rule,title,severity,status,observation,impact,proposal,nodes,evidence`.
Severity is `high`, `medium`, `low` or `info`; status is `verified`, `documented`,
`inference` or `unknown`. Potential impact usually remains an inference even when
the underlying source property is verified. Do not mark a risk resolved by logging it.

New views require `id,title,description,nodes,edges`; optional `category: workflow`.
New components and connections are added to the system view except the `flow`
group, which belongs in explicit execution views. Reuse the actual node IDs.

The renderer rejects missing references and evidence but cannot verify that an
agent's interpretation follows logically from a quoted line. Human-readable
reasoning and inspection of representative links remain part of acceptance.

## Mandatory completion assessment (0.2)

`--finalize` and `validate --require-complete` require an `assessment` object with
five keys: `architecture`, `dependencies`, `data`, `execution`, `review`.
Each contains `status` (`reviewed`, `partial`, `unknown`), a substantive `summary`
and `evidence` in the same format as nodes/edges. Only `reviewed` passes completion.

`execution.paths` must also contain `success`, `error`, `retry_or_cancellation`.
Each needs a summary, source evidence, and `reviewed` or `not_applicable`. Explain
why a path is not applicable; do not invent a retry/cancellation mechanism.

Every inventoried implementation module outside tests needs `node_updates`
covering purpose, inputs and outputs with real evidence. A cut-short scan or
unreadable file blocks completion. Exclusions must be explicit source scope,
not a trick to bypass missing review. Unknown semantics stay documented.

The example `examples/python-review.json` in the source repository demonstrates
all required fields on a three-module service. The gate checks recorded coverage
and references; it does not independently prove the agent's interpretation.
