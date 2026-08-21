---
title: Architecture
---

# Architecture

## One hosted memory plane, two provider paths

```
Hosted Provider Proxy
client -> api.spmos.ai -> recall/compress -> configured provider
                         | receipts + eligible ingest
                         v
                    hosted SPM memory

Local credential custody
client -> 127.0.0.1 Local Proxy -> configured provider
              |
              +---- recall + eligible ingest ----> hosted SPM memory

MCP
agent -> api.spmos.ai/mcp -> hosted SPM memory
```

The Local Proxy changes provider-key custody and the path taken by model traffic. It does not move the SPM memory plane onto the user's machine.

## Control and request planes

**Console plane** (`app.spmos.ai`) manages accounts, usernames and OAuth sign-in, tenants, SPM keys, provider configurations, billing metadata, usage views, sources, and deletion requests.

**Request plane** (`api.spmos.ai`) authenticates agent traffic, enforces plan limits, performs recall/compression, forwards hosted-provider traffic, serves MCP, writes receipts, and queues memory ingestion.

Configured SPM keys remain usable when the console is unavailable because model and MCP traffic do not pass through the dashboard.

## Recall boundary

Recall combines lexical and vector candidates, applies stored trust before admission, favors source diversity, and enforces one final global `top_k`. The evidence gate rechecks tenant, namespace, generation, ACL, source state, and signed provenance.

The public `answer` field renders only the highest-priority admitted evidence item. A bounded `evidence_refs` list retains broader provenance and multiple premises. Source-span read tokens resolve the exact selected span; extracted-record tokens resolve their verified backing source.

No generative answer model is added to this memory path.

## Provider transparency and capture hygiene

Hosted forwarding uses a guarded native transport rather than parsing provider output through a cross-dialect translator. Unknown provider JSON fields, SSE event order, response/item/part identifiers, reasoning objects, thinking blocks, and tool state are relayed unchanged.

The observer works on a separate capture copy. Only user-visible assistant text is eligible for assistant memory capture:

- Chat Completions: visible assistant content
- Responses: `output_text`
- Anthropic Messages: `text` / `text_delta`

Reasoning summaries, thinking/redacted-thinking blocks, function/tool arguments, and partial JSON remain in provider traffic but never become memory sources.

## Compression boundary

Memory mode and compression mode are separate:

- Memory controls recall and ingest permissions.
- Compression controls whether old eligible exchanges are removed before forwarding.
- System/developer instructions, tool state, Responses reasoning, and Anthropic thinking are protected.
- The two most recent eligible exchanges remain protected. Older exchanges are removed only when the injected best evidence is bound to a source in the removal set; empty, degraded, or unrelated recall falls back to passthrough.
- Compression commits only after recall reports `status=recalled`, `gate_reason=passed`, and at least one admitted evidence source in the exact removal set.

These continuity rules are deployed on Hosted Provider Proxy and included in the Local Proxy source prepared for `0.1.1`. Public npm `0.1.0` does not include them.

The conservative fallback input budget is 8,192 estimated tokens. Requests below the budget, single-turn requests, or histories containing no safely removable complete exchange can correctly show 0% reduction.

MCP-capable agents can silently call `recall`, then `read` when exact provenance is needed, if an earlier conversation decision or constraint is absent from active context. Current files, Git state, configuration, and runtime state remain authoritative and should still be inspected directly when they may have changed.

## Storage and deletion

The authoritative store owns sources, extracted records, jobs, fences, and receipts. Retrieval indexes are derived and rebuildable. Clear memory advances the write fence, purges history through that fence, and verifies absence. Account closure adds credential revocation and final account-state transitions.

Targeted purge and source enqueue share a tenant-and-namespace serialization boundary. A purge tombstone blocks the same source ID from being enqueued again in that memory generation, while a later generation may reuse it. This prevents an old purge receipt from masking newly resurrected source or vector state.

Deletion does not imply that pre-existing backups, WAL, or replicas disappear before their documented rotation periods.

## Failure behavior

| Failure | Behavior |
|---------|----------|
| Rate limiter unavailable | Fail closed with `503 RATE_LIMITER_UNAVAILABLE` |
| No admissible evidence | Explicit empty/refused recall; no invented memory |
| Provider unavailable | Provider-shaped upstream failure; memory integrity remains independent |
| Ingest worker unavailable | Model request completes; jobs retry with backoff |
| Console unavailable | Existing SPM keys continue on the request plane |
| Retrieval dependency degraded | Explicit failure/degradation, never silent cross-tenant fallback |
