---
title: FAQ
description: Answers about SPM hosting, Local Proxy, MCP, provider billing, memory refusal, evidence, compression, privacy, deletion, and availability.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
schema: FAQPage
---

# FAQ

Everyday questions about using SPM.

## Getting started

**Do I have to move my model provider account?**  
No. You keep your own provider account and billing. SPM adds the memory layer around it.

**Which integration should I pick?**  
Hosted Provider Proxy if you want the simplest setup with dashboard receipts. Local Proxy if your provider key must stay on your machine. MCP if your agent should save and find memories explicitly without changing its model connection.

**Is SPM self-hosted?**  
No. The memory service is hosted. Local Proxy is a local traffic component for credential custody, not a self-hosted edition.

## Your memory

**What does SPM save?**  
What you explicitly save (MCP `remember`, console) and — through the proxy — your messages and the assistant's visible replies. Reasoning, thinking blocks, tool-call arguments, and partial streamed JSON are never saved as memory.

**What happens when I change my mind about something?**  
Your memory evolves: related facts consolidate into observations that show the current state and keep the earlier state as history. You will not end up with two contradictory memories fighting each other.

**What happens when the answer isn't in memory?**  
Recall says so explicitly, with a machine-readable reason — instead of returning a look-alike answer. Your agent can then ask you or look elsewhere.

**Which recall depth should I use?**  
Keep the default `auto`. It answers most questions with a free bounded lookup and only pays for deeper gathering when the question genuinely needs it. Use `deep` for hard multi-part questions, `fast` when you want guaranteed zero extra model cost.

**Can another account see my memory?**  
No. Every memory belongs to your tenant, and results are checked against your account before being returned.

## Cost and savings

**When will I see token savings?**  
When conversations get long: once older exchanges are safely stored as memory, they stop being resent to the model. Short conversations correctly show no reduction.

**What does SPM charge for?**  
Your SPM plan covers memory features (see [Plans & quotas](plans.html)). Model usage is billed by your provider directly — SPM does not resell inference.

## Credentials and providers

**Must SPM store my provider key?**  
No. Use Local Proxy: the key stays in a protected local configuration and goes directly from your machine to the provider.

**What still reaches SPM when I use Local Proxy?**  
Memory lookups, recall results, and eligible saved text. The full provider request goes directly to the provider.

**Who selects the model?**  
Your client. SPM routes the requested model against your configured provider; Local Proxy does not select or rewrite it.

## Deletion

**Can I delete my data?**  
Yes — one memory, all memory (**Clear memory**), or your whole account (**Close account**). Deletion from active memory is verified, and you get a signed receipt.

**Why can't I reuse a deleted source ID?**  
Until you clear memory, a deleted ID stays blocked so deleted content cannot reappear under an old receipt. Use a new ID for new content.

## Troubleshooting

**Why does `spm doctor` pass while a live request fails?**  
`doctor` validates local configuration. It does not prove key scopes, provider credentials, or a complete live request.

**Where are Local Proxy receipts?**  
Local Proxy exposes per-request `x-spm-*` headers. It does not create hosted receipts or appear in dashboard savings views.

**Why did my request go through unchanged?**  
A safety check did not pass — for example the memory lookup was unavailable or could not prove coverage for the older history. SPM always prefers sending the complete request over risking your provider's state.
