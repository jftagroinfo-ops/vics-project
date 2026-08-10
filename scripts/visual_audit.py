#!/usr/bin/env python3
"""Browser-based visual health audit for every renderable HTML page."""

from __future__ import annotations

import argparse
import asyncio
import json
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote, urlsplit

from playwright.async_api import BrowserContext, Page, async_playwright

from audit_website import ROOT, UNPUBLISHED_BLOGS, page_paths


VIEWPORTS = {
    "desktop": {"width": 1440, "height": 900},
    "mobile": {"width": 390, "height": 844},
}
IGNORED_CONSOLE_PATTERNS = (
    "favicon.ico",
    "net::err_blocked_by_client",
)

VISUAL_CHECK = r"""
() => {
  const visible = (el) => {
    const s = getComputedStyle(el);
    const r = el.getBoundingClientRect();
    return s.display !== 'none' && s.visibility !== 'hidden' &&
      Number(s.opacity) > 0.02 && r.width > 1 && r.height > 1;
  };
  const label = (el) => {
    const id = el.id ? `#${el.id}` : '';
    const cls = [...el.classList].slice(0, 2).map(x => `.${x}`).join('');
    return `${el.tagName.toLowerCase()}${id}${cls}`;
  };
  const doc = document.documentElement;
  const body = document.body;
  const h1 = document.querySelector('h1');
  const brokenImages = [...document.images]
    .filter(img => visible(img) && img.complete && img.naturalWidth === 0)
    .filter(img => !img.currentSrc || new URL(img.currentSrc, location.href).origin === location.origin)
    .map(img => img.currentSrc || img.src || label(img)).slice(0, 10);
  const clipped = [...document.querySelectorAll('button, [role="button"], h1, h2, h3, nav a')]
    .filter(visible)
    .filter(el => {
      const s = getComputedStyle(el);
      const clipsX = ['hidden', 'clip', 'auto', 'scroll'].includes(s.overflowX);
      const clipsY = ['hidden', 'clip', 'auto', 'scroll'].includes(s.overflowY);
      return (clipsX && el.scrollWidth > el.clientWidth + 3) ||
        (clipsY && el.scrollHeight > el.clientHeight + 3);
    })
    .map(label).slice(0, 10);
  const outside = [...document.querySelectorAll('button, input, select, textarea, h1, h2, h3')]
    .filter(visible)
    .filter(el => {
      const r = el.getBoundingClientRect();
      let intentionallyClipped = false;
      for (let parent = el.parentElement; parent; parent = parent.parentElement) {
        if (['auto', 'scroll', 'hidden'].includes(getComputedStyle(parent).overflowX)) {
          intentionallyClipped = true;
          break;
        }
      }
      return !intentionallyClipped && (r.right < -2 || r.left > innerWidth + 2);
    }).map(label).slice(0, 10);
  const interactives = [...document.querySelectorAll('a, button, input, select, textarea')]
    .filter(visible).filter(el => {
      const r = el.getBoundingClientRect();
      return r.bottom > 0 && r.top < innerHeight &&
        !el.matches('.wa-fab, .smart-wa-widget, #backToTop');
    }).slice(0, 100);
  const overlaps = [];
  for (let i = 0; i < interactives.length && overlaps.length < 10; i++) {
    for (let j = i + 1; j < interactives.length && overlaps.length < 10; j++) {
      const a = interactives[i], b = interactives[j];
      if (a.closest('#jft-cookie-bar') || b.closest('#jft-cookie-bar')) continue;
      if (a.contains(b) || b.contains(a) || a.parentElement === b.parentElement &&
          getComputedStyle(a.parentElement).display === 'flex') continue;
      const x = a.getBoundingClientRect(), y = b.getBoundingClientRect();
      const w = Math.max(0, Math.min(x.right, y.right) - Math.max(x.left, y.left));
      const h = Math.max(0, Math.min(x.bottom, y.bottom) - Math.max(x.top, y.top));
      const area = w * h;
      const smaller = Math.min(x.width * x.height, y.width * y.height);
      if (smaller > 0 && area / smaller > 0.35) overlaps.push(`${label(a)} <> ${label(b)}`);
    }
  }
  const h1Rect = h1 ? h1.getBoundingClientRect() : null;
  return {
    title: document.title,
    bodyTextLength: (body?.innerText || '').trim().length,
    bodyHeight: body?.scrollHeight || 0,
    horizontalOverflow: Math.max(doc.scrollWidth, body?.scrollWidth || 0) > innerWidth + 3,
    overflowPixels: Math.max(0, Math.max(doc.scrollWidth, body?.scrollWidth || 0) - innerWidth),
    h1Visible: !!(h1 && visible(h1) && h1Rect.bottom > 0),
    brokenImages,
    clipped,
    outside,
    overlaps,
  };
}
"""


def safe_name(relative: str, viewport: str) -> str:
    stem = re.sub(r"[^a-zA-Z0-9._-]+", "_", relative).strip("._")
    return f"{stem[:150]}--{viewport}.png"


async def prepare_page(page: Page, base_host: str, events: dict[str, list[str]]) -> None:
    async def route_request(route):
        host = urlsplit(route.request.url).netloc
        if host and host != base_host:
            await route.abort("blockedbyclient")
        else:
            await route.continue_()

    await page.route("**/*", route_request)

    def on_console(message) -> None:
        if message.type != "error":
            return
        text = message.text
        if not any(pattern in text.lower() for pattern in IGNORED_CONSOLE_PATTERNS):
            events["console"].append(text[:500])

    def on_page_error(error) -> None:
        events["pageErrors"].append(str(error)[:500])

    def on_response(response) -> None:
        parsed = urlsplit(response.url)
        if parsed.netloc == base_host and response.status >= 400:
            events["failedAssets"].append(f"{response.status} {parsed.path}")

    page.on("console", on_console)
    page.on("pageerror", on_page_error)
    page.on("response", on_response)


async def settle_page(page: Page) -> None:
    try:
        await page.wait_for_function(
            """() => {
              const slot = document.querySelector('#header-placeholder');
              return !slot || slot.children.length > 0;
            }""",
            timeout=700,
        )
    except Exception:
        pass
    await page.wait_for_timeout(150)
    await page.add_style_tag(content="""
      *, *::before, *::after { animation-duration: 0s !important; transition-duration: 0s !important; }
      html { scroll-behavior: auto !important; }
      #preloader { display: none !important; }
      .reveal, .reveal-left, .reveal-right { opacity: 1 !important; transform: none !important; }
    """)
    await page.evaluate("""
      async () => {
        const height = Math.min(document.body.scrollHeight, 12000);
        for (const ratio of [0.35, 0.7, 1]) {
          scrollTo(0, height * ratio);
          await new Promise(resolve => setTimeout(resolve, 30));
        }
        scrollTo(0, 0);
        await new Promise(resolve => setTimeout(resolve, 60));
      }
    """)


def result_findings(result: dict) -> list[str]:
    findings = []
    if result.get("status", 200) >= 400:
        findings.append(f"HTTP {result['status']}")
    if result.get("navigationError"):
        findings.append("navigation error")
    checks = result.get("checks", {})
    redirect_page = Path(result.get("page", "")).name in UNPUBLISHED_BLOGS
    if not redirect_page and (checks.get("bodyTextLength", 0) < 40 or checks.get("bodyHeight", 0) < 100):
        findings.append("page appears blank")
    if not checks.get("h1Visible", False):
        findings.append("H1 is not visible")
    if checks.get("horizontalOverflow"):
        findings.append(f"horizontal overflow ({checks.get('overflowPixels', 0)}px)")
    for key, label in (
        ("brokenImages", "broken images"),
        ("clipped", "clipped controls/headings"),
        ("outside", "off-screen content"),
        ("overlaps", "overlapping controls"),
    ):
        if checks.get(key):
            findings.append(f"{label}: {', '.join(checks[key][:3])}")
    events = result.get("events", {})
    if events.get("failedAssets"):
        findings.append(f"failed local assets: {', '.join(sorted(set(events['failedAssets']))[:3])}")
    if events.get("pageErrors"):
        findings.append(f"JavaScript errors: {events['pageErrors'][0]}")
    if events.get("console"):
        findings.append(f"console errors: {events['console'][0]}")
    return findings


async def audit_page(
    context: BrowserContext,
    base_url: str,
    relative: str,
    viewport_name: str,
    screenshot_dir: Path,
) -> dict:
    page = await context.new_page()
    await page.set_viewport_size(VIEWPORTS[viewport_name])
    events = {"console": [], "pageErrors": [], "failedAssets": []}
    base_host = urlsplit(base_url).netloc
    await prepare_page(page, base_host, events)
    url = f"{base_url.rstrip('/')}/{quote(relative, safe='/')}"
    result = {"page": relative, "viewport": viewport_name, "url": url, "events": events}
    try:
        response = await page.goto(url, wait_until="domcontentloaded", timeout=6000)
        result["status"] = response.status if response else 0
        await settle_page(page)
        result["checks"] = await page.evaluate(VISUAL_CHECK)
    except Exception as error:
        result["navigationError"] = str(error)[:500]
        result.setdefault("checks", {})
    result["findings"] = result_findings(result)
    if result["findings"]:
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        try:
            await page.screenshot(
                path=screenshot_dir / safe_name(relative, viewport_name),
                full_page=False,
            )
        except Exception:
            pass
    await page.close()
    return result


async def run(args: argparse.Namespace) -> list[dict]:
    paths = page_paths()
    if args.offset:
        paths = paths[args.offset :]
    if args.limit:
        paths = paths[: args.limit]
    jobs = [
        (path.relative_to(ROOT).as_posix(), viewport)
        for path in paths
        for viewport in VIEWPORTS
    ]
    screenshot_dir = ROOT / args.screenshot_dir
    results: list[dict] = []
    queue: asyncio.Queue[tuple[str, str]] = asyncio.Queue()
    for job in jobs:
        queue.put_nowait(job)

    async with async_playwright() as playwright:
        launch_options = {
            "headless": True,
            "args": ["--disable-gpu", "--no-sandbox"],
        }
        if args.chrome and Path(args.chrome).exists():
            launch_options["executable_path"] = args.chrome
        browser = await playwright.chromium.launch(**launch_options)

        async def worker() -> None:
            context = await browser.new_context(service_workers="block")
            try:
                while not queue.empty():
                    try:
                        relative, viewport = queue.get_nowait()
                    except asyncio.QueueEmpty:
                        return
                    results.append(
                        await audit_page(context, args.base_url, relative, viewport, screenshot_dir)
                    )
                    if len(results) % 10 == 0:
                        print(f"Audited {len(results)}/{len(jobs)} page-viewports", flush=True)
                    queue.task_done()
            finally:
                await context.close()

        await asyncio.gather(*(worker() for _ in range(args.workers)))
        await browser.close()
    return sorted(results, key=lambda item: (item["page"], item["viewport"]))


def write_reports(results: list[dict], report_path: Path) -> None:
    report_path = report_path.resolve()
    report_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generatedAt": datetime.now(timezone.utc).isoformat(),
        "pageViewports": len(results),
        "pages": len({item["page"] for item in results}),
        "viewports": VIEWPORTS,
        "results": results,
    }
    report_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    failures = [item for item in results if item["findings"]]
    counts = Counter(finding.split(":", 1)[0] for item in failures for finding in item["findings"])
    lines = [
        "# Visual Audit Report",
        "",
        f"- Pages: {payload['pages']}",
        f"- Page-viewports: {payload['pageViewports']}",
        f"- Failed page-viewports: {len(failures)}",
        f"- Generated: {payload['generatedAt']}",
        "",
        "## Checks Performed",
        "",
        "- Desktop and mobile responsive rendering",
        "- Blank or hidden primary content and H1 visibility",
        "- Horizontal overflow, clipped text, and off-screen controls",
        "- Interactive-control collisions",
        "- Broken local images and HTTP asset failures",
        "- JavaScript page errors and console errors",
        "",
        "## Finding Counts",
        "",
    ]
    if counts:
        lines.extend(f"- {name}: {count}" for name, count in sorted(counts.items()))
    else:
        lines.append("- None")
    lines.extend(["", "## Findings", ""])
    if not failures:
        lines.append("No automated visual-health findings.")
    for item in failures:
        lines.append(f"### {item['page']} ({item['viewport']})")
        lines.extend(f"- {finding}" for finding in item["findings"])
        lines.append("")
    report_path.with_suffix(".md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Audited {payload['pages']} pages across {payload['pageViewports']} page-viewports.")
    print(f"Failed page-viewports: {len(failures)}")
    print(f"Report: {report_path.relative_to(ROOT).as_posix()}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8765")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--offset", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--report", default="reports/visual-audit.json")
    parser.add_argument("--screenshot-dir", default="reports/visual-audit-screenshots")
    parser.add_argument(
        "--chrome",
        default=r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    )
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    audit_results = asyncio.run(run(arguments))
    write_reports(audit_results, ROOT / arguments.report)
    raise SystemExit(1 if any(item["findings"] for item in audit_results) else 0)
