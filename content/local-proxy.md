---
title: Local Proxy
description: Install and operate the SPM Local Proxy while keeping the provider credential and provider traffic on a machine you control.
published: 2026-08-21
updated: 2026-10-20
applies_to: SPM-Polaris and @spmos/local-proxy 0.1.x
---

# Local Proxy

`@spmos/local-proxy` runs on your machine and keeps your provider key there. Your client talks to the Local Proxy; the Local Proxy talks directly to your provider. SPM handles the memory side: recall lookups and eligible saved text still use the hosted memory service.

It is **not** self-hosted SPM — your memory lives in the hosted service either way. What stays local is the provider credential and the full model traffic.

Current npm release: **`@spmos/local-proxy@0.1.2`**. This package has its own release lifecycle; do not assume that every Hosted Provider Proxy feature or fix is included.

## Install

```bash
npm install --global @spmos/local-proxy@0.1.2
spm setup
spm doctor
spm start
```

Requirements:

- Node.js `>=22.15`
- an SPM key with scopes matching the memory access you want
- an upstream provider key
- a client that supports a custom Base URL

Both `spm` and `spm-local-proxy` invoke the same CLI.

## What the setup wizard asks for

- provider Base URL, API style, key, and optional custom headers/query parameters
- your SPM key and SPM API Base URL
- loopback host/port
- default memory mode, compression mode, and token budgets

Your client—not the Local Proxy—chooses the model for each request.

## Configuration

Review the address, memory/compression modes, and budgets selected by `spm setup` before starting. The client examples below use a listener at `127.0.0.1:8765`; substitute your configured address if it differs. Use `https://api.spmos.ai` for hosted memory.

Configuration is stored under `$SPM_CONFIG_HOME`, `$XDG_CONFIG_HOME/spm`, or `~/.config/spm`. Treat this directory as secret-bearing and restrict access to your local account.

## Client configuration

Codex:

```bash
spm print-config codex
export SPM_LOCAL_PROXY_TOKEN="$(spm config token)"
```

Claude Code:

```bash
spm print-config claude
```

```bash
ANTHROPIC_BASE_URL="http://127.0.0.1:8765"
ANTHROPIC_API_KEY="$SPM_LOCAL_PROXY_TOKEN"
```

OpenAI-compatible SDKs use `http://127.0.0.1:8765/v1`. Anthropic Messages traffic uses the `anthropic_messages` API style. The Local Proxy does not translate between dialects.

## What goes where

| Item | Stored locally | Sent to SPM | Sent to provider | Given to your client |
|------|----------------|-------------|------------------|----------------------|
| Provider key | Yes | No | Yes | No |
| SPM key | Yes | Used for memory calls | No | No |
| Local token | Yes | No | No | Yes |
| Recall query | Transient | Yes | Only if inserted into the prompt | Through the normal request |
| Eligible captured text | Transient | Yes | Already part of model traffic | Originates in request/response |
| Full provider request | Transient | No | Yes | Originates in your client |

Custom headers or query values containing `$API_KEY` are secrets too. Do not include them in shared configuration or diagnostic output.

## Continuity and capture limits

Compression and tool-output elision can shorten older history. A stored or ready source does not prove that recall will return every fact from it. Eligible captured tool results may be trimmed; do not treat memory as a lossless archive or assume that raw tool JSON can be restored on demand.

Automatic capture is best-effort, not a guaranteed durable retry queue. Keep original files and logs when exact recovery matters, and verify important memories with status and read tools. Hosted behavior alone is not evidence of identical behavior in this npm release.

## Local endpoints

| Endpoint | Behavior |
|----------|----------|
| `POST /v1/chat/completions` | OpenAI-compatible upstream |
| `POST /v1/responses` | OpenAI-compatible upstream |
| `POST /v1/messages` | Anthropic Messages upstream |
| `GET /v1/models` | Direct upstream relay when the provider exposes it |
| `GET /health` / `GET /livez` | Local process checks |

JSON and SSE are supported; zstd request bodies used by Codex are decoded.

## Security checklist

- Keep the listener on loopback; do not expose it as a shared gateway.
- Use the separate local token printed for your client, not your provider or SPM key.
- Use an HTTPS provider URL you trust.
- Protect local configuration, custom headers, and diagnostic output as credentials.

You remain responsible for the provider URL you choose, that provider's retention/training settings, and your local machine's security.

## Observability

Responses include `x-spm-local-proxy`, memory/compression state, original/forwarded/recalled token estimates, and `x-spm-continuity-state`.

These input-token counts are SPM estimates, not provider billing-grade usage. Only provider-reported output usage is evidence of the provider's output count; the provider invoice is separate.

Local Proxy requests do **not** create hosted receipts, so they do not appear in the dashboard **Token savings** or **Recent request receipts** views. Use the local response headers for per-request evidence.

## Troubleshooting

- `spm doctor` validates local configuration; it does not prove key scopes or complete a live provider request.
- `GET /v1/models` fails when the upstream does not expose that route.
- No reduction on a short or new conversation is expected — there was nothing safe to remove.
- One config/process selects one upstream transport, not one model. Multiple providers need separate config homes and ports.
- The foreground process stops with `Ctrl+C`; this release has no daemon manager.
