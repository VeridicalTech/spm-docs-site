---
title: Local Proxy
---

# Local Proxy

`@spmos/local-proxy` is an optional loopback Provider Proxy for users who want the upstream provider credential to remain under local custody.

It is **not** self-hosted SPM. Evidence-gated recall and eligible memory ingest still call the hosted SPM memory plane.

Current npm release: **`@spmos/local-proxy@0.1.0`**.

> **Release boundary:** version `0.1.1` is prepared in the public GitHub repository but is not published to npm yet. npm `0.1.0` does not emit `x-spm-continuity-state`, protect the two most recent exchanges, require recalled evidence from the removal set, or reliably exclude streamed tool arguments and Anthropic partial JSON from memory capture. Until `0.1.1` is published, use Hosted Provider Proxy when those guarantees are required.

## Install

```bash
npm install --global @spmos/local-proxy@0.1.0
spm setup
spm doctor
spm start
```

Requirements:

- Node.js `>=22.15`
- an SPM key with scopes matching the selected memory mode
- an upstream provider key
- a downstream client that supports a custom Base URL

Both `spm` and `spm-local-proxy` invoke the same CLI.

## What the wizard configures

- provider Base URL and API style
- provider key, authentication style, headers, and query parameters
- SPM key and API Base URL
- loopback host/port
- default memory and compression modes
- input and recalled-context token budgets

The wizard searches provider metadata through the jsDelivr mirror of models.dev and caches it for 24 hours. Models.dev is discovery metadata only. The downstream harness—not Local Proxy—selects the request model.

## Default configuration

| Setting | Default |
|---------|---------|
| Bind | `127.0.0.1:8765` |
| Memory mode | `read-write` |
| Compression mode | `deterministic` |
| Input budget | 8,192 estimated tokens |
| Maximum recalled context | 512 estimated tokens |
| SPM API | `https://api.spmos.ai` |

Configuration is stored under `$SPM_CONFIG_HOME`, `$XDG_CONFIG_HOME/spm`, or `~/.config/spm`. On POSIX systems the directory is mode `0700` and the config file is mode `0600`.

## Harness configuration

### Codex

```bash
spm print-config codex
export SPM_LOCAL_PROXY_TOKEN="$(spm config token)"
```

Equivalent provider shape:

```toml
[model_providers.spm_local]
name = "SPM Local Proxy"
base_url = "http://127.0.0.1:8765/v1"
env_key = "SPM_LOCAL_PROXY_TOKEN"
wire_api = "responses"
```

### Claude Code

```bash
spm print-config claude
```

```bash
ANTHROPIC_BASE_URL="http://127.0.0.1:8765"
ANTHROPIC_API_KEY="$SPM_LOCAL_PROXY_TOKEN"
```

The provider configuration must use `anthropic_messages` for Messages traffic. OpenAI-compatible SDKs use `http://127.0.0.1:8765/v1`.

## Credential and data boundary

| Item | Stored locally | Sent to SPM | Sent to provider | Given to harness |
|------|----------------|-------------|------------------|------------------|
| Provider key | Yes | No | Yes | No |
| SPM key | Yes | Used for memory calls | No | No |
| Local token | Yes | No | No | Yes |
| Recall query | Transient | Yes | Only if inserted into provider prompt | Through normal request |
| Eligible captured text | Transient | Yes | Already part of model traffic | Originates in request/response |
| Full provider request | Transient | No as a provider request | Yes | Originates in harness |

Custom headers or query values containing `$API_KEY` are secrets and are protected with the same local configuration permissions.

## Local endpoints

| Endpoint | Behavior |
|----------|----------|
| `POST /v1/chat/completions` | OpenAI-compatible upstream |
| `POST /v1/responses` | OpenAI-compatible upstream |
| `POST /v1/messages` | Anthropic Messages upstream |
| `GET /v1/models` | Direct upstream relay when the provider exposes it |
| `GET /health` / `GET /livez` | Local process checks |

Local Proxy supports JSON and SSE and decodes zstd request bodies used by Codex. It does not translate between OpenAI and Anthropic dialects.

## Security controls

- loopback-only listener validation
- separate random local harness token and timing-safe comparison
- browser-origin and unexpected-Host rejection
- HTTPS provider URL without embedded user information
- public-address DNS validation and pinning
- final filtering of SPM, cookie, forwarding, client-IP, and hop-by-hop headers
- provider auth injection after filtering
- masked config output and no request/response-body logging
- 10 MiB request-body limit

These controls do not make an arbitrary upstream trustworthy. You remain responsible for the provider URL, retention/training settings, account security, and local machine.

## Observability

Public npm `0.1.0` responses include `x-spm-local-proxy`, request/memory/compression state, and original/forwarded/recalled token estimates. They do not include `x-spm-continuity-state`.

### Prepared for 0.1.1

The public GitHub source prepared for `0.1.1` adds `x-spm-continuity-state`. Its deterministic compression protects the two most recent eligible exchanges and removes older history only when recall reports `status=recalled`, `gate_reason=passed`, and at least one admitted evidence source bound to the exact removal set.

The prepared safe outcomes include `bypassed_empty_recall`, `bypassed_unproven_recall`, `bypassed_recall_degraded`, `bypassed_protected_context`, and `bypassed_provider_state`. These states preserve the complete request instead of forcing compression.

The prepared assistant capture is limited to visible Chat content, Responses `output_text`, and Anthropic `text`/`text_delta`. It excludes reasoning/thinking, tool/function arguments, signatures, and partial JSON from memory.

Local Proxy requests do **not** currently create hosted gateway receipts or populate Dashboard **Token savings** and **Recent request receipts**. Use the local response headers for per-request evidence.

## Troubleshooting

- `spm doctor` validates local configuration; it does not prove key scopes, bind the port, or complete a live provider request.
- `GET /v1/models` fails when the upstream does not expose that route.
- 0% reduction is normal below budget, when no complete old exchange is removable, or when recall cannot prove continuity for the planned removal.
- npm `0.1.0` predates source-bound continuity and the current capture allowlists. Do not use it when either guarantee is required. The prepared `0.1.1` source still recognizes deterministic source identities written by `0.1.0`.
- One config/process selects one upstream transport, not one model. Multiple providers require separate config homes/processes/ports.
- The foreground process stops with `Ctrl+C`; this release has no daemon manager, `status`, or `stop` command.
