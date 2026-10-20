---
title: SPM Documentation
description: Official documentation for SPM and SPM-Polaris, including Hosted Provider Proxy, Local Proxy, MCP, governed memory, evidence, and operations.
published: 2026-08-19
updated: 2026-10-20
applies_to: SPM-Polaris
schema: WebPage
---

# SPM Documentation

**SPM — StellarPath Memory Operating System** gives your AI agent a memory that lasts across sessions — while you keep the model provider you already use.

SPMOS.ai is the official website and canonical public source for SPMOS.

What that means for you:

- **Your agent remembers.** Facts, decisions, and preferences from earlier sessions can be found again — captured automatically through the proxy, or saved explicitly through memory tools.
- **Long conversations can use fewer input tokens.** Eligible older exchanges can be stored as sources and omitted from later prompts. Source readiness does not guarantee that every fact will be found by semantic recall; read the source when exact details matter.
- **Memory results have evidence boundaries.** Recall can return evidence or an explicit no-evidence result. This does not guarantee that your model provider or agent will never guess or hallucinate.
- **Your memory evolves with you.** When something changes — a preference, a configuration, a decision — SPM records the current state and keeps the earlier state as history, instead of silently overwriting it.
- **You can delete, verifiably.** Remove one memory, all of it, or your whole account, with a signed record of what was removed.

The memory service is hosted. You choose where your provider credential lives:

| Path | Provider credential | Model traffic | Memory traffic |
|------|---------------------|---------------|----------------|
| **Hosted Provider Proxy** | Stored securely by SPM | Through `api.spmos.ai` | Through SPM |
| **Local Proxy** | In a protected configuration on your machine | Directly from Local Proxy to your provider | Memory lookup and eligible saved text still use hosted SPM |
| **MCP** | No provider credential needed | Your agent keeps its existing model path | MCP tools call hosted SPM |

Local Proxy is a credential-custody option, not an offline or self-hosted edition of SPM.

## Three ways to use SPM

| Interface | Endpoint | Best for |
|-----------|----------|----------|
| Provider Proxy | `https://api.spmos.ai/v1` | OpenAI- or Anthropic-compatible apps that want hosted forwarding, smaller prompts, receipts, and memory |
| MCP | `https://api.spmos.ai/mcp` | Codex, Claude Code, and other MCP clients that want explicit memory tools |
| Local Proxy | `http://127.0.0.1:8765` | Harnesses that support a custom Base URL while the provider key stays on your machine |

Hosted interfaces accept an `spm_live_...` key. Local Proxy gives your harness a separate local token; neither the provider key nor the SPM key is exposed to the harness.

## What happens to a hosted request

1. SPM authenticates your key and applies your plan and provider settings.
2. It looks for saved memory that genuinely helps with the current request.
3. For eligible long conversations, SPM can omit older exchanges after source-readiness checks. Compression is not a universal losslessness guarantee: tool outputs can also be elided, and stored text is not a guarantee of complete semantic recall.
4. SPM forwards the request in the configured provider's API dialect and streams the response back.
5. Hosted request receipts provide request metadata and memory-processing outcomes. Token-savings views are separate: the receipt lookup API does not return per-request token counts or a signed request receipt. Signed purge receipts and read tokens serve different purposes.

## Start here

- [Quickstart](quickstart.html) — pick a path and make your first request
- [Your memory](memory.html) — what gets saved, how it evolves, how to recall and delete
- [Bring your own provider](providers.html) — credential custody and model configuration
- [Local Proxy](local-proxy.html) — install `@spmos/local-proxy`
- [MCP server](mcp.html) — `remember`, `recall`, `read`, `delete`, `status`
- [Provider Proxy API](proxy-api.html) — modes, receipts, and errors
- [Best practices](best-practices.html) — reliable memory patterns and multi-user guidance
- [Benchmarks](benchmarks.html) — measured results and their limits
