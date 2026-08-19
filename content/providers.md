---
title: Bring your own provider
---

# Bring your own provider

SPM does not meter inference. Models run on your provider accounts; SPM operates the surrounding memory plane and forwards requests in each provider's native dialect.

## Supported dialects

The gateway natively proxies three API dialects:

| Dialect | Endpoint | Typical providers |
|---------|----------|-------------------|
| OpenAI Chat Completions | `POST /v1/chat/completions` | OpenAI, DeepSeek, Azure OpenAI, most compatible APIs |
| OpenAI Responses | `POST /v1/responses` | OpenAI Responses-API models |
| Anthropic Messages | `POST /v1/messages` | Anthropic Claude and compatible endpoints |

There is no translation loss between dialects. An Anthropic-format request is projected for memory work, then forwarded to an Anthropic-compatible upstream in its native format — never rewritten through OpenAI's dialect.

## Provider presets

The console ships presets for the major providers. A preset pre-fills the base URL, the API style, and direct links to the provider's key page and documentation, so adding a channel is usually just pasting a key and picking a model:

| Preset | API style |
|--------|-----------|
| OpenAI | OpenAI-compatible |
| Anthropic | Anthropic Messages |
| DeepSeek | OpenAI-compatible |
| OpenRouter | OpenAI-compatible |
| Groq | OpenAI-compatible |
| Mistral | OpenAI-compatible |
| xAI | OpenAI-compatible |
| Together AI | OpenAI-compatible |
| Fireworks AI | OpenAI-compatible |
| Moonshot AI | OpenAI-compatible |
| Alibaba DashScope | OpenAI-compatible |

Azure OpenAI works through a custom channel: paste the full deployment URL as the base URL.

## Custom endpoints

Choose **Custom** to connect any endpoint that speaks one of the supported dialects — a self-hosted vLLM/Ollama gateway, a regional provider, or an enterprise proxy. You keep full control of every parameter:

- **Base URL** — the exact upstream root SPM forwards to
- **API style** — OpenAI-compatible or Anthropic Messages; pick the dialect the endpoint actually speaks
- **Model** — any model name the endpoint serves, typed directly or picked from the probed list
- **API key** — vaulted like any preset credential

Custom channels are first-class: they get the same memory plane, the same receipts, and the same quota accounting as preset channels.

Outbound calls from SPM are guarded: HTTPS-only transport, DNS resolution pinned to global addresses (SSRF protection), and response size/time caps. The same guardrails apply when the console probes a connection.

## The live model catalog

Model pickers are fed by a live catalog aggregated from the MIT-licensed [models.dev](https://models.dev) dataset, not a static list baked into a release:

- The catalog refreshes automatically (12-hour TTL with stale-while-revalidate) and falls back to a bundled snapshot if the upstream is unreachable.
- Each channel form labels the catalog state — **live**, **live-stale** (serving the last good fetch), or **bundled** — with its fetch time, so you always know how fresh the list is.
- Models carry badges for context window, max output tokens, input/output price per million tokens, and reasoning / tool-calling capability where the catalog reports them.
- New providers that appear in the upstream dataset enter the catalog for review; they never bypass SPM's transport, SSRF, data-retention, or cost review automatically.

## Test connection

The channel form's **Test connection** button validates the credential against the provider's live model list before you save — with the same SSRF guardrails as production traffic. A successful probe returns the models the key can actually see, which also powers manual model entry for custom endpoints.

## Channel limits

Channels per plan: **Free 1 · Starter 3 · Growth 10 · Enterprise reviewed**. Deleting a channel frees its slot immediately.

## What happens per request

```
your key -> tenant + channel resolution -> memory recall
         -> evidence gate -> deterministic compression
         -> provider forwarding (native dialect)
         -> streaming response -> async ingest -> signed receipt
```

Recall and forwarding are separate stages. The provider does not control what SPM remembers, ranks, admits, or compresses.

## Provider failures

An upstream error maps to a standard provider-shaped error with the upstream status, so your existing retry logic keeps working. A provider outage affects only requests through that channel; the memory plane and your other channels remain available.

## Cost model

- **You pay your provider** for inference as before — reduced by whatever context SPM's compression removes before forwarding.
- **You pay SPM** a flat plan price for the memory plane ([Plans & quotas](plans.html)).
- SPM's extraction, recall ranking, and compression are deterministic code and add nothing to an inference bill.
