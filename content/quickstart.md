---
title: Quickstart
description: Start with SPM Hosted Provider Proxy, Local Proxy, or MCP and verify the chosen credential and memory boundary.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
---

# Quickstart

Give your agent a lasting memory in three steps: create a key, choose how requests reach your model provider, and verify what happened.

## 1. Create an SPM key

Sign in at `https://app.spmos.ai`, open **API Keys**, and create a key. It is shown once.

Recommended scopes:

- Any Provider Proxy or Local Proxy use: keep `gateway:invoke` selected (the console
  pre-selects it) — without it the proxy refuses model requests with 403
- Provider Proxy or Local Proxy with full memory: `memory:read` and `memory:write`
- MCP explicit memory: add `memory:delete` only if the agent should delete memories
- Hosted receipt lookup: add `receipt:read`
- One key for several end users: add `memory:partition` and send a stable `user_partition` value

Your key's scopes set the strongest memory access it can use. A single request can temporarily use less, never more.

## 2. Choose how requests reach your provider

### Option A — Hosted Provider Proxy

The simplest path: SPM forwards your requests, and your dashboard shows token savings and receipts for every request.

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
npm install --global @spmos/local-proxy@0.1.3
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

```toml
[mcp_servers.spm]
url = "https://api.spmos.ai/mcp"
headers = { Authorization = "Bearer spm_live_..." }
```

The production server name is **SPM** and the tools are exactly `remember`, `recall`, `read`, `delete`, and `status`.

## 3. Verify what happened

- **Hosted proxy:** open the dashboard — **Token savings** and **Recent request receipts** show what each request did. Programmatic access: `GET /v1/spm/requests`.
- **Local Proxy:** inspect the local `x-spm-*` response headers. Local Proxy requests do not create hosted receipts.

## 4. When will I see savings?

Savings appear when a conversation is long enough that its older parts are already stored as memory and can stop being resent. Short or new conversations correctly show no reduction — there was nothing safe to remove yet. This is expected behavior, not a malfunction.

## Next steps

- [Your memory](memory.html)
- [Provider Proxy API](proxy-api.html)
- [Local Proxy](local-proxy.html)
- [MCP server](mcp.html)
