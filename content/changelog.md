---
title: Changelog
---

# Changelog

## 2026-08-19 — SPM-Polaris V3.0.0

### Added
- **Plans & quotas enforced end to end** — Free, Starter ($9/mo `·` $99/yr), and Growth ($15/mo `·` $150/yr) now enforce rate limits, monthly memory-write allowances, stored-memory ceilings, and provider-channel counts. Usage progress bars live on the console Dashboard.
- **Live billing** — Stripe Checkout is live for all four paid SKUs; plan changes execute as instant switches against the existing subscription.
- **Live provider model catalog** — channel forms are fed by the models.dev aggregate (12-hour TTL, stale-while-revalidate, bundled fallback) with freshness labeling, searchable model comboboxes, and context/price/reasoning/tool badges.
- **Connection probe** — Test connection validates a credential against the provider's live model list with production SSRF guardrails before saving.
- **Custom provider channels** — any OpenAI-compatible or Anthropic Messages endpoint with full control of base URL, API style, model, and key.
- **Recall transparency** — the console Recall view surfaces gate reason and evidence count per attempt; receipts carry original vs forwarded vs recalled token accounting.

### Changed
- Product identity is now explicit: **SPM** is the StellarPath Memory Operating System brand, **SPM-Polaris** is the hosted provider-proxy product, and **V3.0.0** is the current public release.
- Revoking an API key or provider channel now deletes it — revoked items no longer linger in console lists.
- Account closure runs as a fully tracked pipeline: sync fence, purge, verify-absence, credential revocation, reservation drain, financial review, finalize.

### Fixed
- Purge verification now runs against the advanced memory fence, closing a gap where post-fence writes could survive a purge.
- Deletion-pipeline financial review no longer deadlocks on accounts holding legacy ledger rows.

## 2026-08-14

### Added
- **Signed purge receipts** — Every purge returns an HMAC-SHA256 receipt (`purge-receipt+v1`) persisted with the purge record. The record stores the key id, so receipts survive key rotation.
- **Write-side provenance transport** — Role spans flow from gateway projection through extraction, with user/assistant/mixed stamping and reserved-key overwrite protection.
- **Vector-index rebuild tool** — bulk reindex rebuilds the derived index from the authoritative store at copy speed through the production write path.

### Fixed
- **Agentic self-pollution echo** — Probe and scaffold text no longer round-trip into memory on the gateway path.
- **Cross-role fragment attribution** — Memory fragments spanning a role boundary resolve to mixed instead of the start offset's role.
- **Idempotent vector upsert** — Re-extraction heals through verified overwrite instead of failing terminally.

### Changed
- Product naming was temporarily shortened to **SPM (StellarPath Memory)**. This naming decision was superseded by the explicit **SPM-Polaris V3.0.0** product identity on 2026-08-19.
- Documentation site launched; the console and landing page moved to the English-only cold monochrome design system.

## 2026-07-29 — 0.1.0

Initial pilot build: subscription plans, distributed rate limiting (fail-closed), evidence replay protection, OTel tracing, structured logging, OpenAPI exports, a public documentation skeleton, an incident-response runbook, and a Python SDK skeleton.
