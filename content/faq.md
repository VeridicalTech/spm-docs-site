---
title: FAQ
---

# FAQ

**Is SPM-Polaris open source or self-hosted?**
No. SPM-Polaris is a hosted service accessed through the provider proxy or MCP. It requires no customer-side deployment.

**Do I have to move my models?**
No. Models remain in your provider accounts — OpenAI, Anthropic, DeepSeek, OpenRouter, Groq, Mistral, xAI, Together AI, Fireworks AI, Moonshot AI, Alibaba DashScope, Azure OpenAI, or any custom endpoint speaking a supported dialect. SPM-Polaris forwards requests in each provider's native format.

**Can I use a provider that is not in the preset list?**
Yes. A custom channel accepts any OpenAI-compatible or Anthropic Messages endpoint: you control the base URL, API style, model name, and key. The Test connection button validates the credential against the live model list before saving.

**How current is the model list?**
The catalog aggregates the MIT-licensed models.dev dataset, refreshes automatically (12-hour TTL with stale-while-revalidate), and falls back to a bundled snapshot. The channel form labels the catalog as live, live-stale, or bundled with its fetch time.

**Does SPM-Polaris add LLM calls to my requests?**
No. Recall, ranking, admission, and compression are deterministic code. Provider charges cover inference only; memory growth does not add inference tokens.

**What happens when there is no relevant memory?**
The evidence gate fails closed and returns an explicit UNKNOWN with a machine-readable gate reason, visible in the console Recall view together with the evidence count.

**What are the plan limits?**
Free: 10 req/min, 500 writes/month, 1,000 stored memories, 1 provider channel. Starter ($9/mo or $99/yr): 30 req/min, 3,000 writes, 10,000 memories, 3 channels. Growth ($15/mo or $150/yr): 100 req/min, 8,000 writes, 50,000 memories, 10 channels. Full detail: [Plans & quotas](plans.html).

**What happens when I hit a limit?**
The operation is rejected with `429` — never silently converted into a charge. There is no automatic overage. Upgrade in the console under Billing, or purge sources to free stored-memory capacity.

**Can I delete my data?**
Yes — per source (MCP `delete` or targeted purge), all memory (Clear memory), or the entire account (Close account). Multi-step deletions run as a tracked pipeline with a verify-absence gate, and every completed purge produces an HMAC-SHA256 signed receipt that survives key rotation. Two caveats remain: records created before signed receipts are unsigned, and pre-purge backups age out on their own schedule. Cryptographic erasure through per-tenant key destruction is on the roadmap.

**Can another tenant ever see my memory?**
No. Every object carries a tenant id. Row-level security, namespace fences, signed tokens with replay protection, and a final evidence-gate recheck at render time enforce isolation.

**What providers does the proxy speak?**
OpenAI Chat Completions, OpenAI Responses, and Anthropic Messages, each without cross-dialect rewriting.

**What if the console is down?**
Traffic continues because the request plane does not depend on the console plane. Configured API keys keep authenticating.

**Where are the numbers from?**
The [Benchmarks](benchmarks.html) page provides the scorecard, evidence annotations, and methodology.
