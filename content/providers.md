---
title: Bring your own provider
---

# Bring your own provider

SPM does not resell model inference. You keep an upstream provider account and choose one of two credential-custody models.

## Credential custody

| | Hosted Provider Proxy | Local Proxy |
|---|---|---|
| Provider key storage | Encrypted SPM vault | Protected local config |
| Model request path | Client → SPM → provider | Client → loopback Local Proxy → provider |
| SPM memory path | Hosted | Hosted |
| Hosted gateway receipts | Yes | No |
| Model selection | Request model routed against allowed models | Downstream harness sends the model |

Neither path is universally safer. Hosted forwarding centralizes operations and receipts. Local Proxy reduces provider-key disclosure to SPM but adds local configuration and process-security responsibilities.

## Native API styles

| API style | Endpoint |
|-----------|----------|
| OpenAI Chat Completions | `POST /v1/chat/completions` |
| OpenAI Responses | `POST /v1/responses` |
| Anthropic Messages | `POST /v1/messages` |

SPM is not a cross-dialect translator. Requests and provider responses stay in the configured native style.

## Hosted provider configurations

One active provider configuration represents one upstream Base URL, credential, API style, custom-header/query set, default model, and `allowed_models[]`.

- A request with an explicit model routes to the configuration that owns that model.
- A request without a model uses the default channel/model for that API style.
- Two active configurations under the same tenant and API style cannot claim the same model.
- One upstream configuration can serve multiple models; do not create a new provider row solely to change model.

## Presets and models.dev

Preset provider model choices come from the reviewed models.dev-backed catalog. The catalog refreshes with stale-while-revalidate and a bundled fallback.

Discovery is not transport approval. A provider appearing in models.dev does not automatically bypass SPM's HTTPS, SSRF, data-retention, protocol, or cost review.

Preset providers do **not** live-fetch `/models`. This keeps the catalog stable and avoids provider-specific permission/cost surprises.

## Custom BYO

Use **Custom** for a self-hosted gateway, regional provider, enterprise proxy, or provider not covered by a preset.

You configure:

- HTTPS Base URL
- `openai_compatible` or `anthropic_messages` API style
- provider key
- default model and allowed models
- optional custom headers and query parameters

Only Custom channels can use **Fetch models**. For an existing channel, the server-only BFF reads the credential temporarily from the vault, performs the guarded probe, and returns model identifiers—not the credential—to the browser.

Custom probes and forwarding enforce HTTPS and public-address DNS pinning. SPM, cookie, forwarding, Cloudflare/client-IP, and hop-by-hop headers are removed after caller and custom headers are merged; provider authentication is injected last.

## Protocol transparency

Unknown provider JSON fields and valid diagnostic headers pass through by default. Responses SSE event order and response/item/part IDs are not rebuilt. Anthropic thinking and OpenAI reasoning state stay in provider traffic.

The separate memory observer captures only visible assistant text. Reasoning, thinking, redacted thinking, function/tool arguments, and partial JSON are not written as memory.

## Revocation and limits

Revoking a key or provider configuration removes it from the console and stops it from authenticating or routing. Provider-channel limits are enforced by plan; deleting a provider frees its slot.

## Provider retention and training

The upstream provider's own retention, training opt-out, regional-processing, and account settings apply to model traffic. SPM cannot change those settings for you. Review the provider's terms before sending sensitive content.
