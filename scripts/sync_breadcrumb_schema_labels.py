#!/usr/bin/env python3
"""Synchronize BreadcrumbList names with the visible breadcrumb navigation.

This is intentionally conservative: only localized pages are changed, and only
when a visible breadcrumb nav has exactly the same number of labels as the
JSON-LD BreadcrumbList. No URLs, visible copy, or non-breadcrumb schema change.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
LOCALES = {"ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"}


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def breadcrumb_labels(soup: BeautifulSoup) -> list[str]:
    candidates = []
    for nav in soup.find_all("nav"):
        classes = " ".join(nav.get("class", [])).lower()
        aria = nav.get("aria-label", "").lower()
        if "crumb" not in classes and "breadcrumb" not in aria:
            continue
        labels = [
            compact(node.get_text(" ", strip=True))
            for node in nav.find_all(["a", "span"], recursive=True)
        ]
        labels = [label for label in labels if label]
        if len(labels) >= 2:
            candidates.append(labels)
    return max(candidates, key=len, default=[])


def update_page(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(source, "html.parser")
    visible = breadcrumb_labels(soup)
    if not visible:
        return False

    changed = False

    def replace(match: re.Match[str]) -> str:
        nonlocal changed
        block_changed = False
        raw = match.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        objects = data.get("@graph", []) if isinstance(data, dict) and "@graph" in data else [data]
        for obj in objects:
            if not isinstance(obj, dict) or obj.get("@type") != "BreadcrumbList":
                continue
            items = obj.get("itemListElement", [])
            if len(items) != len(visible):
                continue
            old = [compact(str(item.get("name", ""))) for item in items]
            if old == visible:
                continue
            for item, label in zip(items, visible):
                item["name"] = label
            block_changed = True
        if not block_changed:
            return match.group(0)
        changed = True
        return '<script type="application/ld+json">' + json.dumps(
            data, ensure_ascii=False, separators=(",", ":")
        ) + "</script>"

    updated = re.sub(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        replace,
        source,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if changed and updated != source:
        path.write_text(updated, encoding="utf-8", newline="")
        return True
    return False


def main() -> int:
    changed = []
    for locale in sorted(LOCALES):
        for path in sorted((ROOT / locale).glob("*.html")):
            if update_page(path):
                changed.append(path.relative_to(ROOT).as_posix())
    print(f"Updated localized breadcrumb labels on {len(changed)} pages.")
    for item in changed[:20]:
        print(f"- {item}")
    if len(changed) > 20:
        print(f"- ... and {len(changed) - 20} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
