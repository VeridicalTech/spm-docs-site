#!/usr/bin/env python3
"""Build the SPM documentation site (static, no JS framework).

    docs-site/.venv/bin/python docs-site/build.py

Reads content/*.md (+ front-matter title), renders with the shared page
shell into dist/. Copy-only assets live in assets/; brand assets are copied
into the flat dist/assets path used by the shared page template.
"""

from __future__ import annotations

import html
import json
import re
import shutil
import sys
from pathlib import Path
from xml.sax.saxutils import escape as xml_escape

try:
    import markdown
except ImportError:
    sys.exit(
        "markdown package missing. Create the venv: python3 -m venv docs-site/.venv "
        "&& docs-site/.venv/bin/pip install markdown pymdown-extensions"
    )

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
TEMPLATE = (ROOT / "templates" / "page.html").read_text(encoding="utf-8")
NOT_FOUND_TEMPLATE = (ROOT / "templates" / "404.html").read_text(encoding="utf-8")
DIST = ROOT / "dist"
SITE_URL = "https://docs.spmos.ai"
SITE_NAME = "SPM Documentation"
SYSTEM_NAME = "StellarPath Memory Operating System"
PRODUCT_NAME = "SPM"
PRODUCT_VERSION = ""
PRODUCT_RELEASE = PRODUCT_NAME
SOCIAL_IMAGE = "https://docs.spmos.ai/assets/orbit-light-transparent.png"
# Brand images are vendored here so the docs site builds without the console
# checkout next to it.
WEB_PUBLIC = ROOT / "assets" / "logo"

# Sidebar order. (slug, section, title)
PAGES = [
    ("index", "Start", "Overview"),
    ("integrations", "Start", "Choose an integration"),
    ("quickstart", "Start", "Quickstart"),
    ("authentication", "Start", "Authentication & API keys"),
    ("plans", "Start", "Plans & quotas"),
    ("providers", "Guides", "Bring your own provider"),
    ("local-proxy", "Guides", "Local Proxy"),
    ("proxy-api", "Guides", "Provider proxy API"),
    ("memory", "Guides", "Memory, evidence & deletion"),
    ("mcp", "Guides", "MCP server"),
    ("official-definitions", "Reference", "Official definitions"),
    ("architecture", "Reference", "Architecture"),
    ("security", "Reference", "Security"),
    ("benchmarks", "Reference", "Benchmarks"),
    ("faq", "Reference", "FAQ"),
    ("changelog", "Reference", "Changelog"),
    ("privacy", "Legal", "Privacy Policy"),
    ("terms", "Legal", "Terms of Service"),
]

MD_EXTENSIONS = ["fenced_code", "tables", "toc", "attr_list", "sane_lists"]
VERSIONED_SCOPED_PACKAGE = re.compile(
    r"(?<![A-Za-z0-9_.-])(@[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+@[A-Za-z0-9_.+-]+)"
)
INTERNAL_HTML_LINK = re.compile(
    r'href="(?P<slug>[a-z0-9-]+)\.html(?P<suffix>(?:[?#][^"]*)?)"'
)

REQUIRED_METADATA = {"title", "description", "published", "updated", "applies_to"}


def protect_versioned_package_names(body_html: str) -> str:
    """Prevent Cloudflare from treating scoped package versions as email addresses."""
    return VERSIONED_SCOPED_PACKAGE.sub(
        r"<!--email_off-->\1<!--/email_off-->", body_html
    )


def canonicalize_internal_links(body_html: str) -> str:
    """Link to the extensionless routes Cloudflare Pages serves canonically."""
    return INTERNAL_HTML_LINK.sub(
        lambda match: f'href="/{match.group("slug")}{match.group("suffix")}"',
        body_html,
    )


def parse_source(md_file: Path) -> tuple[dict[str, str], str]:
    raw = md_file.read_text(encoding="utf-8")
    metadata: dict[str, str] = {}
    if raw.startswith("---"):
        _, front_matter, raw = raw.split("---", 2)
        for line in front_matter.splitlines():
            key, separator, value = line.partition(":")
            if separator:
                metadata[key.strip()] = value.strip()
    missing = sorted(REQUIRED_METADATA - metadata.keys())
    if missing:
        sys.exit(f"{md_file.name}: missing front-matter fields: {', '.join(missing)}")
    return metadata, raw


def canonical_url(slug: str) -> str:
    return f"{SITE_URL}/" if slug == "index" else f"{SITE_URL}/{slug}"


def structured_data(slug: str, metadata: dict[str, str]) -> str:
    url = canonical_url(slug)
    page_type = metadata.get("schema", "TechArticle")
    page = {
        "@type": page_type,
        "@id": f"{url}#page",
        "url": url,
        "name": metadata["title"],
        "headline": metadata["title"],
        "description": metadata["description"],
        "datePublished": metadata["published"],
        "dateModified": metadata["updated"],
        "inLanguage": "en",
        "isPartOf": {"@id": f"{SITE_URL}/#website"},
        "publisher": {"@id": "https://spmos.ai/#organization"},
        "about": metadata["applies_to"],
    }
    if page_type == "TechArticle":
        page["proficiencyLevel"] = "Developer"
    breadcrumbs = [
        {"@type": "ListItem", "position": 1, "name": "SPM Documentation", "item": f"{SITE_URL}/"}
    ]
    if slug != "index":
        breadcrumbs.append(
            {"@type": "ListItem", "position": 2, "name": metadata["title"], "item": url}
        )
    graph = {
        "@context": "https://schema.org",
        "@graph": [
            {
                "@type": "Organization",
                "@id": "https://spmos.ai/#organization",
                "name": "Veridical Tech, Inc.",
                "url": "https://spmos.ai/",
            },
            {
                "@type": "WebSite",
                "@id": f"{SITE_URL}/#website",
                "url": f"{SITE_URL}/",
                "name": SITE_NAME,
                "publisher": {"@id": "https://spmos.ai/#organization"},
                "inLanguage": "en",
            },
            page,
            {
                "@type": "BreadcrumbList",
                "@id": f"{url}#breadcrumb",
                "itemListElement": breadcrumbs,
            },
        ],
    }
    return json.dumps(graph, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c")


def render_page(slug: str, metadata: dict[str, str], body_html: str) -> str:
    sections: dict[str, list[tuple[str, str, str]]] = {}
    for s, section, t in PAGES:
        sections.setdefault(section, []).append((s, t, "active" if s == slug else ""))
    nav = []
    for section, items in sections.items():
        nav.append(f'<p class="nav-section">{html.escape(section)}</p>')
        for s, t, active in items:
            href = "/" if s == "index" else f"/{s}"
            nav.append(f'<a class="nav-link {active}" href="{href}">{html.escape(t)}</a>')
    title = metadata["title"]
    description = metadata["description"]
    url = canonical_url(slug)
    page_type = "article" if metadata.get("schema", "TechArticle") == "TechArticle" else "website"
    breadcrumb = ""
    if slug != "index":
        breadcrumb = (
            '<nav class="breadcrumbs" aria-label="Breadcrumb">'
            '<a href="/">Documentation</a><span aria-hidden="true">/</span>'
            f'<span aria-current="page">{html.escape(title)}</span></nav>'
        )
    page_meta = (
        '<p class="page-meta">'
        f'Published <time datetime="{html.escape(metadata["published"])}">{html.escape(metadata["published"])}</time>'
        ' <span aria-hidden="true">·</span> '
        f'Last reviewed <time datetime="{html.escape(metadata["updated"])}">{html.escape(metadata["updated"])}</time>'
        ' <span aria-hidden="true">·</span> '
        f'Applies to {html.escape(metadata["applies_to"])}'
        "</p>"
    )
    body_html = body_html.replace("</h1>", f"</h1>{page_meta}", 1)
    return (
        TEMPLATE.replace("{{TITLE}}", html.escape(title))
        .replace("{{DESCRIPTION}}", html.escape(description, quote=True))
        .replace("{{CANONICAL_URL}}", html.escape(url, quote=True))
        .replace("{{OG_TYPE}}", page_type)
        .replace("{{SOCIAL_IMAGE}}", SOCIAL_IMAGE)
        .replace("{{PUBLISHED}}", html.escape(metadata["published"], quote=True))
        .replace("{{UPDATED}}", html.escape(metadata["updated"], quote=True))
        .replace("{{STRUCTURED_DATA}}", structured_data(slug, metadata))
        .replace("{{SYSTEM_NAME}}", html.escape(SYSTEM_NAME))
        .replace("{{PRODUCT_NAME}}", html.escape(PRODUCT_NAME))
        .replace("{{PRODUCT_VERSION}}", html.escape(PRODUCT_VERSION))
        .replace("{{PRODUCT_RELEASE}}", html.escape(PRODUCT_RELEASE))
        .replace("{{NAV}}", "\n".join(nav))
        .replace("{{BREADCRUMB}}", breadcrumb)
        .replace("{{CONTENT}}", body_html)
    )


def write_machine_files(pages: list[tuple[str, dict[str, str]]]) -> None:
    sitemap_items = []
    for slug, metadata in pages:
        sitemap_items.append(
            "  <url>\n"
            f"    <loc>{xml_escape(canonical_url(slug))}</loc>\n"
            f"    <lastmod>{xml_escape(metadata['updated'])}</lastmod>\n"
            "  </url>"
        )
    sitemap_body = "\n".join(sitemap_items)
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_body}\n"
        "</urlset>\n"
    )
    (DIST / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    (DIST / "robots.txt").write_text(
        "User-agent: *\nAllow: /\n\nSitemap: https://docs.spmos.ai/sitemap.xml\n",
        encoding="utf-8",
    )
    (DIST / "_headers").write_text(
        "/*\n"
        "  Cache-Control: public, max-age=300, stale-while-revalidate=300, stale-if-error=86400\n",
        encoding="utf-8",
    )
    (DIST / "llms.txt").write_text(
        "# SPM Documentation\n\n"
        "> Official technical documentation for SPM, the StellarPath Memory Operating System.\n\n"
        "SPM-Polaris is the current production SPM product: a provider proxy with governed long-term memory for AI agents.\n"
        "SPMOS.ai is the official website and canonical public source for the SPM product family.\n\n"
        "## Primary pages\n\n"
        + "\n".join(
            f"- [{metadata['title']}]({canonical_url(slug)}): {metadata['description']}"
            for slug, metadata in pages
            if slug in {"index", "official-definitions", "integrations", "architecture", "security", "benchmarks", "changelog"}
        )
        + "\n",
        encoding="utf-8",
    )


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    (DIST / "assets").mkdir(parents=True)

    shutil.copytree(ROOT / "assets", DIST / "assets", dirs_exist_ok=True)
    for name in (
        "orbit_light_upscaled.webp",
        "orbit-mark-light.webp",
        "orbit-wordmark-light.webp",
        "orbit-light-transparent.png",
    ):
        shutil.copy(WEB_PUBLIC / name, DIST / "assets" / name)

    expected_slugs = [slug for slug, _, _ in PAGES]
    actual_slugs = sorted(path.stem for path in CONTENT.glob("*.md"))
    if sorted(expected_slugs) != actual_slugs:
        missing = sorted(set(expected_slugs) - set(actual_slugs))
        extra = sorted(set(actual_slugs) - set(expected_slugs))
        sys.exit(f"Page inventory mismatch; missing={missing}, extra={extra}")

    pages: list[tuple[str, dict[str, str]]] = []
    for slug in expected_slugs:
        metadata, raw = parse_source(CONTENT / f"{slug}.md")
        body = canonicalize_internal_links(
            protect_versioned_package_names(
                markdown.markdown(raw, extensions=MD_EXTENSIONS)
            )
        )
        (DIST / f"{slug}.html").write_text(render_page(slug, metadata, body), encoding="utf-8")
        pages.append((slug, metadata))
        print(f"  {slug}.html")
    (DIST / "404.html").write_text(NOT_FOUND_TEMPLATE, encoding="utf-8")
    write_machine_files(pages)
    print(f"Built {len(pages)} pages and machine files -> {DIST}")


if __name__ == "__main__":
    main()
