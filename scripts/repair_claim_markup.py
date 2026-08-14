#!/usr/bin/env python3
"""Repair nested markup affected by claim normalization and simplify risky blocks."""

from __future__ import annotations

import re
from pathlib import Path
from remediate_production_claims import COPY


ROOT = Path(__file__).resolve().parents[1]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
FACILITY = "Processing scope and facility capacity are documented during buyer due diligence and confirmed for the contracted product."
HISTORY = "JFT Agro Overseas LLP was registered in 2016. Any predecessor-business history is supplied for buyer verification before it is relied upon."


def write_if_changed(path: Path, text: str, updated: str) -> int:
    if updated == text:
        return 0
    path.write_text(updated, encoding="utf-8", newline="")
    return 1


def repair_about(path: Path, locale: str) -> int:
    text = path.read_text(encoding="utf-8")
    updated = text
    updated = re.sub(r'<div class="usp-row"><div class="usp-ico"><i class="fa-solid fa-industry"></i></div><div>.*?</div></div>', '', updated, count=1, flags=re.S)
    history = HISTORY if locale == "en" else COPY[locale]["history_p"]
    facility = FACILITY if locale == "en" else COPY[locale]["capacity"]
    updated = re.sub(r'<p class="why-intro">.*?</p>', f'<p class="why-intro">{history}</p>', updated, count=1, flags=re.S)
    story_paragraphs = list(re.finditer(r'<p class="story-p">.*?</p>', updated, flags=re.S))
    if len(story_paragraphs) > 1 and locale != "en":
        item = story_paragraphs[1]
        updated = updated[:item.start()] + f'<p class="story-p">{facility}</p>' + updated[item.end():]
    return write_if_changed(path, text, updated)


def repair_infrastructure(path: Path, locale: str) -> int:
    text = path.read_text(encoding="utf-8")
    updated = text
    facility = FACILITY if locale == "en" else COPY[locale]["capacity"]
    updated = re.sub(r'<p class="jft-page-hero-sub">.*?</p>', f'<p class="jft-page-hero-sub">{facility}</p>', updated, count=1, flags=re.S)
    meta = f'''<div class="jft-page-hero-meta">
      <span class="jft-hero-tag"><i class="fa-solid fa-industry"></i> Capacity evidence on request</span>
      <span class="jft-hero-tag"><i class="fa-solid fa-certificate"></i> Current documents available for verification</span>
      <span class="jft-hero-tag"><i class="fa-solid fa-location-dot"></i> Balap, Raigad processing unit</span>
    </div>''' if locale == "en" else f'''<div class="jft-page-hero-meta">
      <span class="jft-hero-tag"><i class="fa-solid fa-industry"></i> {facility}</span>
      <span class="jft-hero-tag"><i class="fa-solid fa-location-dot"></i> Balap, Raigad</span>
    </div>'''
    updated = re.sub(r'<div class="jft-page-hero-meta">.*?</div>(?=\s*<div style="margin-top:32px)', meta, updated, count=1, flags=re.S)
    return write_if_changed(path, text, updated)


def repair_localized_index(path: Path) -> int:
    text = path.read_text(encoding="utf-8")
    updated = text
    updated = re.sub(r'<div class="vc-stat">[^<]*</span></div>', '<div class="vc-stat">Facility evidence <span>On Request</span></div>', updated)
    updated = re.sub(r'<div class="vc-stat">20\+\s*<span>.*?</span></div>', '<div class="vc-stat">International <span>Markets</span></div>', updated, flags=re.S)
    section = '''<section class="manu-section" id="manufacturing">
  <div class="jft-wide-container"><div class="manu-layout">
    <div class="manu-img-wrap reveal-left"><img src="../images/homepage/rice-milling-facility-premium-v1.webp" alt="Rice processing equipment presented for buyer due diligence" class="manu-img" loading="lazy" width="1448" height="1086"><div class="manu-badge"><span class="bb"><i class="fa-solid fa-file-shield" aria-hidden="true"></i></span><span class="bs">Evidence on request</span></div></div>
    <div class="reveal-right"><span class="brand-tag brand-tag-gold">Facility due diligence</span><h2 class="section-title" style="margin:20px 0 25px;">Processing Scope<br><span>Verified Before Contract</span></h2><p class="manu-body">Processing location, identity, capacity, equipment, testing and operating evidence can be requested before contracting. The written specification controls each product.</p><div class="manu-specs"><div class="manu-spec"><i class="fa-solid fa-location-dot"></i> Publicly listed processing unit: Balap, Raigad</div><div class="manu-spec"><i class="fa-solid fa-file-shield"></i> Capacity and operating evidence on request</div><div class="manu-spec"><i class="fa-solid fa-flask"></i> Testing scope agreed by contract</div><div class="manu-spec"><i class="fa-solid fa-box"></i> Packing confirmed per product</div></div><a href="infrastructure.html" class="btn-gold">Review facility information <i class="fa-solid fa-arrow-right"></i></a></div>
  </div></div>
</section>'''
    updated = re.sub(r'<section class="manu-section" id="manufacturing">.*?</section>', section, updated, count=1, flags=re.S)
    return write_if_changed(path, text, updated)


def main() -> None:
    changed = 0
    for locale in ("",) + LOCALES:
        base = ROOT if not locale else ROOT / locale
        locale_key = locale or "en"
        changed += repair_about(base / "about.html", locale_key)
        changed += repair_infrastructure(base / "infrastructure.html", locale_key)
        if locale:
            changed += repair_localized_index(base / "index.html")
    print(f"Updated {changed} HTML documents")


if __name__ == "__main__":
    main()
