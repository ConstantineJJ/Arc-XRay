# Semantic enrichment contract (schema v1)

The initial scan returns an atlas_id and writes atlas.json. Inspect that file with
host file tools to find node/evidence IDs. If using MCP, the complete graph is in
the tool result's private UI metadata; the model-facing result is intentionally
compact. Use the generated index_html path's sibling atlas.json when available.

Supply a JSON object to `arc_xray_enrich(atlas_id, review)` or the CLI's
`--enrichment FILE`. Existing nodes/edges/findings are retained. New IDs must be
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
