---
title: Changelog
description: Dated public changes to SPM interfaces, behavior, documentation, and supported integration boundaries.
published: 2026-08-19
updated: 2026-10-24
applies_to: SPM public releases
---

# Changelog

This page records dated public changes. Historical entries describe the behavior announced at the time, not a current performance guarantee.

## 2026-10-24 — Recall verdicts are internally consistent, and executable

- An empty recall can no longer report `gate_reason: passed` or
  `diagnostics.stop_reason: sufficient`, and a non-supported verdict never
  reports a passed gate. The three rules are documented in
  [Evidence decisions](mcp.html#evidence-decisions).
- `evidence_decision.sufficiency_source` names who judged: `deep_selector` (a
  model judged the evidence sufficient) or `gate_only` (deterministic checks
  accepted it). `sufficiency_judged: false` therefore no longer means
  "unverified" on fast recall.
- Conversation captures whose speaker cannot be attributed no longer stand
  alone as support: the verdict is `insufficient` with
  `capture_origin_unverified`, and the answer is withheld while the sources stay
  visible.
- Fast recall now reports the same cost fields as deep recall (`rounds_used`,
  provider token and latency counters).
- New conformance probe (`tools/mcp/conformance.py`) verifies the whole contract
  against your own key and exits non-zero on a regression.

## 2026-10-24 — Plan limits: what is metered and what is a hard cap

- **Only recalls are metered.** Rate, memory-write and stored-memory limits reject the operation instead of turning into a charge; the metered line is the recall allowance described below.
- **Manual paid grants need an expiry.** An Enterprise account can be provisioned manually. A manual Starter or Growth grant must carry an expiry date; without one the account is treated as Free, because an unbounded manual grant cannot be distinguished from a legacy pilot row.

## 2026-10-23 — Plan pricing and metered recall overage

- **Plan prices changed**: Starter is now \$29/month (\$290/year) and Growth \$99/month (\$990/year). Annual billing is two months free. Existing subscriptions keep the price they were sold at until their plan is changed.
- **Recalls past the allowance are metered.** Starter includes 5,000 recalls per month and Growth 50,000; beyond that, recalls bill at **\$2 per 1,000**, on the same invoice as the plan. Free plan recall is capped and never metered.
- **A failed renewal no longer drops the plan instantly.** The paid plan stays active for three days past the period end while the card is retried.

## 2026-10-20 — Documentation reconciliation

- Clarified the relationship between **SPMOS** (the master brand), **SPM** (the short form), and **SPM-Polaris** (the current production product), together with existing integration and credential boundaries.
- Reconciled documentation with verified existing interfaces, including MCP evidence reads by source ID, compatibility tools, and bounded tool-output stubs on the Responses path. These are documentation clarifications, not claims that those interfaces first shipped today.
- Clarified that eligible tool results can be captured, while tool-call arguments, reasoning, and signatures are excluded. A failed save is not guaranteed to retry, and readiness guards are not a losslessness guarantee.

## 2026-09-11

- **Lane policy is documented.** `explicit_first`, `blended`, and
  `observed_only` describe the requested recall treatment. Strict lane
  isolation remains an evaluation-gated deployment treatment; this entry does
  not claim that it is active in every production cell.
- **Recall responses now include an `evidence_decision`**: a machine-readable
  verdict (`supported`, `insufficient`, `contradicted`, or `unknown`) with the
  evidence and source IDs it is based on, an authority label, and — when
  evidence is declined — why it failed support (for example a CJK coverage
  floor). Treat `supported` as evidence support under that evaluation,
  not settled truth; treat `insufficient` as "keep looking", not as an answer.
- **Memories become recallable sooner and stop getting stuck.** New database
  indexes cut the wait between saving a memory and it being ready to recall,
  and empty extraction payloads are now skipped instead of parking in a
  permanent retry state.
- **Console dashboard improvements**: usage views paginate server-side and
  refresh automatically instead of loading one giant slow query.

## 2026-09-07

- **Faster, steadier answers through the Provider Proxy**: memory lookups on
  the proxy path now use the bounded fast lookup by default, memory captures
  run in parallel with a hard deadline instead of one-by-one, and unchanged
  history is no longer re-saved on every turn. Every proxied request logs its
  per-stage memory timings, so slow memory behavior is visible instead of
  silent.
- **Chained Responses requests are no longer a memory blind spot**: calls that
  continue a provider-side thread (`previous_response_id`) now save their new
  input and can receive recalled context, while compression stays off for
  provider-managed threads.
- **Token estimates are fairer for CJK text**: Chinese, Japanese, and Korean
  content is now estimated per character instead of by byte count, so budgets
  and billing estimates stop undercounting CJK conversations.
- **Anthropic tool pairing is protected when memory is injected**: recalled
  context never lands between a tool call and its result.
- **New `lane_policy` parameter** on the MCP `recall` tool and recall APIs:
  `explicit_first` (default) ranks deliberate saves ahead of passive proxy
  captures, `blended` keeps one shared pool, and `observed_only` answers
  "what did I say in chat" questions from proxy captures. The parameter is
  accepted today; the server-side lane ordering itself activates after a
  paired evaluation gate.

## 2026-09-05

- **End-user partitions**: one API key can now serve many end users with
  isolated per-user memory spaces. Give the key the `memory:partition` scope and
  send a stable opaque `user_partition` on remember, recall, and read calls.
  Partitions are fenced across writes, recall, evidence reads, and read tokens.
- **Stored Memories** now shows a short topic label derived from each source's
  own content (plus its type: Input, Tool output, or Assistant) instead of a bare
  source ID, so you can tell memories apart at a glance.

## 2026-09-03

- Deep recall now always weighs your saved facts alongside raw conversation
  windows. Previously, a large collection of windows could occupy the whole
  review budget, so answers to multi-part questions could miss facts that were
  actually saved. Saved facts are now guaranteed a share of every deep review.
- Memory evolution is more reliable: long-running background updates no longer
  stop mid-write, and a batch that cannot be processed is now skipped with an
  audited record instead of stalling the queue.
- Fixed a server error that could intermittently reject memory saves and
  deletions.

## 2026-09-01

- `auto` recall now returns a deeper result only after Deep recall completes
  with sufficient evidence. Partial or interrupted gathering stays a clear
  no-evidence result instead of becoming an answer.
- Deep recall keeps gathering when the selected evidence is still missing a
  requested premise, even if the words in the question already appear in the
  current evidence. This improves multi-part questions without weakening
  refusals for absent or look-alike facts.

## 2026-08-29

- Deep recall now uses a search index prepared as memories are saved. Large
  memory collections no longer need to rebuild that index during each recall,
  so repeated questions are more predictable.
- Readiness checks are stricter: Deep recall only uses a memory collection when
  its saved sources are fully searchable. If processing is still underway, SPM
  returns a temporary, retryable unavailable result instead of silently using
  partial evidence.
- Interrupted memory deletion is safer to retry. Repeating the same deletion
  continues its cleanup and returns the original receipt ID after completion,
  rather than treating unfinished work as complete.

## 2026-08-26

- Provider settings rebuild: the model catalog now auto-admits providers that
  models.dev lists with a working HTTPS endpoint and a documented credential
  variable — no waiting for a review cycle — while model pricing, context
  windows, and capability markers refresh automatically with the catalog.
  Custom providers can now accept a manually typed model ID when the upstream
  has no model-list endpoint.

- Published `@spmos/local-proxy@0.1.2`: old tool outputs are now replaced by
  short retrievable stubs once safely stored in memory — on all three
  supported protocols, including Anthropic Messages. Tool pairing is never
  broken and prompt-cache breakpoints are never touched.
- The hosted Provider Proxy now applies the same tool-output stubbing to
  Anthropic Messages traffic, matching the OpenAI-compatible paths.
- The console is reorganized around what you want to do (Overview, Memory,
  Usage, Developer, Account), and Settings now lets you tune memory behavior
  yourself: default recall depth, capture switches, ambient retention period,
  compression defaults, and token budgets.
- Recall is better at real questions in Chinese and English, and no longer
  surfaces a saved copy of your own question as if it were the answer.

## 2026-08-25

- The console is reorganized around tasks: **Memory** (Stored Memories, Recall
  Playground, Activity), **Usage**, **Developer** (API Keys), and **Account**.
- Recall gains a **History tab**: past recalls filter into answered and
  declined, replacing the separate Refusals page (old links redirect).
- **Settings is now tabbed**: General (username and display name), Providers,
  Memory, Proxy, Security (password), and a red-boxed Danger zone (clear
  memory, close account).
- New account preferences in Settings: default recall depth (auto/fast/deep),
  automatic capture toggles for your messages and assistant replies, proxy
  compression default, and input/recalled token budgets. Per-request API
  headers still override them for a single request.
- Fixed the Recall Playground error display: a client-side schema that
  lagged behind the server could dump a raw validation error for newer
  refusal reasons. Refusals now always render as a clean card with a
  plain-language reason, and unexpected responses show one short line.

- Tool-output elision savings now appear in request receipts: agentic
  requests show the `elided_tool_output` continuity state with the
  original and forwarded token counts, so removed old tool outputs are
  visible as real savings instead of a passthrough zero.
- Deep recall now keeps supporting premises in the evidence list even when the
  answer text is intentionally concise. Agents can use the attached read tokens
  to retrieve the exact original wording for each premise. Refusals for
  look-alike evidence are unchanged.
- Deep recall diagnostics now explain how much work was used, whether evidence
  coverage completed, and the provider token and latency cost. Slow selection
  times out sooner so recalls fail clearly instead of hanging.

## 2026-08-24

- Published `@spmos/local-proxy@0.1.1` to npm: one-command install now ships
  the continuity contract (`x-spm-continuity-state`, two most recent
  exchanges protected, removal only on proven recall) and the stricter
  capture hygiene (reasoning and tool-argument blocks never become memory).
- `auto` is now the default recall depth: SPM answers with the bounded fast
  lookup first and only escalates to deeper multi-round gathering when that
  lookup is not confident enough. A question that clearly names something not
  in memory (for example a marker you never saved) is refused without paying
  for deep gathering.
- Deep recall is cheaper and faster: it stops as soon as the gathered
  evidence covers every part of the question, sizes the evidence sent for
  selection to the question's complexity, and only sends newly gathered
  evidence in later rounds instead of resending the full catalog.
- Memory now consolidates related facts into evolving observations. When
  something changes — a preference, a configuration, a decision — SPM records
  the current state with its provenance and keeps the earlier state as
  history instead of silently overwriting it. Each observation accumulates a
  proof count as more saved facts support it.
- Re-saving a large changed document is faster: only the parts that actually
  changed are processed again.
- Fixed recall of pasted code and exact identifiers: asking about an exact
  function, path, or token name now reliably returns what you pasted, in both
  `auto` and `deep` modes.
- Request receipts now show the requested and effective compression mode and
  the continuity state, so a request that compressed nothing is labeled
  truthfully instead of showing a misleading zero.

## 2026-08-23

- Added explicit fast and deep recall modes: `depth=deep` performs multi-round evidence gathering for harder questions and reports rounds, provider usage, and latency; `fast` remains the bounded default.
- Tightened abstention: recall now requires evidence with semantic support for the question beyond shared vocabulary, so unanswerable questions return an explicit no-evidence outcome instead of a look-alike answer.
- The console Dashboard now shows estimated input-token savings (clearly labeled reference estimate, not billing) and a one-click shareable savings receipt.
- Fixed Google and GitHub sign-in completion, account-closure requests, and the post-closure redirect so closed accounts land on sign-in with a clear notice.

## 2026-08-21

- Added Local Proxy for users who want upstream provider credentials to remain on their own machine.
- Improved continuity in long conversations and made recalled evidence more focused.
- Improved provider compatibility, provider and model setup, and usage reporting.
- Updated the public product identity to **SPM — StellarPath Memory Operating System**.

## 2026-08-20

- Added profile management, username sign-in, and Google and GitHub sign-in.
- Added multi-model provider management and model discovery for Custom BYO providers.

## 2026-08-19

- Opened registration for users with a confirmed email address.
- Added plan usage controls and memory and account deletion workflows.

## 2026-08-14

- Improved memory deletion reliability and retrieval quality.
