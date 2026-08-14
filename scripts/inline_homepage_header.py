#!/usr/bin/env python3
"""Embed the shared header in the homepage so it renders with the first response."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
HOME = ROOT / "index.html"
HEADER = ROOT / "header.html"
START = "<!-- JFT_INLINE_HEADER_START -->"
END = "<!-- JFT_INLINE_HEADER_END -->"


def embedded_header(fragment: str) -> str:
    return (
        '<div id="header-placeholder" data-jft-header-state="ready">\n'
        f"{START}\n{fragment.rstrip()}\n{END}\n"
        "</div>"
    )


def main() -> int:
    fragment = "\n".join(
        line.rstrip()
        for line in HEADER.read_text(encoding="utf-8", errors="strict").splitlines()
    )
    original = HOME.read_text(encoding="utf-8", errors="strict")
    replacement = embedded_header(fragment)

    if START in original and END in original:
        updated, count = re.subn(
            rf'<div id="header-placeholder"[^>]*>\s*{re.escape(START)}.*?{re.escape(END)}\s*</div>',
            lambda _match: replacement,
            original,
            count=1,
            flags=re.S,
        )
    else:
        updated, count = re.subn(
            r'<div id="header-placeholder"></div>\s*<script data-jft-early-header-loader>.*?</script>',
            lambda _match: replacement,
            original,
            count=1,
            flags=re.S,
        )

    if count != 1:
        raise SystemExit("Could not identify the homepage header insertion point")
    if updated != original:
        HOME.write_text(updated, encoding="utf-8", newline="")
        print("Embedded the current shared header in index.html")
    else:
        print("Homepage header is already synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
