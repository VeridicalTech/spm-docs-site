---
title: Security
description: Security boundaries for SPM-Polaris V3.0.0, including tenant isolation, credential custody, memory admission, provider forwarding, deletion evidence, and shared responsibilities.
published: 2026-08-22
updated: 2026-08-22
applies_to: SPM-Polaris V3.0.0
---

# Security

SPM-Polaris applies security controls at the tenant, credential, provider-traffic, memory-admission, and deletion boundaries. This page describes the product boundary; it is not a certification or a substitute for reviewing your provider, deployment, and data-handling requirements.

## Trust boundaries

| Boundary | SPM responsibility | Customer responsibility |
|----------|--------------------|-------------------------|
| SPM API access | Authenticate SPM keys, scopes, tenant, namespace, and current memory generation | Protect keys, limit scopes, rotate or revoke compromised credentials |
| Hosted Provider Proxy | Protect hosted provider credentials and filter forwarding headers | Configure an approved provider and review that provider's retention and training settings |
| Local Proxy | Reject unsafe bind, origin, host, URL, and forwarding conditions implemented by the package | Protect the local machine and permissions-restricted configuration file |
| MCP | Authenticate memory tools and enforce tool scopes | Decide which content the agent submits to memory tools |
| Stored memory | Enforce tenant and namespace fences, provenance checks, source state, and deletion controls | Avoid submitting prohibited data and select appropriate retention/deletion workflows |

## Tenant and memory isolation

Requests are admitted for a resolved tenant, namespace, access scope, and current memory generation. Recall rechecks tenant, namespace, generation, ACL, source state, and signed provenance before evidence can enter an answer. A missing or inadmissible result returns an explicit empty or refused outcome rather than a cross-tenant fallback.

The authoritative store owns sources, extracted records, jobs, fences, and receipts. Retrieval indexes are derived and rebuildable; they are not treated as the source of truth.

## Credential custody

Hosted Provider Proxy stores and uses the configured upstream credential in the SPM-hosted request path. Local Proxy keeps the upstream credential in a permissions-restricted local configuration and sends it directly to the configured provider; eligible memory queries and content can still reach hosted SPM. MCP does not require SPM to hold the provider credential because the application owns inference.

See [Choose an integration](integrations.html) and [Bring your own provider](providers.html) before choosing a boundary.

## Provider traffic and capture

Hosted forwarding relays the provider's native JSON and streaming event sequence. The memory observer works from a separate capture copy and limits assistant capture to visible response text. Reasoning, thinking, redacted thinking, tool or function arguments, signatures, and partial JSON remain provider protocol state and are excluded from memory capture.

## Evidence-gated recall

Recall combines lexical and vector candidates, applies stored trust, favors source diversity, and enforces a final result bound. Evidence is admitted only after the final gate checks its tenant, namespace, generation, scope, source state, and provenance. When no evidence passes, SPM returns `UNKNOWN` or a machine-readable refusal state and injects no memory.

## Deletion and limitations

Targeted deletion and clear-memory operations advance or enforce memory fences, purge eligible authoritative and derived state, and return verifiable operation evidence. A purge tombstone prevents the same source identity from being re-enqueued in the same memory generation.

Deletion does not mean that pre-existing backups, write-ahead logs, replicas, provider records, or customer-side copies disappear before their documented retention or rotation periods. Review the [Privacy Policy](privacy.html), [Terms of Service](terms.html), and [Memory, evidence & deletion](memory.html) for the applicable boundary.

## Report a security issue

Do not include secrets, personal data, or exploit details in a public channel. Send a concise report to [contact@spmos.ai](mailto:contact@spmos.ai) with the affected surface, reproducible impact, and a safe way to coordinate further evidence.
