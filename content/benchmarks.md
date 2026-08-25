---
title: Benchmarks
description: Current SPM-Polaris benchmark evidence, measurement boundaries, reproducibility requirements, result limitations, and invalid historical comparisons.
published: 2026-08-19
updated: 2026-08-26
applies_to: SPM-Polaris V3.0.0
---

# Benchmarks

This page reports only currently valid evidence. Historical scores measured on a different recall shape, embedding backend, or incomplete runner are not presented as current production accuracy.

## Verified production observations

| Observation | Result | Scope |
|-------------|--------|-------|
| Long-history deterministic compression | 66,265 original input tokens → 365 forwarded; 279 recalled; **99.45% less provider input** | One real, eligible hosted Provider Proxy request |
| Starter limiter burst | 30 successful requests + 15 HTTP 429 responses from a 45-request burst | One measured Starter 30 req/min window |
| New MCP memory readiness | 8.23 seconds to ready | One production remember/status round trip |
| MCP read integrity | Stored and read text matched byte-for-byte | Production remember → status → recall → read |
| Warm historical MCP recall | 4.93 seconds | One warm production observation; not an SLO |
| Agentic tool-output removal | 43k–53k fewer input tokens per request (about 85% of removable tool output); upstream response from ~2 minutes to ~35 seconds | Sampled production agentic sessions, 2026-08 |

These are observations, not guarantees. Network distance, corpus size, provider latency, cold span indexing, protected protocol state, and request shape all affect results. The compression figures include provider, tunnel, indexing, and queuing costs; they are not an isolated measurement of SPM overhead and must not be extrapolated to every request. Short or new conversations correctly show zero reduction, and when protected state cannot be safely changed, the per-request receipt marks the request as fully preserved.

The [SPM-Polaris technical report](technical-report.html) places these bounded observations in the larger architecture, integration, deletion, and evaluation context.

## Recall depth: cost–quality Pareto

Frozen probe, 2026-08-25, two arms, reproducible in the repository:

| Depth | Unanswerable questions refused | Answerable questions hit | Provider tokens | Typical latency |
|-------|-------------------------------|--------------------------|-----------------|-----------------|
| fast | 23/23 | 15/15 | 0 | ~3 ms |
| auto (default) | all passed | all passed | only ~55% low-confidence queries pay; 52–66% of deep cost | ~3.5 ms |
| deep | all passed | all passed | highest (multi-round evidence collection) | ~1.3 s |

The zero-cost fast path already refuses every unanswerable question in this probe. Auto preserves quality while paying only for queries that genuinely need deep evidence collection; deep retains multi-round capability for the hardest multi-hop questions. Chinese and English memory recall are both verified in production on fast and deep paths.

## When token reduction appears

Deterministic compression needs both:

1. input above the active budget (8,192 estimated tokens when no model-specific budget is available); and
2. at least one complete old exchange that can be removed without touching protected state.

Therefore 0% on short, single-turn, or opaque histories is correct. Do not extrapolate the 99.45% example to every request.

## Recall-quality status

The production embedding service now uses a privately operated Voyage 4 Nano-compatible embedding runtime and no hosted reranker. Historical LoCoMo/payload-recall figures measured with hosted Voyage Large/rerank or older harness shapes are not current evidence.

A 301-question run attempted across a high-latency tunnel degraded after dense-span timeouts and produced no valid result artifact. It is excluded. A current production-near re-anchor must separately report accuracy, abstention, latency, corpus state, and exact model/commit pins before a new recall-quality number is published.

## Methodology rules

- Publish the exact commit, configuration, model/embedding identity, corpus, question set, and launch command.
- Keep degraded or interrupted runs, but label and exclude them from headline anchors.
- Separate retrieval/evidence recall from downstream answer phrasing.
- Report medians and tail latency where sample size permits.
- Do not call a single request an SLO or a general savings guarantee.
