---
title: Changelog
description: Dated public changes to SPM interfaces, behavior, documentation, and supported integration boundaries.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM public releases
---

# Changelog

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

## 2026-09-05

- Added end-user memory partitions: one application key can now serve multiple users
  while keeping each user's saved memory separate. The dashboard API-key flow exposes
  the memory:partition scope, and MCP requests can carry a stable user_partition.
