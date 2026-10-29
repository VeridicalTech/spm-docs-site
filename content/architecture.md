---
title: How SPM works
description: Architecture of SPM-Polaris across hosted memory, provider traffic, recall, compression, storage, deletion, and failure behavior.
published: 2026-08-19
updated: 2026-10-20
applies_to: SPM-Polaris
---

# How SPM works

A short map of which component touches your traffic, your memory, and your credentials.

## One hosted memory service, three ways in

```
Hosted Provider Proxy
client -> api.spmos.ai -> memory lookup -> your provider
                         | receipts + eligible saved text
                         v
                    hosted SPM memory service

Local credential custody
client -> 127.0.0.1 Local Proxy -> your provider
              |
              +---- memory lookup + eligible saving ----> hosted SPM memory service

MCP
agent -> api.spmos.ai/mcp -> hosted SPM memory service
```

The Local Proxy changes where your provider key lives and how model traffic travels. It does not move the memory service onto your machine.

## Console and request service

**Console** (`app.spmos.ai`) is where you manage sign-in, SPM keys, provider configurations, billing, usage, stored memories, and deletion.

**Request service** (`api.spmos.ai`) handles agent traffic: authentication, plan limits, memory lookup, hosted forwarding, MCP, and receipts.

Your configured SPM keys keep working even if the console is unavailable — model and MCP traffic do not pass through the dashboard.

## What becomes memory

Eligible user messages, visible assistant replies, and supported tool-result text can become memory under your capture policy. Model reasoning, thinking blocks, tool-call arguments, partial JSON, and signatures travel to and from your provider but never become memory.

## When history gets shorter

When a conversation is long, SPM can shorten eligible older history after checking source readiness and protected context. Recent context and protocol-sensitive content are guarded against unsafe trimming. These checks do not prove semantic losslessness: saved evidence and a shorter request are not equivalent to keeping every original detail in context. If trimming is not eligible, SPM can forward full history instead; forwarding still depends on normal request validation and provider limits.

### Provider-managed Responses state

An OpenAI Responses request with `previous_response_id` points to history held
by the provider. SPM can see only the new tail, so it does not rewrite or fold
that provider-managed history. It may still recall relevant SPM memory and add
it to the tail. This produces `bypassed_protected_context`, not a compression
failure.

For ordinary history, SPM protects recent messages and opaque tool/reasoning
state, and removes only older exchanges whose content is safely stored. When
the removed range is large enough, the gateway may replace it with a
deterministic summary plus a reversible reference. Session economics records
removed tokens, summary overhead, net saving, and references without changing
billing or provider protocol fields.

## Deletion boundary

Deleting removes memory from active storage and verifies it is gone. **Clear memory** gives your account a clean slate; **Close account** also revokes credentials. A deleted source ID cannot be reused until the next clean slate, which prevents deleted content from reappearing. Backups created before a deletion age out on their normal retention schedule.

## If something fails

| Failure | What you see |
|---------|--------------|
| Rate limiter unavailable | The request is blocked (`503`) instead of guessed |
| No saved memory answers the question | An explicit no-evidence result, never an invented answer |
| Provider unavailable | A normal provider-shaped error; your memory is unaffected |
| Memory saving unavailable | Model forwarding may continue with degraded capture; durable background retry is not guaranteed. Explicitly save critical facts and check readiness |
| Console unavailable | Existing SPM keys keep working on the request service |
| Memory lookup degraded | An explicit failure or a smaller result — never another account's memory |
