---
title: Provider proxy API
description: SPM Hosted Provider Proxy API endpoints, native request dialects, memory and compression modes, response headers, receipts, and errors.
published: 2026-08-19
updated: 2026-10-20
applies_to: SPM-Polaris
---

# Provider Proxy API

The Provider Proxy sends your request to your configured model provider, applies your memory settings, can shorten eligible conversation history, and records hosted request receipts.

Base URL: `https://api.spmos.ai`

Hosted model endpoints authenticate with `Authorization: Bearer spm_live_...`; Anthropic clients may send the same key in `x-api-key`.

## Endpoints

| Endpoint | Dialect |
|----------|---------|
| `POST /v1/chat/completions` | OpenAI Chat Completions |
| `POST /v1/responses` | OpenAI Responses |
| `POST /v1/messages` | Anthropic Messages |

Provider responses are relayed as JSON or SSE in their native dialect. Memory injection and compression can change the outgoing request; this is not a promise of byte-identical request forwarding.

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
| `shadow` | Compression is measured rather than applied to the forwarded history |
| `deterministic` | Eligible older history may be shortened after source-readiness checks. Recent exchanges and protected instructions, reasoning, and tool state constrain removal; eligible older tool results may also be shortened. |

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

Receipt lookup requires the `receipt:read` scope. The lookup response contains request metadata and lifecycle state, not token-count fields:

| Field | Meaning |
|-------|---------|
| `id` / `request_id` | Receipt and request identifiers |
| `protocol` / `model` | Request dialect and model |
| `memory_mode` / `memory_state` | Memory access mode and processing state |
| `compression_mode` | Effective compression mode |
| `request_state` / `billing_state` | Request and SPM billing lifecycle state |
| `bytes_sent` | Recorded delivered-byte count |
| `provider_usage_state` | Whether provider usage was reported; not a token count |
| `error_code` | Recorded error, if any |
| `created_at` / `updated_at` / `terminal_at` | Lifecycle timestamps |

The console exposes usage and savings separately from this lookup schema. These request receipts are not signed deletion receipts. Local Proxy traffic does not create hosted receipts.

### Reading usage numbers

SPM's original, forwarded, and recalled input-token counts are estimates, not provider billing-grade measurements. Reduction estimates do not establish invoice savings: provider caching, pricing, and other billing rules can differ. Only a provider-reported output counter is evidence of reported output usage; a missing counter must not be interpreted as zero. Your provider's invoice remains separate from SPM usage and is authoritative for its charges.

## Response headers

Successful hosted requests carry `x-spm-*` headers with the request/receipt ID and memory and compression state. When compression measurements are available, `x-spm-shadow-original-tokens` and `x-spm-shadow-forwarded-tokens` contain input estimates, not provider billing counts. `x-spm-continuity-state` describes the history decision:

| Value | Meaning |
|-------|---------|
| `committed` | Older eligible exchanges were removed after their sources passed readiness checks |
| `elided_tool_output` | Eligible older tool results were shortened after storage/readiness checks |
| `not_needed` | Nothing needed removing |
| `shadow_only` | Compression was measured but the original request was forwarded |
| `bypassed_*` | A safety check did not pass, so the full request was preserved |
| `not_applicable` | The active mode did not require a continuity decision |

A bypass means a particular compression check prevented removal; it is not proof that no other eligible transformation occurred. Source readiness does not prove that every fact will appear in a later recall. Tool-result capture is eligible for trimming, and raw JSON restoration is not a shipped guarantee. Keep original artifacts when exact reproduction matters.

## Memory lookups on the proxy path

Memory reads use the fast path by default, with bounded work rather than selector model rounds on the request path. Lookup latency can still affect time-to-first-token. A failed lookup can continue without injected context, with a degraded memory state. Compression separately checks source readiness; lookup failure does not by itself guarantee that the original history is forwarded unchanged.

Automatic capture is best-effort. A failed capture is not guaranteed durable retry work; verify important material with memory status and read tools rather than relying on a successful model response as proof of storage.

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
