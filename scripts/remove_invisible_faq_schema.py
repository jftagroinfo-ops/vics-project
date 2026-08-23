#!/usr/bin/env python3
"""Remove FAQPage JSON-LD when none of its questions is visible on-page."""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
IGNORED_DIRS = {".git", ".cloudflare", ".cloudflare-dist", ".wrangler", "reports", "__pycache__"}


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def visible_text(source: str) -> str:
    soup = BeautifulSoup(source, "html.parser")
    for node in soup(["script", "style", "noscript"]):
        node.decompose()
    return compact(soup.get_text(" ", strip=True))


def update_page(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    if "FAQPage" not in source:
        return False
    visible = visible_text(source)
    page_changed = False

    def replace(match: re.Match[str]) -> str:
        nonlocal page_changed
        raw = match.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)

        if isinstance(data, dict) and data.get("@type") == "FAQPage":
            questions = [compact(str(item.get("name", ""))) for item in data.get("mainEntity", [])]
            if questions and not any(question and question in visible for question in questions):
                page_changed = True
                return ""
            return match.group(0)

        if isinstance(data, dict) and isinstance(data.get("@graph"), list):
            original = data["@graph"]
            kept = []
            removed = False
            for obj in original:
                if not isinstance(obj, dict) or obj.get("@type") != "FAQPage":
                    kept.append(obj)
                    continue
                questions = [compact(str(item.get("name", ""))) for item in obj.get("mainEntity", [])]
                if questions and not any(question and question in visible for question in questions):
                    removed = True
                else:
                    kept.append(obj)
            if removed:
                data["@graph"] = kept
                page_changed = True
                return '<script type="application/ld+json">' + json.dumps(
                    data, ensure_ascii=False, separators=(",", ":")
                ) + "</script>"
        return match.group(0)

    updated = re.sub(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        replace,
        source,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if page_changed and updated != source:
        path.write_text(updated, encoding="utf-8", newline="")
        return True
    return False


def main() -> int:
    changed = []
    for path in sorted(ROOT.rglob("*.html")):
        relative = path.relative_to(ROOT)
        if any(part in IGNORED_DIRS or part.startswith("backup_") for part in relative.parts):
            continue
        if update_page(path):
            changed.append(relative.as_posix())
    print(f"Removed non-visible FAQPage schema from {len(changed)} pages.")
    for item in changed:
        print(f"- {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
