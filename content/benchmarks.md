---
title: Benchmarks
description: SPM OS benchmark results, historical observations, measurement boundaries, and reproducibility limitations.
published: 2026-08-19
updated: 2026-10-20
applies_to: SPMOS; current production product SPM-Polaris
---

# Benchmarks

This page separates a completed evaluation result from historical, frozen observations. Scores, answer accuracy, token reduction, and latency measure different things and must not be compared as interchangeable measures of quality.

## AML II: completed official Full evaluation

SPM completed the official Full evaluation for the second edition of the Agent Memory Leaderboard (AML II). The final score is **52.83**, attributed here as the **final evaluation platform result reported by SPM**. This is a completed Full result, not an estimate or pilot result; it is a score, not an accuracy percentage.

As of October 20, 2026, this page does not provide a public per-task scorecard or raw-result archive, and no current public AML II rank has been verified. The September 7 first-edition table does not establish a rank in AML II. Completion and the final score do not imply independent reproduction or certification.

The [official benchmark repository](https://github.com/AML-memory/agent-memory-leaderboard) provides methodology context, not proof of this particular SPM run. The historical LoCoMo result below uses a different question set and scoring setup and is not directly comparable.

## Historical production observations (August 2026)

| Observation | Result | Scope |
|-------------|--------|-------|
| Long-history request (extreme case) | One eligible request compressed 66,265 input tokens to 365 forwarded (279 recalled) — a ~99.5% reduction on that single request only | One real, eligible hosted Provider Proxy request; an extreme observation, not a representative rate or a system-wide bound |
| Agentic tool-output removal | 43k–53k fewer input tokens per request (about 85% of the removable tool-output bulk); upstream response time fell from ~2 minutes to ~35 seconds | Sampled production agentic sessions, 2026-08 |
| Starter limiter burst | 30 successful requests + 15 HTTP 429 responses from a 45-request burst | One measured Starter 30 req/min window |
| New memory readiness | ~8.2 seconds from save to recallable | One production remember/status round trip |
| Saved-text integrity | Stored and re-read text matched byte-for-byte | Production remember → status → recall → read |
| Warm recall | ~5 seconds | One warm production observation; not an SLO |

These are historical observations, not current SLOs, capacity claims, or general quality measurements. Network distance, corpus size, provider latency, protected request content, and request shape all affect results. Do not extrapolate a single observation to every request.

## Historical recall-depth probe (August 25, 2026)

Measured on a frozen probe set (English and Chinese arms) with the production recall stack used on August 25, 2026. This documentation site does not contain a public reproduction package for that probe:

| Depth | Unanswerable questions declined | Answerable questions found | Provider tokens spent | Typical latency |
|-------|---------------------------------|----------------------------|-----------------------|-----------------|
| `fast` | 23/23 | 15/15 | 0 | ~3 ms |
| `auto` (default) | all | all | spent only on low-confidence queries (~55% of probes), at 52–66% of deep's cost | ~3.5 ms |
| `deep` | all | all | highest; multi-round gathering | ~1.3 s |

Reading: in this probe, `fast` declined every unanswerable question and found every answerable one. `auto` used deeper gathering for a subset of queries. The zero provider-token count is a probe observation, not a statement that the service is free; these results do not establish current general recall quality or cost.

Note: the latencies above come from the internal probe harness and exclude network and provider time. End-to-end production calls are slower: a 2026-09-11 single-conversation production probe measured `fast` at roughly 1-3 seconds and `deep` at roughly 5-6 seconds per question, including the multi-round selector.

## When token reduction appears

Reduction needs both: a history long enough to matter, and older exchanges whose content is already stored as memory. Short, new, or fully protected conversations correctly show no reduction.

A 0% reduction is a common and correct result for real agentic and chat traffic: only long, eligible, already-memorized histories reduce at all. The 66,265-token example above is one extreme eligible request, not a user-facing average saving rate, and must not be read as one.

## Historical recall accuracy (LoCoMo-Refined)

Measured on the public LoCoMo-Refined long-conversation memory benchmark: 1,310 scored questions, one historical frozen production-near run. This is not a current production-quality claim or an AML II score.

| Category | Questions | Accuracy |
|---|---:|---:|
| single-hop | 204 | 48.0% |
| temporal | 276 | 63.0% |
| multi-hop | 68 | 67.6% |
| open-domain | 762 | 79.0% |
| **All scored** | **1,310** | **70.2%** |

SPM returns evidence or abstains: in this run it returned evidence for about 95% of scored questions and declined the rest rather than guessing.

### What these numbers mean

- A single frozen run on the public LoCoMo-Refined question set with the recall stack used for that run; it does not describe today's stack.
- Scored with a general open-ended answer model over the evidence SPM returned; a binary judge checked answers against gold strings.
- Not a guarantee for every request, and not an Agent Memory Leaderboard figure: that leaderboard applies its own answer model, prompt, and scoring, while SPM contributes the evidence it returns.

## Methodology rules

- For a reproducible result package, publish the exact commit, configuration, model/embedding identity, corpus, question set, and launch command. This is a publication requirement, not a claim that every result above already has such a public package.
- Keep degraded or interrupted runs, but label and exclude them from headline anchors.
- Separate retrieval/evidence recall from downstream answer phrasing.
- Report medians and tail latency where sample size permits.
- Never present a single request as an SLO or a general savings guarantee.
