#!/usr/bin/env python3
"""Restore the export-documentation contextual link on locale product pages.

Root cause (see reports/phase10-commodity-architecture-2026-08-27.md, Part P):
46 English product pages carry a `.jft-document-path` aside immediately before
the footer placeholder, contextually linking to export-documentation.html (2
of the 46 also link to a specific logistics/article page). This component was
never added to any locale product page -- not mistranslated, simply omitted --
which is why export-documentation.html measured 86 contextual inbound links in
English but only 0-1 per locale (Phase 9 Part J).

This script restores the *generic* variant (the one used by 44 of the 46
English pages) to the locale copies of all 46 affected products, using only
governed cache translations. The 2 English pages with an enhanced variant
(extra links to a Mundra logistics page / a purchase-specification article)
keep that enhancement English-only for now -- replicating it correctly would
require deciding whether every locale's equivalent logistics/article page is
itself in a fit state to receive the link, which is out of this phase's scope;
documented, not silently expanded.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE = json.loads((ROOT / "data/localized-copy-cache.json").read_text(encoding="utf-8"))
PRODUCTS = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")

LABEL_KEY = "Shipment documentation:"
BODY_KEY = "turn the destination, product, specification, inspection and payment requirements into an issuer-and-deadline matrix in the"
LINK_KEY = "agro export documentation centre"

ANCHOR = '<div id="footer-placeholder">'


def find_affected_products() -> list[str]:
    affected = []
    for p in PRODUCTS:
        path = ROOT / p["u"]
        if not path.exists():
            continue
        if "jft-document-path" in path.read_text(encoding="utf-8", errors="replace"):
            affected.append(p["u"])
    return affected


def render_block(locale: str) -> str:
    label = CACHE[locale][LABEL_KEY]
    body = CACHE[locale][BODY_KEY]
    link_text = CACHE[locale][LINK_KEY]
    return (
        '<aside class="jft-document-path" aria-label="Shipment documentation" '
        'style="width:min(1120px,calc(100% - 40px));margin:36px auto;padding:20px 22px;'
        'border:1px solid #dbe4de;border-left:4px solid #3d7030;border-radius:8px;'
        'background:#f7faf7;color:#405049;line-height:1.7;">'
        f'<strong style="color:#173d33;">{label}</strong> {body} '
        f'<a href="export-documentation.html" style="color:#2f7138;font-weight:700;">{link_text}</a>.'
        "</aside>\n"
    )


def main() -> int:
    affected = find_affected_products()
    print(f"{len(affected)} English product pages carry the document-path block.")

    changed = []
    skipped_already_present = []
    errors = []
    for slug in affected:
        for locale in LOCALES:
            path = ROOT / locale / slug
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            if "jft-document-path" in text:
                skipped_already_present.append(str(path.relative_to(ROOT)))
                continue
            if ANCHOR not in text:
                errors.append(f"{path}: anchor not found")
                continue
            if text.count(ANCHOR) != 1:
                errors.append(f"{path}: anchor not unique ({text.count(ANCHOR)} occurrences)")
                continue
            block = render_block(locale)
            updated = text.replace(ANCHOR, block + ANCHOR, 1)
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed.append(str(path.relative_to(ROOT)))

    print(f"Added the block to {len(changed)} locale pages.")
    print(f"Skipped {len(skipped_already_present)} (already present).")
    if errors:
        print(f"ERRORS on {len(errors)} pages:")
        for e in errors[:10]:
            print(" ", e)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
