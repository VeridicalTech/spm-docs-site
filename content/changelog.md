---
title: Changelog
description: Dated public changes to SPM interfaces, behavior, documentation, and supported integration boundaries.
published: 2026-08-19
updated: 2026-08-25
applies_to: SPM public releases
---

# Changelog

Selected user-facing product updates.

## 2026-08-25

- Request receipts now show tool-output elision savings: agentic requests report the `elided_tool_output` continuity state with original and forwarded token counts, so removed old tool outputs appear as real savings instead of a passthrough zero.
- Deep recall now keeps every part of a multi-hop answer: when evidence spans several facts (for example, "who owns it and when is it planned"), the evidence list includes all of them instead of only the part that shares the question's wording. Refusals for look-alike evidence are unchanged.
- Recall diagnostics are richer: deep answers report the selector budget tier, routing, coverage completion, and provider token and latency cost, and slow provider selection now times out sooner so recalls fail fast instead of hanging.

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
