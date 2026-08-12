#!/usr/bin/env python3
"""Qualify repeated commercial claims and remove unsupported rating schema."""

from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parent.parent
REPLACEMENTS = (
    (re.compile(r"within 4 business hours", re.I), "typically within one business day"),
    (re.compile(r"within 24 hours", re.I), "typically within one business day"),
    (re.compile(r"4-Hour Response", re.I), "One-Business-Day Review"),
    (re.compile(r"free samples worldwide", re.I), "trade samples for qualified buyers"),
    (re.compile(r"without a single default", re.I), "across multiple international markets"),
    (re.compile(r"guaranteed container availability", re.I), "container planning subject to carrier confirmation"),
    (re.compile(r"all containers are fumigated", re.I), "fumigation is arranged where required by product and destination"),
    (re.compile(r"every shipment is tested", re.I), "shipment testing is arranged against contracted requirements"),
    (re.compile(r"any global port", re.I), "supported destination ports"),
    (re.compile(r"\bWe respond typically within one business day\b"), "We typically respond within one business day"),
)
JSONLD = re.compile(r"\s*<script\b[^>]*type=[\"']application/ld\+json[\"'][^>]*>(.*?)</script>", re.I | re.S)


def remove_unsupported_rating(match: re.Match[str]) -> str:
    try:
        payload = json.loads(match.group(1))
    except json.JSONDecodeError:
        return match.group(0)
    if isinstance(payload, dict) and payload.get("@type") == "Organization" and ("aggregateRating" in payload or "review" in payload):
        return ""
    return match.group(0)


def main() -> int:
    changed = 0
    replacement_count = 0
    removed_ratings = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        updated = text
        before_schema = len(re.findall(r'"aggregateRating"', updated))
        updated = JSONLD.sub(remove_unsupported_rating, updated)
        removed_ratings += before_schema - len(re.findall(r'"aggregateRating"', updated))
        for pattern, replacement in REPLACEMENTS:
            updated, count = pattern.subn(replacement, updated)
            replacement_count += count
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    print(f"Updated {changed} pages; qualified {replacement_count} claims; removed {removed_ratings} rating schemas.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
