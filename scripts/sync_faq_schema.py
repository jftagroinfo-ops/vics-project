#!/usr/bin/env python3
"""Synchronize existing FAQPage JSON-LD with the visible FAQ content.

The script never creates FAQ markup. It only updates a page when it already has
FAQPage JSON-LD and at least two visible question/answer pairs using the site's
FAQ component classes.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
IGNORED_DIRS = {".git", ".cloudflare", ".cloudflare-dist", ".wrangler", "reports", "__pycache__"}


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def visible_faq(soup: BeautifulSoup) -> list[dict]:
    pairs = []
    for question in soup.select(".faq-q"):
        answer = question.find_next_sibling(class_="faq-a")
        if answer is None:
            continue
        q_text = compact(question.get_text(" ", strip=True))
        a_text = compact(answer.get_text(" ", strip=True))
        if q_text and a_text:
            pairs.append(
                {
                    "@type": "Question",
                    "name": q_text,
                    "acceptedAnswer": {"@type": "Answer", "text": a_text},
                }
            )
    if pairs:
        return pairs
    for details in soup.find_all("details"):
        summary = details.find("summary", recursive=False) or details.find("summary")
        if summary is None:
            continue
        answer = details.select_one(".faq-answer")
        if answer is None:
            answer = details
            summary.extract()
        q_text = compact(summary.get_text(" ", strip=True))
        a_text = compact(answer.get_text(" ", strip=True))
        if q_text and a_text:
            pairs.append(
                {
                    "@type": "Question",
                    "name": q_text,
                    "acceptedAnswer": {"@type": "Answer", "text": a_text},
                }
            )
    return pairs


def update_page(path: Path) -> bool:
    source = path.read_text(encoding="utf-8")
    soup = BeautifulSoup(source, "html.parser")
    faq = visible_faq(soup)
    if len(faq) < 2:
        return False
    language = (soup.html or {}).get("lang", "") if soup.html else ""
    page_changed = False

    def replace(match: re.Match[str]) -> str:
        nonlocal page_changed
        raw = match.group(1)
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            return match.group(0)
        objects = data.get("@graph", []) if isinstance(data, dict) and "@graph" in data else [data]
        block_changed = False
        for obj in objects:
            if not isinstance(obj, dict) or obj.get("@type") != "FAQPage":
                continue
            if obj.get("mainEntity") == faq and (not language or obj.get("inLanguage") == language):
                continue
            obj["mainEntity"] = faq
            if language:
                obj["inLanguage"] = language
            block_changed = True
        if not block_changed:
            return match.group(0)
        page_changed = True
        return '<script type="application/ld+json">' + json.dumps(
            data, ensure_ascii=False, separators=(",", ":")
        ) + "</script>"

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
    print(f"Updated FAQPage schema on {len(changed)} pages.")
    for item in changed[:20]:
        print(f"- {item}")
    if len(changed) > 20:
        print(f"- ... and {len(changed) - 20} more")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
