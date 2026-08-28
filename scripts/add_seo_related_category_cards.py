#!/usr/bin/env python3
"""Extend Phase 25's article-to-category-hub linking to articles that use
the `seo-related-grid` component (rather than the `jft-related-product`
aside Phase 25 already handled). Adds one additional "Category" card to
the grid, derived from the grid's own existing product link — no new
categorization judgment is made. Idempotent: skips a grid that already
links to that category.
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

GRID_RE = re.compile(r'(<div class="seo-related-grid">)(.*?)(</div></section>)', re.S)
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
    skipped_no_grid = 0

    for path in articles:
        source = path.read_text(encoding="utf-8")
        grid_match = GRID_RE.search(source)
        if not grid_match:
            skipped_no_grid += 1
            continue

        grid_body = grid_match.group(2)
        product_files = sorted(set(PRODUCT_LINK_RE.findall(grid_body)))
        if not product_files:
            continue
        # Only trust the grid's *first* product-type card, matching the
        # article's own primary subject (later cards may be comparisons).
        first_href_match = re.search(r'href="([^"]+)"', grid_body)
        if not first_href_match or first_href_match.group(1) not in product_files:
            continue

        categories = {product_category(p, category_map) for p in product_files}
        categories.discard(None)
        if len(categories) != 1:
            skipped_ambiguous += 1
            continue

        category_file = next(iter(categories))
        if f'href="{category_file}"' in source:
            skipped_existing += 1
            continue

        category_name = category_map[category_file]
        card = f'<a class="seo-related-card" href="{category_file}"><span>Category</span><strong>{category_name}</strong></a>'
        new_grid_body = grid_body + card
        new_source = source[: grid_match.start(2)] + new_grid_body + source[grid_match.end(2):]
        path.write_text(new_source, encoding="utf-8")
        updated += 1

    print(
        f"Articles scanned: {len(articles)}. Category card added: {updated}. "
        f"Already present: {skipped_existing}. Ambiguous (skipped): {skipped_ambiguous}. "
        f"No seo-related-grid (skipped): {skipped_no_grid}."
    )


if __name__ == "__main__":
    main()
