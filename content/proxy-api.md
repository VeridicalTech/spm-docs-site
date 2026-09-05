---
title: Provider proxy API
description: SPM Hosted Provider Proxy API endpoints, native request dialects, memory and compression modes, response headers, receipts, and errors.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
---

# Provider Proxy API

The Provider Proxy sends your request to your configured model provider, applies your memory settings, shortens long conversation history when it is safe, and records a receipt for every request.

Base URL: `https://api.spmos.ai`

Hosted model endpoints authenticate with `Authorization: Bearer spm_live_...`; Anthropic clients may send the same key in `x-api-key`.

## Endpoints

| Endpoint | Dialect |
|----------|---------|
| `POST /v1/chat/completions` | OpenAI Chat Completions |
| `POST /v1/responses` | OpenAI Responses |
| `POST /v1/messages` | Anthropic Messages |

Provider JSON and SSE bytes are relayed in their native dialect. Unknown fields, event ordering, reasoning/tool state, and provider identifiers are passed through unchanged.

## Memory modes

Without an override, your SPM key uses the strongest memory access its scopes allow:

| Key scopes | Default memory mode |
|------------|---------------------|
| read + write | `read-write` |
| read only | `read` |
| write only | `write` |
| neither | `off` |

Lower the mode per request:

```text
x-spm-memory-mode: off | read | write | read-write
```

A header cannot grant access beyond the key's scopes.

## Compression modes

```text
x-spm-compression-mode: passthrough | shadow | deterministic
```

| Mode | What your provider receives |
|------|------------------------------|
| `passthrough` | The original request, plus recalled memory when available |
| `shadow` | The original request unchanged; SPM only measures what compression would have done, so you can evaluate it risk-free |
| `deterministic` | Older exchanges are removed when their content is safely stored as memory. The two most recent exchanges, your instructions, tool state, and model reasoning are always kept. |

Memory and compression are independent: you can save and recall memory without shortening anything, or measure compression without saving.

Set account defaults in **Settings → Proxy**: compression mode, input budget, and maximum recalled context. A per-request header still overrides them for a single request.

## Why a receipt can show 0%

Reduction is expected only when the history is long and its older parts are already stored as memory. Short requests, new conversations, and requests dominated by protected state (tools, reasoning) correctly show `original_input_tokens == forwarded_input_tokens`. This is expected behavior, not a malfunction.

## Request receipts

Every hosted request produces a receipt you can inspect:

```text
GET /v1/spm/requests?limit=50
GET /v1/spm/requests/{receipt_id}
```

Receipt lookup requires the `receipt:read` scope. Key fields:

| Field | Meaning |
|-------|---------|
| `original_input_tokens` | Estimated input SPM received |
| `forwarded_input_tokens` | Estimated input actually sent to the provider |
| `recalled_tokens` | Memory added to the provider prompt |
| `output_tokens` | Provider output tokens when reported |
| `memory_mode` / `memory_state` | Requested access and what actually happened |
| `compression_mode` | Effective mode after any safe fallback |

The dashboard **Token savings** and **Recent request receipts** views are built from these records. Local Proxy traffic does not create hosted receipts.

## Response headers

Successful hosted requests carry `x-spm-*` headers with the request/receipt ID, memory and compression state, and token estimates. `x-spm-continuity-state` tells you what happened to older history:

| Value | Meaning |
|-------|---------|
| `committed` | Older exchanges were removed because recalled memory provably covers them |
| `elided_tool_output` | Older tool outputs were removed after being safely stored; they remain retrievable on demand |
| `not_needed` | Nothing needed removing |
| `shadow_only` | Compression was measured but the original request was forwarded |
| `bypassed_*` | A safety check did not pass, so the full request was preserved |
| `not_applicable` | The active mode did not require a continuity decision |

A bypass is a safe fallback, not an error: SPM forwards the complete request rather than risking your provider's state.

## Errors

| HTTP | Example code | Meaning |
|------|--------------|---------|
| 401 | auth invalid/revoked | SPM key is missing, malformed, revoked, or stale |
| 403 | scope/access denied | Key or tenant cannot perform the operation |
| 409 | stale generation or idempotency conflict | Retry only according to the returned state |
| 422 | invalid mode | Request violates policy |
| 429 | `RATE_LIMIT_EXCEEDED` | Plan rate budget exceeded; honor `Retry-After` |
| 503 | `RATE_LIMITER_UNAVAILABLE` | Rate-limit checking is unavailable, so the request is blocked instead of guessed |
| 5xx | provider/dependency failure | Inspect the receipt/error code before retrying |

Health probes: `GET /health`, `GET /livez`, and `GET /readyz`.
