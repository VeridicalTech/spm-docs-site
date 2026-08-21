---
title: Provider Proxy API
---

# Provider Proxy API

Base URL: `https://api.spmos.ai`

Hosted model endpoints authenticate with `Authorization: Bearer spm_live_...`; Anthropic clients may use the same SPM key in `x-api-key`.

## Endpoints

| Endpoint | Dialect |
|----------|---------|
| `POST /v1/chat/completions` | OpenAI Chat Completions |
| `POST /v1/responses` | OpenAI Responses |
| `POST /v1/messages` | Anthropic Messages |

Provider JSON and SSE bytes are relayed in their native dialect. Unknown fields, event ordering, reasoning/tool state, and provider identifiers are not normalized through another protocol.

## Scope-derived memory defaults

Without an override, the SPM key selects its strongest authorized memory mode:

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

A header cannot upgrade beyond the key's scopes.

## Compression modes

```text
x-spm-compression-mode: passthrough | shadow | deterministic
```

| Mode | Provider input |
|------|----------------|
| `passthrough` | Original request, plus recalled context when memory read succeeds |
| `shadow` | Original request unchanged; SPM measures the eligible compression result for observability |
| `deterministic` | Safely removable complete old exchanges may be removed and admitted recall may be inserted |

Memory and compression are separate controls. Opaque provider state—including system/developer instructions, tool exchanges, Responses reasoning, and Anthropic thinking/redacted thinking—is protected from removal.

When pricing metadata is unavailable and charging is disabled, deterministic mode still uses the conservative 8,192-token fallback input budget. When charging is enabled, an unknown unpriced model fails closed with `422 spm_model_unpriced`.

## Why a receipt can show 0%

Reduction is expected only when the history exceeds its active budget and includes a safely removable complete old exchange. Short requests, single-turn requests, and fully protected histories correctly produce:

```text
original_input_tokens == forwarded_input_tokens
```

This does not mean forwarding or receipts are broken.

## Request receipts

```text
GET /v1/spm/requests?limit=50
GET /v1/spm/requests/{receipt_id}
```

Receipt lookup requires `receipt:read`. The public lookup response exposes operational metadata: protocol, model, modes, request/billing/memory states, bytes sent, provider-usage state, errors, and timestamps.

The internal terminal receipt authority also stores token accounting used by Dashboard:

| Field | Meaning |
|-------|---------|
| `original_input_tokens` | Estimated input received by SPM |
| `forwarded_input_tokens` | Estimated input sent to the provider |
| `recalled_tokens` | Admitted memory added to the provider prompt |
| `output_tokens` | Provider output tokens when reported |
| `memory_mode` / `memory_state` | Requested capability and terminal persistence/recall state |
| `compression_mode` | Effective mode after safe bypass/degradation |

Dashboard **Token savings** and **Recent request receipts** use those internal terminal records, including uncharged traffic. Historical receipts created before token columns existed can contain zeros. The current public `/v1/spm/requests` schema does not expose the four token columns directly.

Local Proxy traffic does not traverse this hosted gateway and therefore does not create hosted gateway receipts.

## Response headers

Successful hosted requests include SPM observability headers such as request/receipt ID, memory mode/state, compression mode, and echo-filter counts where applicable. Shadow mode also reports its estimated original and candidate-forwarded token counts.

## Safe bypasses

SPM falls back to passthrough when deterministic compression cannot safely project the protocol state or memory recall is degraded. Provider-managed Responses chains can also require passthrough. A bypass preserves provider semantics instead of forcing reduction.

## Errors

| HTTP | Example code | Meaning |
|------|--------------|---------|
| 401 | auth invalid/revoked | SPM key is missing, malformed, revoked, or stale |
| 403 | scope/access denied | Key or tenant cannot perform the operation |
| 409 | stale fence/idempotency conflict | Retry only according to the returned state |
| 422 | invalid mode / `spm_model_unpriced` | Request violates policy or charging catalog |
| 429 | `RATE_LIMIT_EXCEEDED` | Plan rate budget exceeded; honor `Retry-After` |
| 503 | `RATE_LIMITER_UNAVAILABLE` | Distributed limiter failed closed |
| 5xx | provider/dependency failure | Inspect receipt/error code before retrying |

Health probes: `GET /health`, `GET /livez`, and `GET /readyz`.
