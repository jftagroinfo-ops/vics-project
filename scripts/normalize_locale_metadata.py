#!/usr/bin/env python3
"""Keep translated search snippets concise without changing visible copy."""

from __future__ import annotations

from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")


def shorten(value: str, limit: int) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    candidate = value[: limit - 1].rstrip()
    if " " in candidate and len(candidate.rsplit(" ", 1)[0]) >= limit * 0.72:
        candidate = candidate.rsplit(" ", 1)[0]
    return candidate.rstrip(" ,;:-|–—") + "…"


def main() -> int:
    changed = 0
    for locale in LOCALES:
        for path in (ROOT / locale).glob("*.html"):
            soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html5lib")
            dirty = False
            if soup.title and soup.title.string:
                compact = shorten(str(soup.title.string), 65)
                if compact != str(soup.title.string):
                    soup.title.string.replace_with(compact)
                    dirty = True
            for meta in soup.find_all("meta"):
                key = (meta.get("name") or meta.get("property") or "").lower()
                limit = 65 if key in {"og:title", "twitter:title"} else 170 if key in {"description", "og:description", "twitter:description"} else None
                if not limit or not meta.get("content"):
                    continue
                compact = shorten(meta["content"], limit)
                if compact != meta["content"]:
                    meta["content"] = compact
                    dirty = True
            if dirty:
                path.write_text(str(soup), encoding="utf-8", newline="\n")
                changed += 1
    print(f"Normalized translated search metadata on {changed} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
