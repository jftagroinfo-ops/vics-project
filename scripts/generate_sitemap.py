#!/usr/bin/env python3
"""Build a complete sitemap containing every indexable localized URL."""

from __future__ import annotations

import html
import re
from datetime import date
from pathlib import Path

from generate_hreflang import LANGS, ROOT, is_indexable, locale, public_url


def priority(path: Path) -> tuple[str, str]:
    if path.name == "index.html":
        return "1.0", "weekly"
    if path.name == "products.html":
        return "0.9", "weekly"
    if path.name in {"about.html", "contact.html", "quality-control.html"}:
        return "0.85", "monthly"
    if "-exporter.html" in path.name or "-supplier.html" in path.name:
        return "0.80", "monthly"
    if path.name.startswith("blog"):
        return "0.70", "monthly"
    return "0.50", "yearly"


def main() -> None:
    pages = [path for path in ROOT.rglob("*.html") if is_indexable(path)]
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
                f"    <lastmod>{date.today().isoformat()}</lastmod>",
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
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Generated sitemap.xml with {len(pages)} indexable URLs.")


if __name__ == "__main__":
    main()
