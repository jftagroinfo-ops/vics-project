# -*- coding: utf-8 -*-
"""Phase 11 Gap 1 fix: carry product identity from product pages into the RFQ
and sample-request forms, using the URL-param convention that contact.html's
own inline script (and quote-calculator.js / the article buyer-path) already
implement. Product pages currently link to contact.html#inquiry-form and
sample-request.html with no query string at all, so a buyer who has already
picked a specific product loses that context the moment they click through.

This script only edits the CTA href attributes already present on each
product page - it does not add new CTAs, new fields, or new pages."""
import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ["ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"]

CONTACT_OLD = 'href="contact.html#inquiry-form"'
SAMPLE_OLD = 'href="sample-request.html"'


def patch_file(path: Path, product_name: str) -> tuple[int, int]:
    text = path.read_text(encoding="utf-8")
    encoded = urllib.parse.quote(product_name)
    contact_new = f'href="contact.html?product={encoded}#inquiry-form"'
    sample_new = f'href="sample-request.html?product={encoded}"'
    contact_count = text.count(CONTACT_OLD)
    sample_count = text.count(SAMPLE_OLD)
    if contact_count:
        text = text.replace(CONTACT_OLD, contact_new)
    if sample_count:
        text = text.replace(SAMPLE_OLD, sample_new)
    if contact_count or sample_count:
        path.write_text(text, encoding="utf-8", newline="\n")
    return contact_count, sample_count


def main() -> None:
    products = json.loads((ROOT / "data" / "products.json").read_text(encoding="utf-8"))
    total_contact = 0
    total_sample = 0
    total_files = 0
    for product in products:
        slug = product["u"]
        name = product["t"]
        en_path = ROOT / slug
        if en_path.exists():
            c, s = patch_file(en_path, name)
            total_contact += c
            total_sample += s
            total_files += 1 if (c or s) else 0
        for locale in LOCALES:
            locale_path = ROOT / locale / slug
            if locale_path.exists():
                c, s = patch_file(locale_path, name)
                total_contact += c
                total_sample += s
                total_files += 1 if (c or s) else 0
    print(f"Patched {total_files} files: {total_contact} contact.html CTA(s), {total_sample} sample-request.html CTA(s)")


if __name__ == "__main__":
    main()
