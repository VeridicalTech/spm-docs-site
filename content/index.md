---
title: SPM Documentation
description: Official documentation for SPM and SPM-Polaris V3.0.0, including Hosted Provider Proxy, Local Proxy, MCP, governed memory, evidence, and operations.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
schema: WebPage
---

# SPM Documentation

**SPM — StellarPath Memory Operating System** gives your AI agent a memory that lasts across sessions — while you keep the model provider you already use.

SPMOS.ai is the official website and canonical public source for SPMOS.

What that means for you:

- **Your agent remembers.** Facts, decisions, and preferences from earlier sessions can be found again — captured automatically through the proxy, or saved explicitly through memory tools.
- **Long conversations stop growing.** Once the older parts of a conversation are safely stored as memory, they no longer need to be resent to the model on every request. You pay for fewer input tokens; the agent still has the facts.
- **Your agent stays honest.** When an answer is not in memory, SPM says so instead of guessing — and records why.
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
3. If the conversation is long, older exchanges whose content is safely stored are no longer resent. Recent messages, your instructions, tool state, and model reasoning are always kept intact.
4. The request reaches your provider in its native dialect, and the response streams back unchanged.
5. A receipt records the request: how many input tokens you would have sent, how many you actually sent, and which memory was used.

## Start here

- [Quickstart](quickstart.html) — pick a path and make your first request
- [Your memory](memory.html) — what gets saved, how it evolves, how to recall and delete
- [Bring your own provider](providers.html) — credential custody and model configuration
- [Local Proxy](local-proxy.html) — install `@spmos/local-proxy`
- [MCP server](mcp.html) — `remember`, `recall`, `read`, `delete`, `status`
- [Provider Proxy API](proxy-api.html) — modes, receipts, and errors
- [Best practices](best-practices.html) — reliable memory patterns and multi-user guidance
- [Benchmarks](benchmarks.html) — measured results and their limits
