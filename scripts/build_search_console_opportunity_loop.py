#!/usr/bin/env python3
"""Map GSC non-brand performance and lead outcomes to every sitemap URL."""

from __future__ import annotations

import argparse
import csv
import math
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
import xml.etree.ElementTree as ET


ROOT = Path(__file__).resolve().parent.parent
BRAND_TERMS = ("jft", "jft agro", "jftagro", "jft agro overseas")


def number(value: str | None) -> float:
    if value is None:
        return 0.0
    cleaned = value.strip().replace(",", "").replace("%", "")
    return float(cleaned or 0)


def canonical_url(value: str) -> str:
    value = value.strip()
    if not value:
        return ""
    parts = urlsplit(value if "://" in value else f"https://jftagro.com/{value.lstrip('/')}")
    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path or "/"
    if path.endswith("/index.html"):
        path = path[:-10] or "/"
    if path != "/" and path.endswith("/"):
        path = path.rstrip("/") + "/"
    return urlunsplit(("https", host or "jftagro.com", path, "", ""))


def is_brand(query: str) -> bool:
    normalized = " ".join(query.lower().split())
    return any(term in normalized for term in BRAND_TERMS)


def expected_ctr(position: float) -> float:
    if position <= 1.5:
        return 0.28
    if position <= 3:
        return 0.14
    if position <= 5:
        return 0.08
    if position <= 10:
        return 0.05
    if position <= 20:
        return 0.025
    return 0.01


def position_weight(position: float) -> float:
    if position <= 3:
        return 0.25
    if position <= 10:
        return 1.0
    if position <= 20:
        return 0.85
    if position <= 40:
        return 0.55
    return 0.15


def sitemap_urls(path: Path) -> set[str]:
    root = ET.parse(path).getroot()
    namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    return {canonical_url(node.text or "") for node in root.findall("s:url/s:loc", namespace)}


def read_gsc(path: Path) -> tuple[dict[str, dict], list[dict]]:
    pages: dict[str, dict] = defaultdict(lambda: {"clicks": 0.0, "impressions": 0.0, "position_sum": 0.0, "queries": set(), "potential": 0.0})
    queries: list[dict] = []
    if not path.exists():
        return pages, queries
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = {field.lower(): field for field in (reader.fieldnames or [])}
        required = {"query", "page", "clicks", "impressions", "position"}
        missing = required - fields.keys()
        if missing:
            raise ValueError(f"GSC CSV missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            query = row[fields["query"]].strip()
            if not query or is_brand(query):
                continue
            page = canonical_url(row[fields["page"]])
            clicks = number(row[fields["clicks"]])
            impressions = number(row[fields["impressions"]])
            position = number(row[fields["position"]])
            if not page or impressions <= 0 or position <= 0:
                continue
            actual_ctr = clicks / impressions
            potential = max(expected_ctr(position) - actual_ctr, 0) * impressions * position_weight(position)
            record = pages[page]
            record["clicks"] += clicks
            record["impressions"] += impressions
            record["position_sum"] += position * impressions
            record["queries"].add(query)
            record["potential"] += potential
            queries.append({"query": query, "page": page, "clicks": clicks, "impressions": impressions, "ctr_percent": actual_ctr * 100, "position": position, "potential_click_uplift": potential})
    return pages, queries


def read_leads(path: Path | None) -> dict[str, dict[str, int]]:
    leads: dict[str, dict[str, int]] = defaultdict(lambda: {"enquiries": 0, "qualified_enquiries": 0, "won_contracts": 0})
    if path is None or not path.exists():
        return leads
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = {field.lower(): field for field in (reader.fieldnames or [])}
        required = {"landing_page", "enquiries", "qualified_enquiries", "won_contracts"}
        missing = required - fields.keys()
        if missing:
            raise ValueError(f"Lead CSV missing columns: {', '.join(sorted(missing))}")
        for row in reader:
            page = canonical_url(row[fields["landing_page"]])
            for metric in ("enquiries", "qualified_enquiries", "won_contracts"):
                leads[page][metric] += int(number(row[fields[metric]]))
    return leads


def action(impressions: float, position: float, ctr: float, benchmark: float) -> str:
    if impressions <= 0:
        return "no_gsc_data"
    if position <= 3:
        return "defend_and_refresh_sources"
    if position <= 20 and ctr < benchmark:
        return "improve_snippet_and_intent_match"
    if position <= 20:
        return "strengthen_conversion_path"
    if position <= 40:
        return "expand_content_and_internal_links"
    return "validate_query_relevance_before_investing"


def write_outputs(out_dir: Path, urls: set[str], pages: dict[str, dict], queries: list[dict], leads: dict[str, dict[str, int]]) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    all_urls = sorted(urls | set(pages) | set(leads))
    raw_scores = {page: pages[page]["potential"] + math.log1p(pages[page]["impressions"]) * position_weight((pages[page]["position_sum"] / pages[page]["impressions"]) if pages[page]["impressions"] else 100) for page in all_urls}
    ceiling = max(raw_scores.values(), default=0)
    rows = []
    for page in all_urls:
        item = pages[page]
        impressions = item["impressions"]
        clicks = item["clicks"]
        position = item["position_sum"] / impressions if impressions else 0
        ctr = clicks / impressions if impressions else 0
        benchmark = expected_ctr(position) if position else 0
        conversion = leads[page]
        rows.append({
            "page": page,
            "clicks": round(clicks, 2), "impressions": round(impressions, 2),
            "ctr_percent": round(ctr * 100, 3), "avg_position": round(position, 2),
            "nonbrand_queries": len(item["queries"]), "potential_click_uplift": round(item["potential"], 2),
            "enquiries": conversion["enquiries"], "qualified_enquiries": conversion["qualified_enquiries"], "won_contracts": conversion["won_contracts"],
            "opportunity_score": round((raw_scores[page] / ceiling * 100) if ceiling else 0, 1),
            "recommended_action": action(impressions, position, ctr, benchmark),
        })
    rows.sort(key=lambda row: (-row["opportunity_score"], -row["impressions"], row["page"]))
    page_path = out_dir / "search-console-page-opportunities.csv"
    with page_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]) if rows else ["page"])
        writer.writeheader(); writer.writerows(rows)
    queries.sort(key=lambda row: (-row["potential_click_uplift"], -row["impressions"]))
    query_path = out_dir / "search-console-query-opportunities.csv"
    with query_path.open("w", encoding="utf-8", newline="") as handle:
        fields = ["query", "page", "clicks", "impressions", "ctr_percent", "position", "potential_click_uplift"]
        writer = csv.DictWriter(handle, fieldnames=fields); writer.writeheader(); writer.writerows(queries)
    observed = sum(row["impressions"] > 0 for row in rows)
    summary = ["# Search Console Opportunity Loop", "", f"- Canonical URLs mapped: {len(rows)}", f"- URLs with non-brand impressions: {observed}", f"- Non-brand query rows: {len(queries)}", f"- URLs with recorded enquiries: {sum(row['enquiries'] > 0 for row in rows)}", ""]
    if not queries:
        summary.extend(["## Data gate", "", "No non-brand Search Console rows were supplied. Scores remain zero and `no_gsc_data` is not interpreted as no demand. Export Search Console performance by Query + Page (and Country when evaluating a locale), replace the input template, and rerun the command.", ""])
    else:
        summary.extend(["## Highest page opportunities", "", "| Score | Page | Impressions | CTR | Position | Action |", "|---:|---|---:|---:|---:|---|"])
        for row in rows[:20]:
            summary.append(f"| {row['opportunity_score']} | {row['page']} | {row['impressions']} | {row['ctr_percent']}% | {row['avg_position']} | {row['recommended_action']} |")
        summary.append("")
    summary.extend(["## Method boundary", "", "The score prioritizes observed non-brand impression opportunity and estimated CTR gap. It is a triage score, not a ranking forecast. Review query relevance, seasonality, country, device, regulatory freshness, conversion quality and business capacity before changing a page.", ""])
    (out_dir / "search-console-opportunity-loop.md").write_text("\n".join(summary), encoding="utf-8")
    print(f"Mapped {len(rows)} URLs; {observed} have non-brand impressions; wrote {out_dir}.")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gsc", type=Path, default=ROOT / "data/search-console/gsc-query-page-export.csv")
    parser.add_argument("--leads", type=Path, default=ROOT / "data/search-console/page-lead-outcomes.csv")
    parser.add_argument("--sitemap", type=Path, default=ROOT / "sitemap.xml")
    parser.add_argument("--out", type=Path, default=ROOT / "reports/search-console-opportunity-loop")
    args = parser.parse_args()
    pages, queries = read_gsc(args.gsc)
    leads = read_leads(args.leads)
    write_outputs(args.out, sitemap_urls(args.sitemap), pages, queries, leads)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
