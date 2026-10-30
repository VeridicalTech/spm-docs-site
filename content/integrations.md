---
title: Choose an integration
description: Compare SPM-Polaris Hosted Provider Proxy, Local Proxy, and MCP by credential custody, model traffic, memory data, receipts, and operating responsibility.
published: 2026-08-22
updated: 2026-10-20
applies_to: SPM-Polaris
---

# Choose an integration

SPM-Polaris supports three integration paths. They use the same governed, hosted memory plane but place model traffic, provider credentials, memory invocation, and operating responsibility at different boundaries. There is no universal default or “most secure” option.

## Boundary comparison

| Decision factor | Hosted Provider Proxy | Local Proxy | MCP |
|-----------------|-----------------------|-------------|-----|
| Model request path | Client → SPM hosted proxy → provider | Client → local proxy → provider | Client → provider |
| Provider credential | SPM-hosted custody | Permissions-restricted local config; sent directly to provider | Application custody |
| Memory invocation | Automatic in request path | Automatic unless memory mode is off | Explicit tools |
| Data sent to SPM | Provider requests and eligible memory content | SPM key and eligible query or memory content | Content submitted to memory tools |
| Provider-traffic receipt | Hosted request metadata and memory outcomes; receipt lookup has no token counts or signature | Local response headers; no hosted gateway receipt | Not applicable |
| Runtime responsibility | SPM operates proxy and memory | You operate local runtime; SPM operates memory | You orchestrate provider and tools; SPM operates memory |

## Hosted Provider Proxy

Choose this path when a managed compatible endpoint and hosted request accounting fit your operating model. SPM receives the model request, runs governed recall and eligible compression, forwards the request in the configured provider's API dialect, streams the response, and records request metadata and memory outcomes.

Hosted receipt lookup does not expose per-request token counts or a cryptographic signature. Dashboard token-savings views are a separate surface. Signed purge receipts and evidence read tokens are not signed provider-request receipts. Compression can omit stored exchanges and elide tool outputs; source readiness does not establish complete semantic recall or guarantee an agent's answer.

The upstream provider credential is held by the SPM-hosted service and used to authenticate provider forwarding. Provider requests and eligible memory content pass through SPM. See the [Hosted Proxy quickstart](quickstart.html), [provider configuration](providers.html), and [Provider proxy API](proxy-api.html).

## Local Proxy

Choose this path when the provider-facing credential and request hop should remain on a machine you operate, while the hosted SPM memory plane remains acceptable.

The upstream provider credential is not sent to or stored by SPM. It is stored in a permissions-restricted local configuration file and sent directly from the local proxy to the configured upstream provider. The package does not encrypt that file. The SPM API key and eligible query or memory content still reach hosted SPM unless memory mode is disabled.

Local Proxy is not a fully local, offline, or self-hosted SPM deployment. Provider traffic does not create hosted gateway request receipts or hosted token accounting. Local response headers are not provider billing records. See the [Local Proxy setup guide](local-proxy.html), [source code](https://github.com/VeridicalTech/spm-local-proxy), and [npm package](https://www.npmjs.com/package/@spmos/local-proxy).

## MCP

Choose this path when your application should own inference and call memory explicitly. Your application calls the provider directly, retains its provider credential, and invokes SPM through `remember`, `recall`, `read`, `delete`, and `status` tools.

SPM sees only the content submitted through those memory operations. Inference receipts and provider accounting stay in your application or provider account. See [MCP server](mcp.html).

## Python SDK and drop-in clients

The official pre-release Python client is published as source at
[github.com/VeridicalTech/spm-client](https://github.com/VeridicalTech/spm-client).
It provides typed memory/evidence/receipt APIs plus tested OpenAI and Anthropic
drop-in helpers. See the [Python SDK guide](python-sdk.html).

The public repository uses Veridical Tech's proprietary license. PyPI publishing
is pending legal release approval, so do not document `pip install spm-client`
as a public install path yet.

## Make the decision from the boundary

Use the path that matches your requirements for credential custody, model-traffic routing, data processing, observability, and runtime ownership. Keeping a provider credential local does not by itself make the whole system local; using a managed proxy does not remove the need to review the provider and content-processing boundary.
