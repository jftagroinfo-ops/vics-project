#!/usr/bin/env python3
"""Add a category-hub link to the existing "Related product(s)" aside on
articles whose linked products all belong to exactly one commodity
category, closing Phase 25's confirmed gap: 0/30 articles linked to any
of the 10 category hub pages, leaving the category->article link
direction one-way.

Deliberately scoped to only the articles that already use the shared
`jft-related-product` aside component (the site's one existing, governed
pattern for this), and only where every linked product resolves to a
single category (no forced/ambiguous category choice). Idempotent: skips
any article whose aside already links to that category page.
"""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CATEGORY_PAGES = [
    "rice-exporter-india.html",
    "spices-exporter-india.html",
    "herbs-seeds-exporter-india.html",
    "oilseeds-exporter-india.html",
    "animal-feed-exporter-india.html",
    "flour-exporter-india.html",
    "wheat-exporter-india.html",
    "sugar-exporter-india.html",
    "raisins-exporter-india.html",
    "pulses-exporter-india.html",
]

ASIDE_RE = re.compile(r'(<aside class="jft-related-product"[^>]*>)(.*?)(</aside>)', re.S)
PRODUCT_LINK_RE = re.compile(r'href="([a-z0-9-]+-(?:exporter|supplier)\.html)"')
CATEGORY_LINK_RE = re.compile(r'href="([a-z0-9-]+-exporter-india\.html)"')


def strip_tags(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text).strip()


def build_category_map() -> dict[str, str]:
    mapping = {}
    for filename in CATEGORY_PAGES:
        source = (ROOT / filename).read_text(encoding="utf-8")
        match = re.search(r"<h1[^>]*>(.*?)</h1>", source, re.S)
        mapping[filename] = strip_tags(match.group(1))
    return mapping


def product_category(product_file: str, category_map: dict[str, str]) -> str | None:
    path = ROOT / product_file
    if not path.is_file():
        return None
    source = path.read_text(encoding="utf-8")
    match = CATEGORY_LINK_RE.search(source)
    if not match or match.group(1) not in category_map:
        return None
    return match.group(1)


def main() -> None:
    category_map = build_category_map()
    articles = sorted(ROOT.glob("blog-*.html"))
    updated = 0
    skipped_existing = 0
    skipped_ambiguous = 0
    skipped_no_aside = 0

    for path in articles:
        source = path.read_text(encoding="utf-8")
        aside_match = ASIDE_RE.search(source)
        if not aside_match:
            skipped_no_aside += 1
            continue

        aside_body = aside_match.group(2)
        product_files = sorted(set(PRODUCT_LINK_RE.findall(aside_body)))
        if not product_files:
            continue

        categories = {product_category(p, category_map) for p in product_files}
        categories.discard(None)
        if len(categories) != 1:
            skipped_ambiguous += 1
            continue

        category_file = next(iter(categories))
        if f'href="{category_file}"' in aside_body:
            skipped_existing += 1
            continue

        category_name = category_map[category_file]
        addition = (
            f' <strong style="color:#173d33;">Category:</strong> '
            f'<a href="{category_file}" style="color:#2f7138;font-weight:700;">{category_name}</a>.'
        )
        new_aside_body = aside_body + addition
        new_source = source[: aside_match.start(2)] + new_aside_body + source[aside_match.end(2):]
        path.write_text(new_source, encoding="utf-8")
        updated += 1

    print(
        f"Articles scanned: {len(articles)}. Category link added: {updated}. "
        f"Already present: {skipped_existing}. Ambiguous (multiple categories, skipped): {skipped_ambiguous}. "
        f"No related-product aside (skipped): {skipped_no_aside}."
    )


if __name__ == "__main__":
    main()
