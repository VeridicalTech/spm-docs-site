---
title: FAQ
---

# FAQ

## Is SPM self-hosted?
The SPM memory plane is hosted. Local Proxy is an optional local provider-traffic component, not a self-hosted or offline edition of SPM.

## Must SPM store my provider key?
No. Hosted Provider Proxy vaults it in SPM. Local Proxy keeps it in a protected local config and sends it directly to the configured upstream.

## What data still reaches SPM when I use Local Proxy?
Recall queries, admitted memory responses, and eligible captured text use hosted SPM according to memory mode. The full provider request is sent directly to the provider, not through the hosted Provider Proxy.

## Who selects the model?
The request or downstream harness. Hosted SPM routes that model against the configuration's allowed models. Local Proxy does not select, alias, or rewrite it.

## Why can one provider configuration contain multiple models?
The credential, Base URL, API style, headers, and query parameters belong to the upstream configuration. Model is request routing, so a second row is needed only for a different upstream configuration.

## Which providers can fetch models?
Only Custom BYO channels use a guarded live `/models` probe. Preset providers use the reviewed models.dev-backed catalog.

## Why does `GET /v1/models` fail through Local Proxy?
Local Proxy relays the route to the upstream. It does not synthesize a list from models.dev, so the upstream must expose that route.

## Why does `spm doctor` pass while a live request fails?
`spm doctor` validates local schema, listener, and API-style ownership. It does not prove SPM key scopes, provider credentials, upstream model access, port availability, or a complete request.

## Why does a request show 0% reduction?
The history must exceed the active budget and contain a complete old exchange that is safe to remove. Short, single-turn, or protected tool/reasoning/thinking histories can correctly show 0%.

## Does SPM remove reasoning or tool state?
No. Provider reasoning, Anthropic thinking/redacted thinking, tool/function arguments, event order, and identifiers are protected from compression and relayed unchanged. They are excluded from memory capture.

## Why is recall `answer` not a polished entity answer?
It is the highest-priority admitted evidence item, not an LLM-generated synthesis. Use `evidence_refs` and `read` for exact provenance; let the downstream agent phrase the final answer.

## Where are Local Proxy receipts shown?
Local Proxy exposes per-request `x-spm-*` headers. It does not currently create hosted gateway receipts or populate hosted Dashboard savings/receipt views.

## Does SPM add a generative model call to recall?
No generative answer model is added to the recall path. Evidence admission and best-evidence rendering are deterministic.

## What happens when no memory qualifies?
Recall fails closed with an explicit empty/refused state and gate reason. It does not invent supporting memory.

## Can I delete my data?
Yes: delete one source, Clear memory for tenant history, or Close account. Active-store deletion is verified; pre-existing backups/WAL/replicas expire on their retention schedule.

## Can another tenant see my memory?
Tenant IDs, row-level security, namespace/generation fences, signed tokens, and final evidence-gate checks prevent cross-tenant recall.
