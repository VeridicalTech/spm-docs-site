---
title: MCP server
description: Connect an MCP client to SPM memory tools for governed remember, recall, read, delete, and status operations.
published: 2026-08-19
updated: 2026-10-20
applies_to: SPM-Polaris
---

# MCP server

MCP gives a compatible agent five explicit tools to save, find, read, and delete your SPM memory — without changing how the agent talks to its model.

```text
https://api.spmos.ai/mcp
Authorization: Bearer spm_live_...
```

The production server name is **SPM**. The five primary tools are `remember`, `recall`, `read`, `delete`, and `status`. Compatibility aliases `add_memory`, `search_memory`, and `delete_memory` have the same schemas and behavior as `remember`, `recall`, and `delete`, respectively.

## Tools

| Tool | What it does | Important parameters |
|------|--------------|----------------------|
| `remember` | Saves one memory, idempotently | `text`, `idempotency_key`, optional `source_id`, `topic`, `source_timestamp`, and `user_partition` |
| `status` | Reports whether saved memories are ready to recall | optional `source_ids[]`, `wait_seconds` (up to 30) |
| `recall` | Answers a question with the strongest saved evidence | `question` (one intent, fully qualified — see [Best practices](best-practices.html#3-ask-focused-recall-questions)), optional `top_k` (default 20; raise it for broader evidence coverage), optional `depth`, `lane_policy`, and `user_partition` |
| `read` | Fetches a selected span or backing source | `read_tokens[]`, `source_ids[]`, or both; optional `user_partition` |
| `delete` | Removes one memory and everything derived from it | `source_id`, `idempotency_key` |

Scopes: `remember` requires `memory:write`; `recall`, `read`, and `status` require `memory:read`; `delete` requires `memory:delete`. Selecting a non-empty `user_partition` additionally requires `memory:partition`.

## What a recall result looks like

- `answer` is the single strongest piece of saved evidence — not a rewritten summary.
- `evidence_refs` keep the broader supporting set, each with a short-lived read token.
- Pass returned tokens or source IDs to `read` verbatim as JSON arrays. Use source IDs from evidence references or returned history stubs; do not invent them. Source-ID reads do not require a token, but still enforce current account, memory generation, partition, and access checks.
- When nothing qualifies, you get an explicit no-evidence result with a machine-readable reason — never an invented answer.
- `evidence_decision` is a machine-readable verdict on how strongly the returned evidence is backed (see below).

## Choosing a recall depth

Omit `depth` to use your account default (`auto` until you change it in **Settings → Memory**). The three depths:

- `fast` — one bounded lookup, zero provider-token spend. Best for simple, well-named questions.
- `auto` — fast first; deeper multi-round gathering only when needed and available. A no-evidence result is not a reason to repeat paid deep calls indefinitely.
- `deep` — multi-round gathering from the start, for hard multi-part questions ("how do A and B each relate to C"). The response reports rounds used, provider tokens, latency, why it stopped, and a configured cost estimate. That estimate is not an exact provider bill.

If no deep selector is configured, `deep` fails closed with `DEEP_RECALL_UNAVAILABLE` and `auto` simply stays on the fast path.

## Choosing a recall lane

Memory enters through two kinds of channels: deliberate saves (`remember`,
console, direct API writes) and passive captures from proxy traffic. The
`lane_policy` parameter describes the requested preference between them. Strict lane isolation is separately evaluation-gated:

- `explicit_first` (default) — when lane isolation is enabled, deliberate saves
  hold recall seats first; otherwise the request follows the active retrieval policy.
- `blended` — one shared pool, ranked purely by relevance.
- `observed_only` — answer only from passive captures; use it for "what did I
  say in chat" questions about proxy-captured content.

The Provider Proxy's own continuity lookups use `blended`. Strict lane ordering
is not a universal production guarantee; check the active deployment treatment
before relying on it.

## Evidence decisions

Every recall response carries an `evidence_decision` object that says how
strongly the returned evidence backs the answer:

- `status` — `supported` (the evidence passed the support gate),
  `insufficient` (candidates were found but none proved the claim),
  `contradicted` (the verifier refuted the claim), or `unknown` (nothing to
  judge, for example no candidates).
- `evidence_ids` / `source_ids` — what the decision is based on.
- `support_failure_kinds` — when status is `insufficient`, machine-readable
  reasons why the candidates failed support.
- `authority` and `reason` — provenance of the judgment.
- `sufficiency_judged` / `sufficiency_source` — who judged. `deep_selector` means
  a model was asked and judged the evidence sufficient; `gate_only` means
  deterministic checks accepted it and no model was asked. `gate_only` is a
  fact about the path, not a warning.
- `why_no_answer` — `{code, message, action_hint}` whenever the verdict is not
  `supported`, so a client never has to parse prose to decide what to do next.

Three consistency rules hold on every response, and are worth coding against:

1. `status: supported` always comes with `evidence_count > 0`.
2. An empty result never claims success: with no evidence, `gate_reason` is not
   `passed` and `diagnostics.stop_reason` is not `sufficient`.
3. A non-supported verdict never reports `gate_reason: passed`; the field
   carries the decision's own reason instead (for example
   `no_verified_evidence`).

Evidence captured from a conversation is only usable when its speaker can be
attributed. Captures that cannot be attributed still appear in `source_ids`, but
they cannot stand alone as support: the verdict becomes `insufficient` with
`support_failure_kinds` containing `capture_origin_unverified`, and the answer
text is withheld. Save the fact explicitly with `remember` to make it a
first-class memory.

`supported` is a support-gate verdict, not proof that the saved claim is true in
the world or that every premise in a compound task is covered. Check all needed
premises and verify facts that may have changed. `insufficient` means support was
not established — rephrase, raise `top_k`, or switch to `deep` when appropriate.

### Verify the contract with your own key

The rules above are executable. This probe writes one canary memory in an
isolated partition, exercises the whole tool surface, checks the verdict rules,
and deletes the canary:

```bash
export SPM_API_KEY=spm_live_...
python3 tools/mcp/conformance.py           # human scorecard
python3 tools/mcp/conformance.py --json    # CI output; exits 1 on a break
```

Contract checks must pass; capability observations (how a paraphrased question
fares, for example) are reported separately and never fail the run.

## How agents are asked to use memory

SPM's MCP instructions ask capable agents to use memory quietly:

1. If an earlier decision, constraint, or progress update is missing from active context, call `recall` before asking you to repeat it.
2. Call `read` when the exact original text is needed.
3. Continue the task with the result, without narrating that memory was searched.
4. Not repeat an empty recall within the same logical turn.

Current files, Git state, and runtime observations remain authoritative when they may have changed since a memory was written. SPM cannot force every third-party MCP runtime to follow these instructions.

## Client configuration

Codex (see the [official Streamable HTTP configuration](https://developers.openai.com/codex/mcp#streamable-http-servers)):

Set the key in the environment that launches Codex, separately from the config:

```bash
export SPM_API_KEY="<your SPM API key>"
```

```toml
[mcp_servers.spm]
url = "https://api.spmos.ai/mcp"
bearer_token_env_var = "SPM_API_KEY"
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
2. Pass returned source IDs to `status`; poll or use `wait_seconds` until searchable. Stop and inspect `failed`, `dead_letter`, or `not_found` states rather than polling indefinitely.
3. `recall` with one focused question — the single fact you need, with every
   qualifier the answer depends on:

       "What deployment checks are required before changing the Polaris project?"

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

MCP `status` and `delete` do not accept `user_partition`. Target them with returned
source IDs (`source_ids[]` for status, `source_id` for delete). Your application
must authenticate end users, authorize partition selection and source-ID use,
and keep its SPM key private; partition routing alone is not end-user authorization.
