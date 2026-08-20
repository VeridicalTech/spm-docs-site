---
title: Memory, evidence & deletion
---

# Memory, evidence & deletion

## How memory is written

Memory enters through two paths:

- **Explicit writes** — the MCP `remember` tool or the console, stored idempotently under your account scope with an idempotency key.
- **Automatic ingest** — after each proxied provider exchange, SPM-Polaris projects the conversation, strips control scaffolding, filters probe/scaffold echo, and queues an extraction job.

Extraction jobs are idempotent (a replayed exchange is a no-op), retried with backoff, and dead-lettered after exhausting attempts. Slow or failed ingestion never breaks a live request — the outbox drains when workers return.

At write time each memory receives an origin role on the **provenance ladder**: `user`, `assistant`, `mixed` (a fragment spanning a role boundary, downgraded rather than guessed), or `derived` (SPM-Polaris-synthesized state). Conflicts resolve by authority rank: a user's statement outranks an assistant's proposal, and an assistant cannot promote its own claims to user authority.

## How recall answers

Recall runs lexical and vector searches, fuses their results, selects source spans, and admits candidates through an **evidence gate**. Before anything reaches the prompt, the gate verifies tenancy, namespace, epochs, ACL scope, and signed provenance — and it fails closed. When nothing qualifies, the model receives no memory, and the honest answer is:

```
UNKNOWN — no supporting memory found.
```

This prevents unsupported memory from encouraging a confident invention.

Every gate outcome is inspectable. The console **Recall** view shows each attempt's `gate_reason` and `evidence_count`, so a refusal is debuggable rather than silent. Evidence admitted by the gate carries short-lived read tokens; the MCP `read` tool resolves them back to the original source spans.

## Deletion

Deletion works at three granularities, all idempotent:

| Granularity | How |
|-------------|-----|
| One source | MCP `delete` tool (source id + idempotency key), or targeted purge in the console |
| All memory | **Clear memory** in the console |
| The whole account | **Close account** in the console |

Clearing memory and closing an account run as a tracked pipeline — you can watch each step's state in the console:

1. **Sync fence** — freeze new writes so the purge target is stable
2. **Purge memory** — remove sources and derived candidates from the authoritative store and retrieval index
3. **Verify absence** — re-scan against the advanced fence; the job cannot complete while anything remains
4. **Revoke credentials** — API keys and provider channel secrets are destroyed
5. **Drain reservations** — settle or reverse outstanding usage reservations
6. **Financial review** — ledger reconciliation checkpoint
7. **Finalize** — close the job and, for account closure, ban the auth identity

Steps retry with backoff on transient failure and surface their state (`pending` / `retrying` / `completed` / `waiting_review`) rather than hanging silently.

## The signed purge receipt

Every completed purge produces an HMAC-SHA256 signed receipt persisted with the purge record:

```json
{
  "status": "purged",
  "purge_id": "…",
  "receipt": {
    "payload": {"typ": "purge-receipt+v1", "kid": "…", "deleted_candidates": 12, "…": "…"},
    "signature": "EVhlqoLD3Gky7u…"
  }
}
```

The signature is computed over the canonical JSON payload (sorted keys, UTF-16-ordered, no whitespace) and stored with the purge record. The payload carries its key id (`kid`), so receipts remain verifiable after key rotation. Repeated purges are safe: purging the same source again returns the original signed record.

**Verify a receipt** (operator side):

1. Take `receipt.payload` and canonicalize it (sorted keys, UTF-16-ordered, no whitespace).
2. Compute `HMAC-SHA256(signing_key, canonical_bytes)`, base64url-encode without padding.
3. Constant-time compare with `receipt.signature`.

**Documented caveats:** records created before signed receipts existed carry no signature. Purge removes data from the online stores; backups, WAL, and replicas taken before a purge age out on their own rotation schedule. Cryptographically enforced erasure (per-tenant keys with key destruction) is on the maturity roadmap.

## Tenant isolation

Every memory object — records, candidates, jobs, vectors, and receipts — carries `tenant_id`. The data path enforces isolation through row-level security in the authoritative store, namespace fences, signed capability tokens with replay protection, and an evidence gate that rechecks all content at render time.
