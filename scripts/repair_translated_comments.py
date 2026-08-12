#!/usr/bin/env python3
"""Remove source comments that an earlier serializer exposed as translated text."""

from __future__ import annotations

import json
from pathlib import Path

from bs4 import BeautifulSoup, Comment


ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
CACHE = json.loads((ROOT / "data" / "localized-copy-cache.json").read_text(encoding="utf-8"))


def main() -> int:
    source_comments: set[str] = set()
    translated_names = {path.name for path in (ROOT / "ar").glob("*.html") if path.name in CACHE.get("ar", {})}
    # Use every English source: comments are harmless to scan and exact matching keeps visible copy intact.
    for path in ROOT.glob("*.html"):
        soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
        source_comments.update(" ".join(str(node).split()) for node in soup.find_all(string=lambda value: isinstance(value, Comment)))

    changed = removed = 0
    for language in LOCALES:
        translated_comments = {CACHE.get(language, {}).get(value) for value in source_comments}
        translated_comments.discard(None)
        for path in (ROOT / language).glob("*.html"):
            text = path.read_text(encoding="utf-8", errors="replace")
            soup = BeautifulSoup(text, "html.parser")
            count = 0
            for node in list(soup.find_all(string=True)):
                if isinstance(node, Comment):
                    continue
                normalized = " ".join(str(node).split())
                if normalized in translated_comments:
                    node.extract()
                    count += 1
            if count:
                rendered = str(soup)
                if not rendered.lstrip().lower().startswith("<!doctype html>"):
                    rendered = "<!DOCTYPE html>\n" + rendered[rendered.lower().find("<html"):]
                path.write_text(rendered, encoding="utf-8", newline="\n")
                changed += 1
                removed += count
    print(f"Removed {removed} exposed translated comments from {changed} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
