#!/usr/bin/env python3
"""Apply safe, mechanical remediations shared by generated HTML pages."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def update_csp(text: str) -> str:
    if "Content-Security-Policy" not in text:
        return text
    text = text.replace("script-src 'self'", "script-src 'self' https://static.cloudflareinsights.com")
    text = text.replace("connect-src 'self'", "connect-src 'self' https://cloudflareinsights.com")
    while "https://static.cloudflareinsights.com https://static.cloudflareinsights.com" in text:
        text = text.replace("https://static.cloudflareinsights.com https://static.cloudflareinsights.com", "https://static.cloudflareinsights.com")
    while "https://cloudflareinsights.com https://cloudflareinsights.com" in text:
        text = text.replace("https://cloudflareinsights.com https://cloudflareinsights.com", "https://cloudflareinsights.com")
    return text.replace(" 'unsafe-eval'", "")


def qualify_commercial_claims(text: str) -> str:
    replacements = {
        "Ready stock \u00b7 Ex-Nhava Sheva/Mundra": "Availability confirmed per enquiry \u00b7 Ex-Nhava Sheva/Mundra",
        "dedicated slot agreements": "routing options confirmed per booking",
        "ensure container slots even in peak season": "support routing reviews for each confirmed booking",
        "testing before every container is sealed": "testing according to the agreed shipment specification",
        "Every certification is active, annually renewed, and independently verified. No claims \u2014 only proof.": "Registration and certification summaries are provided for buyer reference. Request current copies and verify their scope before contracting.",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def self_host_static_assets(text: str) -> str:
    if "<head" not in text.lower():
        return text
    text = re.sub(r'\s*<link\b[^>]*href=["\']https://fonts\.googleapis\.com/[^>]*>', "", text, flags=re.I)
    text = re.sub(r'\s*<link\b[^>]*href=["\']https://fonts\.gstatic\.com[^>]*>', "", text, flags=re.I)
    text = re.sub(r'\s*<link\b[^>]*href=["\']https://cdnjs\.cloudflare\.com/ajax/libs/font-awesome/[^>]*>', "", text, flags=re.I)
    if "assets/fonts/jft-fonts.css" not in text:
        text = re.sub(r'(<head\b[^>]*>)', r'\1\n  <link rel="stylesheet" href="/assets/fonts/jft-fonts.css">', text, count=1, flags=re.I)
    if "assets/fontawesome/css/all.min.css" not in text:
        text = re.sub(r'(<head\b[^>]*>)', r'\1\n  <link rel="stylesheet" href="/assets/fontawesome/css/all.min.css">', text, count=1, flags=re.I)
    return text


def main() -> int:
    updated = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts:
            continue
        original = path.read_text(encoding="utf-8", errors="replace")
        text = self_host_static_assets(qualify_commercial_claims(update_csp(original)))
        if text != original:
            path.write_text(text, encoding="utf-8")
            updated += 1
    print(f"Applied shared CSP, claims and self-hosted asset remediation to {updated} HTML files.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
