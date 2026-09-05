---
title: MCP server
description: Connect an MCP client to SPM memory tools for governed remember, recall, read, delete, and status operations.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
---

# MCP server

SPM exposes account-scoped memory as a stateless streamable HTTP MCP server:

```text
https://api.spmos.ai/mcp
Authorization: Bearer spm_live_...
```

The production server name is **SPM**. Tool names are exactly `remember`, `recall`, `read`, `delete`, and `status`; clients do not need product-version aliases.

## Tools

| Tool | Important parameters | Result |
|------|----------------------|--------|
| `remember` | `text`, `idempotency_key`, optional `source_id`, `topic`, and `user_partition` | Queues one source idempotently |
| `status` | optional `source_ids[]` | Reports readiness without reading full records |
| `recall` | `question`, optional `top_k` (default 20, max 50) and `user_partition` | Best-evidence answer plus bounded evidence refs |
| `read` | `read_tokens[]`, optional `user_partition` | Resolves selected evidence to verified source text |
| `delete` | `source_id`, `idempotency_key` | Deletes a source and derived candidates idempotently |

Scopes: `remember` requires `memory:write`; `recall`, `read`, and `status` require `memory:read`; `delete` requires `memory:delete`. Selecting a non-empty `user_partition` additionally requires `memory:partition`.

### One key, many end users

For a multi-user application, keep one application key and pass a stable opaque
partition identifier (normally your internal user UUID) on every `remember`,
`recall`, and `read` call for that user:

```json
{
  "question": "Which writing style do I prefer?",
  "user_partition": "user-123"
}
```

Partitions are isolated within the tenant. A different partition receives no evidence
from this one, and a read token minted for one partition cannot be used in another.
Omitting the field selects the tenant's default space, so use omission only when a
shared default area is intentional. If you supply `source_id`, keep it unique across
the tenant (for example, prefix it with the partition) instead of reusing one ID for
multiple users.

## Recall and read contract

`top_k` is one global ceiling across extracted records and selected source spans. The returned `answer` renders only the highest-priority admitted evidence item; SPM does not concatenate every match into it.

`evidence_refs` can retain up to `top_k` broader items for provenance or multiple premises. Each ref contains a short-lived `read_token`:

- source-span evidence resolves to the exact selected span;
- extracted-record evidence resolves to its verified backing source.

Pass tokens to `read` verbatim as a JSON array. Do not decode and re-serialize them.

When no evidence qualifies, recall returns an explicit empty/refused outcome with a machine-readable gate reason. It does not invent an answer.

## Silent continuity policy

SPM's MCP instructions ask capable agents to use memory without narrating the lookup:

1. If an earlier decision, constraint, progress update, or rationale is missing from active context, call `recall` before asking the user to repeat it.
2. Call `read` when the exact source text or additional premises are needed.
3. Continue the task using the result; do not announce that memory was searched or restored.
4. Do not repeat an empty recall in the same logical turn.

Current files, Git state, configuration, and runtime observations remain authoritative when they may have changed since a memory was written. Tool instructions guide the client agent; SPM cannot force every third-party MCP runtime to follow them.

## Codex

```toml
[mcp_servers.spm]
url = "https://api.spmos.ai/mcp"
headers = { Authorization = "Bearer spm_live_..." }
```

Prefer an environment-backed secret mechanism when your client supports one. A 401 `invalid_token` means the server was reached but the SPM key is missing, malformed, expired, revoked, or belongs to another environment.

## Claude Code and generic MCP JSON

```json
{
  "mcpServers": {
    "spm": {
      "url": "https://api.spmos.ai/mcp",
      "headers": {
        "Authorization": "Bearer spm_live_..."
      }
    }
  }
}
```

Restart the client after adding a server so it reloads the tool catalog.

## Recommended round trip

1. `remember` with a stable idempotency key and, when supplied, a source ID that has not already been deleted in the current memory generation.
2. Poll `status` until the source is ready.
3. `recall` using a natural-language question.
4. Use `read` when the agent needs exact provenance or additional premises.
5. `delete` test data when the workflow is complete.

The MCP service is memory-only. It does not proxy your model request and does not require an upstream provider key.

After targeted deletion, reusing the same `source_id` in the same memory generation fails closed with `409 SOURCE_ID_PURGED`. Advancing to a new memory generation permits that ID again. Use a new source ID for genuinely new content instead of trying to resurrect a deleted identity.

## Health

`/health`, `/livez`, and `/readyz` are unauthenticated probes. The MCP endpoint itself requires authentication.
