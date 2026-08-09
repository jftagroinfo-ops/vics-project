#!/usr/bin/env python3
"""Enforce lightweight static performance budgets for production pages."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
CRITICAL_IMAGE = ROOT / "images" / "homepage" / "export-trust-hero-v2.webp"


def main() -> int:
    findings: list[str] = []
    if not CRITICAL_IMAGE.is_file():
        findings.append("missing premium homepage hero")
    else:
        if CRITICAL_IMAGE.stat().st_size > 350_000:
            findings.append(f"homepage hero exceeds 350 KB: {CRITICAL_IMAGE.stat().st_size}")
        with Image.open(CRITICAL_IMAGE) as image:
            if image.width / image.height < 1.6:
                findings.append("homepage hero is not sufficiently wide")
    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    if "<video autoplay" in homepage:
        findings.append("homepage still autoplays a hero video")
    if "export-trust-hero-v2.webp" not in homepage:
        findings.append("homepage does not use the optimized trust hero")
    for path in ROOT.glob("*.html"):
        if path.stat().st_size > 240_000:
            findings.append(f"oversized HTML document: {path.name} ({path.stat().st_size} bytes)")
    print(f"Static performance findings: {len(findings)}")
    for finding in findings: print(f"  - {finding}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
