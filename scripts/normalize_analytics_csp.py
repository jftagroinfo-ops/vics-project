#!/usr/bin/env python3
"""Allow the consent-gated GA4 client through page-level CSP directives."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
CSP_META = re.compile(
    r'<meta\b(?=[^>]*http-equiv=["\']Content-Security-Policy["\'])[^>]*>',
    re.I,
)
SCRIPT_SOURCES = ("https://www.googletagmanager.com",)
CONNECT_SOURCES = (
    "https://www.google-analytics.com",
    "https://region1.google-analytics.com",
    "https://www.googletagmanager.com",
    "https://www.google.com",
)


def add_sources(tag: str, directive: str, required: tuple[str, ...]) -> str:
    pattern = re.compile(rf'({re.escape(directive)}\s+)([^;"<>]+)', re.I)

    def update(match: re.Match[str]) -> str:
        value = match.group(2).rstrip()
        missing = [source for source in required if source not in value]
        return match.group(1) + value + (" " + " ".join(missing) if missing else "")

    return pattern.sub(update, tag, count=1)


def normalize(tag: str) -> str:
    tag = add_sources(tag, "script-src", SCRIPT_SOURCES)
    return add_sources(tag, "connect-src", CONNECT_SOURCES)


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or "reports" in path.parts:
            continue
        original = path.read_text(encoding="utf-8", errors="strict")
        updated = CSP_META.sub(lambda match: normalize(match.group(0)), original)
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="")
            changed += 1
    print(f"Normalized analytics CSP in {changed} HTML files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
