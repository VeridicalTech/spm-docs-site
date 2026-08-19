---
title: Quickstart
---

# Quickstart

Create a memory-backed request in about five minutes.

## 1. Create your account and API key

Sign in to the console at `app.spmos.ai` (email sign-up; no credit card required for the Free plan). Under **API Keys**, create a key. Keys look like `spm_live_...` and are shown once — store the key securely.

Choose the scopes the key needs: `memory:write`, `memory:read`, `memory:delete`, `receipt:read`. One key per agent or environment keeps revocation surgical; see [Authentication & API keys](authentication.html).

## 2. Add a provider channel

Under **Providers**, add the LLM account SPM should forward to:

1. Pick a preset (OpenAI, Anthropic, DeepSeek, OpenRouter, Groq, Mistral, xAI, Together AI, Fireworks AI, Moonshot AI, Alibaba DashScope) or choose a **custom endpoint**.
2. Paste the provider API key. It is written to the credential vault and is never returned to the browser, written to memory, or logged.
3. Select a default model from the searchable catalog — entries show context window, pricing, and reasoning/tool capability badges — or type a model name manually.
4. Optionally press **Test connection** to validate the credential against the provider's live model list before saving.

The Free plan includes 1 provider channel; Starter allows 3; Growth allows 10. Full detail: [Bring your own provider](providers.html).

## 3. Make a call

**OpenAI SDK** (Python):

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://api.spmos.ai/v1",
    api_key="spm_live_...",          # your SPM key, not the provider key
)

reply = client.chat.completions.create(
    model="deepseek-chat",           # any model your channel serves
    messages=[{"role": "user", "content": "Remember: my deploy window is Friday."}],
)
print(reply.choices[0].message.content)
```

**Anthropic SDK**:

```python
import anthropic

client = anthropic.Anthropic(
    base_url="https://api.spmos.ai",
    api_key="spm_live_...",
)
```

**curl**:

```bash
curl https://api.spmos.ai/v1/chat/completions \
  -H "Authorization: Bearer spm_live_..." \
  -H "Content-Type: application/json" \
  -d '{"model":"deepseek-chat","messages":[{"role":"user","content":"Hello"}]}'
```

Migration requires only the **base URL + key**. The rest of your agent code does not change; streaming, tool calling, and provider-specific parameters pass through.

## 4. See memory work

Send several turns, then ask about an earlier statement. SPM recalls relevant memory through the evidence gate and folds it into the prompt. On our benchmark harness this added 791 tokens instead of the complete history — a 99.507% context reduction ([Benchmarks](benchmarks.html)).

When no stored memory qualifies, the gate fails closed: the model receives no invented context, and the console **Recall** view shows the gate reason and evidence count for the attempt.

## 5. Watch it in the console

- **Dashboard** — plan usage bars (monthly writes, stored memories) and recent activity.
- **Sources** — every stored memory source, with targeted purge.
- **Recall** — gate outcomes with `gate_reason` and `evidence_count` per attempt.
- **Audit** — signed request receipts (original vs forwarded tokens, recalled memory tokens, latency, status) and purge receipts.

## Next steps

- [Provider proxy API](proxy-api.html) — endpoints, streaming, receipts, error codes
- [MCP server](mcp.html) — plug SPM into Codex or Claude Code
- [Memory, evidence & deletion](memory.html) — what gets remembered, and how to prove deletion
- [Plans & quotas](plans.html) — what happens when you approach a limit
