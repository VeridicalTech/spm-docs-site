#!/usr/bin/env python3
"""Validate the generated documentation's GEO and crawl contracts."""

from __future__ import annotations

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
        require("{{" not in document and "}}" not in document, f"{output.name}: unresolved template token")

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
            "TechArticle" in serialized or "WebPage" in serialized,
            f"{output.name}: supported page schema missing",
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

    llms = (DIST / "llms.txt").read_text(encoding="utf-8")
    require("<html" not in llms.lower(), "llms.txt contains HTML")
    for entity in ("SPM", "SPMOS.ai", "SPM-Polaris", "StellarPath Memory Operating System"):
        require(entity in llms, f"llms.txt missing {entity}")

    not_found = (DIST / "404.html").read_text(encoding="utf-8")
    require('content="noindex, follow"' in not_found, "404.html must be noindex")
    require("Page not found" in not_found, "404.html content missing")

    home = (DIST / "index.html").read_text(encoding="utf-8")
    for entity in ("SPM", "SPMOS.ai", "SPM-Polaris", "StellarPath Memory Operating System"):
        require(entity in home, f"index.html missing {entity}")

    print(f"PASS {len(slugs)} pages, {len(canonicals)} canonicals, and 4 machine/error files verified")


if __name__ == "__main__":
    try:
        main()
    except FileNotFoundError as error:
        fail(f"missing generated file: {error.filename}")
