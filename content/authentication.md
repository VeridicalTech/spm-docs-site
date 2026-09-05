---
title: Authentication & API keys
description: Create and protect SPM API keys, choose least-privilege memory scopes, and configure authentication for hosted proxy and MCP clients.
published: 2026-08-19
updated: 2026-09-05
applies_to: SPM-Polaris V3.0.0
---

# Authentication & API keys

## The one credential your agents need

Agents authenticate to hosted SPM interfaces with a single API key. They never receive your console session or provider keys stored by SPM:

In plain terms: give an agent its own key so it can use only the memory features you allow.

```
Authorization: Bearer spm_live_...
```

Anthropic-dialect clients may send the same key in `x-api-key`; both headers are accepted.

## What a key resolves to

Before processing memory, SPM identifies the request and keeps its memory separate from other accounts:

- **tenant** — every memory object carries a tenant id; recall cannot cross tenants
- **namespace** — the memory partition inside the tenant
- **policy and scopes** — what the key may do
- **provider channel** — which configured provider credential can be used

SPM does not log keys, and request receipts contain no key material.

## Scopes

Keys carry least-privilege scopes:

| Scope | Allows |
|-------|--------|
| `memory:write` | Store memory (MCP `remember`, automatic ingest) |
| `memory:read` | Recall, read back evidence, and query memory status |
| `memory:delete` | Delete memory sources and purge |
| `memory:partition` | Select an end-user partition within the tenant |
| `receipt:read` | Query request receipts |

A proxy-only integration uses memory scopes for each request; grant `receipt:read` only to tools that audit traffic.

The key's read/write scopes also select the Provider Proxy's default memory mode. A request may lower that mode with `x-spm-memory-mode`, but it cannot upgrade beyond the key.

Console sign-in uses separate credentials from agent keys. A leaked agent key cannot open the console, and a console session cannot retrieve provider secrets.

## Hygiene

- Create one key per agent or environment; revoking a key deletes it — revoked keys no longer appear in console lists and immediately stop authenticating.
- Rotate keys on suspicion; frequent rotation has no usage penalty.
- Never commit keys. SPM rejects malformed keys promptly, but a committed `spm_live` key remains live until revoked.

## Local Proxy credential domains

Local Proxy stores the SPM key and provider key in its protected local configuration and gives the downstream harness a separate random local token. The provider key goes directly to the configured upstream; the SPM key goes only to hosted memory endpoints.

In plain terms: the harness receives only a local token, while the two provider-facing keys stay in Local Proxy's local configuration.

Treat all three values as secrets. `spm config` masks them; `spm config token` intentionally prints the local harness token.

## Console sign-in

The console accepts email or unique username login. Google and GitHub sign-in are optional alternatives. OAuth providers receive only their configured authentication redirect; SPM does not request Gmail, Drive, Contacts, or Calendar access.

## End-user partitions

One application key can serve multiple end users without putting everyone in one
memory space. Give the key the `memory:partition` scope and send a stable opaque
`user_partition` value with each memory operation. Use an internal user UUID when
possible, not a display name or secret.

Requests that select a non-empty partition require `memory:partition` in addition to
the normal `memory:read` or `memory:write` scope. Requests without a partition use the
tenant's default space.
