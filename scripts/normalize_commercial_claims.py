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
    (re.compile(r"NABL-certified lab with full residue testing before every shipment", re.I), "Accredited laboratory testing arranged to contracted product and destination requirements"),
    (re.compile(r"We conduct Codex-aligned pesticide residue testing before every shipment", re.I), "We arrange Codex-aligned pesticide residue testing where required by the contracted specification and destination"),
    (re.compile(r"We arrange this automatically for every shipment", re.I), "We arrange this where required for the contracted product and destination"),
    (re.compile(r"34\+ years of building trusted Indian agro-commodity supply partnerships", re.I), "building trusted Indian agro-commodity supply partnerships since 1980"),
    (re.compile(r'<div class="ab-badge-gold"><span class="bnum">34\+</span><span class="blbl">Years Legacy</span></div>', re.I), '<div class="ab-badge-gold"><span class="bnum">1980</span><span class="blbl">Established</span></div>'),
    (re.compile(r"34\+ Years of<br><span>Milestones</span>", re.I), "A Legacy of<br><span>Milestones</span>"),
    (re.compile(r"We(?:'|’)ve spent 34\+ years earning the trust", re.I), "Since 1980, we have worked to earn the trust"),
    (re.compile(r"34\+ years of combined leadership experience at the helm", re.I), "Hands-on leadership since the company's founding in 1980"),
    (re.compile(r"34\+ Years in Agro Exports", re.I), "Agro Trade Leadership"),
    (re.compile(r'>34\+</div><div class="stat-label">Years in Trade</div>', re.I), '>1980</div><div class="stat-label">Established</div>'),
    (re.compile(r'<div class="ss-item reveal d1"><div class="ss-num"><span class="cnt" data-v="45">0</span>\+</div><div class="ss-lbl">Years in Business</div></div>', re.I), '<div class="ss-item reveal d1"><div class="ss-num"><span class="cnt" data-v="1980">0</span></div><div class="ss-lbl">Established</div></div>'),
    (re.compile(r'<div class="gs-box d3"><div class="gs-num"><span class="cnt" data-v="45">0</span>\?</?\+?</div><div class="gs-lbl">Years Experience</div></div>', re.I), '<div class="gs-box d3"><div class="gs-num"><span class="cnt" data-v="1980">0</span></div><div class="gs-lbl">Established</div></div>'),
    (re.compile(r'<div class="vc-stat">(?:34|45)\+ <span>Years Legacy</span></div>', re.I), '<div class="vc-stat">Since 1980 <span>Company Legacy</span></div>'),
    (re.compile(r'<div class="prod-stat-num">34\+</div>\s*<div class="prod-stat-lbl">Years Experience</div>', re.I), '<div class="prod-stat-num">1980</div>\n          <div class="prod-stat-lbl">Established</div>'),
    (re.compile(r'<span class="stat-bg">45</span><span class="stat-num"><span class="cnt"\s+data-v="45">0</span><span class="stat-unit">\+</span></span>\s*<div class="stat-div"></div><span class="stat-lbl">Years of Legacy</span>', re.I), '<span class="stat-bg">1980</span><span class="stat-num"><span class="cnt" data-v="1980">0</span></span><div class="stat-div"></div><span class="stat-lbl">Established</span>'),
    (re.compile(r"<h4>container planning subject to carrier confirmation</h4><p>Dedicated slot agreements with Maersk, MSC, CMA CGM — even during peak Ramadan and harvest seasons\.</p>", re.I), '<h4>Planned Export Logistics</h4><p>Carrier options, sailing schedules, and container availability are coordinated and confirmed for each shipment.</p>'),
    (re.compile(r"<h4>Third-Party Certified Quality</h4><p>Every container inspected by SGS or Intertek before sealing\. Full lab report shared with buyer pre-shipment\.</p>", re.I), '<h4>Third-Party Inspection Options</h4><p>SGS, Intertek, or other agreed inspection can be arranged before sealing when required by the contract.</p>'),
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
