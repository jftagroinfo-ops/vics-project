#!/usr/bin/env python3
"""Enforce lightweight static performance budgets for production pages."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
CRITICAL_IMAGE = ROOT / "images" / "homepage" / "rice-milling-facility-premium-v1.webp"


def main() -> int:
    findings: list[str] = []
    if not CRITICAL_IMAGE.is_file():
        findings.append("missing premium homepage hero")
    else:
        if CRITICAL_IMAGE.stat().st_size > 350_000:
            findings.append(f"homepage hero exceeds 350 KB: {CRITICAL_IMAGE.stat().st_size}")
        with Image.open(CRITICAL_IMAGE) as image:
            if image.width / image.height < 1.3:
                findings.append("homepage hero is not sufficiently wide for responsive cover cropping")
    homepage = (ROOT / "index.html").read_text(encoding="utf-8")
    if "<video autoplay" in homepage:
        findings.append("homepage still autoplays a hero video")
    if "rice-milling-facility-premium-v1.webp" not in homepage:
        findings.append("homepage does not use the optimized trust hero")
    # The homepage includes the full interactive product/sourcing experience.
    # Keep a narrow, explicit allowance for it while retaining the stricter
    # budget for every other root document.
    html_budgets = {"index.html": 250_000}
    for path in ROOT.glob("*.html"):
        budget = html_budgets.get(path.name, 240_000)
        if path.stat().st_size > budget:
            findings.append(f"oversized HTML document: {path.name} ({path.stat().st_size} bytes; budget {budget})")
    print(f"Static performance findings: {len(findings)}")
    for finding in findings: print(f"  - {finding}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
