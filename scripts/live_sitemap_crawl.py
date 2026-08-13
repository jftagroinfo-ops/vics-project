#!/usr/bin/env python3
"""Check every sitemap URL on production without downloading response bodies."""

from concurrent.futures import ThreadPoolExecutor, as_completed
import json
import math
import time
import xml.etree.ElementTree as ET
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent.parent
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
URLS = [node.text.strip() for node in ET.parse(ROOT / "sitemap.xml").findall(".//s:loc", NS) if node.text]


def percentile(values: list[float], percentage: float) -> float:
    if not values:
        return 0.0
    ordered = sorted(values)
    return ordered[min(len(ordered) - 1, math.ceil(len(ordered) * percentage) - 1)]


def check(url: str) -> dict:
    start = time.perf_counter()
    last_error = ""
    headers = {"User-Agent": "JFT-Site-Audit/2.0 (+https://jftagro.com/.well-known/security.txt)"}
    for attempt in range(1, 4):
        try:
            response = requests.head(url, allow_redirects=False, timeout=(8, 20), headers=headers)
            if response.status_code in {403, 405}:
                response = requests.get(url, allow_redirects=False, timeout=(8, 20), headers=headers, stream=True)
            if response.status_code in {429, 500, 502, 503, 504} and attempt < 3:
                time.sleep(0.5 * attempt)
                continue
            return {"url": url, "status": response.status_code, "location": response.headers.get("location", ""), "attempts": attempt, "seconds": round(time.perf_counter() - start, 3)}
        except requests.RequestException as error:
            last_error = str(error)
            if attempt < 3:
                time.sleep(0.5 * attempt)
    return {"url": url, "status": 0, "error": last_error, "attempts": 3, "seconds": round(time.perf_counter() - start, 3)}


def main() -> int:
    results = []
    checkpoint = ROOT / "reports" / "live-sitemap-crawl.checkpoint.json"
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = [pool.submit(check, url) for url in URLS]
        for index, future in enumerate(as_completed(futures), start=1):
            results.append(future.result())
            if index % 100 == 0:
                checkpoint.write_text(json.dumps(sorted(results, key=lambda item: item["url"]), indent=2), encoding="utf-8")
    results.sort(key=lambda item: item["url"])
    failures = [item for item in results if item["status"] != 200]
    slow = [item for item in results if item["seconds"] > 2]
    timings = [item["seconds"] for item in results if item["status"]]
    payload = {"checked": len(results), "failures": failures, "slow_over_2s": slow, "latency_seconds": {"p50": round(percentile(timings, .50), 3), "p95": round(percentile(timings, .95), 3), "max": round(max(timings, default=0), 3)}, "retried": sum(item.get("attempts", 1) > 1 for item in results), "status_counts": {str(code): sum(item["status"] == code for item in results) for code in sorted({item["status"] for item in results})}}
    (ROOT / "reports" / "live-sitemap-crawl.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(json.dumps({"checked": payload["checked"], "status_counts": payload["status_counts"], "failures": len(failures), "slow_over_2s": len(slow)}, indent=2))
    checkpoint.unlink(missing_ok=True)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
