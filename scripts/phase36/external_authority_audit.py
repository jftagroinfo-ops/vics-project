#!/usr/bin/env python3
"""Phase 36 - Stage G: Read-only external authority discoverability audit.

Checks public discoverability of JFT Agro Overseas across institutional/business sources
using read-only HTTP requests (no login, no submission, no profile creation). Records
reachability + a best-effort brand-presence signal. Does NOT modify website/source/config.
Writes reports/phase36/external-authority-baseline.csv (plus a JSON mirror).
"""
import csv
import json
import re
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent.parent
CSV_OUT = ROOT / "reports" / "phase36" / "external-authority-baseline.csv"
JSON_OUT = ROOT / "reports" / "phase36" / "external-authority-baseline-2026-08-29.json"

HDR = {"User-Agent": "JFT-Phase36-Audit/1.0 (+https://jftagro.com/.well-known/security.txt)"}

# Each target: category, source, url. We only test read-only reachability + look for brand string.
TARGETS = [
    ("institutional", "APEDA directory (public search landing)", "https://apeda.gov.in/apedawebsite/directory_of_exporters.htm"),
    ("institutional", "FIEO member directory (public landing)", "https://www.fieo.in/"),
    ("institutional", "DGFT (public landing)", "https://dgft.gov.in/"),
    ("business", "LinkedIn company page", "https://www.linkedin.com/company/jft-agro-overseas"),
    ("business", "LinkedIn (public people search)", "https://www.linkedin.com/search/results/companies/?keywords=JFT%20Agro%20Overseas"),
    ("business", "Facebook (sameAs in JSON-LD)", "https://www.facebook.com/jftagro"),
    ("business", "Instagram (sameAs in JSON-LD)", "https://www.instagram.com/jftagro"),
    ("directory", "ExportHub listing", "https://www.exporthub.com/jft-agro-overseas"),
    ("directory", "IndiaMART (brand search)", "https://www.indiamart.com/jft-agro/"),
    ("directory", "TradeIndia (brand search)", "https://www.tradeindia.com/search?keyword=JFT+Agro+Overseas"),
    ("directory", "Go4WorldBusiness (brand search)", "https://www.go4worldbusiness.com/search.html?kw=JFT+Agro+Overseas"),
    ("directory", "Kompass (brand search)", "https://www.kompass.com/searchCompanies?text=JFT%20Agro%20Overseas"),
    ("publication", "Google web index (brand query, read-only SERP)", "https://www.google.com/search?q=%22JFT+Agro+Overseas%22"),
    ("publication", "Bing web index (brand query, read-only SERP)", "https://www.bing.com/search?q=%22JFT+Agro+Overseas%22"),
]

BRAND = re.compile(r"jft\s*agro", re.IGNORECASE)


def check(category, source, url) -> dict:
    rec = {"category": category, "source": source, "url": url, "status": None,
           "reachable": None, "brand_mention_observed": None, "evidence_class": "OBSERVED",
           "note": ""}
    try:
        r = requests.get(url, headers=HDR, timeout=(8, 25), allow_redirects=True)
        rec["status"] = r.status_code
        rec["final_url"] = r.url
        # 2xx/3xx = reachable; 4xx/5xx = page not found/blocked
        rec["reachable"] = r.status_code < 400
        body = r.text or ""
        rec["brand_mention_observed"] = bool(BRAND.search(body[:200000])) if rec["reachable"] else False
        if r.status_code in (401, 403, 429, 999):
            rec["note"] = "ACCESS BLOCKED / AUTH REQUIRED - treat brand presence as UNKNOWN"
            rec["brand_mention_observed"] = None
            rec["evidence_class"] = "INACCESSIBLE"
        elif r.status_code >= 400:
            rec["note"] = "PAGE NOT RETURNED (HTTP error) - brand presence UNKNOWN"
            rec["brand_mention_observed"] = None
            rec["evidence_class"] = "UNKNOWN"
    except requests.RequestException as e:
        rec["status"] = 0
        rec["reachable"] = False
        rec["brand_mention_observed"] = None
        rec["evidence_class"] = "INACCESSIBLE"
        rec["note"] = "REQUEST FAILED: " + str(e)
    return rec


def main() -> int:
    CSV_OUT.parent.mkdir(parents=True, exist_ok=True)
    rows = [check(c, s, u) for c, s, u in TARGETS]
    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["category", "source", "url", "status", "reachable",
                    "brand_mention_observed", "evidence_class", "note"])
        for r in rows:
            w.writerow([r["category"], r["source"], r["url"], r["status"], r["reachable"],
                        r["brand_mention_observed"], r["evidence_class"], r["note"]])
    doc = {"audit_date": "2026-08-29", "targets_checked": len(rows), "results": rows}
    JSON_OUT.write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    reached = sum(1 for r in rows if r["reachable"])
    print(f"Checked {len(rows)} external sources; reachable={reached} -> {CSV_OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
