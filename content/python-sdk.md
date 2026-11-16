---
title: Python SDK
description: Install and use the pre-release official SPM Python client and its OpenAI and Anthropic drop-in integrations.
published: 2026-10-30
updated: 2026-11-17
applies_to: spm-client 0.2.1 pre-release
schema: TechArticle
---

# Python SDK

The official pre-release Python client is available at
[VeridicalTech/spm-client](https://github.com/VeridicalTech/spm-client).

It covers typed memory/evidence calls, gateway chat sessions, receipts, offline
evidence verification, and drop-in OpenAI/Anthropic clients. The repository is
public, but the current release remains proprietary and PyPI publication is
pending legal approval.

## Install from GitHub checkout

```bash
git clone https://github.com/VeridicalTech/spm-client.git
cd spm-client
pip install ".[integrations]"
```

The base package needs `httpx`. The optional `integrations` extra installs the
official OpenAI and Anthropic SDKs. The package is currently `spm-client`
version `0.2.1`; there is no supported public `pip install spm-client` path yet.

## OpenAI drop-in

```python
from openai import OpenAI
from spm_client import patch_openai

client = patch_openai(
    OpenAI(api_key="sk-upstream"),
    api_key="spm_live_...",
    base_url="https://api.spmos.ai",
)

reply = client.chat.completions.create(
    model="your-configured-model",
    messages=[{"role": "user", "content": "Hello"}],
)
```

The helper updates the official SDK's actual HTTP transport, URL, and
authentication header. It does not merely change a public attribute. Passing a
new `base_url` requires an explicit SPM key; an upstream provider key is never
silently forwarded to SPM. Both `https://api.spmos.ai` and
`https://api.spmos.ai/v1` are accepted.

## Anthropic drop-in

```python
from anthropic import Anthropic
from spm_client import patch_anthropic

client = patch_anthropic(
    Anthropic(api_key="sk-ant-upstream"),
    api_key="spm_live_...",
    base_url="https://api.spmos.ai",
)

reply = client.messages.create(
    model="your-configured-model",
    max_tokens=256,
    messages=[{"role": "user", "content": "Hello"}],
)
```

## One-line OpenAI setup

```bash
export SPM_API_KEY=spm_live_...
export SPM_GATEWAY_URL=https://api.spmos.ai
```

```python
from spm_client import auto

client = auto()
```

`auto()` validates the environment before importing the optional OpenAI
dependency and reports an actionable install error when it is missing.

## Two surfaces, one package

`spm_client` exposes two independent surfaces. They have separate entry points
and separate error bases, and the near-identical names are the SDK's own trap.

| Surface | Entry point | Talks to | Base error |
| --- | --- | --- | --- |
| Gateway | `SpmClient`, `ChatSession` | `/v1` on the gateway: chat completions, health, request receipts | `SpmError` |
| Memory | `AsyncSPMMemoryClient` | `/mcp`: remember, recall, read, delete, status | `SPMError` |

Catch the one that belongs to the surface you called; they share no base class.

## Streaming

`stream=True` works through the official OpenAI client without further changes:

```python
stream = client.chat.completions.create(
    model="your-configured-model",
    messages=[{"role": "user", "content": "Stream a two-line summary."}],
    stream=True,
    )
for chunk in stream:
    print(chunk.choices[0].delta.content or "", end="")
```

The SDK's own client has the same switch: `SpmClient(api_key=..., base_url=...)
.chat(messages, stream=True)` returns an iterator of raw SSE lines, and
`stream=False` returns the decoded response dict.

## Memory (async)

The memory surface is `async`. Use it as a context manager so the pool closes:

```python
import asyncio
from spm_client import AsyncSPMMemoryClient, SPMConfig

async def main() -> None:
    config = SPMConfig(api_key="spm_live_...", mcp_url="https://api.spmos.ai/mcp")
    async with AsyncSPMMemoryClient(config) as memory:
        await memory.remember(
            text="The docs-smoke project deploys on Fridays at 16:00 UTC.",
            idempotency_key="docs-smoke-20261117-01",
            source_id="docs-smoke-20261117-01",
            topic="docs-smoke",
        )
        await memory.status(source_ids=["docs-smoke-20261117-01"])

        result = await memory.recall("When does the docs-smoke project deploy?")
        if result.supported:
            await memory.read([ref.read_token for ref in result.evidence])

        await memory.delete(
            source_id="docs-smoke-20261117-01",
            idempotency_key="docs-smoke-20261117-01-delete",
        )

asyncio.run(main())
```

`recall()` returns a `RecallResult` (`answer`, `status`, `evidence`, `raw`). Each
evidence item carries `source_id` and `read_token`, and `raw` keeps the untouched
payload so `evidence_decision` stays readable. Branch on `status`, not on the
prose; see [Recall verdicts](verdicts.html).

Passing `user_partition` requires the `memory:partition` scope. MCP `status` and
`delete` do not accept a partition, so target them with source IDs.

## Verifying evidence offline

A read token can be checked without calling back to the server that minted it.
Ed25519-signed handles need the optional extra: `pip install ".[evidence]"`.

```python
from spm_client import verify_evidence_token

verified = verify_evidence_token(read_token, public_keys=published_keys)
print(verified.kid, verified.expiry, verified.payload)
```

`EvidenceVerificationError.reason` names the failed check (signature, expiry,
encoding), so a caller can tell "expired" from "wrong key".

## Verification

The release was tested with the official OpenAI and Anthropic clients against a
local HTTP capture server, including endpoint paths and authentication headers.
The repository test suite also covers memory, evidence, receipts, session
options, optional dependencies, and package import isolation.

```bash
pip install ".[dev]"
python -m pytest client_tests -q
```

Do not commit SPM keys or provider keys. The SDK does not turn Local Proxy or
Hosted Provider Proxy into a self-hosted SPM deployment; see [integration
boundaries](integrations.html).
