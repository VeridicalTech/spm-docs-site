---
title: SPM-Polaris technical report
description: First-party SPM-Polaris V3.0.0 report on evidence-governed memory, protected context compilation, integration boundaries, deletion, observations, and limitations.
published: 2026-08-23
updated: 2026-08-23
applies_to: SPM-Polaris V3.0.0; evidence cutoff 2026-08-23
---

# SPM-Polaris: Evidence-Governed Memory and Context Management for Long-Horizon AI Agents

**Technical report:** Version 1.0<br>
**Publication date:** August 23, 2026<br>
**Evidence cutoff:** August 23, 2026<br>
**Author and publisher:** Veridical Tech, Inc.<br>
**Contact:** contact@spmos.ai<br>
**Status:** First-party technical report; not peer reviewed or independently evaluated

> This report describes the public behavior and evidence boundaries of SPM-Polaris V3.0.0. It is not an SLA, compliance certification, legal opinion, investment memorandum, or universal performance guarantee.

## Abstract

Long context and long-term memory solve different problems. A context window is the input space of one model request. Long-term memory is a cross-request lifecycle involving selective writing, candidate retrieval, evidence admission, context compilation, provider-state preservation, deletion, and auditability.

SPM-Polaris is the current SPM product: a provider proxy with governed long-term memory for AI agents. It separates candidate retrieval from evidence admission, protects provider-native state during context reduction, refuses unsupported memory, and records request-level evidence and token boundaries. Hosted Provider Proxy, Local Proxy, and MCP use the hosted SPM memory plane but differ in credential custody, model-traffic routing, invocation, receipts, and operating responsibility.

This report presents the architecture, current bounded first-party observations, limitations, and an evaluation agenda. It intentionally excludes withdrawn historical accuracy and comparative-efficiency figures that do not yet satisfy the current republication gate.

## 1. Long context is not long-term memory

Long-context models are valuable, but a larger input limit does not answer several systems questions:

- Which past content should become durable memory?
- Is a recalled item a user statement, an observed source, or an assistant proposal?
- Is the item still active, or has it been superseded or deleted?
- Can older history be removed without breaking system instructions, tool linkage, reasoning state, multimodal blocks, or provider-managed conversation lineage?
- Can a developer explain what memory entered a request and what history was removed?

Research has also shown that relevant information can be used less reliably depending on its position in a long context, that hard negatives can reduce long-context RAG quality, and that input length itself can harm task performance even under favorable retrieval conditions.

The practical distinction is:

```text
Context window = input available to one model request
Long-term memory = governed state maintained across requests and time
```

## 2. System scope

SPM means StellarPath Memory Operating System, the product family developed by Veridical Tech, Inc. SPM-Polaris V3.0.0 is the current production product.

SPM-Polaris is not:

- a foundation model;
- a model reseller;
- a complete agent runtime or workflow orchestrator;
- a universal compressor that reduces every request;
- a fully self-hosted or air-gapped memory plane;
- a certified compliance program or formal production SLA.

Its role is to govern how memory is written, recalled, admitted, compiled into model context, audited, and deleted around provider workflows.

## 3. Request and memory lifecycle

The public architecture can be summarized as:

```text
Eligible source content
  -> extraction and indexing
  -> lexical and vector candidates
  -> tenant, namespace, generation, ACL, source-state, and provenance checks
  -> evidence admission or explicit refusal
  -> protected context compilation
  -> provider-native forwarding or MCP tool response
  -> receipt, lifecycle maintenance, and deletion controls
```

### 3.1 Write path

Memory can enter through explicit MCP `remember` calls, console/source operations, or eligible visible text captured around Provider Proxy and Local Proxy exchanges.

The observer uses a separate capture copy. Visible user text and eligible visible assistant text can be captured. Reasoning summaries, thinking or redacted-thinking blocks, tool/function arguments, signatures, and partial JSON remain provider protocol state and are excluded from memory capture.

### 3.2 Candidate retrieval and evidence admission

SPM-Polaris does not treat vector similarity as sufficient authority. Current stored precedence is:

```text
user statement > externally observed source > assistant proposal
```

This ordering does not make a user statement objectively true. It prevents a lower-authority assistant proposal from silently overwriting an explicit user statement.

Recall combines lexical and vector candidates, applies source diversity, and performs a final evidence gate. When no evidence qualifies, the system returns an explicit empty or refused state such as `UNKNOWN` and injects no memory.

### 3.3 Best evidence and provenance

The public recall contract separates a concise best-evidence `answer` from bounded `evidence_refs`. Read tokens allow an agent to retrieve the exact backing source or selected span when multiple premises or precise provenance are required.

The memory path adds no generative answer model. The configured upstream provider still performs the requested inference.

## 4. Protected context compilation

Context reduction is treated as a state-integrity operation, not simple truncation.

Protected content includes system and developer instructions, the latest user task, tool-call and tool-result linkage, OpenAI Responses reasoning and lineage, Anthropic thinking state, multimodal objects, and unknown provider fields that cannot be reconstructed safely.

The two most recent eligible exchanges remain protected. An older complete exchange can be removed only when admitted evidence is bound to a source in the exact removal set. Empty, degraded, unrelated, or refused recall produces passthrough.

Therefore, a 0% reduction can be the correct result for a short, single-turn, opaque, stateful, or otherwise ineligible request.

## 5. Integration and credential boundaries

| Path | Provider credential | Model traffic | Memory invocation | Hosted receipt |
|---|---|---|---|---|
| Hosted Provider Proxy | Protected SPM-hosted custody | Client -> SPM -> provider | Automatic in request path | Yes |
| Local Proxy | Permissions-restricted local configuration | Client -> local proxy -> provider | Automatic unless memory mode is off | No |
| MCP | Application custody | Application -> provider | Explicit memory tools | Tool result, not hosted proxy receipt |

All three paths use hosted SPM memory. Local Proxy changes provider-key custody and model-traffic routing; it does not move the SPM memory plane onto the user's machine.

Proxy and MCP are different experimental treatments. MCP invocation timing and context placement depend on the host or model, so a Proxy result must not be presented as an MCP result without a matched-path rerun.

## 6. Deletion and auditability

Deletion is a cross-object lifecycle, not a single row deletion. Targeted purge and clear-memory operations enforce tenant, namespace, account-epoch, and generation boundaries; remove eligible authoritative and derived objects; advance or enforce memory fences; persist operation evidence; and verify absence.

A source tombstone prevents the same source identity from being re-enqueued in the same memory generation. This reduces resurrection through delayed jobs or index rebuilding.

Deletion from active systems does not imply immediate disappearance from pre-existing backups, write-ahead logs, replicas, provider records, or customer-side copies before their documented retention or rotation periods.

## 7. Current bounded first-party observations

The current public evidence contains observations, not universal benchmarks or guarantees.

| Observation | Result | Boundary |
|---|---:|---|
| One eligible Hosted Provider Proxy request | 66,265 original input tokens -> 365 forwarded; 279 recalled | One request; not an average, SLA, or general savings guarantee |
| One Starter limiter window | 30 successful requests and 15 HTTP 429 responses in a 45-request burst | One measured 30-request-per-minute window; not a capacity benchmark |
| One production MCP remember/status round trip | Ready in 8.23 seconds | Not a latency SLO |
| One production MCP remember-to-read sequence | Stored and read text matched byte-for-byte | Not a general integrity-rate benchmark |
| One warm historical MCP recall | 4.93 seconds | One observation; not a distribution or SLO |

The production-near embedding and retrieval stack changed after earlier internal runs. Historical accuracy, evidence-containment, and comparative token-efficiency values remain withdrawn from public promotion until a new immutable result package satisfies the republication gate.

## 8. Limitations

The current evidence does not establish:

- current production-near recall or final-answer accuracy;
- p95 or p99 latency distributions;
- sustained soak or 100+ concurrency behavior;
- equal quality across Hosted Proxy, Local Proxy, and MCP;
- a universal token or cost reduction;
- third-party reproduction or independent certification;
- complete automated moderation, SOC 2, ISO 27001, or a formal enterprise SLA.

## 9. Evaluation agenda

Useful next experiments include:

1. immutable production-near reruns with exact commits, configuration, model and embedding identities, corpus identifiers, launch commands, raw per-case outputs, exclusions, and digests;
2. paired Proxy, Local Proxy, and MCP experiments controlling the downstream model, tool schema, invocation policy, context placement, judge, and seed;
3. evidence-admission ablations with stale facts, conflicts, assistant speculation, and semantic hard negatives;
4. provider-state integrity tests covering tool identifiers, partial streams, reasoning state, and stateful lineage;
5. deletion fault injection involving delayed jobs, reindexing, replay, and repeated ingest;
6. latency decomposition across gateway, extraction, embedding, retrieval, reranking, queueing, and provider execution.

## 10. Official sources

- [Official website](https://spmos.ai/)
- [Official definitions](official-definitions.html)
- [Architecture](architecture.html)
- [Integration boundaries](integrations.html)
- [Memory, evidence, and deletion](memory.html)
- [Security](security.html)
- [Benchmarks and limitations](benchmarks.html)
- [Open-source Local Proxy](https://github.com/VeridicalTech/spm-local-proxy)

## References

1. Maharana et al. *Evaluating Very Long-Term Conversational Memory of LLM Agents.* [arXiv:2402.17753](https://arxiv.org/abs/2402.17753).
2. Liu et al. *Lost in the Middle: How Language Models Use Long Contexts.* TACL 2023; [arXiv:2307.03172](https://arxiv.org/abs/2307.03172).
3. Jin et al. *Long-Context LLMs Meet RAG: Overcoming Challenges for Long Inputs in RAG.* [arXiv:2410.05983](https://arxiv.org/abs/2410.05983).
4. Du et al. *Context Length Alone Hurts LLM Performance Despite Perfect Retrieval.* Findings of EMNLP 2025; [arXiv:2510.05381](https://arxiv.org/abs/2510.05381).
5. Packer et al. *MemGPT: Towards LLMs as Operating Systems.* [arXiv:2310.08560](https://arxiv.org/abs/2310.08560).

## Disclosure and rights

Veridical Tech, Inc. develops SPM and SPM-Polaris and therefore has a direct product interest in this report. The observations are first-party and have not been independently reproduced. AI-assisted editorial review was used to help reorganize and polish the report; Veridical Tech, Inc. reviewed the public claim boundaries and accepts responsibility for the published content.

Suggested citation:

> Veridical Tech, Inc. (2026). *SPM-Polaris: Evidence-Governed Memory and Context Management for Long-Horizon AI Agents* (Version 1.0). https://docs.spmos.ai/technical-report

Copyright © 2026 Veridical Tech, Inc. All rights reserved. Public reading and citation are permitted. Redistribution or derivative publication requires permission from the publisher.
