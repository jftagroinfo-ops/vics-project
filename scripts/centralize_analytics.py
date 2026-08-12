#!/usr/bin/env python3
"""Remove duplicated page-level GA4 configuration; shared consent client owns it."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
SCRIPT = re.compile(r"\s*<script\b[^>]*>(.*?)</script>", re.I | re.S)
GA_ID = "G-MWZ2ZWZP4G"


def is_duplicate_ga(block: str) -> bool:
    compact = re.sub(r"\s+", "", block)
    return (
        GA_ID in compact
        and "window.dataLayer=window.dataLayer||[]" in compact
        and "functiongtag(){dataLayer.push(arguments);}" in compact
        and "gtag('js',newDate());" in compact
        and f"gtag('config','{GA_ID}');" in compact
        and "gtag('event'" not in compact
    )


def main() -> int:
    changed = 0
    removed = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="replace")

        def replace(match: re.Match[str]) -> str:
            nonlocal removed
            if is_duplicate_ga(match.group(1)):
                removed += 1
                return ""
            return match.group(0)

        updated = SCRIPT.sub(replace, text)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    print(f"Removed {removed} duplicate GA4 config blocks from {changed} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
