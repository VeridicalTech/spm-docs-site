---
title: Local Proxy
description: Install and operate the SPM Local Proxy while keeping the provider credential and provider traffic on a machine you control.
published: 2026-08-21
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0 and @spmos/local-proxy 0.1.x
---

# Local Proxy

`@spmos/local-proxy` runs on your machine and keeps your provider key there. Your client talks to the Local Proxy; the Local Proxy talks directly to your provider. SPM handles the memory side: recall lookups and eligible saved text still use the hosted memory service.

It is **not** self-hosted SPM — your memory lives in the hosted service either way. What stays local is the provider credential and the full model traffic.

Current npm release: **`@spmos/local-proxy@0.1.2`**. It adds the same conversation-continuity, capture-hygiene, and tool-output elision protections as the Hosted Provider Proxy.

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

## Default configuration

| Setting | Default |
|---------|---------|
| Bind | `127.0.0.1:8765` |
| Memory mode | `read-write` |
| Compression mode | `deterministic` |
| Input budget | 8,192 estimated tokens |
| Maximum recalled context | 512 estimated tokens |
| SPM API | `https://api.spmos.ai` |

Configuration is stored under `$SPM_CONFIG_HOME`, `$XDG_CONFIG_HOME/spm`, or `~/.config/spm`, with owner-only file permissions.

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

Custom headers or query values containing `$API_KEY` are secrets and are protected with the same local file permissions.

## What 0.1.2 protects

- The two most recent exchanges are never removed from a request.
- Older history is removed only when its content is provably covered by recalled memory; otherwise the full request is sent.
- Old tool outputs are replaced by short retrievable stubs once the identical content is safely stored in memory and can be recalled — on every supported protocol, including Anthropic Messages (tool pairing is never broken, and prompt-cache breakpoints are never touched).
- Reasoning, thinking blocks, tool-call arguments, and partial streamed JSON are never saved as memory.
- Every response carries `x-spm-continuity-state` so you can see which decision was made, plus `x-spm-elided-items` / `x-spm-elided-tokens` when stubs were used.

Optional knobs: `proxy.elisionEnabled` (default on), `proxy.elisionKeepRounds` (default 4), `proxy.elisionCaptureLimit` (default 8).

## Local endpoints

| Endpoint | Behavior |
|----------|----------|
| `POST /v1/chat/completions` | OpenAI-compatible upstream |
| `POST /v1/responses` | OpenAI-compatible upstream |
| `POST /v1/messages` | Anthropic Messages upstream |
| `GET /v1/models` | Direct upstream relay when the provider exposes it |
| `GET /health` / `GET /livez` | Local process checks |

JSON and SSE are supported; zstd request bodies used by Codex are decoded.

## Security controls

- accepts connections only from the local machine
- uses a separate random local token for your client
- rejects browser-origin and unexpected-host requests
- requires an HTTPS provider URL and validates the address before use
- strips SPM, cookie, forwarding, and client-IP headers before forwarding
- masks config output and never logs request or response bodies
- 10 MiB request-body limit

You remain responsible for the provider URL you choose, that provider's retention/training settings, and your local machine's security.

## Observability

Responses include `x-spm-local-proxy`, memory/compression state, original/forwarded/recalled token estimates, and `x-spm-continuity-state`.

Local Proxy requests do **not** create hosted receipts, so they do not appear in the dashboard **Token savings** or **Recent request receipts** views. Use the local response headers for per-request evidence.

## Troubleshooting

- `spm doctor` validates local configuration; it does not prove key scopes or complete a live provider request.
- `GET /v1/models` fails when the upstream does not expose that route.
- No reduction on a short or new conversation is expected — there was nothing safe to remove.
- One config/process selects one upstream transport, not one model. Multiple providers need separate config homes and ports.
- The foreground process stops with `Ctrl+C`; this release has no daemon manager.
