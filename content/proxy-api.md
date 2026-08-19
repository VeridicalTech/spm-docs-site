---
title: Provider proxy API
---

# Provider proxy API

Base URL: `https://api.spmos.ai`

All endpoints except health probes require `Authorization: Bearer spm_live_...` (or `x-api-key` for the Anthropic dialect).

## Chat Completions

`POST /v1/chat/completions` — a drop-in endpoint for the OpenAI Chat Completions API.

```json
{
  "model": "deepseek-chat",
  "messages": [{"role": "user", "content": "What did we decide about the deploy window?"}],
  "stream": true
}
```

Streaming passes provider chunks through as they are emitted while SPM observes usage and completion in parallel. Tool calling and provider-specific parameters pass through unmodified.

## Responses

`POST /v1/responses` — OpenAI Responses API dialect.

## Messages

`POST /v1/messages` — Anthropic Messages dialect. Send Anthropic model names and payload shapes; they are forwarded natively.

## What every request gets

Regardless of dialect, each request passes through the same pipeline: authentication and tenant resolution, plan rate limit, evidence-gated memory recall, deterministic compression, native-dialect forwarding, streaming, asynchronous ingest, and a signed receipt.

## Request receipts

Every request writes a signed receipt:

```
GET /v1/spm/requests?limit=50        # list (requires receipt:read)
GET /v1/spm/requests/{receipt_id}    # single receipt
```

A receipt records the protocol dialect, model, latency, status, and full token accounting:

| Field | Meaning |
|-------|---------|
| `original_input_tokens` | Estimated tokens of the request exactly as SPM received it |
| `forwarded_input_tokens` | Estimated tokens actually sent to the provider after memory-gated assembly |
| `recalled_tokens` | Memory evidence tokens SPM added to the prompt |
| `output_tokens` | Completion tokens returned by the provider |

Receipts are the source of truth for usage and debugging. On long conversations, the gap between `original_input_tokens` and `forwarded_input_tokens` shows how much replayed context the memory plane removed, while `recalled_tokens` shows precisely what gated evidence SPM added back.

## Rate limits

Requests are throttled per plan by a distributed, fail-closed limiter:

| Plan | Budget |
|------|--------|
| Free | 10 requests/minute |
| Starter | 30 requests/minute |
| Growth | 100 requests/minute |
| Enterprise | Reviewed before activation |

Exceeding the budget returns `429`. If the limiter itself is unavailable, SPM returns `503 RATE_LIMITER_UNAVAILABLE` — it fails closed rather than serving unlimited traffic.

## Health

`GET /health`, `GET /livez`, `GET /readyz` — no auth, for load balancers and monitors.

## Errors

| HTTP | Code | Meaning |
|------|------|---------|
| 401 | auth | Missing, malformed, or revoked key |
| 403 | scope | Key lacks the required scope |
| 429 | quota | Plan quota or rate budget exceeded — back off or upgrade |
| 503 | `RATE_LIMITER_UNAVAILABLE` | The distributed limiter is down; SPM fails closed |
| 5xx | upstream | Provider errors are mapped through with their original status |

Retry `429` and `503` responses with exponential backoff. Requests are idempotent at the memory layer, so a retried response never writes memory twice.
