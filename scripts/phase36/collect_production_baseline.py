#!/usr/bin/env python3
"""Phase 36 - Stage B: Read-only live production baseline collector.

Performs read-only HTTP GET/HEAD against https://jftagro.com and representative pages.
Captures: status, canonical, hreflang set, x-default, title, meta description, H1,
JSON-LD @type(s). Writes reports/phase36/production-baseline-2026-08-29.json.
Does NOT modify website/source/config. Requires `requests` (already used by repo scripts).
"""
import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent.parent
OUT = ROOT / "reports" / "phase36" / "production-baseline-2026-08-29.json"
BASE = "https://jftagro.com"

PAGES = [
    "/", "/about.html", "/contact.html", "/products.html", "/product-catalogue.html",
    "/rice-exporter-india.html", "/spices-exporter-india.html", "/pulses-exporter-india.html",
    "/1121-basmati-rice-exporter.html", "/5-parboiled-rice-ir-64-exporter.html",
    "/turmeric-finger-exporter.html", "/certificates.html", "/infrastructure.html",
    "/quality-control.html", "/faq.html", "/blog.html", "/africa-trade.html", "/uae-trade.html",
    "/europe-trade.html", "/asia-trade.html", "/quote-calculator.html", "/packing-calculator.html",
    "/blog-how-to-choose-indian-agro-exporter.html", "/blog-sgs-inspection-indian-agro-exports.html",
    "/terms.html", "/privacy.html", "/legal.html",
    "/ar/", "/es/", "/fr/", "/id/", "/ms/", "/pt/", "/ru/", "/si/", "/th/", "/vi/",
    "/sitemap.xml", "/robots.txt", "/.well-known/security.txt",
]

HDR = {"User-Agent": "JFT-Phase36-Audit/1.0 (+https://jftagro.com/.well-known/security.txt)"}


def extract(html: str, patterns):
    found = {}
    for name, pat in patterns.items():
        m = re.search(pat, html, re.IGNORECASE | re.DOTALL)
        found[name] = m.group(1).strip() if m else None
    return found


def schema_types(html: str):
    types = []
    for m in re.finditer(r'"@type"\s*:\s*"([^"]+)"', html):
        types.append(m.group(1))
    # dedupe keep order
    seen = set()
    out = []
    for t in types:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def collect_page(path: str) -> dict:
    url = BASE + path
    rec = {"path": path, "url": url}
    try:
        r = requests.get(url, headers=HDR, timeout=(8, 25), allow_redirects=True)
        rec["status"] = r.status_code
        rec["final_url"] = r.url
        body = r.text
        rec["content_type"] = r.headers.get("content-type", "")
        meta = extract(body, {
            "canonical": r'<link rel="canonical" href="([^"]+)"',
            "title": r"<title>([^<]*)</title>",
            "meta_description": r'<meta name="description" content="([^"]*)"',
            "h1": r"<h1[^>]*>(.*?)</h1>",
        })
        rec.update(meta)
        hreflangs = re.findall(r'<link rel="alternate" hreflang="([^"]+)" href="([^"]+)"', body)
        rec["hreflang"] = {h: u for h, u in hreflangs}
        rec["x_default"] = rec["hreflang"].get("x-default")
        rec["schema_types"] = schema_types(body)
        rec["evidence_class"] = "VERIFIED"
    except requests.RequestException as e:
        rec["status"] = 0
        rec["error"] = str(e)
        rec["evidence_class"] = "OBSERVED"
    return rec


def main() -> int:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    results = [collect_page(p) for p in PAGES]
    summary = {
        "audit_date": "2026-08-29",
        "production_url": BASE,
        "repository_sha": "4535656d830c4fb5ede7928cab7f6920597aaa67",
        "pages_checked": len(results),
        "ok_200": sum(1 for r in results if r.get("status") == 200),
        "non_200": sum(1 for r in results if r.get("status") not in (200, None)),
        "results": results,
    }
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Checked {len(results)} pages; 200-OK={summary['ok_200']} -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
