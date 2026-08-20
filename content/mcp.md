---
title: MCP server
---

# MCP server

SPM-Polaris provides a streamable HTTP MCP server for agent memory:

```
https://api.spmos.ai/mcp
Authorization: Bearer spm_live_...
```

The MCP server and the provider proxy accept the same `spm_live` key and enforce the same tenancy, scopes, and evidence gate.

## Tools

| Tool | Parameters | What it does | Scope |
|------|-----------|--------------|-------|
| `remember` | `text` (required), `idempotency_key` (required), `source_id`?, `topic`? (default `general`) | Store one memory source idempotently | `memory:write` |
| `recall` | `question` (required), `top_k`? (default 20, max 50) | Evidence-gated recall; returns `evidence_refs` with short-lived `read_token` values | `memory:read` |
| `read` | `read_tokens` (required, JSON array) | Resolve read tokens from a recall result back to the original source span text | `memory:read` |
| `delete` | `source_id` (required), `idempotency_key` (required) | Delete one source and its derived candidates idempotently | `memory:delete` |
| `status` | `source_ids`? (array) | Account-scoped memory readiness without loading all records | `memory:read` |

Notes on usage:

- Pass the `read_token` strings from `recall` evidence refs to `read` **verbatim** — do not parse, unwrap, or re-serialize them. The parameter is always an array, even for a single token.
- `recall` applies the same evidence gate as the proxy path: when nothing qualifies, the result is an explicit empty/refused outcome with a gate reason, never invented content.
- `remember` and `delete` are idempotent — retrying with the same idempotency key is safe and does not double-write.

## Client configuration

**Codex** (`config.toml`):

```toml
[mcp_servers.spm]
url = "https://api.spmos.ai/mcp"
headers = { Authorization = "Bearer spm_live_..." }
```

**Claude Code** / generic MCP JSON:

```json
{
  "mcpServers": {
    "spm": {
      "url": "https://api.spmos.ai/mcp",
      "headers": { "Authorization": "Bearer spm_live_..." }
    }
  }
}
```

## Health

The MCP server exposes unauthenticated `/health`, `/livez`, and `/readyz` probes; readiness reports the memory API and control-database dependencies individually and returns `503` while degraded.
