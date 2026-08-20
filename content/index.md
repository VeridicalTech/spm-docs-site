---
title: SPM-Polaris Documentation
---

# SPM-Polaris Documentation

**SPM** is the StellarPath Memory Operating System brand. **SPM-Polaris** is its hosted provider-proxy product; the current public release is **V3.0.0**. You point any OpenAI- or Anthropic-compatible client at the SPM endpoint and keep your existing LLM provider account; every request then gains evidence-gated recall, deterministic context compression, and a signed audit trail — with no generative LLM call added to the memory path.

SPM-Polaris is a **hosted service**. There is no appliance or self-deployment: you integrate through the provider proxy or the MCP server while we operate the memory plane.

## Two doors in

| Door | Endpoint | For |
|------|----------|-----|
| Provider proxy | `https://api.spmos.ai/v1` | Any OpenAI/Anthropic-compatible app or agent |
| MCP server | `https://api.spmos.ai/mcp` | Codex, Claude Code, and other MCP clients |

Both doors accept the same `spm_live_...` API key and enforce the same tenancy, quota, and evidence-gate rules.

## What SPM-Polaris does inside a request

1. **Authenticates** your API key and resolves your tenant, namespace, policy, and provider channel.
2. **Recalls** relevant memory through lexical and vector legs, fused and admitted through an evidence gate. If nothing qualifies, the gate fails closed instead of guessing.
3. **Compresses** the assembled context deterministically. The memory path does not call a generative LLM, so memory growth does not increase inference cost.
4. **Forwards** to your provider in its native dialect (OpenAI Chat Completions, OpenAI Responses, or Anthropic Messages) and streams the response back.
5. **Ingests** the exchange asynchronously through idempotent, retried, dead-lettered jobs, then writes a signed request receipt with full token accounting.

Recall and forwarding are explicitly separate stages: your provider never decides what is remembered, ranked, admitted, or compressed.

## Plans at a glance

| | Free | Starter | Growth | Enterprise |
|---|---|---|---|---|
| Price | $0 | $9/mo · $99/yr | $15/mo · $150/yr | Custom |
| API rate limit | 10 req/min | 30 req/min | 100 req/min | Reviewed |
| Memory writes / month | 500 | 3,000 | 8,000 | Reviewed |
| Stored memories | 1,000 | 10,000 | 50,000 | Reviewed |
| Provider channels | 1 | 3 | 10 | Reviewed |

Full terms and enforcement behavior: [Plans & quotas](plans.html).

## Where to go next

- [Quickstart](quickstart.html) — first memory-backed call in five minutes
- [Authentication & API keys](authentication.html) — keys, scopes, and hygiene
- [Plans & quotas](plans.html) — pricing, allowances, and limit behavior
- [Bring your own provider](providers.html) — presets, live model catalog, custom endpoints
- [Provider proxy API](proxy-api.html) — endpoints, receipts, error codes
- [Memory, evidence & deletion](memory.html) — the gate, provenance, and signed purge receipts
- [MCP server](mcp.html) — agent-native memory tools
- [Architecture](architecture.html) — planes, storage doctrine, failure behavior
- [Benchmarks](benchmarks.html) — the scorecard, with footnotes
