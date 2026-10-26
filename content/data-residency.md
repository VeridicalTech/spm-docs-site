---
title: Data residency and subprocessors
description: Where SPM stores memory, which parties can see customer content, how deletion works, and what an enterprise review can verify today.
published: 2026-10-26
updated: 2026-10-26
applies_to: SPM-Polaris
---

# Data residency and subprocessors

This page describes the hosted SPM deployment as it runs today: where customer memory is stored, which parties can see it, how deletion works, and which claims an enterprise reviewer can check without taking our word for it. It is a description of the current deployment, not a certification.

## Where memory lives

| Component | Location | Holds |
|-----------|----------|-------|
| Authoritative store (PostgreSQL) | OVHcloud US-East, Virginia | sources, extracted records, candidates, audit events, generation fences |
| Vector index (Weaviate) | OVHcloud US-East, Virginia (two hosts) | embeddings of memory spans; reads query both, and the index is derived and rebuildable |
| Embedding model | OVHcloud US-East, Virginia | a self-hosted Voyage model; reached over a private tunnel between the two hosts |
| Control plane (Supabase) | managed | accounts, authentication and plan pointers - no memory content |

Compute and storage are single-region US-East. Memory is not replicated outside these hosts.

## Who can see customer content

| Party | What it sees | When |
|-------|--------------|------|
| SPM | everything it stores | always |
| Self-hosted embedding model | the text being embedded, and query strings | ingestion and every recall |
| Deep-recall selector provider (DeepSeek) | the candidate passages shortlisted for a deep recall | deep recall only |
| Typesafe (fast-recall admission) | up to 24 candidate passages, 600 characters each | only if fast vector admission is enabled; it is disabled in the current deployment |
| Supabase | account, authentication and plan metadata | account operations |
| Stripe | billing records | billing operations |
| Cloudflare | request metadata at the edge | every API call |

Two details that matter in a review:

* Embeddings never leave the deployment. The embedding endpoint resolves to the self-hosted model over a private tunnel; there is no third-party embedding API in the path.
* The fast recall path is deterministic and calls no external model. Deep recall is the only path that sends candidate text to a model provider, and only the passages that survived gating.

## Retention and deletion

* Deletion is source-scoped: the source is removed from the authoritative store and from the vector indexes, and a tombstone prevents the same key from being recreated by a later ingest.
* Purges are audited; the audit event outlives the deleted content.
* Failed extraction jobs are retained for a bounded window (24 hours by default) and then expire.
* Audit events are append-only: no endpoint rewrites or deletes them.

## Getting your data out

`GET /v2/audit` supports a time window (`since_unix`, `until_unix`) and a keyset cursor (`before_event_id`), so an export reads one index range per page instead of re-scanning history. The reference exporter writes newline-delimited JSON plus a manifest with the row count, first and last event id, the requested window, the stop reason and a SHA-256 of the body - evidence a reviewer can check rather than trust.

## Boundaries of what we can promise today

* **Regional pinning**: there is one deployment, in US-East. EU or APAC residency requires a separate stack rather than a configuration flag.
* **SSO and SCIM**: not yet available; console access is email/password plus API keys.
* **Certifications**: no SOC 2 report yet. The audit export and the security page are the evidence available now.

See [Security](security.html) for the isolation, credential and provider-traffic boundaries, and [Privacy](privacy.html) for the policy view.
