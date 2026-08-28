#!/usr/bin/env python3
"""Restore missing product<->article reciprocal links (Phase 10, Parts J/K).

data/products.json's `b` field already establishes 35 genuine product<->article
relationships. This script does not invent any new relationship -- it only
completes the 2 directions of the 35 that already exist in governed data but
were not both rendered as links (14 products missing the forward link to their
article, 15 articles missing the back-link to their product).
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))

# Never link to a placeholder article the site's own audit_website.py already
# tracks as unpublished (UNPUBLISHED_BLOGS) -- e.g. blog-toor-dal-export-
# india-2026.html is a literal "create full content as needed" stub. See
# reports/phase10-commodity-architecture-2026-08-27.md.
import re as _re

_audit_website_src = (ROOT / "scripts/audit_website.py").read_text(encoding="utf-8")
_match = _re.search(r"UNPUBLISHED_BLOGS\s*=\s*\{([^}]*)\}", _audit_website_src, _re.S)
UNPUBLISHED_BLOGS = set(_re.findall(r'"([^"]+)"', _match.group(1))) if _match else set()

FORWARD_ANCHOR = 'Dedicated export manager — single point of contact from inquiry to delivery</span></li>\n        </ul>'

ARTICLE_LINK_TEXT = {
    "blog-basmati-export-guide.html": "Basmati export guide",
    "blog-ir64-export.html": "IR64 export guide",
    "blog-india-rice-export-sri-lanka-bangladesh.html": "India rice export to Bangladesh &amp; Sri Lanka",
    "blog-turmeric-market-outlook-2026.html": "Turmeric market outlook 2026",
    "blog-cumin-jeera-price-outlook-2026.html": "Cumin price outlook 2026",
    "blog-top-indian-agro-commodities-import-2026.html": "Top Indian agro commodities to import",
    "blog-groundnut-peanut-export-india-2026.html": "Groundnut import guide",
    "blog-toor-dal-export-india-2026.html": "Toor dal export guide",
    "blog-green-mung-beans-export-india-2026.html": "Green mung bean export guide",
}

# 7 products where a "Further reading" link ALREADY exists but points to a less
# relevant or (for black cumin) an entirely different-commodity article than
# the one data/products.json's `b` field specifies -- e.g. every non-Basmati
# rice grade (Silky Sortex, Samba, PR-11) defaulted to "Basmati export guide,"
# and black cumin linked to a turmeric article. These are corrected to the
# governed, product-specific article. 2 other products in the original list
# (turmeric-finger-exporter.html, groundnut-oil-cake-exporter.html) already
# link to a different but genuinely relevant article and are deliberately left
# unchanged -- see the report for why a second link was not forced there.
MISMATCHED_REPLACEMENTS = {
    "5-silky-sortex-white-exporter.html": "blog-ir64-export.html",
    "25-silky-sortex-white-exporter.html": "blog-ir64-export.html",
    "5-silky-sortex-short-grain-exporter.html": "blog-ir64-export.html",
    "25-silky-sortex-short-grain-exporter.html": "blog-ir64-export.html",
    "samba-rice-exporter.html": "blog-india-rice-export-sri-lanka-bangladesh.html",
    "pr-11-rice-exporter.html": "blog-india-rice-export-sri-lanka-bangladesh.html",
    "black-cumin-seeds-nigella-exporter.html": "blog-cumin-jeera-price-outlook-2026.html",
}


def fix_mismatched_links() -> list[str]:
    changed = []
    for slug, correct_article in MISMATCHED_REPLACEMENTS.items():
        path = ROOT / slug
        text = path.read_text(encoding="utf-8", errors="replace")
        import re

        pattern = re.compile(
            r'(Further reading: <a href=")[^"]*("[^>]*>)[^<]*(</a>)'
        )
        match = pattern.search(text)
        if not match:
            print(f"SKIP (pattern not found): {slug}")
            continue
        link_text = ARTICLE_LINK_TEXT.get(correct_article, correct_article)
        replacement = f'{match.group(1)}{correct_article}{match.group(2)}{link_text} &rarr;{match.group(3)}'
        updated = pattern.sub(lambda m: replacement, text, count=1)
        path.write_text(updated, encoding="utf-8", newline="\n")
        changed.append(slug)
    return changed


def add_forward_links() -> list[str]:
    changed = []
    for p in PRODUCTS:
        article = p.get("b")
        if not article or article in UNPUBLISHED_BLOGS:
            continue
        if p["u"] in MISMATCHED_REPLACEMENTS:
            continue  # handled by fix_mismatched_links() instead
        path = ROOT / p["u"]
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if article in text:
            continue  # forward link already present somewhere on the page
        if FORWARD_ANCHOR not in text:
            print(f"SKIP (anchor not found): {p['u']}")
            continue
        link_text = ARTICLE_LINK_TEXT.get(article, article)
        new_li = (
            '\n          <li style="display:flex;align-items:flex-start;gap:14px;margin-top:6px;">'
            '<i class="fa-solid fa-arrow-up-right-from-square" style="color:var(--green);margin-top:3px;flex-shrink:0;"></i>'
            f'<span style="font-size:.95rem;color:#555;line-height:1.65;">Further reading: '
            f'<a href="{article}" style="color:#3d7030;font-weight:700;">{link_text} &rarr;</a></span></li>\n        </ul>'
        )
        updated = text.replace(FORWARD_ANCHOR, FORWARD_ANCHOR.replace("\n        </ul>", "") + new_li, 1)
        path.write_text(updated, encoding="utf-8", newline="\n")
        changed.append(p["u"])
    return changed


def add_back_links() -> list[str]:
    # Group by article first: some articles (e.g. the 2026 commodities roundup)
    # are the designated `b` article for more than one product. Insert ONE
    # combined aside per article listing every related product, rather than
    # one box per product -- avoids stacking near-duplicate boxes (Part T).
    by_article: dict[str, list[dict]] = {}
    for p in PRODUCTS:
        article = p.get("b")
        if article:
            by_article.setdefault(article, []).append(p)

    changed = []
    for article, prods in by_article.items():
        art_path = ROOT / article
        if not art_path.exists():
            continue
        text = art_path.read_text(encoding="utf-8", errors="replace")
        missing = [p for p in prods if p["u"] not in text]
        if not missing:
            continue  # every related product already linked from this article
        anchor = '<div id="footer-placeholder">'
        if text.count(anchor) != 1:
            print(f"SKIP (anchor not found or not unique): {article}")
            continue
        if len(missing) == 1:
            p = missing[0]
            links_html = f'<a href="{p["u"]}" style="color:#2f7138;font-weight:700;">{p["t"]}</a>'
            label = "Related product:"
        else:
            links_html = ", ".join(
                f'<a href="{p["u"]}" style="color:#2f7138;font-weight:700;">{p["t"]}</a>' for p in missing
            )
            label = "Related products:"
        block = (
            f'\n<aside class="jft-related-product" aria-label="Related products" '
            'style="width:min(1120px,calc(100% - 40px));margin:36px auto;padding:20px 22px;'
            'border:1px solid #dbe4de;border-left:4px solid #3d7030;border-radius:8px;'
            'background:#f7faf7;color:#405049;line-height:1.7;">'
            f'<strong style="color:#173d33;">{label}</strong> {links_html}</aside>\n'
        )
        updated = text.replace(anchor, block + anchor, 1)
        art_path.write_text(updated, encoding="utf-8", newline="\n")
        changed.append(article)
    return changed


def main() -> int:
    fixed = fix_mismatched_links()
    forward = add_forward_links()
    back = add_back_links()
    print(f"Fixed {len(fixed)} mismatched further-reading links: {fixed}")
    print(f"Added {len(forward)} new forward (product->article) links: {forward}")
    print(f"Added {len(set(back))} back (article->product) links: {sorted(set(back))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
