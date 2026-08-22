---
title: SPM Documentation
description: Official documentation for SPM and SPM-Polaris V3.0.0, including Hosted Provider Proxy, Local Proxy, MCP, governed memory, evidence, and operations.
published: 2026-08-19
updated: 2026-08-22
applies_to: SPM-Polaris V3.0.0
schema: WebPage
---

# SPM Documentation

**SPM** is the StellarPath Memory Operating System: a hosted, evidence-gated memory plane for AI agents. It adds durable memory, bounded recall, deterministic context compression, deletion controls, and auditable token accounting around the model provider you already use.

**SPM-Polaris V3.0.0** is the current production SPM product. **SPMOS.ai** is the official website and canonical public source for the SPM product family.

The memory plane is hosted. You can choose where the upstream provider credential lives:

| Path | Provider credential | Model traffic | Memory traffic |
|------|---------------------|---------------|----------------|
| **Hosted Provider Proxy** | Encrypted in the SPM credential vault | Through `api.spmos.ai` | Through SPM |
| **Local Proxy** | In a protected loopback configuration on your machine | Directly from Local Proxy to your provider | Recall and eligible ingest still use hosted SPM |
| **MCP** | No provider credential required | Your agent uses its existing model path | MCP tools call hosted SPM |

Local Proxy is optional credential custody, not an offline or self-hosted edition of SPM.

## Three ways to integrate

| Interface | Endpoint | Best for |
|-----------|----------|----------|
| Provider Proxy | `https://api.spmos.ai/v1` | OpenAI- or Anthropic-compatible apps that want hosted forwarding, compression, receipts, and memory |
| MCP | `https://api.spmos.ai/mcp` | Codex, Claude Code, and other MCP clients that need explicit memory tools |
| Local Proxy | `http://127.0.0.1:8765` | Harnesses that support a custom Base URL while keeping the upstream key under local custody |

Hosted interfaces accept an `spm_live_...` key. Local Proxy gives the downstream harness a separate local token; it does not expose the upstream key or SPM key to that harness.

## What happens in a hosted proxy request

1. Authenticate the SPM key and resolve its tenant, scopes, provider configuration, and model route.
2. Recall admissible memory through lexical and vector retrieval, trust-aware ranking, and the evidence gate.
3. Apply deterministic compression only when the input exceeds its budget and complete old exchanges can be removed safely.
4. Forward the request in its native OpenAI Chat, OpenAI Responses, or Anthropic Messages dialect.
5. Relay provider JSON and SSE bytes without rebuilding reasoning, tool, or event state.
6. Record a terminal receipt and asynchronously ingest only eligible visible conversation text.

Provider reasoning, Anthropic thinking, redacted thinking, tool arguments, and other opaque protocol state are preserved for the provider but excluded from memory capture.

## Start here

- [Choose an integration](integrations.html) — compare credential, traffic, data, receipt, and operating boundaries
- [Quickstart](quickstart.html) — choose hosted forwarding, Local Proxy, or MCP
- [Bring your own provider](providers.html) — provider/model configuration and credential boundaries
- [Local Proxy](local-proxy.html) — install `@spmos/local-proxy`
- [Provider Proxy API](proxy-api.html) — memory/compression modes, receipts, and errors
- [MCP server](mcp.html) — `remember`, `recall`, `read`, `delete`, and `status`
- [Memory, evidence & deletion](memory.html) — trust, best-evidence answers, and purge behavior
- [Security](security.html) — isolation, credential custody, capture, refusal, deletion, and shared responsibilities
- [Benchmarks](benchmarks.html) — measured evidence and explicit limits
