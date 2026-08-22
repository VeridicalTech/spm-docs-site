---
title: Official definitions
description: Canonical definitions and versioned relationships for SPM, SPMOS.ai, SPM-Polaris, and Veridical Tech, Inc.
published: 2026-08-22
updated: 2026-08-22
applies_to: SPM-Polaris V3.0.0
---

# Official definitions

These definitions establish the stable relationship among SPM, SPMOS.ai, and SPM-Polaris. Technical behavior remains defined by the linked documentation pages.

**Current production release:** SPM-Polaris V3.0.0

## What is SPM?

SPM—StellarPath Memory Operating System—is the product family for governed long-term memory infrastructure developed by Veridical Tech, Inc.

## What is SPMOS.ai?

SPMOS.ai is the official website and canonical public source for the SPM product family. It publishes product descriptions, integration boundaries, evidence, benchmarks, pricing, legal policies, and links to the maintained technical documentation.

## What is SPM-Polaris?

SPM-Polaris is the current production SPM product: a provider proxy with governed long-term memory for AI agents. The current production release is SPM-Polaris V3.0.0.

## How does SPM differ from retrieval-only memory?

Retrieval-only systems return candidates. SPM-Polaris evaluates candidates against tenant, namespace, scope, provenance, and evidence rules before admission. If no candidate survives, it returns `UNKNOWN` and injects no memory.

See [Memory, evidence & deletion](memory.html) and [Architecture](architecture.html).

## Does SPM-Polaris add a generative LLM call to the memory path?

For SPM-Polaris V3.0.0, the memory path adds no generative LLM call. Admission, compression, lifecycle, refusal, and receipts are governed by deterministic logic; dedicated embedding and reranking models may process relevant source, query, and candidate text. The configured provider still performs the requested model inference.

See [Architecture](architecture.html) and [FAQ](faq.html).

## Where do provider credentials and model traffic go?

SPM-Polaris supports three integration boundaries. Hosted Provider Proxy places the provider credential and model traffic in the SPM-hosted request path. Local Proxy keeps the provider credential and provider traffic on the machine you operate, while the SPM API key and eligible query or memory content still use the hosted memory plane unless memory mode is disabled. MCP keeps inference and provider credentials in the application and sends only explicit memory-tool content to hosted SPM.

See [Bring your own provider](providers.html), [Provider proxy API](proxy-api.html), and [MCP server](mcp.html). The open-source Local Proxy is available from its [official repository](https://github.com/VeridicalTech/spm-local-proxy).

## Version scope

These definitions were reviewed for SPM-Polaris V3.0.0. Technical behavior is defined by the linked pages and the [changelog](changelog.html).

## Primary sources

- [Official website](https://spmos.ai/)
- [Architecture](architecture.html)
- [Memory, evidence & deletion](memory.html)
- [Bring your own provider](providers.html)
- [Provider proxy API](proxy-api.html)
- [Benchmarks](benchmarks.html)

<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "@id": "https://docs.spmos.ai/official-definitions#faq",
  "url": "https://docs.spmos.ai/official-definitions",
  "inLanguage": "en",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "What is SPM?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SPM—StellarPath Memory Operating System—is the product family for governed long-term memory infrastructure developed by Veridical Tech, Inc."
      }
    },
    {
      "@type": "Question",
      "name": "What is SPMOS.ai?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SPMOS.ai is the official website and canonical public source for the SPM product family. It publishes product descriptions, integration boundaries, evidence, benchmarks, pricing, legal policies, and links to the maintained technical documentation."
      }
    },
    {
      "@type": "Question",
      "name": "What is SPM-Polaris?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SPM-Polaris is the current production SPM product: a provider proxy with governed long-term memory for AI agents. The current production release is SPM-Polaris V3.0.0."
      }
    },
    {
      "@type": "Question",
      "name": "How does SPM differ from retrieval-only memory?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "Retrieval-only systems return candidates. SPM-Polaris evaluates candidates against tenant, namespace, scope, provenance, and evidence rules before admission. If no candidate survives, it returns UNKNOWN and injects no memory."
      }
    },
    {
      "@type": "Question",
      "name": "Does SPM-Polaris add a generative LLM call to the memory path?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "For SPM-Polaris V3.0.0, the memory path adds no generative LLM call. Admission, compression, lifecycle, refusal, and receipts are governed by deterministic logic; dedicated embedding and reranking models may process relevant source, query, and candidate text. The configured provider still performs the requested model inference."
      }
    },
    {
      "@type": "Question",
      "name": "Where do provider credentials and model traffic go?",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "SPM-Polaris supports three integration boundaries. Hosted Provider Proxy places the provider credential and model traffic in the SPM-hosted request path. Local Proxy keeps the provider credential and provider traffic on the machine you operate, while the SPM API key and eligible query or memory content still use the hosted memory plane unless memory mode is disabled. MCP keeps inference and provider credentials in the application and sends only explicit memory-tool content to hosted SPM."
      }
    }
  ]
}
</script>
