#!/usr/bin/env python3
"""Keep localized SERP metadata concise and distinguish exact locale duplicates."""

from html import escape, unescape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
AUDIT = ROOT / "reports" / "full-site-audit.json"
TITLE_RE = re.compile(r"(<title>)(.*?)(</title>)", re.I | re.S)
DESC_RE = re.compile(r'(<meta\b[^>]*\bname=["\']description["\'][^>]*\bcontent=")([^"]*)("[^>]*>)', re.I | re.S)
LOCALE_LABELS = {"si": "ශ්‍රී ලංකාව", "vi": "Việt Nam"}


def clip_words(value: str, limit: int) -> str:
    value = re.sub(r"\s+", " ", unescape(value)).strip()
    if len(value) <= limit:
        return value
    clipped = value[: limit + 1]
    if " " in clipped:
        clipped = clipped.rsplit(" ", 1)[0]
    return clipped.rstrip(" ,;:|-–—")


def concise_title(value: str, locale: str, distinguish: bool) -> str:
    value = re.sub(r"\s+", " ", unescape(value)).strip()
    parts = [part.strip() for part in value.split("|")]
    brand = "JFT Agro"
    lead = parts[0]
    suffix = f" | {brand}"
    if distinguish:
        suffix += f" {LOCALE_LABELS.get(locale, locale.upper())}"
    return clip_words(lead, 65 - len(suffix)) + suffix


def concise_description(value: str, locale: str, distinguish: bool) -> str:
    value = re.sub(r"\s+", " ", unescape(value)).strip()
    if distinguish:
        label = LOCALE_LABELS.get(locale, locale.upper())
        value = f"{label}: {value}"
    clipped = clip_words(value, 160)
    return clipped if clipped.endswith((".", "!", "?", "。")) else clipped + "."


def paths_from(findings: list[str]) -> set[str]:
    paths = set()
    for finding in findings:
        paths.update(part.strip() for part in finding.rsplit(" (", 1)[0].split(", "))
    return paths


def main() -> int:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))["findings"]
    long_titles = paths_from(audit.get("seo_title_length", []))
    long_descriptions = paths_from(audit.get("seo_description_length", []))
    duplicate_titles = paths_from(audit.get("seo_duplicate_title", []))
    duplicate_descriptions = paths_from(audit.get("seo_duplicate_description", []))
    targets = long_titles | long_descriptions | duplicate_titles | duplicate_descriptions
    changed = 0
    for relative in sorted(targets):
        path = ROOT / relative
        if not path.exists():
            continue
        locale = Path(relative).parts[0] if len(Path(relative).parts) > 1 else "en"
        text = path.read_text(encoding="utf-8", errors="replace")
        updated = text
        if relative in long_titles or (relative in duplicate_titles and locale != "en"):
            updated = TITLE_RE.sub(
                lambda m: m.group(1) + escape(concise_title(m.group(2), locale, relative in duplicate_titles and locale != "en"), quote=False) + m.group(3),
                updated,
                count=1,
            )
        if relative in long_descriptions or (relative in duplicate_descriptions and locale != "en"):
            updated = DESC_RE.sub(
                lambda m: m.group(1) + escape(concise_description(m.group(2), locale, relative in duplicate_descriptions and locale != "en"), quote=True) + m.group(3),
                updated,
                count=1,
            )
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    print(f"Normalized localized metadata in {changed} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
