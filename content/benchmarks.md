---
title: Benchmarks
description: Current SPM-Polaris benchmark evidence, measurement boundaries, reproducibility requirements, result limitations, and invalid historical comparisons.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
---

# Benchmarks

This page reports only currently valid evidence. Results measured with a different recall stack, embedding service, or incomplete runner are not presented as current accuracy. These are observations from stated cases, not guarantees for every request.

## Measured in production

| Observation | Result | Scope |
|-------------|--------|-------|
| Long-history request | 66,265 input tokens reduced to 365 forwarded; 279 recalled; **99.45% less provider input** | One real, eligible hosted Provider Proxy request |
| Agentic tool-output removal | 43k–53k fewer input tokens per request (about 85% of the removable tool-output bulk); upstream response time fell from ~2 minutes to ~35 seconds | Sampled production agentic sessions, 2026-08 |
| Starter limiter burst | 30 successful requests + 15 HTTP 429 responses from a 45-request burst | One measured Starter 30 req/min window |
| New memory readiness | ~8.2 seconds from save to recallable | One production remember/status round trip |
| Saved-text integrity | Stored and re-read text matched byte-for-byte | Production remember → status → recall → read |
| Warm recall | ~5 seconds | One warm production observation; not an SLO |

Network distance, corpus size, provider latency, protected request content, and request shape all affect results. Do not extrapolate a single observation to every request.

## Recall depth: cost and quality trade-offs

Measured on a frozen probe set (English and Chinese arms, reproducible from this repository) with the production recall stack, 2026-08-25:

| Depth | Unanswerable questions declined | Answerable questions found | Provider tokens spent | Typical latency |
|-------|---------------------------------|----------------------------|-----------------------|-----------------|
| `fast` | 23/23 | 15/15 | 0 | ~3 ms |
| `auto` (default) | all | all | spent only on low-confidence queries (~55% of probes), at 52–66% of deep's cost | ~3.5 ms |
| `deep` | all | all | highest; multi-round gathering | ~1.3 s |

Reading: the free `fast` path already declines every unanswerable question in the probe set. `auto` keeps that quality and only pays for deeper gathering when it is genuinely needed. `deep` exists for the hardest multi-part questions.

## When token reduction appears

Reduction needs both: a history long enough to matter, and older exchanges whose content is already stored as memory. Short, new, or fully protected conversations correctly show no reduction.

## Recall-quality status

The current recall stack uses a privately operated Voyage 4 Nano-compatible embedding service and no hosted reranker. Historical LoCoMo figures measured with hosted Voyage Large/rerank or older evaluation shapes are not current evidence and are intentionally not quoted here. A new production-near number will be published only with its accuracy, abstention, latency, corpus state, and exact model/commit pins.

## Methodology rules

- Publish the exact commit, configuration, model/embedding identity, corpus, question set, and launch command.
- Keep degraded or interrupted runs, but label and exclude them from headline anchors.
- Separate retrieval/evidence recall from downstream answer phrasing.
- Report medians and tail latency where sample size permits.
- Never present a single request as an SLO or a general savings guarantee.
