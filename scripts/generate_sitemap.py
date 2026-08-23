#!/usr/bin/env python3
"""Build a complete sitemap containing every indexable localized URL."""

from __future__ import annotations

import html
from pathlib import Path

from generate_hreflang import LANGS, ROOT, is_indexable, locale, public_url


UPDATED_2026_08_16 = {
    "blog.html",
    "quality-control.html",
    "infrastructure.html",
    "blog-how-to-write-agro-commodity-purchase-specification.html",
    "blog-certificate-of-analysis-food-imports.html",
    "blog-food-container-loading-inspection-checklist.html",
}

UPDATED_2026_08_20 = {
    "editorial-policy.html",
    "india-agricultural-export-market-data-sources.html",
    "blog-how-to-write-agro-commodity-purchase-specification.html",
    "blog-certificate-of-analysis-food-imports.html",
    "blog-food-container-loading-inspection-checklist.html",
    "blog-how-to-choose-indian-agro-exporter.html",
}


def last_modified(path: Path) -> str:
    """Reuse the checked-in value so routine verification is deterministic."""
    if locale(path) == "en" and path.name in UPDATED_2026_08_20:
        return "2026-08-20"
    if locale(path) == "en" and path.name in UPDATED_2026_08_16:
        return "2026-08-16"
    sitemap = ROOT / "sitemap.xml"
    if sitemap.exists():
        text = sitemap.read_text(encoding="utf-8", errors="replace")
        marker = f"<loc>{html.escape(public_url(path))}</loc>"
        position = text.find(marker)
        if position >= 0:
            start = text.find("<lastmod>", position)
            end = text.find("</lastmod>", start)
            if start >= 0 and end >= 0:
                return text[start + len("<lastmod>") : end]
    return "2026-08-16"


def priority(path: Path) -> tuple[str, str]:
    if path.name == "index.html":
        return "1.0", "weekly"
    if path.name == "products.html":
        return "0.9", "weekly"
    if path.name in {"about.html", "contact.html", "quality-control.html"}:
        return "0.85", "monthly"
    if path.name == "infrastructure.html":
        return "0.80", "monthly"
    if "-exporter.html" in path.name or "-supplier.html" in path.name:
        return "0.80", "monthly"
    if path.name.startswith("blog"):
        return "0.70", "monthly"
    return "0.50", "yearly"


def main() -> None:
    # Only source pages belong in the public sitemap. Build/deployment folders
    # such as .cloudflare-dist contain copies of the same HTML and must never be
    # crawled as a second set of URLs.
    candidates = list(ROOT.glob("*.html"))
    for language in LANGS:
        candidates.extend((ROOT / language).glob("*.html"))
    pages = [path for path in candidates if is_indexable(path)]
    directory_pages = [
        path for path in (ROOT / "logistics").glob("*/index.html")
        if is_indexable(path)
    ]
    by_name: dict[str, list[Path]] = {}
    for path in pages:
        by_name.setdefault(path.name, []).append(path)

    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
    ]
    for path in sorted(pages, key=public_url):
        url = public_url(path)
        score, frequency = priority(path)
        lines.extend(
            [
                "  <url>",
                f"    <loc>{html.escape(url)}</loc>",
                f"    <lastmod>{last_modified(path)}</lastmod>",
                f"    <changefreq>{frequency}</changefreq>",
                f"    <priority>{score}</priority>",
            ]
        )
        for item in sorted(by_name[path.name], key=lambda candidate: (locale(candidate) != "en", locale(candidate))):
            lines.append(
                f'    <xhtml:link rel="alternate" hreflang="{locale(item)}" href="{html.escape(public_url(item))}"/>'
            )
        english = next((item for item in by_name[path.name] if locale(item) == "en"), None)
        if english:
            lines.append(
                f'    <xhtml:link rel="alternate" hreflang="x-default" href="{html.escape(public_url(english))}"/>'
            )
        lines.append("  </url>")
    for path in sorted(directory_pages):
        relative = path.parent.relative_to(ROOT).as_posix().strip("/")
        url = f"https://jftagro.com/{relative}/"
        lines.extend(
            [
                "  <url>",
                f"    <loc>{html.escape(url)}</loc>",
                "    <lastmod>2026-08-20</lastmod>",
                "    <changefreq>monthly</changefreq>",
                "    <priority>0.70</priority>",
                f'    <xhtml:link rel="alternate" hreflang="en" href="{html.escape(url)}"/>',
                f'    <xhtml:link rel="alternate" hreflang="x-default" href="{html.escape(url)}"/>',
                "  </url>",
            ]
        )
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated sitemap.xml with {len(pages) + len(directory_pages)} indexable URLs.")


if __name__ == "__main__":
    main()
