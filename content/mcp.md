---
title: MCP server
description: Connect an MCP client to SPM memory tools for governed remember, recall, read, delete, and status operations.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
---

# MCP server

MCP gives a compatible agent five explicit tools to save, find, read, and delete your SPM memory — without changing how the agent talks to its model.

```text
https://api.spmos.ai/mcp
Authorization: Bearer spm_live_...
```

The production server name is **SPM**. Tool names are exactly `remember`, `recall`, `read`, `delete`, and `status`.

## Tools

| Tool | What it does | Important parameters |
|------|--------------|----------------------|
| `remember` | Saves one memory, idempotently | `text`, `idempotency_key`, optional `source_id`, `topic`, and `user_partition` |
| `status` | Reports whether saved memories are ready to recall | optional `source_ids[]` |
| `recall` | Answers a question with the strongest saved evidence | `question`, optional `top_k` (default 20; raise it for broader evidence coverage), optional `depth`, and `user_partition` |
| `read` | Fetches the exact original text behind a recall result | `read_tokens[]` and optional `user_partition` |
| `delete` | Removes one memory and everything derived from it | `source_id`, `idempotency_key` |

Scopes: `remember` requires `memory:write`; `recall`, `read`, and `status` require `memory:read`; `delete` requires `memory:delete`. Selecting a non-empty `user_partition` additionally requires `memory:partition`.

## What a recall result looks like

- `answer` is the single strongest piece of saved evidence — not a rewritten summary.
- `evidence_refs` keep the broader supporting set, each with a short-lived read token.
- Pass tokens to `read` verbatim (as a JSON array) to get the exact original text.
- When nothing qualifies, you get an explicit no-evidence result with a machine-readable reason — never an invented answer.

## Choosing a recall depth

Omit `depth` to use your account default (`auto` until you change it in **Settings → Memory**). The three depths:

- `fast` — one bounded lookup, zero provider-token spend. Best for simple, well-named questions.
- `auto` — fast first; deeper multi-round gathering only when the fast answer is not confident enough. A question about something you never saved is declined without paying for deep gathering.
- `deep` — multi-round gathering from the start, for hard multi-part questions ("how do A and B each relate to C"). The response reports rounds used, provider tokens, latency, and why it stopped.

If no deep selector is configured, `deep` fails closed with `DEEP_RECALL_UNAVAILABLE` and `auto` simply stays on the fast path.

## How agents are asked to use memory

SPM's MCP instructions ask capable agents to use memory quietly:

1. If an earlier decision, constraint, or progress update is missing from active context, call `recall` before asking you to repeat it.
2. Call `read` when the exact original text is needed.
3. Continue the task with the result, without narrating that memory was searched.
4. Not repeat an empty recall within the same logical turn.

Current files, Git state, and runtime observations remain authoritative when they may have changed since a memory was written. SPM cannot force every third-party MCP runtime to follow these instructions.

## Client configuration

Codex:

```toml
[mcp_servers.spm]
url = "https://api.spmos.ai/mcp"
headers = { Authorization = "Bearer spm_live_..." }
```

Claude Code and generic MCP JSON:

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

Restart the client after adding a server so it reloads the tool catalog. A 401 `invalid_token` means the server was reached but the SPM key is missing, malformed, expired, revoked, or belongs to another environment.

## Recommended round trip

1. `remember` with a stable idempotency key.
2. Poll `status` until the memory is ready.
3. `recall` with a natural-language question.
4. `read` when exact original text or multiple premises are needed.
5. `delete` test data when the workflow is complete.

After deleting a memory, reusing the same `source_id` returns `409 SOURCE_ID_PURGED` until you clear memory and start fresh. Use a new source ID for genuinely new content.

The MCP service is memory-only. It does not proxy model requests and does not need a provider key.

## Health

`/health`, `/livez`, and `/readyz` are unauthenticated probes. The MCP endpoint itself requires authentication.

## One key, many end users

For a multi-user application, keep one application key and pass a stable opaque
partition identifier, normally your internal user UUID, on every remember, recall,
and read call for that user:

    {
      "question": "Which writing style do I prefer?",
      "user_partition": "user-123"
    }

Selecting a non-empty partition additionally requires the `memory:partition` scope.
Partitions are isolated within the tenant, and a read token minted for one partition
cannot be used in another. Omitting the field selects the tenant's default space.
