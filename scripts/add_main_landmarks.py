#!/usr/bin/env python3
"""Add a real main landmark to legacy shells and remove duplicate header UI IDs."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or path.name in {"header.html", "footer.html", "product-page-template.html", "inner-page-hero-snippet.html"}:
            continue
        text = path.read_text(encoding="utf-8")
        updated = text
        if "header-placeholder" in updated:
            updated = re.sub(r'<div id="page-progress"></div>\s*', '', updated, count=1)
        if not re.search(r'<main\b', updated, flags=re.I):
            updated, opened = re.subn(r'<div id="main-content"(?:\s+tabindex="-1")?></div>', '<main id="main-content" tabindex="-1">', updated, count=1, flags=re.I)
            if opened:
                updated, closed = re.subn(r'(<div id="footer-placeholder"></div>)', r'</main>\n\1', updated, count=1, flags=re.I)
                if not closed:
                    updated = text
            else:
                main_content_tag = re.search(r'<(?:section|div)\b[^>]*\bid="main-content"[^>]*>', updated, flags=re.I)
                if main_content_tag and not re.search(r'\brole="main"', main_content_tag.group(0), flags=re.I):
                    tag = main_content_tag.group(0)[:-1] + ' role="main">'
                    updated = updated[:main_content_tag.start()] + tag + updated[main_content_tag.end():]
        updated = re.sub(r'(\srole="main")(?:\srole="main")+', r'\1', updated, flags=re.I)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="")
            changed += 1
    print(f"Updated {changed} HTML documents")


if __name__ == "__main__":
    main()
