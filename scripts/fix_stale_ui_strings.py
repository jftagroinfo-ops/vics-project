#!/usr/bin/env python3
"""Replace orphaned English UI strings in locale HTML with the governed
translation of the current English source string that replaced them.

This targets the class of defect where a page's English source text is
edited (e.g. a button relabeled), the governed cache is updated with
translations for the *new* string, but already-localized HTML pages keep
shipping the *old* string verbatim because nothing regenerates them. The
fix is driven entirely by data/localized-copy-cache.json -- never a
hand-typed per-locale translation -- so it fails loudly if the cache does
not yet cover a locale rather than silently leaving English behind.

Each entry maps the exact stale HTML fragment (as currently shipped in
locale pages) to the current governed English source string whose cached
translation should replace the stale English text inside that fragment.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CACHE_PATH = ROOT / "data" / "localized-copy-cache.json"
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")

STALE_FRAGMENTS = {
    '<i class="fa-brands fa-whatsapp"></i> Order on WhatsApp</a>': {
        "stale_text": "Order on WhatsApp",
        "current_source": "WhatsApp Inquiry",
    },
}


def main() -> int:
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8"))

    for fragment, spec in STALE_FRAGMENTS.items():
        current_source = spec["current_source"]
        missing_locales = [loc for loc in LOCALES if current_source not in cache.get(loc, {})]
        if missing_locales:
            raise SystemExit(
                f"Refusing to fix: {current_source!r} missing from governed cache for {missing_locales}"
            )

    changed_files: list[str] = []
    for locale in LOCALES:
        folder = ROOT / locale
        for path in sorted(folder.glob("*.html")):
            text = path.read_text(encoding="utf-8", errors="replace")
            updated = text
            for fragment, spec in STALE_FRAGMENTS.items():
                if fragment not in updated:
                    continue
                translation = cache[locale][spec["current_source"]]
                new_fragment = fragment.replace(spec["stale_text"], translation)
                updated = updated.replace(fragment, new_fragment)
            if updated != text:
                path.write_text(updated, encoding="utf-8", newline="\n")
                changed_files.append(str(path.relative_to(ROOT)))

    print(f"Fixed {len(changed_files)} files.")
    for f in changed_files[:5]:
        print(" ", f)
    if len(changed_files) > 5:
        print(f"  ... and {len(changed_files) - 5} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
