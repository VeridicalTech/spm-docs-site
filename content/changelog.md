---
title: Changelog
---

# Changelog

## 2026-08-21

### Added

- Published `@spmos/local-proxy` for loopback provider credential custody, with Codex/Claude configuration output, local token isolation, DNS-pinned HTTPS forwarding, and hosted SPM recall/ingest.
- Prepared `@spmos/local-proxy@0.1.1` source with source-bound continuity, two-exchange protection, visible-text capture allowlists, role provenance, Unicode-safe source chunking, and `0.1.0` identity compatibility. npm publication remains pending.
- Added a complete public distinction between hosted Provider Proxy, MCP, and Local Proxy.

### Changed

- Public product naming is **SPM — StellarPath Memory Operating System**. Seed/codename and console version labels are no longer part of the user-facing identity.
- Hosted Provider Proxy memory defaults now derive from the SPM key's scopes. Deterministic compression uses an 8,192-token fallback budget even when charging is disabled.
- One provider configuration can own multiple allowed models. Preset providers use the reviewed models.dev catalog; only Custom BYO can fetch the upstream model list.
- Hosted embedding moved to a privately operated Voyage 4 Nano-compatible runtime; hosted Voyage API and reranker dependencies are no longer in the active production path.

### Fixed

- Provider JSON/SSE transparency now preserves reasoning/thinking/tool state and provider event identifiers without cross-dialect rebuilding.
- Memory capture now uses protocol-specific visible-text allowlists and excludes reasoning, thinking, redacted thinking, tool/function arguments, and partial JSON.
- Recall applies trust precedence, source diversity, normalized-text deduplication, and one global `top_k`.
- Recall `answer` now renders one best evidence item instead of concatenating unrelated sources.
- Source-span read tokens return the exact selected span; extracted records return their verified backing source.
- Dashboard Token savings and Recent request receipts now read the terminal hosted-gateway receipt authority.
- Hosted deterministic compression now protects the two most recent eligible exchanges and requires source-bound continuity evidence before removing older history; empty, degraded, or unrelated recall safely falls back to passthrough. Equivalent Local Proxy behavior is prepared for `0.1.1` but not in npm `0.1.0`.
- Hosted captures now use content-stable source identities for exact repeats, preserve public-ingest role provenance, and suppress standalone assistant context-loss refusals from recall candidates. Equivalent Local Proxy behavior is prepared for `0.1.1` but not in npm `0.1.0`.
- MCP instructions now direct agents to recall missing conversation history silently while keeping current files, Git, configuration, and runtime state authoritative.
- Targeted purge tombstones now reject same-generation source-ID reuse with `409 SOURCE_ID_PURGED`; a later memory generation may reuse the ID.

## 2026-08-20

- Added unique username login, profile username/display-name/password updates, Google and GitHub sign-in surfaces, and English-only account UI.
- Added multi-model provider ownership and server-only Custom BYO model probing.
- Replaced provider protocol normalization with guarded native forwarding.

## 2026-08-19

- Enforced Free, Starter, and Growth quotas for request rate, monthly memory writes, stored memories, and provider configurations.
- Opened confirmed-email registration and removed the pilot approval gate.
- Added complete tenant-history Clear memory and account-closure workflows.

## 2026-08-14

- Added signed purge receipts, write-side provenance transport, vector-index rebuild tooling, and self-echo filtering.
