---
title: Memory, evidence & deletion
description: How SPM writes, retrieves, admits, reads, and deletes memory with provenance, evidence gates, scopes, and verifiable lifecycle controls.
published: 2026-08-19
updated: 2026-08-26
applies_to: SPM-Polaris V3.0.0
---

# Memory, evidence & deletion

## How memory is written

Memory enters through:

- explicit MCP `remember` calls;
- console/source operations; and
- eligible text captured around Provider Proxy or Local Proxy exchanges.

Write jobs are idempotent, retried with backoff, and dead-lettered after exhausting attempts. A slow ingest job does not block the provider response.

For Hosted Provider Proxy and Local Proxy source prepared for `0.1.1`, capture and provider forwarding are separate copies:

- visible user text can be captured according to the request's memory mode;
- Chat assistant content, Responses `output_text`, and Anthropic `text` can be captured;
- reasoning summaries, reasoning objects, thinking/redacted-thinking blocks, tool/function arguments, signatures, and partial JSON are never memory content;
- those excluded objects still pass to and from the provider unchanged.
- short standalone assistant messages that only report missing memory/context and inability to continue remain auditable sources but are not promoted into recall candidates;
- an assistant message containing a path, URL, hash, assignment, status, or any other durable fact still follows normal extraction even if it also mentions missing context;
- exact repeated proxy captures reuse a content-stable source identity inside the active namespace generation.

Hosted Proxy ingest carries `source_kind` and positional `role_spans`, so extraction can retain whether visible text came from the user or assistant. The Local Proxy source prepared for `0.1.1` carries the same fields and recognizes deterministic source identities created by `0.1.0` during continuity checks. Exact repeated content uses a stable source identity instead of creating duplicate source records.

Public npm `0.1.0` predates the current Local Proxy capture allowlists: streamed Chat tool-call arguments and Anthropic partial JSON can enter its assistant capture. Use Hosted Provider Proxy when capture hygiene is required until `0.1.1` is published.

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
- agents should call `recall` silently before filesystem or shell searches used only to reconstruct missing conversation history; an empty recall should not be repeated in the same logical turn.
- agents should inspect current files, Git, configuration, and runtime state directly whenever those authorities may have changed since the memory was written.

SPM deliberately does not add a generative answer model or brittle entity-extraction heuristic to turn `hello im apollo` into a cosmetically normalized answer. The downstream agent can phrase the final response while preserving provenance.

When nothing qualifies:

```text
UNKNOWN — no supporting memory found.
```

## Recall depth (fast / auto / deep)

Recall runs at three depths:

- **fast** — lexical/vector evidence gate only; zero provider tokens.
- **auto** (default) — confidence-based routing: high-confidence queries stay on the fast path; only low-confidence queries escalate to deep evidence collection.
- **deep** — multi-round evidence collection for the hardest multi-hop queries; this is the only depth that may spend provider tokens, and the spend is itemized on the request receipt.

The default recall depth, capture switches, compression mode, input budget, and recall caps are tenant-level preferences, adjustable in console **Settings**; changes apply to all three integration paths in about a minute.

## Memory evolution and quarantine

Related facts consolidate into **observations**. When a preference or fact changes, the observation presents the current state and keeps its history — for example, “uses Vue (previously: React)” — with proof counts and provenance attached. Nothing is silently overwritten.

Content captured automatically around proxied exchanges first lands in an isolated **quarantine ring** and is promoted into the main memory layer only after quality checks. Ambient agent noise therefore does not pollute long-term memory.

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

Targeted deletion also leaves a source tombstone inside the exact tenant, namespace, account epoch, and namespace generation. Once a source ID has a pending, completed, or not-found purge record, ingest cannot reuse that ID in the same generation and returns `409 SOURCE_ID_PURGED`. This prevents deleted source, job, candidate, lineage, or vector state from being resurrected behind an older purge receipt. The same ID can be used after a deliberate generation advance.

## Retention caveat

Purge removes data from active stores and derived indexes. Backups, WAL, and replicas created before the purge age out according to their retention schedules. Per-tenant cryptographic erasure by key destruction is not currently claimed.

## Tenant isolation

Sources, records, candidates, jobs, vectors, receipts, and replay tokens carry tenant and generation boundaries. Row-level security, namespace fences, signed capability/evidence tokens, and final render-time checks enforce isolation.

### End-user partitions inside a tenant

Applications that serve several end users can use one SPM key with a stable
`user_partition` per user. The key must include `memory:partition`; the value is then
carried through writes, recall, evidence reads, and deletion checks. Partitions are
isolated from one another even though they share a tenant and billing account.

An omitted partition is the tenant's default space. Keep that space separate from
per-user data unless shared memory is explicitly intended. Use opaque, stable IDs such
as application user UUIDs, not secrets or mutable display names.
