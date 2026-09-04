---
title: Best practices
description: Practical guidance for reliable, useful, and safe SPM memory.
published: 2026-09-04
updated: 2026-09-04
applies_to: SPM-Polaris V3.0.0
---

# Best practices

SPM works best when memory is treated as evidence, not as a transcript dump. The
patterns below apply whether you use the Provider Proxy, MCP, or Local Proxy.

## 1. Start with a clear memory contract

Decide what should be remembered, what should not, and who owns the memory.

Good candidates include durable preferences, project decisions, account constraints,
recurring workflows, and facts that will matter later. Avoid passwords, access tokens,
one-time debugging output, and content belonging to another user.

Keep each person, workspace, or customer in a separate account and namespace. Never
use a shared namespace as a substitute for access control.

## 2. Save durable facts explicitly

Use remember when a future session should reliably find a fact. Good entries are:

- Specific: “I prefer vegetarian lunches on weekdays.”
- Actionable: “The billing service must remain compatible with PostgreSQL 16.”
- Scoped: “For the Polaris project, deploy after the migration smoke test.”
- Time-aware: “Use the old API until the migration is complete.”

Avoid vague entries such as “we discussed the project” or “remember this.” Include the
subject and decision so the evidence can stand on its own.

Example payload:

    {
      "text": "For the Polaris project, run focused tests before a full suite.",
      "topic": "polaris-workflow",
      "idempotency_key": "polaris-change-policy-2026-09"
    }

Use a stable idempotency key when retrying the same write. A retry should not create
duplicates.

## 3. Ask focused recall questions

Ask for the fact you need:

    What deployment checks are required before changing the Polaris project?

Prefer one question per intent. Combining unrelated topics makes it harder to select
the smallest sufficient evidence and increases context cost.

SPM may return UNKNOWN when no stored evidence qualifies. Treat that as a useful
answer: the system did not find enough trustworthy support. Do not silently replace
UNKNOWN with a guess.

## 4. Choose the right interface

### MCP

Use MCP when your agent can call tools explicitly:

1. remember durable facts;
2. recall when a question depends on earlier context;
3. read only when an evidence summary needs exact source text;
4. delete when a source must be removed;
5. status when you need readiness without loading content.

The normal path is recall, then read. Do not call read first without a read token
returned by recall.

### Provider Proxy

Use the Provider Proxy when an existing OpenAI- or Anthropic-compatible application
already has a model endpoint and you want memory without changing its tool loop.
Keep the application provider credential and SPM credential separate, and inspect the
request receipt when comparing cost or latency.

### Local Proxy

Use Local Proxy when the provider credential must stay on your machine. Local Proxy
is a credential-custody option, not an offline memory database. Memory lookup and
eligible saved text still use hosted SPM.

## 5. Keep context small but sufficient

Memory is most useful when it supplies the minimum sufficient context:

- Ask for the specific decision or preference needed now.
- Prefer a small top_k for simple questions.
- Increase top_k only when the question genuinely needs multiple facts.
- For multi-part questions, ask each premise explicitly or verify that all premises
  are covered by the returned evidence.

More memory is not automatically better. A large mixed context can bury the relevant
fact and increase model input cost.

## 6. Use read for provenance

Recall returns concise evidence references. Use read for exact wording, ambiguity
resolution, or an audit trail.

Best practices:

- Copy evidence_refs[].read_token exactly; do not parse or re-serialize it.
- Send tokens as an array, even for one token.
- Read several needed tokens in one call instead of making one call per token.
- Call read soon after recall; read tokens are short-lived.
- Treat expired or invalid tokens as not_found, not as valid evidence.

If read is slow, check whether the client is making repeated single-token calls.
Batch tokens from one recall whenever possible.

## 7. Separate users, workspaces, and environments

Use distinct namespaces for personal preferences, team decisions, production and test
environments, and different customers. Never rely on a prompt instruction for
isolation; use account, namespace, and credential boundaries.

## 8. Be deliberate about proxy auto-capture

Proxy capture is convenient, but not every conversation line deserves durable memory.
Treat tool output, generated code, logs, and repeated summaries as provisional unless
they contain a clearly supported user decision or fact.

Good practices:

- Keep sensitive or transient work in an explicitly excluded path.
- Save the final user-owned decision explicitly with remember.
- Delete a source when it was captured by mistake.
- Avoid repeatedly pasting the same long transcript; repetition makes topics harder
  to distinguish.

## 9. Record changes with scope and time

When a preference or decision changes, record the new state and why it differs:

    I now prefer TypeScript for frontend work; the earlier JavaScript preference applied only to the legacy dashboard.

This preserves history instead of leaving two contradictory facts with no context.

## 10. Handle errors as signals

| Response | Meaning | Recommended action |
|---|---|---|
| UNKNOWN / no supporting memory | No evidence passed support checks | Rephrase, save the fact explicitly, or proceed without memory |
| not_found from read | Token expired, changed, or is outside the scope | Run a fresh recall |
| memory data plane unavailable | Temporary service or network problem | Retry with backoff; avoid tight loops |
| DATA_PLANE_BACKPRESSURE | Write queue is busy | Wait for the indicated retry window |
| STALE_MEMORY_FENCE or access denied | Scope is stale or unauthorized | Refresh the session and verify credential scope |

Do not treat a transient error as proof that memory is absent. Conversely, a successful
HTTP response does not prove that the requested fact was found: inspect gate_reason,
evidence_count, and evidence references.

## 11. Measure quality and cost honestly

Keep a small private test set containing answerable questions, similar but unsupported
questions, wrong-attribute questions, changed or deleted facts, and multi-premise
questions.

Track useful evidence, safe UNKNOWN responses, unsupported evidence, cross-user
leakage, latency, provider token cost, and the complete recall-then-read flow.

Do not judge memory quality from answer accuracy alone. A system that answers more
questions by inventing support is worse than one that honestly says UNKNOWN.

## 12. Protect credentials and source content

- Store SPM keys in a secret manager or protected environment variable.
- Never commit keys, read tokens, or full source text to Git, tickets, or logs.
- Use separate keys for development, evaluation, and production.
- Grant only the scopes a client needs: memory:read, memory:write, or deletion.
- Rotate a key immediately if it appears in a terminal, screenshot, or log.
- Treat returned source text as sensitive even when the evidence summary looked safe.

## 13. A reliable daily workflow

1. Start with the correct account and namespace.
2. Ask a focused recall question when earlier decisions matter.
3. Use only returned evidence; accept UNKNOWN when it is not supported.
4. Call read for exact wording or provenance, batching needed tokens.
5. Save a new durable decision explicitly with remember.
6. Delete accidental or obsolete sources.
7. Review receipts and errors when latency or cost changes.

The goal is not to maximize the amount of memory shown to the model. The goal is to
assemble the smallest trustworthy context that lets the agent act correctly.
