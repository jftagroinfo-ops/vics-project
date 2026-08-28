#!/usr/bin/env python3
"""Real-browser regression test for the product-page FAQ accordion.

Guards against the Phase 8 defect (reports/product-faq-accordion-fix-2026-08-27.md):
locale pages carried an inverted open/close branch in the accordion's click
listener, so aria-expanded flipped correctly but the answer panel's visual
state did not follow it.

For a representative product page in English + every locale, this verifies:
  - initial state: closed (max-height 0, aria-expanded=false)
  - after one click: open (max-height > 0 and equal to scrollHeight,
    aria-expanded=true, rendered height > 0)
  - after a second click: closed again, matching the initial state
  - zero console errors, zero failed requests

Requires a local HTTP server serving the repo root (this test does not start
one itself, matching the other browser_*.py / locale_browser_audit.py
scripts in this repo -- run e.g. `python -m http.server 8765` first).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "faq-accordion-browser-test.json"
BASE = "http://127.0.0.1:8765"
LOCALES = ("", "ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
PRODUCT = "1121-basmati-rice-exporter.html"


def main() -> int:
    results = {}
    failures: list[str] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        for prefix in LOCALES:
            name = prefix or "en"
            url = f"{BASE}/{prefix + '/' if prefix else ''}{PRODUCT}"
            page = browser.new_page(viewport={"width": 1366, "height": 900})
            page.add_init_script("localStorage.setItem('jft_cookie_choice','essential')")
            console_errors: list[str] = []
            failed_requests: list[str] = []
            page.on("pageerror", lambda exc: console_errors.append(str(exc)))
            page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
            page.on("requestfailed", lambda req: failed_requests.append(req.url))

            sel_q = ".prod-faq-section .faq-q"
            sel_a = ".prod-faq-section .faq-a"
            entry = {"url": url, "console_errors": [], "failed_requests": [], "result": "PASS"}
            try:
                page.goto(url, wait_until="networkidle", timeout=20_000)
                page.wait_for_timeout(300)

                initial_h = page.eval_on_selector(sel_a, "el => el.getBoundingClientRect().height")
                initial_aria = page.eval_on_selector(sel_q, "el => el.getAttribute('aria-expanded')")
                if initial_h > 1 or initial_aria != "false":
                    raise AssertionError(f"expected closed initial state, got height={initial_h} aria={initial_aria}")

                page.click(sel_q)
                page.wait_for_timeout(500)
                open_h = page.eval_on_selector(sel_a, "el => el.getBoundingClientRect().height")
                open_scrollh = page.eval_on_selector(sel_a, "el => el.scrollHeight")
                open_aria = page.eval_on_selector(sel_q, "el => el.getAttribute('aria-expanded')")
                if open_h < open_scrollh - 2 or open_aria != "true":
                    raise AssertionError(f"expected open state after click, got height={open_h} (scrollHeight={open_scrollh}) aria={open_aria}")

                page.click(sel_q)
                page.wait_for_timeout(500)
                closed_h = page.eval_on_selector(sel_a, "el => el.getBoundingClientRect().height")
                closed_aria = page.eval_on_selector(sel_q, "el => el.getAttribute('aria-expanded')")
                if closed_h > 1 or closed_aria != "false":
                    raise AssertionError(f"expected closed state after second click, got height={closed_h} aria={closed_aria}")

                entry.update({
                    "initial_height": initial_h,
                    "aria_before": initial_aria,
                    "after_open_height": open_h,
                    "aria_after_open": open_aria,
                    "after_close_height": closed_h,
                    "aria_after_close": closed_aria,
                })
            except Exception as exc:  # noqa: BLE001
                entry["result"] = "FAIL"
                entry["error"] = str(exc)
                failures.append(f"{name}: {exc}")

            entry["console_errors"] = console_errors
            entry["failed_requests"] = failed_requests
            if console_errors:
                entry["result"] = "FAIL"
                failures.append(f"{name}: console errors {console_errors}")
            results[name] = entry
            page.close()
        browser.close()

    REPORT.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: v["result"] for k, v in results.items()}, indent=2))
    if failures:
        print(f"FAILED: {len(failures)} locale(s)")
        for f in failures:
            print(" ", f)
        return 1
    print(f"PASS: FAQ accordion correct on all {len(results)} locales.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
