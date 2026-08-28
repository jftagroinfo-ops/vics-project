#!/usr/bin/env python3
"""Fix P29-4: the contact-page trust-strip certificate badges (FSSAI, APEDA,
Star Export House) constrain only `height` in CSS, leaving `width` unset.
Correct, non-distorted scaling then depends entirely on the browser's
implicit aspect-ratio-from-attributes behavior rather than an explicit
declaration - a fragile pattern. Add `width:auto` explicitly so scaling is
guaranteed proportional regardless of browser/engine behavior.

Exact-match-guarded: only touches files containing the precise, known-buggy
rule; reports skips rather than guessing. Idempotent.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OLD = ".trust-strip img{height:26px;filter:brightness(0) invert(1);opacity:.55;transition:.3s}"
NEW = ".trust-strip img{height:26px;width:auto;filter:brightness(0) invert(1);opacity:.55;transition:.3s}"

FILES = [
    "contact.html",
    "ar/contact.html",
    "es/contact.html",
    "fr/contact.html",
    "id/contact.html",
    "ms/contact.html",
    "pt/contact.html",
    "ru/contact.html",
    "si/contact.html",
    "th/contact.html",
    "vi/contact.html",
]


def main() -> None:
    fixed = 0
    skipped = 0
    for relative in FILES:
        path = ROOT / relative
        source = path.read_text(encoding="utf-8")
        count = source.count(OLD)
        if count == 0:
            if NEW in source:
                skipped += 1
                continue
            raise SystemExit(f"{relative}: expected pattern not found, aborting")
        if count != 1:
            raise SystemExit(f"{relative}: expected exactly 1 match, found {count}, aborting")
        path.write_text(source.replace(OLD, NEW, 1), encoding="utf-8")
        fixed += 1
    print(f"Fixed: {fixed}. Already fixed (skipped): {skipped}. Total files: {len(FILES)}.")


if __name__ == "__main__":
    main()
