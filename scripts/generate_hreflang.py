#!/usr/bin/env python3
"""Synchronize self-canonicals and hreflang tags for existing page variants."""

from __future__ import annotations

import re
import time
from pathlib import Path

from bs4 import BeautifulSoup


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
ALTERNATE_RE = re.compile(r"\s*<link\b(?=[^>]*\brel=[\"']alternate[\"'])[^>]*>", re.I)
CANONICAL_RE = re.compile(r"<link\b(?=[^>]*\brel=[\"']canonical[\"'])[^>]*>", re.I)
OG_URL_RE = re.compile(r'<meta\b(?=[^>]*\bproperty=["\']og:url["\'])[^>]*>', re.I)
FALLBACK_MARKER = '<meta name="jft-localization" content="english-fallback">'
ROBOTS_RE = re.compile(r'<meta\b(?=[^>]*\bname=["\']robots["\'])[^>]*>', re.I)


def visible_english_tokens(text: str) -> set[str]:
    soup = BeautifulSoup(text, "html.parser")
    for element in soup(["head", "script", "style", "noscript"]):
        element.decompose()
    for selector in ("#header-placeholder", "#footer-placeholder"):
        for element in soup.select(selector):
            element.decompose()
    return set(re.findall(r"[a-z]{3,}", soup.get_text(" ", strip=True).lower()))


def is_english_fallback(path: Path, text: str, english_tokens: dict[str, set[str]]) -> bool:
    if locale(path) == "en" or path.name not in english_tokens:
        return False
    localized_tokens = visible_english_tokens(text)
    source_tokens = english_tokens[path.name]
    if len(localized_tokens) < 20 or len(source_tokens) < 20:
        return False
    similarity = len(localized_tokens & source_tokens) / len(localized_tokens | source_tokens)
    return similarity >= 0.90


def synchronize_localization_fallbacks() -> tuple[int, int]:
    english_tokens = {
        path.name: visible_english_tokens(path.read_text(encoding="utf-8"))
        for path in ROOT.glob("*.html")
        if path.name not in EXCLUDED and not path.name.startswith("yandex_")
    }
    marked = restored = 0
    for language in LANGS:
        for path in (ROOT / language).glob("*.html"):
            original = path.read_text(encoding="utf-8")
            text = original
            fallback = is_english_fallback(path, text, english_tokens)
            marked_before = FALLBACK_MARKER in text
            if fallback:
                english_url = public_url(ROOT / path.name)
                text = ALTERNATE_RE.sub("", text)
                text = re.sub(r'<html\s+lang=["\'][^"\']+["\'](?:\s+dir=["\']rtl["\'])?', '<html lang="en"', text, count=1, flags=re.I)
                if CANONICAL_RE.search(text):
                    text = CANONICAL_RE.sub(f'<link rel="canonical" href="{english_url}">', text, count=1)
                if OG_URL_RE.search(text):
                    text = OG_URL_RE.sub(f'<meta property="og:url" content="{english_url}">', text, count=1)
                if ROBOTS_RE.search(text):
                    text = ROBOTS_RE.sub('<meta name="robots" content="noindex,follow">', text, count=1)
                else:
                    text = text.replace("<head>", '<head>\n  <meta name="robots" content="noindex,follow">', 1)
                if not marked_before:
                    text = text.replace("<head>", f"<head>\n  {FALLBACK_MARKER}", 1)
                    marked += 1
            elif marked_before:
                text = text.replace(f"\n  {FALLBACK_MARKER}", "", 1).replace(FALLBACK_MARKER, "", 1)
                text = ROBOTS_RE.sub("", text, count=1)
                direction = ' dir="rtl"' if language == "ar" else ""
                text = re.sub(r'<html\s+lang=["\'][^"\']+["\'](?:\s+dir=["\']rtl["\'])?', f'<html lang="{language}"{direction}', text, count=1, flags=re.I)
                localized_url = public_url(path)
                if OG_URL_RE.search(text):
                    text = OG_URL_RE.sub(f'<meta property="og:url" content="{localized_url}">', text, count=1)
                restored += 1
            if text != original:
                for attempt in range(3):
                    try:
                        path.write_text(text, encoding="utf-8")
                        break
                    except OSError:
                        if attempt == 2:
                            raise
                        time.sleep(0.1 * (attempt + 1))
    return marked, restored


def is_indexable(path: Path) -> bool:
    if path.name in EXCLUDED or path.name.startswith("yandex_"):
        return False
    text = path.read_text(encoding="utf-8")
    if not re.search(r"<html\b", text, re.I):
        return False
    soup = BeautifulSoup(text, "html.parser")
    robots = soup.find("meta", attrs={"name": lambda value: value and value.lower() == "robots"})
    return not bool(robots and "noindex" in robots.get("content", "").lower())


def locale(path: Path) -> str:
    return path.parent.name if path.parent.name in LANGS else "en"


def public_url(path: Path) -> str:
    lc = locale(path)
    if path.name == "index.html":
        return f"{BASE_URL}/{lc}/" if lc != "en" else f"{BASE_URL}/"
    return f"{BASE_URL}/{lc}/{path.name}" if lc != "en" else f"{BASE_URL}/{path.name}"


def main() -> None:
    marked, restored = synchronize_localization_fallbacks()
    # Keep noindex and redirect documents tidy too. They are not part of the
    # hreflang graph, but every renderable page should still have one canonical.
    for path in ROOT.rglob("*.html"):
        if path.name in EXCLUDED or path.name.startswith("yandex_"):
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if not re.search(r"<html\b", text, re.I):
            continue
        existing = CANONICAL_RE.findall(text)
        if len(existing) == 1:
            continue
        canonical = existing[0] if existing else f'<link rel="canonical" href="{public_url(path)}">'
        text = CANONICAL_RE.sub("", text)
        text = re.sub(r"</head>", f"  {canonical}\n</head>", text, count=1, flags=re.I)
        path.write_text(text, encoding="utf-8")
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
        # Remove every historical variant before inserting one canonical. This
        # remains stable even when an HTML serializer reorders link attributes.
        head = CANONICAL_RE.sub("", head)
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

    print(
        f"Updated canonical/hreflang metadata on {updated} indexable pages; "
        f"marked {marked} English fallback pages and restored {restored} translated pages."
    )


if __name__ == "__main__":
    main()
