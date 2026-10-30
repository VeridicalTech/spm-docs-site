#!/usr/bin/env python3
"""Validate the generated documentation's GEO and crawl contracts."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DIST = ROOT / "dist"
SITE_URL = "https://docs.spmos.ai"


def fail(message: str) -> None:
    print(f"FAIL {message}")
    raise SystemExit(1)


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


def match_one(pattern: str, text: str, label: str) -> str:
    matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
    require(len(matches) == 1, f"{label}: expected one match, found {len(matches)}")
    return matches[0]


def main() -> None:
    require(DIST.is_dir(), "dist is missing; run build.py first")
    slugs = sorted(path.stem for path in CONTENT.glob("*.md"))
    require(bool(slugs), "no content pages found")

    titles: set[str] = set()
    descriptions: set[str] = set()
    canonicals: set[str] = set()

    for slug in slugs:
        output = DIST / f"{slug}.html"
        require(output.is_file(), f"{output.name} is missing")
        document = output.read_text(encoding="utf-8")
        require(
            re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}", document) is None,
            f"{output.name}: unresolved template token",
        )

        title = match_one(r"<title>(.*?)</title>", document, f"{output.name} title")
        description = match_one(
            r'<meta\s+name="description"\s+content="([^"]+)"\s*/?>',
            document,
            f"{output.name} description",
        )
        canonical = match_one(
            r'<link\s+rel="canonical"\s+href="([^"]+)"\s*/?>',
            document,
            f"{output.name} canonical",
        )
        expected = f"{SITE_URL}/" if slug == "index" else f"{SITE_URL}/{slug}"
        require(canonical == expected, f"{output.name}: canonical {canonical!r}, expected {expected!r}")
        require(title not in titles, f"duplicate title: {title}")
        require(description not in descriptions, f"duplicate description: {description}")
        require("Published <time" in document, f"{output.name}: visible publication date missing")
        require("Last reviewed <time" in document, f"{output.name}: visible review date missing")
        require("Applies to" in document, f"{output.name}: visible version scope missing")
        require('class="content reveal"' not in document, f"{output.name}: delayed reveal remains")
        require(
            'src="/assets/orbit-lockup-186.webp"' in document,
            f"{output.name}: optimized header lockup missing",
        )
        require(
            'href="/assets/orbit-favicon-64.webp"' in document,
            f"{output.name}: optimized favicon missing",
        )
        scripts = re.findall(
            r'<script\s+type="application/ld\+json">(.*?)</script>',
            document,
            re.IGNORECASE | re.DOTALL,
        )
        require(bool(scripts), f"{output.name}: JSON-LD missing")
        parsed = []
        for script in scripts:
            try:
                parsed.append(json.loads(script))
            except json.JSONDecodeError as error:
                fail(f"{output.name}: invalid JSON-LD: {error}")
        serialized = json.dumps(parsed)
        require("BreadcrumbList" in serialized, f"{output.name}: BreadcrumbList missing")
        require(
            any(schema in serialized for schema in ("TechArticle", "WebPage", "FAQPage")),
            f"{output.name}: supported page schema missing",
        )
        if slug == "faq":
            faq_pages = []
            for item in parsed:
                if not isinstance(item, dict):
                    continue
                if item.get("@type") == "FAQPage":
                    faq_pages.append(item)
                faq_pages.extend(
                    node
                    for node in item.get("@graph", [])
                    if isinstance(node, dict) and node.get("@type") == "FAQPage"
                )
            require(len(faq_pages) == 1, "faq.html: expected one FAQPage schema")
            questions = faq_pages[0].get("mainEntity", [])
            heading_count = len(re.findall(r"<h2\b", document, re.IGNORECASE))
            require(
                len(questions) == heading_count,
                "faq.html: visible questions and FAQPage entries differ",
            )
            require(
                all(
                    question.get("@type") == "Question"
                    and question.get("name")
                    and question.get("acceptedAnswer", {}).get("@type") == "Answer"
                    and question.get("acceptedAnswer", {}).get("text")
                    for question in questions
                ),
                "faq.html: incomplete FAQPage question or answer",
            )

        titles.add(title)
        descriptions.add(description)
        canonicals.add(canonical)

    sitemap_path = DIST / "sitemap.xml"
    require(sitemap_path.is_file(), "sitemap.xml missing")
    try:
        sitemap = ET.parse(sitemap_path)
    except ET.ParseError as error:
        fail(f"sitemap.xml is invalid XML: {error}")
    namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    sitemap_urls = {
        element.text for element in sitemap.findall("sm:url/sm:loc", namespace) if element.text
    }
    require(sitemap_urls == canonicals, "sitemap URLs do not match page canonicals")

    robots = (DIST / "robots.txt").read_text(encoding="utf-8")
    require("<html" not in robots.lower(), "robots.txt contains HTML")
    require("Sitemap: https://docs.spmos.ai/sitemap.xml" in robots, "robots.txt sitemap missing")

    headers = (DIST / "_headers").read_text(encoding="utf-8")
    require(
        "Cache-Control: public, max-age=300, stale-while-revalidate=300, stale-if-error=86400"
        in headers,
        "bounded public cache policy missing",
    )

    optimized_assets = {
        "orbit-favicon-64.webp": 8_000,
        "orbit-lockup-186.webp": 8_000,
    }
    for name, maximum_bytes in optimized_assets.items():
        asset = DIST / "assets" / name
        require(asset.is_file(), f"missing optimized asset: {name}")
        require(
            asset.stat().st_size <= maximum_bytes,
            f"optimized asset too large: {name} is {asset.stat().st_size} bytes",
        )

    require(
        not (DIST / "assets" / "orbit-mark-light.webp").exists(),
        "oversized favicon was copied into the public build",
    )
    require(
        not (DIST / "assets" / "orbit_light_upscaled.webp").exists(),
        "unused upscaled logo was copied into the public build",
    )

    llms = (DIST / "llms.txt").read_text(encoding="utf-8")
    require("<html" not in llms.lower(), "llms.txt contains HTML")
    for entity in ("SPM", "SPMOS.ai", "SPM-Polaris", "StellarPath Memory Operating System"):
        require(entity in llms, f"llms.txt missing {entity}")

    not_found = (DIST / "404.html").read_text(encoding="utf-8")
    require(
        re.search(r"\{\{[A-Z][A-Z0-9_]*\}\}", not_found) is None,
        "404.html: unresolved template token",
    )
    require('content="noindex, follow"' in not_found, "404.html must be noindex")
    require("Page not found" in not_found, "404.html content missing")
    require('src="/assets/orbit-lockup-186.webp"' in not_found, "404 optimized lockup missing")
    require('href="/assets/orbit-favicon-64.webp"' in not_found, "404 optimized favicon missing")

    home = (DIST / "index.html").read_text(encoding="utf-8")
    for entity in ("SPM", "SPMOS.ai", "SPM-Polaris", "StellarPath Memory Operating System"):
        require(entity in home, f"index.html missing {entity}")

    sidebar_sample = (DIST / "index.html").read_text(encoding="utf-8")
    require('<p class="nav-section">Legal</p>' in sidebar_sample, "Legal sidebar section missing")
    require('href="/privacy"' in sidebar_sample, "Privacy footer link missing")
    require('href="/terms"' in sidebar_sample, "Terms footer link missing")

    # Every published page must be reachable from the sidebar, and no internal
    # link may point at a page that does not exist (including pages we removed).
    sidebar_block = re.search(
        r'<details class="nav-disclosure".*?</details>', sidebar_sample, re.DOTALL
    )
    require(sidebar_block is not None, "sidebar disclosure missing")
    sidebar_hrefs = {
        "index" if path == "" else path
        for path in re.findall(
            r'<a class="nav-link[^"]*" href="/([a-z0-9-]*)"', sidebar_block.group(0)
        )
    }
    require(
        sidebar_hrefs == set(slugs),
        f"sidebar does not list every page: {sorted(sidebar_hrefs ^ set(slugs))}",
    )
    for output in DIST.glob("*.html"):
        document = output.read_text(encoding="utf-8")
        for target in re.findall(r'href="/([a-z0-9-]+)(?:#[^"]*)?"', document):
            if target == "assets":
                continue
            require(target in slugs, f"{output.name}: link to missing page /{target}")
    for removed in ("security", "compare", "roadmap", "official-definitions", "technical-report"):
        require(removed not in slugs, f"removed page still present in inventory: {removed}")
    require('main id="main-content" class="content" tabindex="-1"' in sidebar_sample, "skip target missing")

    # Assets are content-addressed so HTML and CSS cannot desynchronise across
    # a release. A stale stylesheet renders the hidden skip link as page text.
    dist_css = (DIST / "assets" / "site.css").read_text(encoding="utf-8")
    dist_js = (DIST / "assets" / "site.js").read_text(encoding="utf-8")
    css_hash = hashlib.sha256(dist_css.encode("utf-8")).hexdigest()[:12]
    js_hash = hashlib.sha256(dist_js.encode("utf-8")).hexdigest()[:12]
    require(
        f'href="/assets/site.css?v={css_hash}"' in sidebar_sample,
        "stylesheet is not content-addressed",
    )
    require(
        f'src="/assets/site.js?v={js_hash}"' in sidebar_sample,
        "script is not content-addressed",
    )
    require(
        re.search(r"\.skip-link \{[^}]*transform: translateY\(-180%\)", dist_css) is not None,
        "skip link is not hidden at rest",
    )
    require(".skip-link:focus-visible" in dist_css, "skip link does not reveal on keyboard focus")

    print(f"PASS {len(slugs)} pages, {len(canonicals)} canonicals, and 4 machine/error files verified")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as error:
        fail(f"missing generated file: {error.filename}")
