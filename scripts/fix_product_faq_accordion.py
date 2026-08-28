#!/usr/bin/env python3
"""Fix the inverted product-FAQ accordion open/close logic on locale pages.

Root cause (see reports/product-faq-accordion-fix-2026-08-27.md): every
localized product page's FAQ accordion carries two click listeners on each
`.faq-q` question -- an inline `onclick` attribute that toggles the `.open`
CSS class on the answer panel (and updates `aria-expanded`), and a second
listener attached by a trailing `<script>` block that sets `max-height` based
on whether the `.open` class is present. Because the inline handler always
fires first, by the time the second listener reads `.open` it already
reflects the *post-toggle* state -- so the height-setting branches must map
"class is open" -> "show the panel". On the English root pages they do
(`open ? scrollHeight : '0'`). On every one of the 830 locale pages the
branches are reversed (`if(open){height='0'}else{height=scrollHeight}`),
so the panel is set to height 0 exactly when it should be showing, and to
full height exactly when it should be hidden -- confirmed identical,
byte-for-byte, across all 830 files via a real-browser reproduction.

This script performs the single-line correction (swap the two branch bodies)
identically to how the English root pages already do it -- no markup change,
no CSS change, no content/translation change.
"""

from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")

STALE_SCRIPT = (
    "document.querySelectorAll('.faq-q').forEach(function(q){q.addEventListener('click',"
    "function(){var a=this.nextElementSibling;"
    "if(a.classList.contains('open')){a.style.maxHeight='0';}"
    "else{a.style.maxHeight=a.scrollHeight+'px';}});});"
)
FIXED_SCRIPT = (
    "document.querySelectorAll('.faq-q').forEach(function(q){q.addEventListener('click',"
    "function(){var a=this.nextElementSibling;"
    "if(a.classList.contains('open')){a.style.maxHeight=a.scrollHeight+'px';}"
    "else{a.style.maxHeight='0';}});});"
)


def main() -> int:
    changed: list[str] = []
    for locale in LOCALES:
        folder = ROOT / locale
        for path in sorted(folder.glob("*-exporter.html")):
            text = path.read_text(encoding="utf-8", errors="replace")
            if STALE_SCRIPT not in text:
                continue
            if text.count(STALE_SCRIPT) != 1:
                raise SystemExit(f"{path}: expected exactly 1 occurrence, found {text.count(STALE_SCRIPT)}")
            updated = text.replace(STALE_SCRIPT, FIXED_SCRIPT)
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed.append(str(path.relative_to(ROOT)))

    print(f"Fixed {len(changed)} files.")
    for f in changed[:5]:
        print(" ", f)
    if len(changed) > 5:
        print(f"  ... and {len(changed) - 5} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
