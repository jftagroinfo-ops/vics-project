#!/usr/bin/env python3
"""Real-browser accessibility and interaction smoke test for key templates."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "browser-accessibility-smoke.json"
BASE = "http://127.0.0.1:8765"
PAGES = (
    "index.html", "about.html", "products.html", "1121-basmati-rice-exporter.html",
    "contact.html", "sample-request.html", "quote-calculator.html", "privacy.html",
    "terms.html", "buyer-security.html",
)
VIEWPORTS = ({"name": "mobile", "width": 390, "height": 844}, {"name": "desktop", "width": 1440, "height": 1000})


AUDIT_JS = """() => {
  const visible = el => !!(el.offsetWidth || el.offsetHeight || el.getClientRects().length);
  const controls = [...document.querySelectorAll('input:not([type=hidden]),select,textarea')].filter(visible).filter(el => el.getAttribute('aria-hidden') !== 'true');
  const missingLabels = controls.filter(el => {
    const idLabel = el.id && document.querySelector(`label[for="${CSS.escape(el.id)}"]`);
    return !idLabel && !el.closest('label') && !el.getAttribute('aria-label') && !el.getAttribute('aria-labelledby');
  }).map(el => el.name || el.id || el.tagName);
  const unnamedButtons = [...document.querySelectorAll('button')].filter(visible).filter(el =>
    !(el.innerText || '').trim() && !el.getAttribute('aria-label') && !el.getAttribute('title')
  ).length;
  const ids = [...document.querySelectorAll('[id]')].map(el => el.id);
  const duplicateIds = [...new Set(ids.filter((id, i) => ids.indexOf(id) !== i))];
  return {
    lang: document.documentElement.lang,
    h1: document.querySelectorAll('h1').length,
    main: document.querySelectorAll('main,[role=main]').length,
    overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
    brokenImages: [...document.images].filter(img => img.getAttribute('src') && img.complete && img.naturalWidth === 0).length,
    missingLabels,
    unnamedButtons,
    duplicateIds,
  };
}"""


def main() -> int:
    results = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        for viewport in VIEWPORTS:
            context = browser.new_context(viewport={"width": viewport["width"], "height": viewport["height"]})
            context.add_init_script("localStorage.setItem('jft_cookie_choice','essential')")
            for route in PAGES:
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                page.goto(f"{BASE}/{route}", wait_until="networkidle", timeout=45_000)
                page.wait_for_timeout(500)
                metrics = page.evaluate(AUDIT_JS)
                page.keyboard.press("Tab")
                focus_moved = page.evaluate("document.activeElement !== document.body")
                passed = (
                    not errors and metrics["lang"] == "en" and metrics["h1"] == 1 and metrics["main"] >= 1
                    and metrics["overflow"] <= 1 and metrics["brokenImages"] == 0 and not metrics["missingLabels"]
                    and metrics["unnamedButtons"] == 0 and not metrics["duplicateIds"] and focus_moved
                )
                results.append({"viewport": viewport["name"], "route": route, "passed": passed, "errors": errors, "focusMoved": focus_moved, **metrics})
                page.close()
            context.close()
        browser.close()
    REPORT.write_text(json.dumps(results, indent=2), encoding="utf-8")
    failures = [item for item in results if not item["passed"]]
    print(json.dumps({"tested": len(results), "passed": len(results) - len(failures), "failed": failures}, indent=2))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
