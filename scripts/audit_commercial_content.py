#!/usr/bin/env python3
"""Validate the commercial contract surface of every English product page."""

from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path
from urllib.parse import unquote, urlsplit

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
ABSOLUTE_CLAIMS = (
    "guaranteed container availability",
    "all containers are fumigated",
    "tests every lot",
    "every shipment is tested against",
)


def product_names() -> list[str]:
    master = ROOT / "data" / "products.json"
    if master.is_file():
        return sorted({item["u"] for item in json.loads(master.read_text(encoding="utf-8")) if item.get("u")})
    text = (ROOT / "products.html").read_text(encoding="utf-8")
    return sorted(set(re.findall(r"\bu:\s*'([^']+\.html)'", text)))


def local_image(source: str) -> Path | None:
    parsed = urlsplit(source)
    if parsed.scheme or parsed.netloc or not source:
        return None
    return ROOT / unquote(parsed.path.lstrip("/"))


def main() -> int:
    findings: list[str] = []
    seen: dict[str, dict[str, list[str]]] = {
        "title": defaultdict(list), "description": defaultdict(list), "h1": defaultdict(list)
    }
    products = product_names()
    for name in products:
        path = ROOT / name
        if not path.is_file():
            findings.append(f"{name}: missing page")
            continue
        text = path.read_text(encoding="utf-8")
        soup = BeautifulSoup(text, "html.parser")
        title = soup.title.get_text(" ", strip=True) if soup.title else ""
        description_tag = soup.find("meta", attrs={"name": "description"})
        description = description_tag.get("content", "").strip() if description_tag else ""
        h1s = soup.find_all("h1")
        h1 = h1s[0].get_text(" ", strip=True) if len(h1s) == 1 else ""
        for field, value in (("title", title), ("description", description), ("h1", h1)):
            seen[field][value.casefold()].append(name)
        if not (35 <= len(title) <= 70): findings.append(f"{name}: title length {len(title)}")
        if not (90 <= len(description) <= 180): findings.append(f"{name}: description length {len(description)}")
        if len(h1s) != 1: findings.append(f"{name}: expected one h1, found {len(h1s)}")
        if len(soup.select("table.jft-spec-table tr")) < 4: findings.append(f"{name}: incomplete specification table")
        if "spec-contract-note" not in text: findings.append(f"{name}: missing contract specification note")
        related = {
            link.get("href") for link in soup.select(".related-grid a[href]")
            if link.get("href", "").endswith(".html") and (ROOT / link.get("href")).is_file()
        }
        if len(related) < 2: findings.append(f"{name}: fewer than two valid related-product links")
        schemas = []
        for node in soup.select('script[type="application/ld+json"]'):
            try: schemas.append(json.loads(node.string or node.get_text()))
            except json.JSONDecodeError: pass
        if any(isinstance(item, dict) and item.get("@type") == "Product" for item in schemas):
            findings.append(f"{name}: ineligible quote-only Product rich-result schema")
        if not any(isinstance(item, dict) and item.get("@type") == "WebPage" for item in schemas):
            findings.append(f"{name}: missing WebPage structured data")
        social = soup.find("meta", attrs={"property": "og:image"})
        image = local_image(social.get("content", "").replace("https://jftagro.com/", "") if social else "")
        if image and not image.is_file(): findings.append(f"{name}: missing social image {image.relative_to(ROOT)}")
        lowered = text.casefold()
        for phrase in ABSOLUTE_CLAIMS:
            if phrase in lowered: findings.append(f"{name}: absolute claim '{phrase}'")

    for field, values in seen.items():
        for value, pages in values.items():
            if value and len(pages) > 1:
                findings.append(f"duplicate {field}: {', '.join(pages)}")

    print(f"Audited {len(products)} product pages for commercial completeness and uniqueness.")
    for finding in findings[:50]: print(f"  - {finding}")
    if len(findings) > 50: print(f"  ... and {len(findings) - 50} more")
    print(f"Total findings: {len(findings)}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
