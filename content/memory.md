---
title: Your memory
description: How SPM writes, retrieves, admits, reads, and deletes memory with provenance, evidence gates, scopes, and verifiable lifecycle controls.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
---

# Your memory

This page answers three questions: what SPM saves for you, what happens to it over time, and how you find it again or remove it.

## What gets saved

Memory enters in three ways:

- **Explicitly** — your agent calls the MCP `remember` tool, or you add a source in the console.
- **Automatically** — when you use the Provider Proxy or Local Proxy, your messages and the assistant's visible replies can be saved for later sessions.

Some things are **never** saved as memory, even though they pass through to your provider unchanged: model reasoning and thinking blocks, tool-call arguments, partial streamed JSON, and signatures. They belong to the provider's protocol, not to your memory.

Practical details:

- Saving the same content twice does not create duplicates.
- Re-saving a large changed document only processes the parts that changed.
- If saving is briefly unavailable, your model request still completes normally; the save is retried in the background.
- Short assistant messages that only say "I don't have that in memory" are kept for audit but never mixed into your real memories.

## How your memory evolves

Your memory is not a pile of frozen notes. As related facts accumulate, SPM consolidates them into **observations**:

- When something changes — you switched from React to Vue, a deploy window moved, a decision was revised — the observation shows the current state and keeps the earlier state as its history (for example, "uses Vue (previously: used React)"). Nothing is silently overwritten.
- Each observation carries a **proof count**: how many distinct saved facts support it.
- Observations are found by recall like any other memory, and deleting the sources behind an observation retires it too.

## Asking questions (recall)

Ask in natural language. You get back the strongest saved evidence for your question — with references back to the original text — not an invented answer.

When nothing in memory actually answers the question, SPM says so explicitly instead of returning a look-alike answer. The refusal carries a machine-readable reason, so your agent can tell "not saved" apart from "search unavailable".

Three depths are available; `auto` is the default and the right choice for almost everyone:

| Depth | Behavior | Cost |
|---|---|---|
| `fast` | One bounded lookup. Never spends provider tokens on selection. | No extra model cost |
| `auto` (default) | Fast lookup first; only when it is not confident enough does SPM run deeper multi-round gathering | Pays for deeper gathering only when needed |
| `deep` | Goes straight to multi-round gathering for the hardest, multi-part questions | Highest; the response reports exactly what it spent |

Set your account's default depth in **Settings → Memory** — every recall that does not name a depth uses it. The same tab controls whether your proxy conversations are saved at all (your messages and assistant replies can each be turned off).

## Reading the exact original text

Recall results include short-lived read tokens. Your agent passes them to the `read` tool to fetch the exact saved span behind a result — useful when it needs the original wording or more than one premise.

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
through writes, recall, evidence reads, and deletion checks. Partitions stay isolated
even though they share a tenant and billing account.

An omitted partition is the tenant's default space. Use opaque, stable IDs such as
application user UUIDs, not secrets or mutable display names.
