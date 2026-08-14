#!/usr/bin/env python3
"""Apply deterministic public-copy safeguards for claims awaiting evidence."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

REPLACEMENTS = (
    (re.compile(r"ISO\s*&\s*APEDA certified Star Export House", re.I), "registration and certification documents available for buyer verification"),
    (re.compile(r"ISO 9001:2015 certified, APEDA registered, and a recogn(?:is|iz)ed Star Export House", re.I), "current registration and certification documents available for buyer verification"),
    (re.compile(r"ISO 9001:2015, APEDA registered, Star Export House", re.I), "registration and certification copies available for buyer verification"),
    (re.compile(r"ISO 9001:2015 certified", re.I), "ISO 9001:2015 documentation available for verification"),
    (re.compile(r"APEDA registered(?: exporter)?", re.I), "APEDA documentation available for verification"),
    (re.compile(r"HACCP certified", re.I), "HACCP documentation available for verification"),
    (re.compile(r"Government Recognized Star Export House", re.I), "Star Export House documentation available for verification"),
    (re.compile(r"Government Recognised Star Export House", re.I), "Star Export House documentation available for verification"),
    (re.compile(r"25\+ countries", re.I), "international markets"),
    (re.compile(r"25\+ global destinations", re.I), "international destinations"),
    (re.compile(r"In-house milling and processing\s*[—-]\s*250\s*MT/day capacity", re.I), "Milling and processing capability — facility evidence available during buyer due diligence"),
    (re.compile(r"250\s*MT\s*/\s*Day Milling", re.I), "Facility Capacity Verified on Request"),
    (re.compile(r"250\s*MT\s*/\s*Day", re.I), "Capacity on Request"),
    (re.compile(r"250\s*MT/day", re.I), "documented facility"),
    (re.compile(r"In-house NABL Lab", re.I), "Accredited Testing by Contract"),
    (re.compile(r"NABL Certified Lab", re.I), "Accredited Laboratory Testing"),
    (re.compile(r"NABL Lab Tested", re.I), "Accredited Lab Testing Available"),
    (re.compile(r"NABL-certified lab", re.I), "testing through an appropriately accredited laboratory when contracted"),
)

OLD_SCHEMA = re.compile(
    r'\n  <script type="text/javascript">\s*\(function injectProductSchema\(\) \{.*?\n  </script>',
    re.S,
)
NEW_SCHEMA = r'''
  <script type="text/javascript">
    (function injectProductSchema() {
      const products = Array.isArray(window.JFT_PRODUCT_DATA) ? window.JFT_PRODUCT_DATA : [];
      const schema = {
        "@context": "https://schema.org",
        "@type": "ItemList",
        "name": "JFT Agro Overseas Export Product Catalogue",
        "url": "https://jftagro.com/products.html",
        "numberOfItems": products.length,
        "itemListElement": products.map(function (product, index) {
          const properties = (product.s || []).map(function (row) {
            return { "@type": "PropertyValue", "name": row[0], "value": row[1] };
          });
          properties.push({ "@type": "PropertyValue", "name": "Indicative container loading", "value": product.l });
          properties.push({ "@type": "PropertyValue", "name": "Packing options", "value": product.p });
          return {
            "@type": "ListItem",
            "position": index + 1,
            "item": {
              "@type": "Product",
              "@id": "https://jftagro.com/" + product.u + "#product",
              "url": "https://jftagro.com/" + product.u,
              "name": product.t,
              "description": "Export specification, packing and shipment planning for " + product.t + ". Final quality parameters and availability are confirmed in writing.",
              "image": "https://jftagro.com/" + encodeURI(product.i),
              "category": product.c,
              "countryOfOrigin": { "@type": "Country", "name": "India" },
              "brand": { "@type": "Brand", "name": "JFT Agro Overseas" },
              "additionalProperty": properties
            }
          };
        })
      };
      const script = document.createElement('script');
      script.type = 'application/ld+json';
      script.textContent = JSON.stringify(schema);
      document.head.appendChild(script);
    })();
  </script>'''


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or "reports" in path.parts:
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        text = original
        for pattern, replacement in REPLACEMENTS:
            text = pattern.sub(replacement, text)
        if path == ROOT / "products.html":
            text, count = OLD_SCHEMA.subn("\n" + NEW_SCHEMA, text, count=1)
            if count != 1 and "fob_usd_min" in text:
                raise RuntimeError("Stale product schema could not be replaced")
        if text != original:
            path.write_text(text, encoding="utf-8")
            changed += 1
    print(f"Evidence-safe copy applied to {changed} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
