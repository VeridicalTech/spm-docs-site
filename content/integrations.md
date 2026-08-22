---
title: Choose an integration
description: Compare SPM-Polaris Hosted Provider Proxy, Local Proxy, and MCP by credential custody, model traffic, memory data, receipts, and operating responsibility.
published: 2026-08-22
updated: 2026-08-22
applies_to: SPM-Polaris V3.0.0
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
| Provider-traffic receipt | Hosted signed gateway receipt | Local response headers; no hosted gateway receipt | Not applicable |
| Runtime responsibility | SPM operates proxy and memory | You operate local runtime; SPM operates memory | You orchestrate provider and tools; SPM operates memory |

## Hosted Provider Proxy

Choose this path when a managed compatible endpoint and hosted request accounting fit your operating model. SPM receives the model request, runs governed recall and compression, forwards the request in its native API dialect, streams the response, and records the signed request receipt.

The upstream provider credential is held by the SPM-hosted service and used to authenticate provider forwarding. Provider requests and eligible memory content pass through SPM. See the [Hosted Proxy quickstart](quickstart.html), [provider configuration](providers.html), and [Provider proxy API](proxy-api.html).

## Local Proxy

Choose this path when the provider-facing credential and request hop should remain on a machine you operate, while the hosted SPM memory plane remains acceptable.

The upstream provider credential is not sent to or stored by SPM. It is stored in a permissions-restricted local configuration file and sent directly from the local proxy to the configured upstream provider. The package does not encrypt that file. The SPM API key and eligible query or memory content still reach hosted SPM unless memory mode is disabled.

Local Proxy is not a fully local, offline, or self-hosted SPM deployment. Provider traffic does not receive the hosted gateway's signed receipt or hosted token accounting. See the [Local Proxy setup guide](local-proxy.html), [source code](https://github.com/VeridicalTech/spm-local-proxy), and [npm package](https://www.npmjs.com/package/@spmos/local-proxy).

## MCP

Choose this path when your application should own inference and call memory explicitly. Your application calls the provider directly, retains its provider credential, and invokes SPM through `remember`, `recall`, `read`, `delete`, and `status` tools.

SPM sees only the content submitted through those memory operations. Inference receipts and provider accounting stay in your application or provider account. See [MCP server](mcp.html).

## Make the decision from the boundary

Use the path that matches your requirements for credential custody, model-traffic routing, data processing, observability, and runtime ownership. Keeping a provider credential local does not by itself make the whole system local; using a managed proxy does not remove the need to review the provider and content-processing boundary.
