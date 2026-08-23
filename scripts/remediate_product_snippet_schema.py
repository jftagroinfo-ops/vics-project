#!/usr/bin/env python3
"""Replace ineligible quote-only Product rich-result markup.

JFT product pages use contract/RFQ pricing and do not publish verified customer
reviews. Google requires Product snippet markup to contain a truthful Offer,
Review, or AggregateRating. This migration preserves page/entity context using
WebPage + Thing without inventing prices or ratings.
"""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
JSON_LD = re.compile(
    r'(<script\s+type="application/ld\+json">)(.*?)(</script>)',
    re.IGNORECASE | re.DOTALL,
)


def replacement_schema(schema: dict, canonical: str, language: str) -> dict:
    name = str(schema.get("name", "")).strip()
    description = str(schema.get("description", "")).strip()
    image = schema.get("image")
    webpage = {
        "@context": "https://schema.org",
        "@type": "WebPage",
        "@id": f"{canonical}#webpage",
        "url": canonical,
        "name": f"{name} Export from India | JFT Agro Overseas",
        "description": description,
        "inLanguage": language,
        "isPartOf": {
            "@type": "WebSite",
            "@id": "https://jftagro.com/#website",
            "url": "https://jftagro.com/",
            "name": "JFT Agro Overseas",
        },
        "publisher": {
            "@type": "Organization",
            "@id": "https://jftagro.com/#organization",
            "name": "JFT Agro Overseas",
            "url": "https://jftagro.com/",
        },
        "about": {
            "@type": "Thing",
            "name": name,
            "description": description,
        },
    }
    if image:
        webpage["primaryImageOfPage"] = {
            "@type": "ImageObject",
            "url": image,
        }
        webpage["about"]["image"] = image
    return webpage


def migrate(path: Path, canonical: str, language: str) -> bool:
    original = path.read_text(encoding="utf-8")
    replaced = False

    def transform(match: re.Match[str]) -> str:
        nonlocal replaced
        try:
            schema = json.loads(match.group(2))
        except json.JSONDecodeError:
            return match.group(0)
        if replaced or not isinstance(schema, dict) or schema.get("@type") != "Product":
            return match.group(0)
        safe = replacement_schema(schema, canonical, language)
        replaced = True
        payload = json.dumps(safe, ensure_ascii=False, separators=(",", ":"))
        return f"{match.group(1)}{payload}{match.group(3)}"

    updated = JSON_LD.sub(transform, original)
    if not replaced:
        raise RuntimeError(f"No root Product JSON-LD found in {path.relative_to(ROOT)}")
    if updated != original:
        path.write_text(updated, encoding="utf-8", newline="")
        return True
    return False


def main() -> int:
    changed = 0
    checked = 0
    for product in PRODUCTS:
        slug = product["u"]
        for locale in ("",) + LOCALES:
            path = ROOT / locale / slug if locale else ROOT / slug
            if not path.is_file():
                raise FileNotFoundError(path)
            relative = f"{locale}/{slug}" if locale else slug
            canonical = f"https://jftagro.com/{relative}"
            checked += 1
            if migrate(path, canonical, locale or "en"):
                changed += 1
    print(f"Migrated {changed} of {checked} quote-only product pages to WebPage schema.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
