"""Evidence-backed completion gate; a survey cannot be labeled a complete audit."""
AREAS = ("architecture", "dependencies", "data", "execution", "review")


def assess(data):
    areas = data.get("assessment", {})
    production = [n for n in data["nodes"] if n["kind"] == "module" and n["group"] != "tests" and n.get("path")]
    pending = [n["id"] for n in production if not n.get("semantic_review") or any(not n.get(key, "").strip() or n.get(key) == "Not established by static inventory." for key in ("purpose", "inputs", "outputs"))]
    gaps = []
    for name in AREAS:
        area = areas.get(name, {})
        if area.get("status") != "reviewed" or not area.get("summary", "").strip() or not area.get("evidence"):
            gaps.append("Area requires source review: " + name)
    for name in ("success", "error", "retry_or_cancellation"):
        path = areas.get("execution", {}).get("paths", {}).get(name, {})
        if path.get("status") not in {"reviewed", "not_applicable"} or not path.get("summary", "").strip() or not path.get("evidence"):
            gaps.append("Execution path requires review or an explained not-applicable verdict: " + name)
    if not production:
        gaps.append("No implementation modules were inventoried")
    if pending:
        gaps.append(f"Implementation modules without semantic review: {len(pending)}")
    if data["coverage"]["truncated"] or data["coverage"]["skipped"]:
        gaps.append("Scan is incomplete: a bound was reached or files could not be read")
    status = "complete" if not gaps else "partial" if areas or any(n.get("semantic_review") for n in production) else "survey"
    return {"status": status, "areas": {name: areas.get(name, {}).get("status", "unknown") for name in AREAS},
            "implementation_modules": len(production), "reviewed_modules": len(production) - len(pending), "pending_nodes": pending, "gaps": gaps,
            "meaning": "Complete refers to the declared static source scope and recorded agent review; it is not runtime or correctness certification."}


def require_complete(data):
    result = assess(data)
    if result["status"] != "complete":
        raise ValueError("Audit is not complete: " + "; ".join(result["gaps"]))
    return result
