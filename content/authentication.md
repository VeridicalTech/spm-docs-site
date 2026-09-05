---
title: Authentication & API keys
description: Create and protect SPM API keys, choose least-privilege memory scopes, and configure authentication for hosted proxy and MCP clients.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
---

# Authentication & API keys

## The one credential your agents need

Agents authenticate to hosted SPM interfaces with a single API key. They never receive your console session or vaulted provider keys:

```
Authorization: Bearer spm_live_...
```

Anthropic-dialect clients may send the same key in `x-api-key`; both headers are accepted.

## What a key resolves to

Before processing memory, the gateway resolves each request key into a fenced identity:

- **tenant** — every memory object carries a tenant id; recall cannot cross tenants
- **namespace** — the memory partition inside the tenant
- **policy and scopes** — what the key may do
- **provider channel** — which vaulted credential to forward with

Keys are stored as peppered hashes. The gateway does not log them, and request receipts contain no key material.

## Scopes

Keys carry least-privilege scopes:

| Scope | Allows |
|-------|--------|
| `memory:write` | Store memory (MCP `remember`, automatic ingest) |
| `memory:read` | Recall, read back evidence, and query memory status |
| `memory:delete` | Delete memory sources and purge |
| `memory:partition` | Select an end-user partition within the tenant |
| `receipt:read` | Query request receipts |

A proxy-only integration still exercises memory scopes internally per request; grant `receipt:read` only to tooling that audits traffic.

### End-user partitions

One application key may serve multiple end users without putting everyone in the
same memory space. Give the key `memory:partition` and send a stable opaque
`user_partition` value with each memory operation. The partition is bound to ingest,
recall, evidence reads, and deletion checks. A non-empty partition without that scope
fails closed; requests without a partition remain in the tenant's default space.

Use an internal user UUID rather than an email address when possible, and never put
secrets or personal data in the identifier. Keep the same value for that user across
sessions so their memory remains addressable.

The key's read/write scopes also select the Provider Proxy's default memory mode. A request may lower that mode with `x-spm-memory-mode`, but it cannot upgrade beyond the key.

After console sign-in, the web backend issues short-lived capability tokens for console operations. This credential domain is separate from agent keys, so a leaked agent key cannot open the console, and a console session cannot retrieve provider secrets.

## Hygiene

- Create one key per agent or environment; revoking a key deletes it — revoked keys no longer appear in console lists and immediately stop authenticating.
- Rotate keys on suspicion; frequent rotation has no usage penalty.
- Never commit keys. SPM rejects malformed keys promptly, but a committed `spm_live` key remains live until revoked.

## Local Proxy credential domains

Local Proxy stores the SPM key and provider key in its protected local configuration and gives the downstream harness a separate random local token. The provider key goes directly to the configured upstream; the SPM key goes only to hosted memory endpoints.

Treat all three values as secrets. `spm config` masks them; `spm config token` intentionally prints the local harness token.

## Console sign-in

The console accepts email or unique username login. Google and GitHub sign-in are optional alternatives. OAuth providers receive only their configured authentication redirect; SPM does not request Gmail, Drive, Contacts, or Calendar access.
