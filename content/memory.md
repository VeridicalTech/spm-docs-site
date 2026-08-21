---
title: Memory, evidence & deletion
---

# Memory, evidence & deletion

## How memory is written

Memory enters through:

- explicit MCP `remember` calls;
- console/source operations; and
- eligible text captured around Provider Proxy or Local Proxy exchanges.

Write jobs are idempotent, retried with backoff, and dead-lettered after exhausting attempts. A slow ingest job does not block the provider response.

For proxied conversations, capture and provider forwarding are separate copies:

- visible user text can be captured according to the request's memory mode;
- Chat assistant content, Responses `output_text`, and Anthropic `text` can be captured;
- reasoning summaries, reasoning objects, thinking/redacted-thinking blocks, tool/function arguments, signatures, and partial JSON are never memory content;
- those excluded objects still pass to and from the provider unchanged.

Single-turn input can be stored. In multi-turn histories, SPM avoids duplicating the latest user unit when it is expected to return as part of later history.

## Trust and provenance

Every extracted record carries signed provenance and stored trust. Current admission precedence is:

```text
user statement (0.90) > externally observed/source span (0.68) > assistant proposal (0.35)
```

Equal-trust records preserve existing relevance/reranker order. SPM first gives distinct sources a seat, then allows additional distinct evidence from the same source up to the configured per-source cap.

This does not make a user statement objectively true; it means the system will not let a lower-authority assistant proposal overwrite what the user explicitly stated.

## Best-evidence recall

Recall combines lexical and vector candidates, verifies the active tenant/fence/ACL, deduplicates normalized evidence, and applies one final global `top_k`.

- `answer` contains only the highest-priority admitted evidence item.
- `evidence_count` and `evidence_refs` describe the broader bounded evidence set.
- agents use `read` when they need exact source text or multiple premises.

SPM deliberately does not add a generative answer model or brittle entity-extraction heuristic to turn `hello im apollo` into a cosmetically normalized answer. The downstream agent can phrase the final response while preserving provenance.

When nothing qualifies:

```text
UNKNOWN — no supporting memory found.
```

## Read tokens

Read tokens are short-lived and bound to the authenticated tenant and memory fence.

- A `temporary-source-span+v1` token returns exactly the selected source span.
- A `gated-evidence+v1` extracted-record token returns the verified backing source.

Multiple refs from the same source remain separate and positionally aligned; they may represent different spans or record/source views.

## Deletion

| Scope | Interface | Behavior |
|-------|-----------|----------|
| One source | MCP `delete` or targeted purge | Idempotently removes that source and derived candidates |
| All memory | Console **Clear memory** | Synchronous tenant-history purge with fence advance and absence verification |
| Whole account | Console **Close account** | Asynchronous tracked deletion workflow including credential revocation and finalization |

Revoked API keys and provider configurations disappear from the console and behave as deleted.

A completed purge receipt is signed and persisted. Repeating the same idempotent operation returns the established result rather than advancing the generation twice.

## Retention caveat

Purge removes data from active stores and derived indexes. Backups, WAL, and replicas created before the purge age out according to their retention schedules. Per-tenant cryptographic erasure by key destruction is not currently claimed.

## Tenant isolation

Sources, records, candidates, jobs, vectors, receipts, and replay tokens carry tenant and generation boundaries. Row-level security, namespace fences, signed capability/evidence tokens, and final render-time checks enforce isolation.
