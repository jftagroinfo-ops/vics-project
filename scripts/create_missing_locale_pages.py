#!/usr/bin/env python3
"""Create locale-ready copies for source pages missing from language folders."""

from __future__ import annotations

from pathlib import Path
import re

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
IGNORED = {
    "cookie-consent-snippet.html",
    "footer.html",
    "header.html",
    "inner-page-hero-snippet.html",
    "product-page-template.html",
    "seo-universal-head-snippet.html",
    "thank-you.html",
}
FALLBACK_MARKER = '<meta name="jft-localization" content="english-fallback"/>'
ASSET_SUFFIXES = (
    ".css", ".js", ".json", ".webmanifest", ".png", ".jpg", ".jpeg", ".webp",
    ".avif", ".gif", ".svg", ".ico", ".woff", ".woff2", ".ttf", ".pdf",
)


def is_document(path: Path) -> bool:
    text = path.read_text(encoding="utf-8", errors="replace")
    return "<html" in text.lower() and path.name not in IGNORED and not path.name.startswith("yandex_")


def local_asset(value: str) -> bool:
    clean = value.split("?", 1)[0].split("#", 1)[0].lower()
    return clean.endswith(ASSET_SUFFIXES)


def prepare(source: Path, target: Path, language: str) -> None:
    soup = BeautifulSoup(source.read_text(encoding="utf-8", errors="replace"), "html5lib")
    soup.html["lang"] = language
    if language == "ar":
        soup.html["dir"] = "rtl"
    elif soup.html.has_attr("dir"):
        del soup.html["dir"]

    marker = BeautifulSoup(FALLBACK_MARKER, "html.parser").meta
    soup.head.insert(0, marker)
    for element in soup.find_all(True):
        for attribute in ("src", "href", "poster"):
            value = element.get(attribute)
            if not value or value.startswith(("../", "/", "#", "http://", "https://", "mailto:", "tel:", "data:", "javascript:")):
                continue
            if local_asset(value):
                element[attribute] = "../" + value
        style = element.get("style")
        if style:
            element["style"] = re.sub(r"url\((['\"]?)(?!\.\./|/|https?:|data:)([^)'\"]+)\1\)", r"url(\1../\2\1)", style)

    for style in soup.find_all("style"):
        if style.string:
            style.string.replace_with(re.sub(r"url\((['\"]?)(?!\.\./|/|https?:|data:)([^)'\"]+)\1\)", r"url(\1../\2\1)", style.string))
    for script in soup.find_all("script"):
        if script.string:
            text = script.string
            text = text.replace("'header.html'", "'../header.html'").replace('"header.html"', '"../header.html"')
            text = text.replace("'footer.html'", "'../footer.html'").replace('"footer.html"', '"../footer.html"')
            script.string.replace_with(text)

    target.write_text(str(soup), encoding="utf-8", newline="\n")


def preserve_source_noindex(source: Path, target: Path) -> bool:
    source_soup = BeautifulSoup(source.read_text(encoding="utf-8", errors="replace"), "html.parser")
    source_robots = source_soup.find("meta", attrs={"name": lambda value: value and value.lower() == "robots"})
    if not source_robots or "noindex" not in source_robots.get("content", "").lower():
        return False
    soup = BeautifulSoup(target.read_text(encoding="utf-8", errors="replace"), "html5lib")
    robots = soup.find("meta", attrs={"name": lambda value: value and value.lower() == "robots"})
    if robots and "noindex" in robots.get("content", "").lower():
        return False
    if not robots:
        robots = soup.new_tag("meta")
        robots["name"] = "robots"
        soup.head.insert(0, robots)
    robots["content"] = "noindex,follow"
    target.write_text(str(soup), encoding="utf-8", newline="\n")
    return True


def main() -> int:
    sources = [path for path in sorted(ROOT.glob("*.html")) if is_document(path)]
    created = preserved = 0
    for language in LOCALES:
        folder = ROOT / language
        for source in sources:
            target = folder / source.name
            if target.exists():
                preserved += preserve_source_noindex(source, target)
                continue
            prepare(source, target, language)
            print(f"Created {target.relative_to(ROOT)}")
            created += 1
    print(f"Created {created} missing locale pages; restored noindex policy on {preserved} variants.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
