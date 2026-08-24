#!/usr/bin/env python3
"""Exercise representative interactive journeys in a real browser."""

from __future__ import annotations

import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "interaction-gap-audit.json"
BASE = "http://127.0.0.1:8765/"


def main() -> int:
    results: list[dict] = []
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(channel="msedge", headless=True)
        context = browser.new_context(viewport={"width": 1440, "height": 1000}, service_workers="block")
        context.add_init_script("localStorage.setItem('jft_cookie_choice','essential')")

        def run(name: str, route: str, action, setup=None) -> None:
            page = context.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.on("console", lambda message: errors.append(message.text) if message.type == "error" else None)
            if setup:
                setup(page)
            try:
                page.goto(BASE + route, wait_until="networkidle", timeout=45_000)
                page.wait_for_timeout(600)
                details = action(page)
                overflow = page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth")
                results.append({"journey": name, "route": route, "passed": not errors and overflow <= 1, "overflow": overflow, "errors": errors, "details": details})
            except Exception as error:
                results.append({"journey": name, "route": route, "passed": False, "errors": errors + [str(error)]})
            finally:
                page.close()

        def quote(page):
            page.wait_for_selector("#mainPriceRange:not(:has-text('$0 - $0'))", timeout=12_000)
            before = page.locator("#mainPriceRange").inner_text()
            page.select_option("#calc-product", "cumin")
            page.click("#calculate-button")
            after = page.locator("#mainPriceRange").inner_text()
            return {"before": before, "after": after, "updated": before != after}

        def packing(page):
            page.wait_for_selector("#result-bags:not(:text-is('0'))", timeout=12_000)
            before = page.locator("#result-bags").inner_text()
            page.select_option("#bag-size", "25")
            page.click("#calculate-packing")
            after = page.locator("#result-bags").inner_text()
            return {"before": before, "after": after, "updated": before != after}

        def transit(page):
            page.wait_for_selector("#destination-port option", state="attached", timeout=12_000)
            options = page.locator("#destination-port option").all()
            value = options[min(2, len(options) - 1)].get_attribute("value")
            page.select_option("#destination-port", value)
            page.click("#update-transit")
            return {"route": page.locator("#result-route").inner_text(), "dates": page.locator("#result-dates").inner_text()}

        def tracker(page):
            page.fill("#shipment-reference", "INVALID")
            page.locator("form").first.evaluate("form => form.noValidate = true")
            page.locator("form").first.locator('button[type="submit"]').click()
            page.wait_for_timeout(200)
            return {"error": page.locator("#reference-error").inner_text(), "resultHidden": page.locator("#result-ready").is_hidden()}

        def faq(page):
            page.fill("#faq-search", "phytosanitary")
            visible = page.locator(".faq-item:visible").count()
            return {"visibleResults": visible}

        def blog(page):
            page.fill("#article-search", "psyllium")
            page.wait_for_timeout(150)
            return {"visibleArticles": page.locator(".article-card:visible").count()}

        def contact(page):
            page.click("#submitBtn")
            page.wait_for_timeout(200)
            invalid = page.locator("#rfqForm :invalid")
            return {"invalidControls": invalid.count(), "focusedControl": page.evaluate("document.activeElement && document.activeElement.id")}

        def inject_fallback_marker(page):
            marker = '<meta name="jft-localization" content="english-fallback">'

            def handle(route):
                response = route.fetch()
                body = response.text()
                if marker not in body:
                    body = body.replace("<head>", "<head>" + marker, 1)
                route.fulfill(response=response, body=body)

            page.route("**/ar/about.html", handle)

        def fallback(page):
            notice = page.locator("#jft-language-fallback")
            return {"visible": notice.is_visible(), "text": notice.inner_text()}

        run("quote recalculation", "quote-calculator.html", quote)
        run("packing recalculation", "packing-calculator.html", packing)
        run("transit route update", "port-transit-calculator.html", transit)
        run("tracker invalid reference", "shipment-tracker.html", tracker)
        run("FAQ search", "faq.html", faq)
        run("blog search", "blog.html", blog)
        run("contact validation", "contact.html", contact)
        run("localized fallback notice", "ar/about.html", fallback, setup=inject_fallback_marker)
        browser.close()

    REPORT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(results, indent=2, ensure_ascii=False))
    return 0 if all(item["passed"] for item in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
