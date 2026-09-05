---
title: Bring your own provider
description: Configure upstream model providers for SPM Hosted Provider Proxy or Local Proxy and understand credential, traffic, and billing boundaries.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
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

## Presets, auto-admission, and models.dev

The provider catalog is backed by models.dev and refreshes automatically with stale-while-revalidate plus a committed snapshot fallback.

Two tiers of providers appear in Settings:

- **Preset providers** (major providers such as OpenAI, Anthropic, DeepSeek) carry curated metadata — console links, docs, and connection details.
- **Auto-admitted providers**: when the live catalog lists a provider with a working HTTPS endpoint, a documented credential variable, and at least one chat-capable model, it becomes selectable without waiting for a review cycle. Pricing (input/output per 1M tokens), context window, and capability markers (reasoning, tool calling) refresh with the catalog.

Auto-admission is not a safety bypass: every request still goes through the same HTTPS-only, public-IP-pinned, SSRF-checked transport, and an auto-admitted channel stores its catalog-provided endpoint at creation time. Providers whose catalog entry is incomplete (no usable endpoint or credential variable) remain discovery-only and are never routable.

Preset providers do **not** live-fetch `/models`. This keeps the catalog stable and avoids provider-specific permission/cost surprises.

## Custom BYO

Use **Custom** for a self-hosted gateway, regional provider, enterprise proxy, or provider not covered by a preset.

You configure:

- HTTPS Base URL
- `openai_compatible` or `anthropic_messages` API style
- provider key
- default model and allowed models
- optional custom headers and query parameters

Only Custom channels can use **Fetch models**. For an existing channel, the server-only BFF reads the credential temporarily from the vault, performs the guarded probe, and returns model identifiers—not the credential—to the browser. If the upstream has no model-list endpoint at all, you can also type a model ID in manually.

Custom probes and forwarding enforce HTTPS and public-address DNS pinning. SPM, cookie, forwarding, Cloudflare/client-IP, and hop-by-hop headers are removed after caller and custom headers are merged; provider authentication is injected last.

## Protocol transparency

Unknown provider JSON fields and valid diagnostic headers pass through by default. Responses SSE event order and response/item/part IDs are not rebuilt. Anthropic thinking and OpenAI reasoning state stay in provider traffic.

The separate memory observer captures only visible assistant text. Reasoning, thinking, redacted thinking, function/tool arguments, and partial JSON are not written as memory.

## Revocation and limits

Revoking a key or provider configuration removes it from the console and stops it from authenticating or routing. Provider-channel limits are enforced by plan; deleting a provider frees its slot.

## Provider retention and training

The upstream provider's own retention, training opt-out, regional-processing, and account settings apply to model traffic. SPM cannot change those settings for you. Review the provider's terms before sending sensitive content.
