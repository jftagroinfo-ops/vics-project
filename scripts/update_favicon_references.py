#!/usr/bin/env python3
"""Install the JFT Agro favicon set on every public source page."""

from __future__ import annotations

from pathlib import Path
import re


ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
ICON_RE = re.compile(
    r"[ \t]*<link\b(?=[^>]*\brel=[\"'](?:shortcut\s+)?icon[\"'])[^>]*>[ \t]*(?:\r?\n)?",
    re.I,
)
APPLE_RE = re.compile(
    r"[ \t]*<link\b(?=[^>]*\brel=[\"']apple-touch-icon[\"'])[^>]*>[ \t]*(?:\r?\n)?",
    re.I,
)
ICON_BLOCK = """  <link rel=\"icon\" href=\"/favicon.ico\" sizes=\"any\">
  <link rel=\"icon\" type=\"image/png\" sizes=\"32x32\" href=\"/images/favicon-jft-agro-32.png\">
  <link rel=\"icon\" type=\"image/png\" sizes=\"48x48\" href=\"/images/favicon-jft-agro-48.png\">
  <link rel=\"apple-touch-icon\" sizes=\"180x180\" href=\"/images/apple-touch-icon-jft-agro.png\">"""


def public_pages() -> list[Path]:
    pages = list(ROOT.glob("*.html"))
    for locale in LOCALES:
        pages.extend((ROOT / locale).glob("*.html"))
    return pages


def main() -> int:
    updated = 0
    for path in public_pages():
        original = path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"<html\b", original, re.I) or not re.search(r"</head>", original, re.I):
            continue
        text = ICON_RE.sub("", original)
        text = APPLE_RE.sub("", text)
        text = re.sub(r"</head>", ICON_BLOCK + "\n</head>", text, count=1, flags=re.I)
        if text != original:
            path.write_text(text, encoding="utf-8", newline="\n")
            updated += 1
    print(f"Updated favicon metadata on {updated} public pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
