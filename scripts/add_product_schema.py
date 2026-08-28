#!/usr/bin/env python3
"""Add Product JSON-LD to the 84 English product pages, sourced only from
each page's own existing title/description/H1/image/category link.

No price, offers, SKU, review, or rating is added: this is a B2B RFQ
business with no fixed public pricing and no genuine customer reviews on
file, and inventing either would violate the site's claims-governance
standard. Idempotent: pages that already carry a Product block are skipped.
"""

from __future__ import annotations

import glob
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ORG_REF = {"@type": "Organization", "name": "JFT Agro Overseas", "@id": "https://jftagro.com/#organization"}

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


def strip_tags(text: str) -> str:
    return html.unescape(re.sub(r"<[^>]+>", "", text)).strip()


def build_category_map() -> dict[str, str]:
    mapping = {}
    for filename in CATEGORY_PAGES:
        source = (ROOT / filename).read_text(encoding="utf-8")
        match = re.search(r"<h1[^>]*>(.*?)</h1>", source, re.S)
        if not match:
            raise SystemExit(f"no H1 found in category page {filename}")
        mapping[filename] = strip_tags(match.group(1))
    return mapping


def find_product_files() -> list[Path]:
    candidates = sorted(set(glob.glob(str(ROOT / "*-exporter.html"))) | set(glob.glob(str(ROOT / "*-supplier.html"))))
    files = [Path(p) for p in candidates if not Path(p).name.startswith("blog-")]
    return files


def extract(source: str, pattern: str, filename: str, label: str) -> str:
    match = re.search(pattern, source, re.S)
    if not match:
        raise SystemExit(f"{filename}: could not find {label}")
    return match.group(1)


def main() -> None:
    category_map = build_category_map()
    files = find_product_files()
    added = 0
    skipped_existing = 0
    for path in files:
        source = path.read_text(encoding="utf-8")
        if '"@type":"Product"' in source:
            skipped_existing += 1
            continue

        title = strip_tags(extract(source, r"<title>(.*?)</title>", path.name, "<title>"))
        description = html.unescape(
            extract(source, r'<meta name="description"[^>]*content="(.*?)"', path.name, "meta description")
        )
        canonical = extract(source, r'rel="canonical" href="(.*?)"', path.name, "canonical link")
        h1 = strip_tags(extract(source, r"<h1[^>]*>(.*?)</h1>", path.name, "<h1>"))
        og_image = html.unescape(extract(source, r'og:image" content="(.*?)"', path.name, "og:image"))

        category_match = re.search(r'href="([a-z0-9-]+-exporter-india\.html)"', source)
        if not category_match or category_match.group(1) not in category_map:
            raise SystemExit(f"{path.name}: could not resolve category page link")
        category = category_map[category_match.group(1)]

        product = {
            "@context": "https://schema.org",
            "@type": "Product",
            "name": h1 or title,
            "description": description,
            "image": og_image,
            "url": canonical,
            "brand": ORG_REF,
            "category": category,
        }
        script_tag = f'<script type="application/ld+json">{json.dumps(product, ensure_ascii=False, separators=(",", ":"))}</script>\n'

        if "</head>" not in source:
            raise SystemExit(f"{path.name}: no </head> found")
        updated = source.replace("</head>", script_tag + "</head>", 1)
        path.write_text(updated, encoding="utf-8")
        added += 1

    print(f"Added Product schema: {added}. Skipped (already present): {skipped_existing}. Total scanned: {len(files)}.")


if __name__ == "__main__":
    main()
