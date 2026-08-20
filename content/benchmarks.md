---
title: Benchmarks
---

# Benchmarks

Current product release: **SPM-Polaris V3.0.0**.

These are first-party SPM-Polaris results from our own harnesses and frozen-anchor runs — the same evidence class as vendor self-reports. We report bands rather than best runs and exclude degraded-validity runs from anchors. Scorecard date: 2026-08-16. Early runs predate both V3.0.0 and our launch-manifest discipline, so their full argv/commit records are not all preserved and they are not relabeled as V3.0.0 results; every new anchor run publishes a complete launch manifest (argv, commit SHA, worktree state, model and endpoint pins).

## Headline

| Metric | Value | Re-anchor status (2026-08-16) |
|--------|-------|-------|
| Context reduction | **99.507%** | Terminal-Bench v2: 160,509 → 791 tokens per query; stable |
| Reader-token savings | **8.4×** | vs full-context replay, 20.2k reader tokens/query (LoCoMo arm); stable |
| Agentic SWE-Atlas | **9/9** indicative | **Re-confirmed at current build**: gateway arm 4/4 on checkpoints 1–5, anchor-identical degraded caveat (ck1) |
| LoCoMo accuracy | **67.9–69.2%** band | **Load-bearing recall re-measured: 77.8%** gold-evidence recall on a 301-question subset with the production embedding stack (voyage-4-large + rerank-2.5). The 99.7% payload-gold-recall figure from the original harness did not reproduce; the band is kept with this caveat |
| LongMemEval v2-Small | **48.1%** | **Not reproducible**: the original harness was never committed and is lost. Current re-anchor at production shape: 22–25% with deterministic-hash embeddings (abstention protocol recovered 47–57% of false-premise questions); the production embedding arm is in flight |
| Payload gold recall | **99.7%** | **Not reproduced**: 72.8–77.8% on the re-anchor subset across embedding backends (hash 29.6%). Treated as harness-era, unverifiable |

## How to read these

- **First-party evidence standard.** These results use our harness and runs, the same evidence class as vendor self-reports. Depending on protocol, academic LoCoMo reproductions place Mem0 at 63–66.9 and Zep at 63.8–71.2; vendor pages self-report higher. The published harness keeps the comparison falsifiable.
- **Bands, not bests.** The LoCoMo result is a band across three full runs. We discarded a higher single run (74.1%) under our drift discipline.
- **Small N is annotated.** The agentic probe is 9/9 on both arms with validity caveats: a directional signal, not a superiority claim.
- **Cost honesty.** The 99.507% context reduction pays back in ~4 queries under favorable conditions and 31–53 queries under adverse cache behavior. The report includes both figures.


## What the 2026-08-15 alignment changed

An audit found the served recall shape had drifted from the shape the anchors were measured on: the production data plane asked for 6 evidence items with no source-span leg, while the anchors measured ~50 items plus source spans. The served shape is now aligned with the measured shape (deterministic span selector, top_k 50, 120k span budget, shared span-scan caches, 200k assembly budget) — benchmark numbers from now on describe what the product actually serves.

## Method

Benchmarks use frozen-anchor paired evaluations. Each checkpoint has one anchor configuration, and both arms (with-memory and baseline) receive the same canonical evidence stream. Runs missing forced compaction or transport symmetry are retained but marked degraded. Reader and judge models are pinned per anchor; readers cannot change mid-comparison.
