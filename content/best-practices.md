---
title: Best practices
description: Practical guidance for reliable, useful, and safe SPM memory, including how to phrase recall questions.
published: 2026-09-04
updated: 2026-10-20
applies_to: SPM-Polaris
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

A recall question should be **minimal and sufficient**: name the one fact you
need, and include every qualifier the answer depends on. Both halves matter —
too broad, and you get an evidence dump instead of an answer; too narrow, and
the gate cannot find what you already saved.

| Question | Verdict |
|----------|---------|
| What deployment checks are required before changing the Polaris project? | Good — one intent, names the subject and the decision point |
| Tell me about the Polaris project. | Too broad — invites a dump instead of the one fact you need |
| `deployment checks` | Too narrow — keywords alone cannot say which project or which decision |
| What deployment checks are required before changing Polaris, and who approved the budget? | Two intents — split into two recalls |

Rules that follow from the table:

- **One intent per recall.** Split compound questions and run them separately.
- **Name the subject and the decision point.** Qualifiers such as "before
  changing X", "for project Y", or "as of last week" let the evidence gate
  pick the smallest sufficient set.
- **Do not pad.** "Please tell me..." and "I was wondering..." add tokens,
  not information.
- **Ask in the language you saved in** when you can. Cross-language recall
  works, but exact saved terms still match most reliably.
- **If a recall refuses, split before you broaden.** A refused compound
  question usually means one premise was unsupported — splitting tells you
  which one.

SPM may refuse with a verdict of `unknown` (nothing to judge) or `insufficient`
(candidates were found but none proved the claim). Treat that as a useful answer:
the system did not find enough trustworthy support. Do not silently replace a
refusal with a guess.

## 4. Choose the right interface

### MCP

Use MCP when your agent can call tools explicitly:

1. remember durable facts;
2. recall when a question depends on earlier context;
3. read only when an evidence summary needs exact source text;
4. delete when a source must be removed;
5. status when you need readiness without loading content.

The normal path is recall, then read. Read accepts returned `read_tokens[]` or
`source_ids[]` from evidence references or history stubs. Copy those values; do not
invent identifiers. Direct source-ID reads still enforce current access checks.

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

- Ask for the specific decision or preference needed now (see section 3 for
  how to shape that question).
- Prefer a small `top_k` for simple questions; raise it only when the question
  genuinely needs multiple facts.
- For multi-part work, run one recall per premise instead of one broad recall
  for everything.
- After recall, verify every premise your task depends on is covered by
  returned evidence — an uncovered premise is a silent gap, not a refusal.

More memory is not automatically better. A large mixed context can bury the relevant
fact and increase model input cost.

## 6. Use read for provenance

Recall returns concise evidence references. Use read for exact wording, ambiguity
resolution, or an audit trail.

Best practices:

- Copy evidence_refs[].read_token exactly; do not parse or re-serialize it.
- Alternatively, copy a returned source ID into `source_ids[]`; this is not an access-control bypass.
- Send tokens as an array, even for one token.
- Read several needed tokens in one call instead of making one call per token.
- Call read soon after recall; read tokens are short-lived.
- Treat expired or invalid tokens as not_found, not as valid evidence.
- Distinguish a call-level `error` from `not_found`: an unavailable service does not prove a token expired or a source is absent.

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
- Check readiness for critical saves; a failed automatic capture is not guaranteed a durable background retry.
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
| `unknown` / `insufficient` refusal | No evidence qualified, or none proved support | Rephrase, save the fact explicitly, or proceed without memory |
| not_found from read | Token expired, changed, or is outside the scope | Run a fresh recall |
| memory data plane unavailable | Temporary service or network problem | Retry with backoff; avoid tight loops |
| DATA_PLANE_BACKPRESSURE | Write queue is busy | Wait for the indicated retry window |
| Stale session or access denied | The session or key is no longer authorized | Refresh the session and verify credential scope |

Do not treat a transient error as proof that memory is absent. Conversely, a successful
HTTP response does not prove that the requested fact was found: inspect the status,
evidence count, and evidence references.

Likewise, `supported` means the support gate passed, not that the saved statement
is independently true or that every premise of your task has been checked.

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

## 14. Use one key for several end users safely

If your application serves many people, you can keep one SPM key for the application
while assigning every person a stable `user_partition`. A partition is an opaque,
application-defined identifier such as your user UUID. It is not a display name and
should not contain secrets.

Enable the `memory:partition` scope in addition to the scopes the integration already
needs:

| Scope | Use |
|---|---|
| `memory:read` | Recall and read evidence for the current user partition |
| `memory:write` | Remember facts for the current user partition |
| `memory:partition` | Allow the key to select an end-user partition |

Then pass the same partition on every `remember`, `recall`, and `read` call for
that user. With MCP, a remember payload is:

```json
{
  "text": "I prefer concise status updates.",
  "idempotency_key": "user-123-status-style-2026-09",
  "user_partition": "user-123"
}
```

Use `user_partition: "user-123"` on the corresponding `recall` and `read` calls.
SPM binds the value to the request and evidence token, so a recall in `user-456`
cannot return `user-123` memory. A key that lacks `memory:partition` is rejected when
it attempts to select a non-empty partition.

MCP `status` and `delete` have no `user_partition` parameter. Use the returned
source IDs to target them: `source_ids[]` for status and `source_id` for delete.
Your application must authenticate users and authorize their partition and source-ID
access. Possession of a partition-capable application key is not end-user authorization.

Keep the value stable across sessions and environments, and test the three important
cases: a user can see their own memory, a different user cannot see it, and an
unpartitioned request cannot accidentally become a shared catch-all. If you provide
explicit `source_id` values, make them unique across the tenant (for example,
`user-123:preferences`) rather than reusing the same ID for different users.

Requests that omit `user_partition` use the tenant's default space. Treat that as a
separate, intentional shared area; do not mix it with per-user data by accident.
