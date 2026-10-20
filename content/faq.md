---
title: FAQ
description: Answers about SPM hosting, Local Proxy, MCP, provider billing, memory refusal, evidence, compression, privacy, deletion, and availability.
published: 2026-08-19
updated: 2026-10-20
applies_to: SPM-Polaris
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
What you explicitly save (MCP `remember`, console) and — when automatic capture is enabled — eligible messages, visible assistant replies, and tool results from proxy traffic. Eligible tool results may be trimmed. Reasoning, thinking blocks, tool-call arguments, and partial streamed JSON are excluded from automatic memory capture. Automatic capture is best-effort; a successful model request does not prove that its content was stored or guarantee durable retries after capture failure.

**What happens when I change my mind about something?**  
SPM can consolidate related facts and retain historical context, but it cannot guarantee perfect conflict resolution. State the correction explicitly, including what changed and when, then inspect the recalled evidence. Delete obsolete material if it should no longer be available.

**What happens when the answer isn't in memory?**  
Recall can return no usable evidence with a machine-readable reason. That does not prove the fact never existed in memory: retrieval can miss relevant material. Your agent should inspect the evidence, then ask you or look elsewhere rather than invent an answer.

**Which recall depth should I use?**  
Keep the default `auto`. It answers most questions with a free bounded lookup and only pays for deeper gathering when the question genuinely needs it. Use `deep` for hard multi-part questions, `fast` when you want guaranteed zero extra model cost.

**How should I phrase a recall question?**  
Ask for one fact, with the qualifiers it depends on: "What deployment checks are required before changing the Polaris project?" — not "tell me about Polaris" and not a bare keyword list. See [Best practices](best-practices.html#3-ask-focused-recall-questions).

**Can another account see my memory?**  
No. Every memory belongs to your tenant, and results are checked against your account before being returned.

## Cost and savings

**When will I see token savings?**  
When eligible older history can be shortened under the active compression policy. Short conversations may correctly show no reduction. A stored or ready source is not proof that every fact will be recalled later; memory is not a lossless archive of the original conversation or tool JSON.

**Are the token numbers my provider's bill?**
No. SPM input-token and reduction figures are estimates, not provider billing-grade measurements. Only provider-reported output counters establish reported output usage; missing usage is not zero. Your provider invoice is separate, and caching or pricing rules can change the actual cost.

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
A compression check may have prevented removal, or the request may have had nothing eligible to shorten. Inspect its memory, compression, and continuity state. Source readiness is checked separately from recall: a failed lookup does not guarantee unchanged history, and readiness does not prove complete recall coverage. Eligible tool-output shortening may also occur independently.
