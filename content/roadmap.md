---
title: Roadmap
description: SPM OS capabilities and evaluation work, separated into available, experimental, and under-consideration status; no delivery dates are promised.
published: 2026-08-26
updated: 2026-10-20
applies_to: SPMOS; current production product SPM-Polaris
---

# Roadmap

Status as of October 20, 2026. This page distinguishes available capabilities from experimental work and possible future directions. Not every item is actively being developed; no delivery date or deployment commitment is implied.

## Available

- **Hosted Provider Proxy, Local Proxy, and MCP integrations** — with distinct credential and traffic boundaries; see [Integrations](integrations.html).
- **Evidence-backed recall and source reads** — MCP exposes evidence references and source-ID reads; support does not make a recalled statement settled truth. See [MCP](mcp.html).
- **Completed official AML II Full evaluation** — final score **52.83**, attributed as the final evaluation platform result reported by SPM. See [Benchmarks](benchmarks.html) for limits; this does not establish a current public rank or public raw-result archive.

## Experimental

- **Evaluation and reproducibility work** — controlled experiments remain separate from released interfaces and deployed behavior. Experimental artifacts or fixtures do not establish production availability, and historical results require their own measurement boundaries.

## Under consideration

- **Public reproduction packages** — per-task scorecards, raw results, and pinned configuration where publishable; these are not currently linked as public artifacts here.
- **Cross-language recall improvements** and paired evaluation of embedding-stack changes.
- **Graph-aware writing, temporal recall, and cross-encoder reranking** — possible approaches, not assertions of current deployment.
- **Additional discovery channels** — including MCP directories; a listing is not promised or implied by this roadmap.
- **Manual memory-pinning controls** — subject to evidence, lifecycle, and API design review.

For what already shipped, see the [changelog](changelog.html).
