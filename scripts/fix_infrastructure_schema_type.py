#!/usr/bin/env python3
"""Fix the ManufacturingBusiness schema governance bug on locale infrastructure pages.

Root cause (see reports/phase10-commodity-architecture-2026-08-27.md): the English
root infrastructure.html describes the company via `"@type":"Organization"` with
`"@id":"https://jftagro.com/#organization"` (the same Organization entity used
site-wide), matching Phase 7's established claim-governance decision that JFT
Agro Overseas is an exporter/coordinator, not a manufacturer. Every one of the
10 locale copies instead used `"@type":"ManufacturingBusiness"` with no `@id`,
a distinct, uncorrected claim that predates that governance decision and was
never re-synced -- the same "translated once, English source changed later,
nothing re-synced" pattern already found and fixed in Phases 6-8.

This script performs only the narrow, confirmed correction: the @type value
and adding the same @id used on the English page, so the schema references
the same Organization entity everywhere. It does not touch the surrounding
capability/address claims already present on each locale page, which are a
separate, broader content-parity question outside this phase's scope (see the
report's "Findings not fixed" section).
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")

STALE = '"@type":"ManufacturingBusiness","name":"JFT Agro Overseas"'
FIXED = '"@type":"Organization","name":"JFT Agro Overseas"'
ID_INSERT_BEFORE = '}'  # appended just before the closing brace of the schema object


def main() -> int:
    changed = []
    for locale in LOCALES:
        path = ROOT / locale / "infrastructure.html"
        text = path.read_text(encoding="utf-8", errors="replace")
        if STALE not in text:
            raise SystemExit(f"{path}: expected pattern not found")
        if text.count(STALE) != 1:
            raise SystemExit(f"{path}: expected exactly 1 occurrence, found {text.count(STALE)}")
        updated = text.replace(STALE, FIXED)

        # Add the same @id the English page uses, right after hasOfferCatalog's
        # closing brace, so this locale's Organization schema refers to the
        # same entity as every other page's Organization/WebSite schema.
        marker = '"hasOfferCatalog"'
        start = updated.find(marker)
        if start == -1:
            raise SystemExit(f"{path}: hasOfferCatalog block not found")
        # find the end of this whole ld+json script's JSON object by matching
        # the closing of the <script> tag, then insert @id just before the
        # final closing brace of the JSON object (right before </script>).
        script_close = updated.find("</script>", start)
        if script_close == -1:
            raise SystemExit(f"{path}: </script> not found after hasOfferCatalog")
        insert_pos = updated.rfind("}", start, script_close)
        if insert_pos == -1:
            raise SystemExit(f"{path}: closing brace not found")
        updated = (
            updated[:insert_pos]
            + ',"@id":"https://jftagro.com/#organization"'
            + updated[insert_pos:]
        )

        path.write_text(updated, encoding="utf-8", newline="\n")
        changed.append(str(path.relative_to(ROOT)))

    print(f"Fixed {len(changed)} files.")
    for f in changed:
        print(" ", f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
