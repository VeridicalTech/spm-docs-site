---
title: Architecture
---

# Architecture

## One sentence

SPM-Polaris V3.0.0 is a provider proxy with a governed memory plane. Agents send requests to `api.spmos.ai`; SPM-Polaris handles memory around each request, and the configured provider serves the inference.

## Two planes

**Console plane** (`app.spmos.ai`) — accounts, organizations, tenants, API keys, vaulted provider credentials, and subscription and usage metadata.

**Request plane** (`api.spmos.ai`) — the request gateway, the authoritative memory store, the derived retrieval index, runtime state, and optional local embedding/reranking.

The request plane has no critical dependency on the console plane. If the console is unavailable, configured keys continue to work because traffic does not pass through the dashboard.

## The request chain

```
client -> edge (TLS, limits) -> gateway
  -> authenticate + resolve tenant/provider
  -> memory recall (lexical + vector legs, fused)
  -> evidence gate (fail-closed)
  -> deterministic compression
  -> provider forwarding (native dialect, streaming)
  -> signed receipt + async ingest
```

Recall and forwarding are separate stages. The provider does not decide what is remembered, ranked, admitted, or compressed.

## Supporting subsystems

- **Provider catalog** — channel model lists are aggregated live from the models.dev dataset (12-hour TTL, stale-while-revalidate, bundled fallback). New upstream providers enter the catalog for review; they never bypass transport, SSRF, data-retention, or cost review automatically.
- **Deletion pipeline** — purges and account closures run as leased, ordered steps (sync fence, purge, verify-absence, credential revocation, reservation drain, financial review, finalize) with retry, backoff, and per-step state. The verify-absence step re-scans against the write fence, so a purge cannot complete while data remains.
- **Usage metering** — the write guard and the distributed rate limiter enforce plan quotas (requests per minute, monthly writes, stored memories, provider channels) and fail closed on limiter outage.

## Zero-LLM memory

Extraction, ranking, admission, and compression are deterministic. Consequently:

- Memory growth does not increase inference cost.
- Recall latency depends on code and indexes, not model queues.
- The memory path has no hidden model drift; benchmarked behavior remains deterministic.

## Storage doctrine

The authoritative store holds every memory record, job, receipt, and exact vector. The retrieval index is derived and rebuildable. It can be dropped and reconstructed from the authoritative store at copy speed, so the index is never the sole copy of data.

## Failure behavior

| When | What happens |
|------|--------------|
| Cache layer down | Rate limiting fails closed (clean 503) and self-recovers; no memory data at risk |
| Retrieval index down | Recall degrades explicitly, never silently; index rebuilds from the authoritative store |
| Provider down | Upstream error mapped to a standard provider error; your retries work |
| Console down | Configured API keys keep serving traffic |
| Ingest worker down | Requests unaffected; jobs queue and drain when the worker returns |
