#!/usr/bin/env python3
"""Synchronize self-canonicals and hreflang tags for existing page variants."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
BASE_URL = "https://jftagro.com"
LANGS = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
EXCLUDED = {
    "404.html",
    "cookie-consent-snippet.html",
    "footer.html",
    "header.html",
    "inner-page-hero-snippet.html",
    "product-page-template.html",
    "seo-universal-head-snippet.html",
    "thank-you.html",
}
ALTERNATE_RE = re.compile(r"\s*<link\s+rel=[\"']alternate[\"'][^>]*>", re.I)
CANONICAL_RE = re.compile(r"<link\s+rel=[\"']canonical[\"'][^>]*>", re.I)


def is_indexable(path: Path) -> bool:
    if path.name in EXCLUDED or path.name.startswith("yandex_"):
        return False
    text = path.read_text(encoding="utf-8")
    return bool(re.search(r"<html\b", text, re.I)) and not bool(
        re.search(r'<meta\s+name=["\']robots["\'][^>]*\bnoindex\b', text, re.I)
    )


def locale(path: Path) -> str:
    return path.parent.name if path.parent.name in LANGS else "en"


def public_url(path: Path) -> str:
    lc = locale(path)
    if path.name == "index.html":
        return f"{BASE_URL}/{lc}/" if lc != "en" else f"{BASE_URL}/"
    return f"{BASE_URL}/{lc}/{path.name}" if lc != "en" else f"{BASE_URL}/{path.name}"


def main() -> None:
    pages = [path for path in ROOT.rglob("*.html") if is_indexable(path)]
    by_name: dict[str, list[Path]] = {}
    for path in pages:
        by_name.setdefault(path.name, []).append(path)

    updated = 0
    for path in pages:
        text = path.read_text(encoding="utf-8")
        head_end = re.search(r"</head>", text, re.I)
        if not head_end:
            continue
        head, tail = text[: head_end.start()], text[head_end.start() :]
        head = ALTERNATE_RE.sub("", head)

        own_url = public_url(path)
        canonical = f'<link rel="canonical" href="{own_url}">'
        if CANONICAL_RE.search(head):
            head = CANONICAL_RE.sub(canonical, head, count=1)
        else:
            head += "\n  " + canonical

        variants = sorted(by_name[path.name], key=lambda item: (locale(item) != "en", locale(item)))
        links = [
            f'  <link rel="alternate" hreflang="{locale(item)}" href="{public_url(item)}">'
            for item in variants
        ]
        english = next((item for item in variants if locale(item) == "en"), None)
        if english:
            links.append(f'  <link rel="alternate" hreflang="x-default" href="{public_url(english)}">')
        new_text = head.rstrip() + "\n" + "\n".join(links) + "\n" + tail
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            updated += 1

    print(f"Updated canonical/hreflang metadata on {updated} indexable pages.")


if __name__ == "__main__":
    main()
