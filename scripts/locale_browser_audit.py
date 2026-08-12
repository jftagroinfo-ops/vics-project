#!/usr/bin/env python3
"""Render representative pages for every locale at desktop and mobile sizes."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "locale-browser-audit.json"
BASE = "http://127.0.0.1:8765"
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
PAGES = ("index.html", "products.html", "blog-basmati-export-guide.html", "terms.html")


def main() -> int:
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        for viewport in ({"name": "desktop", "width": 1440, "height": 1000}, {"name": "mobile", "width": 390, "height": 844}):
            context = browser.new_context(viewport={"width": viewport["width"], "height": viewport["height"]})
            context.add_init_script("localStorage.setItem('jft_cookie_choice','essential')")
            for locale in LOCALES:
                for route in PAGES:
                    page = context.new_page()
                    errors = []
                    page.on("pageerror", lambda error: errors.append(str(error)))
                    page.on("console", lambda message: errors.append(message.text) if message.type == "error" and "Failed to load resource" not in message.text else None)
                    try:
                        page.goto(f"{BASE}/{locale}/{route}", wait_until="networkidle", timeout=45_000)
                        page.wait_for_timeout(400)
                        metrics = page.evaluate("""() => ({
                          lang: document.documentElement.lang,
                          dir: document.documentElement.dir,
                          overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
                          h1: document.querySelector('h1')?.innerText.trim() || '',
                          images: [...document.images].filter(img => img.getAttribute('src') && img.complete && img.naturalWidth === 0).length,
                          fallback: !!document.querySelector('meta[name="jft-localization"][content="english-fallback"]')
                        })""")
                        passed = not errors and metrics["overflow"] <= 1 and metrics["images"] == 0 and metrics["lang"] == locale and bool(metrics["h1"]) and not metrics["fallback"] and (locale != "ar" or metrics["dir"] == "rtl")
                        results.append({"viewport": viewport["name"], "locale": locale, "route": route, "passed": passed, "errors": errors, **metrics})
                    except Exception as error:
                        results.append({"viewport": viewport["name"], "locale": locale, "route": route, "passed": False, "errors": errors + [str(error)]})
                    page.close()
            context.close()
        browser.close()
    REPORT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    failed = [item for item in results if not item["passed"]]
    summary = json.dumps({"tested": len(results), "passed": len(results) - len(failed), "failed": failed}, ensure_ascii=False, indent=2)
    try:
        print(summary)
    except UnicodeEncodeError:
        print(summary.encode("ascii", "backslashreplace").decode("ascii"))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
