---
title: Quickstart
---

# Quickstart

Choose the integration that matches your credential boundary.

## 1. Create an SPM key

Sign in at `https://app.spmos.ai`, open **API Keys**, and create a key. It is shown once.

Recommended scopes:

- Provider Proxy or Local Proxy with full memory: `memory:read` and `memory:write`
- MCP explicit memory: add `memory:delete` only if the agent should delete sources
- Hosted receipt lookup: add `receipt:read`

The key's memory scopes determine the hosted proxy's default memory mode. A request can lower that mode, but it cannot grant itself a scope the key does not have.

## 2. Choose a provider path

### Option A — Hosted Provider Proxy

Use this when you want SPM to operate forwarding and hosted gateway receipts.

1. Open **Providers** in the console.
2. Select one upstream configuration and one or more allowed models.
3. For a preset provider, select models from the models.dev-backed catalog. Presets do not probe provider `/models`.
4. For **Custom**, enter the Base URL, API style, key, and optional headers/query parameters. Custom channels can fetch the upstream model list.
5. Store the channel. Provider secrets are vaulted and are never returned to the browser.

Point an OpenAI-compatible client at:

```text
https://api.spmos.ai/v1
```

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

### Option B — Local provider credential custody

Use this when the harness supports a custom Base URL and you do not want to vault the upstream provider key in SPM.

Requirements: Node.js `>=22.15`, an SPM key, and an upstream provider key.

```bash
npm install --global @spmos/local-proxy@0.1.0
spm setup
spm doctor
spm start
```

Public npm `0.1.0` predates `x-spm-continuity-state`, two-exchange protection, source-bound evidence matching, and visible-text capture allowlists. Those changes are prepared in public GitHub source for `0.1.1`, but npm publication is pending. Use Hosted Provider Proxy when these guarantees are required.

In another terminal:

```bash
export SPM_LOCAL_PROXY_TOKEN="$(spm config token)"
spm print-config codex
# or
spm print-config claude
```

The harness sends its chosen model to Local Proxy. Local Proxy sends the provider key directly to the configured upstream, while recall queries and eligible memory content still go to hosted SPM.

See [Local Proxy](local-proxy.html) before using custom headers or query parameters.

### Option C — MCP memory tools

Use MCP when the agent should explicitly remember and recall while keeping its existing model transport:

```toml
[mcp_servers.spm]
url = "https://api.spmos.ai/mcp"
headers = { Authorization = "Bearer spm_live_..." }
```

The production server name is **SPM** and the tools are exactly `remember`, `recall`, `read`, `delete`, and `status`.

## 3. Verify behavior

For hosted proxy requests, inspect:

- `x-spm-memory-mode`
- `x-spm-memory-state`
- `x-spm-compression-mode`
- `x-spm-continuity-state`
- `x-spm-request-id`
- `x-spm-receipt-id`

Dashboard **Token savings** and **Recent request receipts** are backed by terminal hosted-gateway receipts.

For Local Proxy, inspect its local `x-spm-*` response headers. Public npm `0.1.0` does not include `x-spm-continuity-state`; that header is prepared for `0.1.1`. Local Proxy requests do not currently create hosted gateway receipts and do not populate hosted gateway savings views.

## 4. Understand 0% reduction

The default deterministic input budget is 8,192 estimated tokens. Token reduction requires:

1. a history above the active budget; and
2. at least one complete old exchange that is safe to remove.

Short histories, single-turn requests, provider-managed state, or histories composed only of protected system/tool/reasoning/thinking content can correctly show 0%.

## Next steps

- [Provider Proxy API](proxy-api.html)
- [Local Proxy](local-proxy.html)
- [MCP server](mcp.html)
- [Memory, evidence & deletion](memory.html)
