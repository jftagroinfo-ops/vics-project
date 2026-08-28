# -*- coding: utf-8 -*-
"""Phase 15 finding: buyer-security.html and export-documentation.html (English
+ all 10 locale copies = 22 files) each carry a redundant, direct
`<script src="jft-conversion.js">` tag IN ADDITION TO fetching and injecting
header.html, which itself already contains the same script tag and delivers
it correctly on every other page of the site (verified in Phase 14 for all
37 articles). The result on these 22 pages specifically: jft-conversion.js's
top-level IIFE runs twice, registering two `click` listeners on `document`
and two `focusin` listeners per form - so every click-based analytics event
(WhatsApp/phone/email/outbound/conversion-link clicks) and the `form_start`/
`rfq_start` intent event fire twice, and the GA4 gtag.js library plus its
`config` call load twice.

Fix: remove only the redundant direct script tag. header.html's own copy
(already proven correct everywhere else) remains the sole delivery
mechanism. This script is exact-match guarded - it edits nothing if the
expected string is not found exactly once, so it fails safe rather than
silently under- or over-applying."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ["ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"]
PAGES = ["buyer-security.html", "export-documentation.html"]

EN_TAG = '<script src="jft-conversion.js" defer></script>'
LOCALE_TAG = '<script defer="" src="../jft-conversion.js"></script>'


def patch(path: Path, tag: str) -> str:
    text = path.read_text(encoding="utf-8")
    count = text.count(tag)
    if count != 1:
        return f"SKIPPED (expected 1 occurrence, found {count})"
    text = text.replace(tag, "", 1)
    path.write_text(text, encoding="utf-8", newline="\n")
    return "patched"


def main() -> None:
    results = []
    for page in PAGES:
        en_path = ROOT / page
        if en_path.exists():
            results.append((str(en_path.relative_to(ROOT)), patch(en_path, EN_TAG)))
        for locale in LOCALES:
            loc_path = ROOT / locale / page
            if loc_path.exists():
                results.append((str(loc_path.relative_to(ROOT)), patch(loc_path, LOCALE_TAG)))
    for path, result in results:
        print(f"{path}: {result}")
    print(f"\nTotal files processed: {len(results)}")
    print(f"Patched: {sum(1 for _, r in results if r == 'patched')}")
    print(f"Skipped: {sum(1 for _, r in results if r != 'patched')}")


if __name__ == "__main__":
    main()
