#!/usr/bin/env python3
"""Build the SPM documentation site (static, no JS framework).

    docs-site/.venv/bin/python docs-site/build.py

Reads content/*.md (+ front-matter title), renders with the shared page
shell into dist/. Copy-only assets live in assets/; brand assets are copied
into the flat dist/assets path used by the shared page template.
"""

from __future__ import annotations

import html
import re
import shutil
import sys
from pathlib import Path

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
DIST = ROOT / "dist"
SYSTEM_NAME = "StellarPath Memory Operating System"
PRODUCT_NAME = "SPM"
PRODUCT_VERSION = ""
PRODUCT_RELEASE = PRODUCT_NAME
# Brand images are vendored here so the docs site builds without the console
# checkout next to it.
WEB_PUBLIC = ROOT / "assets" / "logo"

# Sidebar order. (slug, section, title)
PAGES = [
    ("index", "Start", "Overview"),
    ("quickstart", "Start", "Quickstart"),
    ("authentication", "Start", "Authentication & API keys"),
    ("plans", "Start", "Plans & quotas"),
    ("providers", "Guides", "Bring your own provider"),
    ("local-proxy", "Guides", "Local Proxy"),
    ("proxy-api", "Guides", "Provider proxy API"),
    ("memory", "Guides", "Memory, evidence & deletion"),
    ("mcp", "Guides", "MCP server"),
    ("architecture", "Reference", "Architecture"),
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


def protect_versioned_package_names(body_html: str) -> str:
    """Prevent Cloudflare from treating scoped package versions as email addresses."""
    return VERSIONED_SCOPED_PACKAGE.sub(
        r"<!--email_off-->\1<!--/email_off-->", body_html
    )


def render_page(slug: str, title: str, body_html: str) -> str:
    sections: dict[str, list[tuple[str, str, str]]] = {}
    for s, section, t in PAGES:
        sections.setdefault(section, []).append((s, t, "active" if s == slug else ""))
    nav = []
    for section, items in sections.items():
        nav.append(f'<p class="nav-section">{html.escape(section)}</p>')
        for s, t, active in items:
            href = "index.html" if s == "index" else f"{s}.html"
            nav.append(f'<a class="nav-link {active}" href="{href}">{html.escape(t)}</a>')
    return (
        TEMPLATE.replace("{{TITLE}}", html.escape(title))
        .replace("{{SYSTEM_NAME}}", html.escape(SYSTEM_NAME))
        .replace("{{PRODUCT_NAME}}", html.escape(PRODUCT_NAME))
        .replace("{{PRODUCT_VERSION}}", html.escape(PRODUCT_VERSION))
        .replace("{{PRODUCT_RELEASE}}", html.escape(PRODUCT_RELEASE))
        .replace("{{NAV}}", "\n".join(nav))
        .replace("{{CONTENT}}", body_html)
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

    for md_file in sorted(CONTENT.glob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        title = md_file.stem
        if raw.startswith("---"):
            _, fm, raw = raw.split("---", 2)
            match = re.search(r"^title:\s*(.+)$", fm, re.M)
            if match:
                title = match.group(1).strip()
        body = protect_versioned_package_names(
            markdown.markdown(raw, extensions=MD_EXTENSIONS)
        )
        slug = md_file.stem
        (DIST / f"{slug}.html").write_text(render_page(slug, title, body), encoding="utf-8")
        print(f"  {slug}.html")
    print(f"Built {len(list(CONTENT.glob('*.md')))} pages -> {DIST}")


if __name__ == "__main__":
    main()
