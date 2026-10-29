---
title: Proxy behavior & safety
description: When SPM recall, compression, reversible fold, and protected-state bypass apply.
published: 2026-10-30
updated: 2026-10-30
applies_to: Hosted Provider Proxy and Local Proxy
schema: TechArticle
---

# Proxy behavior & safety

SPM makes independent decisions for recall, capture, and history shortening.
Seeing recall activity does not imply that compression is allowed.

| Request shape | Recall | History shortening | Continuity state |
| --- | --- | --- | --- |
| Ordinary long chat/history with searchable older exchanges | Yes | May commit removal or fold | `committed` or fold receipt |
| Short/new history | Yes | Nothing to remove | `not_needed` |
| Memory unavailable or source coverage unproven | May be empty/degraded | No | `bypassed_*` |
| Responses with `previous_response_id` | Tail only | No | `bypassed_protected_context` |
| Reasoning/tool state that cannot be safely rewritten | Yes, when allowed | No | `bypassed_protected_context` |
| `shadow` mode | Yes, when allowed | Measured only | `shadow_only` |

## Testing the two paths

For eligible compression, use a normal multi-turn chat request whose older
exchanges have already become searchable memory. Verify lower forwarded tokens,
a committed continuity state, and (when a fold is selected) a fold economics
receipt.

For provider-managed Responses state, send a request with `previous_response_id`.
SPM preserves provider history and may add only recalled memory at the tail. A
large request with a small positive memory addition is intentional, not evidence
that SPM was skipped.

Token counters are SPM estimates used for routing, compression, and receipts;
provider usage may differ. `recalled_tokens > 0` means memory was injected; it
does not mean older history was removed.

Provider reasoning, thinking, tool-call arguments, tool-result pairing, and
provider-managed history are never rewritten for savings. If coverage,
readiness, or evidence is insufficient, SPM forwards the complete request.
