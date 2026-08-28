#!/usr/bin/env python3
"""Insert the new commodity-category level into English product page breadcrumbs.

Before: Home > Products > [Product]
After:  Home > Products > [Category] > [Product]

Updates both the visible `.jft-breadcrumb` nav and the BreadcrumbList JSON-LD
in the same pass, so they never go out of sync (English pages are not covered
by scripts/sync_breadcrumb_schema_labels.py, which only touches locales -- see
reports/phase10-commodity-architecture-2026-08-27.md Part A). Locale product
pages are not touched in this pass; their breadcrumbs remain Home > Products >
[Product] until locale category pages exist (see the report's Part F).
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from category_content import CATEGORIES  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))


def main() -> int:
    changed = []
    skipped = []
    errors = []
    for p in PRODUCTS:
        cat = CATEGORIES.get(p["c"])
        if not cat:
            errors.append(f"{p['u']}: no category mapping for commodity {p['c']!r}")
            continue
        path = ROOT / p["u"]
        if not path.exists():
            errors.append(f"{p['u']}: file not found")
            continue
        text = path.read_text(encoding="utf-8", errors="replace")

        # Visible breadcrumb: <a href="products.html">Products</a><i .../><span ...>NAME</span>
        old_visible = '<a href="products.html">Products</a>\n          <i class="fa-solid fa-chevron-right"></i>\n'
        if old_visible not in text:
            errors.append(f"{p['u']}: visible breadcrumb pattern not found")
            continue
        category_label = cat["label"].replace("&amp;", "&")
        new_visible = (
            '<a href="products.html">Products</a>\n          <i class="fa-solid fa-chevron-right"></i>\n'
            f'          <a href="{cat["slug"]}">{category_label}</a>\n          <i class="fa-solid fa-chevron-right"></i>\n'
        )
        if text.count(old_visible) != 1:
            errors.append(f"{p['u']}: visible breadcrumb not unique ({text.count(old_visible)})")
            continue
        updated = text.replace(old_visible, new_visible, 1)

        # JSON-LD BreadcrumbList: insert a position-3 category ListItem, renumber
        # the existing product ListItem to position 4. The product's displayed
        # breadcrumb name is captured from the file itself (it does not always
        # match data/products.json's "t" field verbatim), not reconstructed.
        pattern = re.compile(
            r'(\{"@type":"ListItem","position":2,"name":"Products","item":"https://jftagro\.com/products\.html"\},)'
            r'(\{"@type":"ListItem","position":3,"name":"((?:[^"\\]|\\.)*)","item":"https://jftagro\.com/'
            + re.escape(p["u"])
            + r'"\})'
        )
        match = pattern.search(updated)
        if not match:
            errors.append(f"{p['u']}: JSON-LD breadcrumb fragment not found")
            continue
        if len(pattern.findall(updated)) != 1:
            errors.append(f"{p['u']}: JSON-LD breadcrumb fragment not unique")
            continue
        product_name_escaped = match.group(3)
        category_name_escaped = json.dumps(category_label)[1:-1]
        replacement = (
            match.group(1)
            + f'{{"@type":"ListItem","position":3,"name":"{category_name_escaped}","item":"https://jftagro.com/{cat["slug"]}"}},'
            + f'{{"@type":"ListItem","position":4,"name":"{product_name_escaped}","item":"https://jftagro.com/{p["u"]}"}}'
        )
        updated = pattern.sub(lambda m: replacement, updated, count=1)

        path.write_text(updated, encoding="utf-8", newline="\n")
        changed.append(p["u"])

    print(f"Updated {len(changed)} product pages.")
    if errors:
        print(f"{len(errors)} errors:")
        for e in errors[:15]:
            print(" ", e)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
