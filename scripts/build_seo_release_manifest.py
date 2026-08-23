#!/usr/bin/env python3
"""Build a deployment and post-deployment URL manifest from the dirty worktree."""

from __future__ import annotations

import argparse
import csv
import subprocess
from collections import Counter
from pathlib import Path
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parent.parent
NS = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
IGNORED_PARTS = {".git", ".cloudflare-dist", ".wrangler", ".wrangler-dry-run", "node_modules", "reports", "__pycache__"}
EXCLUDED_NAMES = {
    "cookie-consent-snippet.html",
    "footer.html",
    "header.html",
    "inner-page-hero-snippet.html",
    "product-page-template.html",
    "seo-universal-head-snippet.html",
}


def sitemap_urls(path: Path) -> set[str]:
    root = ET.parse(path).getroot()
    return {node.text.strip() for node in root.findall(".//s:loc", NS) if node.text}


def production_urls(url: str) -> set[str]:
    request = Request(url, headers={"User-Agent": "JFT-SEO-Release-Manifest/1.0"})
    with urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())
    return {node.text.strip() for node in root.findall(".//s:loc", NS) if node.text}


def changed_files() -> list[tuple[str, Path]]:
    result = subprocess.run(
        ["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"],
        cwd=ROOT, check=True, capture_output=True,
    )
    entries = result.stdout.decode("utf-8", errors="surrogateescape").split("\0")
    changed: list[tuple[str, Path]] = []
    index = 0
    while index < len(entries):
        entry = entries[index]
        if not entry:
            index += 1
            continue
        state = entry[:2]
        relative = entry[3:]
        if "R" in state or "C" in state:
            index += 1  # Skip the old path emitted as the next NUL field.
        path = Path(relative)
        if (
            path.suffix.lower() == ".html"
            and path.name not in EXCLUDED_NAMES
            and not path.name.startswith("yandex_")
            and not any(
                part in IGNORED_PARTS
                or part.startswith(".cloudflare-dist")
                or part.startswith(".wrangler")
                or part.startswith("backup_")
                for part in path.parts
            )
        ):
            changed.append((state.strip() or "M", path))
        index += 1
    return changed


def inspect_html(path: Path, local_urls: set[str], live_urls: set[str]) -> dict[str, str]:
    absolute = ROOT / path
    if not absolute.exists():
        return {"canonical_url": "", "indexable": "no", "in_local_sitemap": "no", "production_state": "deleted", "release_action": "review_deletion_or_redirect"}
    soup = BeautifulSoup(absolute.read_text(encoding="utf-8", errors="replace"), "html.parser")
    canonical = soup.find("link", rel="canonical")
    url = canonical.get("href", "").strip() if canonical else ""
    robots = soup.find("meta", attrs={"name": lambda value: value and value.lower() == "robots"})
    indexable = not bool(robots and "noindex" in robots.get("content", "").lower())
    in_sitemap = bool(url and url in local_urls)
    if not indexable:
        production_state, action = "nonindexable", "deploy_no_index_submission"
    elif not url:
        production_state, action = "missing_canonical", "block_release"
    elif not in_sitemap:
        production_state, action = "missing_local_sitemap", "block_release"
    elif url not in live_urls:
        production_state, action = "new_url", "crawl_after_deploy_then_submit"
    else:
        production_state, action = "changed_existing_url", "crawl_after_deploy"
    return {
        "canonical_url": url,
        "indexable": "yes" if indexable else "no",
        "in_local_sitemap": "yes" if in_sitemap else "no",
        "production_state": production_state,
        "release_action": action,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--production-sitemap", default="https://jftagro.com/sitemap.xml")
    parser.add_argument("--out", type=Path, default=ROOT / "reports/seo-release-manifest")
    args = parser.parse_args()
    local_urls = sitemap_urls(ROOT / "sitemap.xml")
    try:
        live_urls = production_urls(args.production_sitemap)
        live_status = "fetched"
    except Exception as error:  # The manifest remains useful offline.
        live_urls = set()
        live_status = f"unavailable: {error}"
    rows = []
    for state, path in changed_files():
        rows.append({"git_state": state, "file": path.as_posix(), **inspect_html(path, local_urls, live_urls)})
    rows.sort(key=lambda row: (row["production_state"], row["canonical_url"], row["file"]))
    args.out.mkdir(parents=True, exist_ok=True)
    fields = ["git_state", "file", "canonical_url", "indexable", "in_local_sitemap", "production_state", "release_action"]
    with (args.out / "changed-html-manifest.csv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(rows)
    submit_urls = sorted({row["canonical_url"] for row in rows if row["release_action"] in {"crawl_after_deploy_then_submit", "crawl_after_deploy"}})
    (args.out / "post-deploy-crawl-urls.txt").write_text("\n".join(submit_urls) + ("\n" if submit_urls else ""), encoding="utf-8")
    states = Counter(row["production_state"] for row in rows)
    blockers = [row for row in rows if row["release_action"] == "block_release"]
    new_urls = sorted(local_urls - live_urls) if live_urls else []
    missing_urls = sorted(live_urls - local_urls) if live_urls else []
    summary = [
        "# SEO Release Manifest",
        "",
        f"- Changed source HTML files: {len(rows)}",
        f"- Unique changed indexable URLs for post-deployment crawl: {len(submit_urls)}",
        f"- Local sitemap URLs: {len(local_urls)}",
        f"- Production sitemap status: {live_status}",
        f"- Production sitemap URLs: {len(live_urls)}",
        f"- New local URLs: {len(new_urls)}",
        f"- Production URLs missing locally: {len(missing_urls)}",
        f"- Release blockers: {len(blockers)}",
        "",
        "## Changed-page states",
        "",
    ]
    summary.extend(f"- {key}: {value}" for key, value in sorted(states.items()))
    summary.extend(["", "## New URLs to verify after deployment", ""])
    summary.extend(f"- {url}" for url in new_urls) if new_urls else summary.append("- None detected or production sitemap unavailable.")
    summary.extend(["", "## Guardrail", "", "This manifest authorizes no deployment or indexing submission. Crawl the deployed URLs first, confirm direct 200 responses, self-canonicals, rendered content and sitemap inclusion, then submit only verified URLs.", ""])
    (args.out / "seo-release-manifest.md").write_text("\n".join(summary), encoding="utf-8")
    print(f"Manifested {len(rows)} changed HTML files; {len(new_urls)} new URLs; {len(blockers)} blockers.")
    return 1 if blockers else 0


if __name__ == "__main__":
    raise SystemExit(main())
