#!/usr/bin/env python3
"""Check every sitemap URL on production without downloading response bodies."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
URLS = [node.text.strip() for node in ET.parse(ROOT / "sitemap.xml").findall(".//s:loc", NS) if node.text]


def check(url: str) -> dict:
    start = time.perf_counter()
    try:
        response = requests.head(url, allow_redirects=False, timeout=20, headers={"User-Agent": "JFT-Site-Audit/1.0"})
        return {"url": url, "status": response.status_code, "location": response.headers.get("location", ""), "seconds": round(time.perf_counter() - start, 3)}
    except requests.RequestException as error:
        return {"url": url, "status": 0, "error": str(error), "seconds": round(time.perf_counter() - start, 3)}


def main() -> int:
    results = []
    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = [pool.submit(check, url) for url in URLS]
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["url"])
    failures = [item for item in results if item["status"] != 200]
    slow = [item for item in results if item["seconds"] > 2]
    payload = {"checked": len(results), "failures": failures, "slow_over_2s": slow, "status_counts": {str(code): sum(item["status"] == code for item in results) for code in sorted({item["status"] for item in results})}}
    (ROOT / "reports" / "live-sitemap-crawl.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"checked": payload["checked"], "status_counts": payload["status_counts"], "failures": len(failures), "slow_over_2s": len(slow)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
