#!/usr/bin/env python3
"""Validate published blog navigation, images, and legacy redirects."""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup
from PIL import Image

from apply_site_audit_fixes import BLOG_REPLACEMENTS, LANGS, ROOT


BASMATI_TITLE = "1121 vs 1509 Basmati Rice: Which Variety Should You Import in 2026?"


def local_path(page: Path, value: str) -> Path:
    path = unquote(urlsplit(value).path)
    return ROOT / path.lstrip("/") if path.startswith("/") else page.parent / path


def main() -> None:
    errors: list[str] = []
    indexes = [ROOT / "blog.html", *(ROOT / language / "blog.html" for language in sorted(LANGS))]
    card_count = 0
    for index in indexes:
        soup = BeautifulSoup(index.read_text(encoding="utf-8"), "html.parser")
        for card in soup.select("a.article-card[href]"):
            card_count += 1
            destination = local_path(index, card["href"])
            if not destination.is_file():
                errors.append(f"Missing card destination: {index.relative_to(ROOT)} -> {card['href']}")
                continue
            destination_soup = BeautifulSoup(destination.read_text(encoding="utf-8"), "html.parser")
            heading = destination_soup.find("h1")
            if heading and heading.get_text(" ", strip=True) == BASMATI_TITLE and destination.name != "blog-basmati-export-guide.html":
                errors.append(f"Wrong Basmati content: {destination.relative_to(ROOT)}")
            image = card.select_one(".card-img img[src]")
            if not image:
                errors.append(f"Missing card image: {index.relative_to(ROOT)} -> {card['href']}")
                continue
            image_path = local_path(index, image["src"])
            try:
                with Image.open(image_path) as source:
                    source.verify()
            except Exception as error:
                errors.append(f"Invalid card image: {image_path.relative_to(ROOT)} ({error})")

    redirect_count = 0
    for language in [None, *sorted(LANGS)]:
        folder = ROOT if language is None else ROOT / language
        for old_name, new_name in BLOG_REPLACEMENTS.items():
            redirect_count += 1
            page = folder / old_name
            soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
            refresh = soup.find("meta", attrs={"http-equiv": lambda value: value and value.lower() == "refresh"})
            expected = ("../" if language else "") + new_name
            if not refresh or f"url={expected}" not in refresh.get("content", ""):
                errors.append(f"Incorrect redirect: {page.relative_to(ROOT)} -> {expected}")

    stale_schema = 0
    for page in ROOT.rglob("blog*.html"):
        soup = BeautifulSoup(page.read_text(encoding="utf-8"), "html.parser")
        for script in soup.select('script[type="application/ld+json"]'):
            try:
                data = json.loads(script.string or "")
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and data.get("@type") == "Article" and "ANIMAL FEED.webp" in str(data.get("image", "")):
                stale_schema += 1
                errors.append(f"Generic Article schema image: {page.relative_to(ROOT)}")

    print(f"Validated {card_count} published blog cards and {redirect_count} legacy redirects.")
    print(f"Stale generic Article schema images: {stale_schema}")
    if errors:
        print("\n".join(errors))
        raise SystemExit(1)
    print("Blog navigation and image validation passed.")


if __name__ == "__main__":
    main()
