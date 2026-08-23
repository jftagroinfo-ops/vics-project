#!/usr/bin/env python3
"""Analyze the separate CSV tables produced by a GSC Performance export."""

from __future__ import annotations

import argparse
import csv
import math
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit


BRAND_TERMS = ("jft", "jft agro", "jftagro", "jft agro overseas")


def number(value: str | None) -> float:
    return float((value or "0").strip().replace(",", "").replace("%", "") or 0)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def canonical_url(value: str) -> str:
    parts = urlsplit(value.strip())
    host = parts.netloc.lower().removeprefix("www.")
    path = parts.path or "/"
    if path.endswith("/index.html"):
        path = path[:-10] or "/"
    return urlunsplit(("https", host, path, "", ""))


def is_brand(query: str) -> bool:
    normalized = " ".join(query.casefold().split())
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


def candidate_target(query: str) -> tuple[str, str]:
    q = query.casefold()
    rules = (
        (("cif", "fob", "price calculator"), "https://jftagro.com/quote-calculator.html", "calculator intent"),
        (("bags", "container"), "https://jftagro.com/packing-calculator.html", "container packing intent"),
        (("cumin", "jeera", "சீரகம்"), "https://jftagro.com/blog-cumin-jeera-price-outlook-2026.html", "cumin price/information intent"),
        (("psyllium",), "https://jftagro.com/blog-psyllium-husk-export-india-2026.html", "psyllium export-guide intent"),
        (("re-export dubai", "seeds to dubai", "pulses in dubai", "herbs business in united arab emirates"), "https://jftagro.com/uae-trade.html", "UAE trade intent"),
        (("grains trade in asia",), "https://jftagro.com/asia-trade.html", "Asia trade intent"),
        (("chakki", "atta exporter"), "https://jftagro.com/wheat-flour-chakki-fresh-atta-exporter.html", "wheat-flour product intent"),
        (("moringa powder",), "https://jftagro.com/moringa-powder-exporter.html", "moringa product intent"),
    )
    for needles, target, rationale in rules:
        if any(needle in q for needle in needles):
            return target, rationale
    return "", "requires query-to-page API export"


def action(impressions: float, position: float, ctr: float) -> str:
    if position <= 3:
        return "defend_and_monitor"
    if position <= 20 and ctr < expected_ctr(position):
        return "review_snippet_and_intent_after_post_release_window"
    if position <= 20:
        return "strengthen_conversion_measurement"
    if position <= 40:
        return "expand_relevant_content_and_links_after_validation"
    return "validate_relevance_before_investing"


def write_csv(path: Path, output_rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(output_rows[0]) if output_rows else ["no_data"])
        writer.writeheader()
        writer.writerows(output_rows)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    source = args.input_dir
    out = args.out
    out.mkdir(parents=True, exist_ok=True)

    filters = rows(source / "Filters.csv")
    date_range = next((row["Value"] for row in filters if row.get("Filter") == "Date"), "unknown")

    chart = []
    for row in rows(source / "Chart.csv"):
        start_text, end_text = row["Date range"].split(" - ")
        days = (date.fromisoformat(end_text) - date.fromisoformat(start_text)).days + 1
        clicks, impressions = number(row["Clicks"]), number(row["Impressions"])
        chart.append({"date_range": row["Date range"], "days": days, "clicks": int(clicks), "impressions": int(impressions), "ctr_percent": round(number(row["CTR"]), 2), "position": round(number(row["Position"]), 2), "clicks_per_day": round(clicks / days, 3), "impressions_per_day": round(impressions / days, 3)})

    page_items = []
    for row in rows(source / "Pages.csv"):
        clicks, impressions = number(row["Clicks"]), number(row["Impressions"])
        ctr, position = number(row["CTR"]) / 100, number(row["Position"])
        potential = max(expected_ctr(position) - ctr, 0) * impressions * position_weight(position)
        page_items.append({"page": canonical_url(row["Top pages"]), "clicks": int(clicks), "impressions": int(impressions), "ctr_percent": round(ctr * 100, 2), "position": round(position, 2), "estimated_ctr_gap_clicks": round(potential, 2), "recommended_action": action(impressions, position, ctr)})
    ceiling = max((item["estimated_ctr_gap_clicks"] + math.log1p(item["impressions"]) for item in page_items), default=1)
    for item in page_items:
        raw = item["estimated_ctr_gap_clicks"] + math.log1p(item["impressions"])
        item["opportunity_score"] = round(raw / ceiling * 100, 1)
    page_items.sort(key=lambda item: (-item["opportunity_score"], -item["impressions"], item["page"]))

    query_items = []
    brand_queries = 0
    for row in rows(source / "Queries.csv"):
        query = row["Top queries"].strip()
        if is_brand(query):
            brand_queries += 1
            continue
        clicks, impressions = number(row["Clicks"]), number(row["Impressions"])
        ctr, position = number(row["CTR"]) / 100, number(row["Position"])
        potential = max(expected_ctr(position) - ctr, 0) * impressions * position_weight(position)
        target, rationale = candidate_target(query)
        query_items.append({"query": query, "clicks": int(clicks), "impressions": int(impressions), "ctr_percent": round(ctr * 100, 2), "position": round(position, 2), "estimated_ctr_gap_clicks": round(potential, 2), "candidate_target": target, "mapping_basis": rationale, "recommended_action": action(impressions, position, ctr)})
    query_items.sort(key=lambda item: (-item["estimated_ctr_gap_clicks"], -item["impressions"], item["query"]))

    country_items = [{"country": row["Country"], "clicks": int(number(row["Clicks"])), "impressions": int(number(row["Impressions"])), "ctr_percent": round(number(row["CTR"]), 2), "position": round(number(row["Position"]), 2)} for row in rows(source / "Countries.csv")]
    device_items = [{"device": row["Device"], "clicks": int(number(row["Clicks"])), "impressions": int(number(row["Impressions"])), "ctr_percent": round(number(row["CTR"]), 2), "position": round(number(row["Position"]), 2)} for row in rows(source / "Devices.csv")]
    appearance_items = [{"search_appearance": row["Search Appearance"], "clicks": int(number(row["Clicks"])), "impressions": int(number(row["Impressions"])), "ctr_percent": round(number(row["CTR"]), 2), "position": round(number(row["Position"]), 2)} for row in rows(source / "Search appearance.csv")]

    write_csv(out / "page-opportunities.csv", page_items)
    write_csv(out / "nonbrand-query-opportunities.csv", query_items)
    write_csv(out / "countries.csv", country_items)
    write_csv(out / "devices.csv", device_items)
    write_csv(out / "search-appearance.csv", appearance_items)
    write_csv(out / "trend.csv", chart)

    clicks = sum(item["clicks"] for item in chart)
    impressions = sum(item["impressions"] for item in chart)
    weighted_position = sum(item["position"] * item["impressions"] for item in chart) / impressions
    nonbrand_clicks = sum(item["clicks"] for item in query_items)
    nonbrand_impressions = sum(item["impressions"] for item in query_items)
    summary = [
        "# Search Console Performance Analysis",
        "",
        f"- Export date range: {date_range}",
        f"- Total clicks: {clicks:,}",
        f"- Total impressions: {impressions:,}",
        f"- Weighted CTR: {(clicks / impressions * 100):.2f}%",
        f"- Impression-weighted average position: {weighted_position:.2f}",
        f"- Exported non-brand query rows: {len(query_items):,}",
        f"- Visible non-brand query clicks/impressions: {nonbrand_clicks:,}/{nonbrand_impressions:,}",
        f"- Brand query rows excluded: {brand_queries:,}",
        f"- Page rows: {len(page_items):,}; country rows: {len(country_items):,}; device rows: {len(device_items):,}",
        "",
        "## Highest observed page opportunities",
        "",
        "| Score | Page | Impressions | CTR | Position | Estimated CTR-gap clicks |",
        "|---:|---|---:|---:|---:|---:|",
    ]
    for item in page_items[:15]:
        summary.append(f"| {item['opportunity_score']} | {item['page']} | {item['impressions']} | {item['ctr_percent']}% | {item['position']} | {item['estimated_ctr_gap_clicks']} |")
    summary.extend(["", "## Highest visible non-brand query opportunities", "", "| Query | Impressions | CTR | Position | Candidate target |", "|---|---:|---:|---:|---|"])
    for item in query_items[:15]:
        summary.append(f"| {item['query'].replace('|', '/')} | {item['impressions']} | {item['ctr_percent']}% | {item['position']} | {item['candidate_target'] or 'Needs Query + Page API export'} |")
    summary.extend([
        "",
        "## Decision",
        "",
        "This export predates the 20 August production SEO release, so it is the pre-release performance baseline. Preserve the newly deployed pages long enough to collect comparable post-release data. Immediate priorities are measurement validation and snippet monitoring for the calculator, packing and cumin clusters; do not rewrite the site again from this baseline alone.",
        "",
        "## Data boundary",
        "",
        "Google exported Query, Page, Country and Device as separate tables. Their totals are valid independently, but the rows cannot be joined to claim which query, country or device produced a specific page result. Candidate targets are transparent intent-based suggestions, not observed query-to-page mappings. A Search Analytics API export using Query + Page (+ Country/Device when needed) is required for that attribution. Search Console also suppresses some low-volume queries, so visible query totals do not equal site totals.",
        "",
    ])
    (out / "search-console-performance-analysis.md").write_text("\n".join(summary), encoding="utf-8")
    print(f"Analyzed {clicks} clicks and {impressions} impressions; wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
