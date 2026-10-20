---
title: Your memory
description: How SPM writes, retrieves, admits, reads, and deletes memory with provenance, evidence gates, scopes, and verifiable lifecycle controls.
published: 2026-08-19
updated: 2026-10-20
applies_to: SPM-Polaris
---

# Your memory

This page answers three questions: what SPM saves for you, what happens to it over time, and how you find it again or remove it.

## What gets saved

Memory enters in two ways:

- **Explicitly** — your agent calls the MCP `remember` tool, or you add a source in the console.
- **Automatically** — when you use the Provider Proxy or Local Proxy, eligible user messages, visible assistant replies, and supported tool-result text can be saved for later sessions, subject to your capture policy.

Some things are **never** saved as memory, even though they pass through to your provider unchanged: model reasoning and thinking blocks, tool-call arguments, partial streamed JSON, and signatures. They belong to the provider's protocol, not to your memory.

Practical details:

- Saving the same content twice does not create duplicates.
- Re-saving a large changed document only processes the parts that changed.
- If saving is unavailable, your model request may continue with degraded memory capture. A failed capture is not guaranteed a durable background retry; explicitly save critical facts with `remember` and check readiness.
- Short assistant messages that only say "I don't have that in memory" are kept for audit but never mixed into your real memories.
- Deliberate saves (MCP `remember`, console, direct API) are **committed** memory; proxy-captured conversation is **observed** memory. Observed memory is retrievable, but it is never promoted to committed on its own — only consolidation or an explicit save does that. See the MCP recall `lane_policy` parameter for how the two compete at recall time.

## How your memory evolves

SPM can consolidate related saved facts into **observations**, where this capability is available:

- An observation can connect a changed fact with earlier supporting facts — for example, a switch from React to Vue. This does not guarantee that every change is detected or that conflicting facts are always resolved correctly; save changes with scope and time, and check the sources.
- Each observation carries a **proof count**: how many distinct saved facts support it.
- Observations may be available to recall when supported for your account. Deleting their backing sources also removes or retires derived memory.

## Asking questions (recall)

Ask in natural language. You get back the strongest saved evidence for your question — with references back to the original text — not an invented answer.

Shape the question to name one fact and the qualifiers it depends on —
"What deployment checks are required before changing the Polaris project?",
not "tell me about Polaris". See [Best practices](best-practices.html#3-ask-focused-recall-questions)
for the full pattern.

When no saved evidence qualifies, SPM returns an explicit no-evidence result instead of inventing an answer. Its machine-readable reason distinguishes insufficient evidence from an unavailable search; a refusal alone does not prove the fact was never saved.

Three depths are available; `auto` is the default and the right choice for almost everyone:

| Depth | Behavior | Cost |
|---|---|---|
| `fast` | One bounded lookup. Never spends provider tokens on selection. | No extra model cost |
| `auto` (default) | Fast lookup first; only when it is not confident enough does SPM run deeper multi-round gathering | Pays for deeper gathering only when needed |
| `deep` | Goes straight to multi-round gathering for the hardest, multi-part questions | Highest; reports provider-token usage and a configured cost estimate, not an exact bill |

Set your account's default depth in **Settings → Memory** — every recall that does not name a depth uses it. The same tab controls whether your proxy conversations are saved at all (your messages and assistant replies can each be turned off).

## Reading the exact original text

Recall results include short-lived read tokens and source IDs. Your agent can pass returned values as `read_tokens[]` or `source_ids[]` to `read` to fetch the saved span or backing source — useful when it needs original wording or more than one premise. Both paths enforce the current account, memory generation, partition, and access checks; a source ID does not bypass them.

## Deleting

| You want to remove | Do this | What happens |
|---|---|---|
| One memory | MCP `delete` or the console | That memory and everything derived from it is removed; repeating the same deletion returns the original result |
| All memory | Console **Clear memory** | Active memory is wiped and verified absent; you start with a clean slate |
| Your account | Console **Close account** | Tracked deletion workflow, including credential revocation |

A deleted source ID cannot be reused until you clear memory — this prevents deleted content from quietly reappearing under an old receipt. Every completed purge produces a signed receipt.

Deletion removes data from active memory. Backups created before a purge age out on their normal retention schedule.

## Who can see your memory

Only your account. Every memory object belongs to your tenant, and results are checked against your account and current memory generation before they are returned. A degraded memory lookup fails openly or returns less — it never returns someone else's memory.

## End-user partitions inside a tenant

Applications that serve several end users can use one SPM key with a stable
user_partition per user. The key must include memory:partition; the value is carried
through `remember`, `recall`, and `read`. MCP `status` and `delete` do not accept
`user_partition`; use returned source IDs to target those operations.
Partition selection is not end-user authentication: your application must authorize
which partition and source IDs each user may access, and protect its application key.

An omitted partition is the tenant's default space. Use opaque, stable IDs such as
application user UUIDs, not secrets or mutable display names.
