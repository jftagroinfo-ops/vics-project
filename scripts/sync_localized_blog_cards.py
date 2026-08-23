#!/usr/bin/env python3
"""Add the newest English blog cards to every localized blog index.

The localized article title and description are read from the translated page,
so navigation copy stays aligned with the page that search engines and buyers open.
"""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
SLUGS = (
    "blog-how-to-write-agro-commodity-purchase-specification.html",
    "blog-certificate-of-analysis-food-imports.html",
    "blog-food-container-loading-inspection-checklist.html",
)


def clean(value: str) -> str:
    return " ".join(value.split())


def main() -> int:
    source = BeautifulSoup((ROOT / "blog.html").read_text(encoding="utf-8"), "html.parser")
    source_cards = {
        slug: source.select_one(f'a.article-card[href="{slug}"]') for slug in SLUGS
    }
    if any(card is None for card in source_cards.values()):
        raise RuntimeError("One or more source blog cards are missing")

    updated = 0
    for locale in LOCALES:
        index_path = ROOT / locale / "blog.html"
        index = BeautifulSoup(index_path.read_text(encoding="utf-8"), "html.parser")
        grid = index.select_one("#articlesGrid") or index.select_one(".articles-grid")
        if grid is None:
            raise RuntimeError(f"Article grid missing in {index_path}")

        existing_read = index.select_one(".card-read")
        read_label = "Read"
        if existing_read:
            read_label = clean(existing_read.get_text(" ", strip=True)).replace("→", "").strip()

        insert_before = grid.find("a", class_="article-card")
        for slug in reversed(SLUGS):
            if grid.select_one(f'a[href="{slug}"]'):
                continue
            page_path = ROOT / locale / slug
            page = BeautifulSoup(page_path.read_text(encoding="utf-8"), "html.parser")
            heading = page.find("h1")
            description = page.select_one('meta[name="description"]')
            if heading is None or description is None:
                raise RuntimeError(f"Localized metadata missing in {page_path}")

            card = deepcopy(source_cards[slug])
            image = card.find("img")
            if image:
                image["src"] = "../" + image["src"].lstrip("./")
                image["alt"] = clean(heading.get_text(" ", strip=True))
            title = card.select_one(".card-title")
            excerpt = card.select_one(".card-excerpt")
            read = card.select_one(".card-read")
            if title:
                title.string = clean(heading.get_text(" ", strip=True))
            if excerpt:
                excerpt.string = clean(description.get("content", ""))
            if read:
                icon = read.find("i")
                read.clear()
                read.append(read_label + " ")
                if icon:
                    read.append(icon)
            if insert_before:
                insert_before.insert_before(card)
            else:
                grid.append(card)
            updated += 1

        rendered = str(index)
        if not rendered.lstrip().lower().startswith("<!doctype html>"):
            rendered = "<!DOCTYPE html>\n" + rendered
        index_path.write_text(rendered, encoding="utf-8", newline="\n")

    print(f"Added {updated} localized blog navigation cards.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
