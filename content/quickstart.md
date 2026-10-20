---
title: Quickstart
description: Start with SPM Hosted Provider Proxy, Local Proxy, or MCP and verify the chosen credential and memory boundary.
published: 2026-08-19
updated: 2026-10-20
applies_to: SPM-Polaris
---

# Quickstart

Give your agent a lasting memory in three steps: create a key, choose how requests reach your model provider, and verify what happened.

## 1. Create an SPM key

Sign in at `https://app.spmos.ai`, open **API Keys**, and create a key. It is shown once.

Recommended scopes:

- Any Provider Proxy or Local Proxy use: keep `gateway:invoke` selected (the console
  pre-selects it) — without it the proxy refuses model requests with 403
- Provider Proxy or Local Proxy with full memory: `memory:read` and `memory:write`
- MCP explicit memory: `memory:read` and `memory:write`; add `memory:delete` only if the agent should delete memories
- Hosted receipt lookup: add `receipt:read`
- One key for several end users: add `memory:partition` and send a stable `user_partition` value

Your key's scopes set the strongest memory access it can use. A single request can temporarily use less, never more.

## 2. Choose how requests reach your provider

### Option A — Hosted Provider Proxy

The simplest path: SPM forwards your requests, and your dashboard provides token-savings views and hosted request receipts.

1. In the console, open **Settings → Providers**.
2. Choose a preset provider and the models you want, or add a **Custom** upstream with its Base URL, API style, key, and optional headers.
3. Store it. Provider secrets are stored by SPM and never shown again.

Point your OpenAI-compatible client at SPM instead of the provider:

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.spmos.ai/v1",
    api_key="spm_live_...",
)

response = client.chat.completions.create(
    model="your-configured-model",
    messages=[{"role": "user", "content": "Remember that our deploy window is Friday."}],
)
print(response.choices[0].message.content)
```

### Option B — Local Proxy (provider key stays on your machine)

Use this when your agent supports a custom Base URL and you do not want to store the provider key in SPM. The Local Proxy runs on your machine and sends the provider key directly to your provider; only memory lookups and eligible saved text use hosted SPM.

Requirements: Node.js `>=22.15`, an SPM key, and an upstream provider key.

```bash
npm install --global @spmos/local-proxy@0.1.2
spm setup
spm doctor
spm start
```

In another terminal:

```bash
export SPM_LOCAL_PROXY_TOKEN="$(spm config token)"
spm print-config codex   # or: spm print-config claude
```

See [Local Proxy](local-proxy.html) before using custom headers or query parameters.

### Option C — MCP memory tools

Use MCP when the agent should save and find memories explicitly, without changing how it sends model requests:

Set `SPM_API_KEY` in the environment used to launch Codex, outside the configuration file:

```bash
export SPM_API_KEY="spm_live_..."
```

```toml
[mcp_servers.spm]
url = "https://api.spmos.ai/mcp"
bearer_token_env_var = "SPM_API_KEY"
```

This uses the [official Codex Streamable HTTP configuration](https://developers.openai.com/codex/mcp#streamable-http-servers). Do not commit the key; restart the client with the environment variable available.

The production server name is **SPM**. Its five primary tools are `remember`, `recall`, `read`, `delete`, and `status`; compatibility aliases `add_memory`, `search_memory`, and `delete_memory` may also appear in the catalog.

## 3. Verify what happened

- **Hosted proxy:** open **Token savings** and **Recent request receipts** in the dashboard. `GET /v1/spm/requests` provides request metadata and memory outcomes, not per-request token counts or cryptographic signatures.
- **Local Proxy:** inspect the local `x-spm-*` response headers. Local Proxy requests do not create hosted receipts.
- **MCP:** verify a complete save → ready → recall → read round trip, not just a successful connection or tool listing. See the [MCP round trip](mcp.html#recommended-round-trip).

For example, ask the agent to call `remember` with this tool-argument object (choose a fresh source ID and idempotency key for your test):

```json
{
  "text": "The docs-smoke project deployment window is Friday at 16:00 UTC.",
  "source_id": "docs-smoke-20261020-01",
  "idempotency_key": "docs-smoke-20261020-01-save"
}
```

Call `status` with `{"source_ids":["docs-smoke-20261020-01"]}` and wait for that source to be searchable. A failed or missing source is not ready. Then call `recall` with `{"question":"When is the docs-smoke project deployment window?"}`.

Check the returned evidence against your saved fact, then pass `evidence_refs[].read_token` verbatim as an element of `read_tokens` to `read` and check the original text. Readiness alone does not prove recall completeness. Delete the test source afterward with `delete`, using the same `source_id` and a new `idempotency_key` (requires `memory:delete`).

## 4. When will I see savings?

Savings can appear when eligible older exchanges are stored as sources and omitted from the forwarded prompt. Short or new conversations can correctly show no reduction. The result depends on the request and memory settings; compression and source readiness do not promise that semantic recall will recover every detail. Read original sources when exact content matters.

## Next steps

- [Your memory](memory.html)
- [Provider Proxy API](proxy-api.html)
- [Local Proxy](local-proxy.html)
- [MCP server](mcp.html)
