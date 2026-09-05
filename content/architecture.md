---
title: How SPM works
description: Architecture of SPM-Polaris V3.0.0 across hosted memory, provider traffic, recall, compression, storage, deletion, and failure behavior.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
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

Only conversation content that would be visible to you: your messages and the assistant's visible replies. Model reasoning, thinking blocks, tool-call arguments, partial JSON, and signatures travel to and from your provider but never become memory.

## When history gets shorter

When a conversation is long, SPM stops resending older exchanges whose content is safely stored as memory. It always keeps recent messages, your instructions, tool state, and reasoning intact. If any safety check fails — for example the memory lookup is unavailable — the complete original request is sent instead. A full-history request is the safe fallback, never a failure.

## Deletion boundary

Deleting removes memory from active storage and verifies it is gone. **Clear memory** gives your account a clean slate; **Close account** also revokes credentials. A deleted source ID cannot be reused until the next clean slate, which prevents deleted content from reappearing. Backups created before a deletion age out on their normal retention schedule.

## If something fails

| Failure | What you see |
|---------|--------------|
| Rate limiter unavailable | The request is blocked (`503`) instead of guessed |
| No saved memory answers the question | An explicit no-evidence result, never an invented answer |
| Provider unavailable | A normal provider-shaped error; your memory is unaffected |
| Memory saving unavailable | Your model request completes; saving is retried later |
| Console unavailable | Existing SPM keys keep working on the request service |
| Memory lookup degraded | An explicit failure or a smaller result — never another account's memory |
