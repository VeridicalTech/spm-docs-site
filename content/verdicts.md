---
title: Recall verdicts
description: Machine-readable evidence and sufficiency decisions returned by SPM recall.
published: 2026-10-30
updated: 2026-10-30
applies_to: SPM recall and MCP clients
schema: TechArticle
---

# Recall verdicts

SPM separates what it found from whether the evidence is sufficient to answer.
Only `evidence_decision.status` is authoritative for that decision.

```json
{
  "evidence_decision": {
    "schema": "evidence-decision-v1",
    "status": "supported",
    "sufficiency_judged": false,
    "sufficiency_source": "gate_only",
    "support_failure_kinds": [],
    "why_no_answer": null
  }
}
```

| Field | Meaning |
| --- | --- |
| `status` | `supported`, `insufficient`, `contradicted`, or `unknown` |
| `sufficiency_judged` | `true` only when a deep selector judged the evidence sufficient |
| `sufficiency_source` | `deep_selector` or deterministic `gate_only` |
| `support_failure_kinds` | Why evidence was refused, such as `cjk_floor`, `identifier`, `entity_binding`, or `capture_origin_unverified` |
| `why_no_answer` | Machine-readable `{code, message, action_hint}` for non-supported outcomes |

Three rules are stable:

1. Only `supported` means the evidence answers the question.
2. An empty result never reports a passed or sufficient gate.
3. `gate_only` is honest deterministic acceptance, not a claim that a model
   independently judged sufficiency.

Proxy captures whose speaker cannot be attributed may remain visible as
evidence, but they cannot stand alone as a supported answer. Explicitly save
important facts with MCP `remember` when provenance matters.

See [MCP](mcp.html), [Memory](memory.html), and the [Provider Proxy API](proxy-api.html)
for integration details.
