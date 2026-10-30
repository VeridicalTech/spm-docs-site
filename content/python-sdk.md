---
title: Python SDK
description: Install and use the pre-release official SPM Python client and its OpenAI and Anthropic drop-in integrations.
published: 2026-10-30
updated: 2026-10-30
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
