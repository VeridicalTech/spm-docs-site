---
title: Plans & quotas
---

# Plans & quotas

SPM plans cover the memory plane. Your models stay on your own provider accounts and are billed by your provider directly; SPM does not resell generative inference.

## Plans

| | Free | Starter | Growth | Enterprise |
|---|---|---|---|---|
| Monthly price | $0 | $9 | $15 | Custom |
| Yearly price | — | $99 (two months free) | $150 (two months free) | Custom |
| API rate limit | 10 requests/min | 30 requests/min | 100 requests/min | Reviewed before activation |
| Memory writes / month | 500 | 3,000 | 8,000 | Reviewed before activation |
| Stored memories | 1,000 | 10,000 | 50,000 | Reviewed before activation |
| Provider channels | 1 | 3 | 10 | Reviewed before activation |
| Support | Community | Email | Priority | Dedicated |

Monthly and yearly SKUs of the same plan unlock identical quotas; the yearly SKU simply costs two months less.

## How limits are enforced

- **Rate limit** — a distributed, fail-closed limiter guards the request plane. Exceeding the budget returns `429`; if the limiter itself is unavailable, SPM returns `503 RATE_LIMITER_UNAVAILABLE` instead of silently dropping your limits.
- **Monthly memory writes** — each stored memory source counts against the current billing-period allowance. Writes beyond the allowance are rejected with `429` until the period resets or the plan is upgraded.
- **Stored memories** — the write guard rejects new sources once the plan's stored-memory ceiling is reached. Purging sources frees capacity immediately.
- **Provider channels** — creating a channel beyond the plan allowance is rejected in the console. Revoking (deleting) a channel frees the slot; revoked channels and keys disappear from console lists entirely.

Current usage is visible on the console **Dashboard** as progress bars, so you can see consumption before hitting a wall.

## Upgrading and billing

1. Open **Billing** in the console.
2. Choose a plan and cadence (monthly or yearly).
3. When self-service checkout is available for the account, complete payment through Stripe. The plan activates after Stripe confirmation and control-plane sync.

If the console disables self-service checkout or plan changes, no billing mutation is attempted. Contact [contact@spmos.ai](mailto:contact@spmos.ai). Enterprise terms are reviewed individually.

There is no automatic overage: hitting a quota rejects the operation, it never silently converts into a charge.

## What a "memory write" means

A write is one stored memory source — through the MCP `remember` tool, the console, or the automatic ingest pipeline that extracts memory from proxied conversations. Recall, reads, receipts, and status checks are not writes and are covered by the request rate limit instead.
