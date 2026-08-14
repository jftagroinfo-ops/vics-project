#!/usr/bin/env python3
"""Release gate for unsupported claims and master-product/page consistency."""

from __future__ import annotations

import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parent.parent
MASTER = ROOT / "data" / "products.json"
FORBIDDEN = {
    "absolute customs timing": re.compile(r"48[- ]hour customs", re.I),
    "absolute zero-claim wording": re.compile(r"zero[- ]claim|zero claim guarantee", re.I),
    "unsupported container volume": re.compile(r"(?:382\+?\s*TEU|500\+?\s*containers)", re.I),
    "unsupported capacity": re.compile(r"250\s*MT(?:\s*/\s*day|\s+per\s+day)", re.I),
    "unsupported country count": re.compile(r"25\+\s*(?:countries|global destinations)", re.I),
    "mis-scoped laboratory claim": re.compile(r"(?:in-house\s+)?NABL[- ]certified\s+lab", re.I),
    "unqualified ISO claim": re.compile(r"ISO 9001:2015 certified", re.I),
    "unqualified APEDA claim": re.compile(r"APEDA registered(?: exporter)?", re.I),
    "unqualified HACCP claim": re.compile(r"HACCP certified", re.I),
    "unqualified status-holder claim": re.compile(r"Government recogn(?:is|iz)ed Star Export House", re.I),
}


def visible_text(path: Path) -> str:
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"<script\b.*?</script>|<style\b.*?</style>", " ", text, flags=re.I | re.S)
    return re.sub(r"<[^>]+>", " ", text)


def main() -> int:
    findings: list[str] = []
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or "reports" in path.parts:
            continue
        content = visible_text(path)
        for label, pattern in FORBIDDEN.items():
            if pattern.search(content):
                findings.append(f"{path.relative_to(ROOT).as_posix()}: {label}")

    products = json.loads(MASTER.read_text(encoding="utf-8"))
    if len(products) != 84:
        findings.append(f"data/products.json: expected governed catalogue count 84, found {len(products)}")
    names = set()
    urls = set()
    required_specs = {"HS Code", "MOQ"}
    for product in products:
        name = product.get("t", "").strip()
        url = product.get("u", "").strip()
        specs = {row[0] for row in product.get("s", []) if isinstance(row, list) and row}
        if not name or name.casefold() in names:
            findings.append(f"data/products.json: missing or duplicate product name {name!r}")
        names.add(name.casefold())
        if not url or url in urls or not (ROOT / url).is_file():
            findings.append(f"data/products.json: missing, duplicate, or unresolved product URL {url!r}")
        urls.add(url)
        missing = required_specs - specs
        if missing:
            findings.append(f"{name}: missing master fields {sorted(missing)}")
        for section in ("identity", "trade", "compliance"):
            if not isinstance(product.get(section), dict) or not product[section]:
                findings.append(f"{name}: missing governed {section} data")
        trade = product.get("trade", {})
        for field in ("hs_code", "moq", "container_20ft", "container_40ft", "packaging", "private_label", "fob", "cif", "port_of_loading"):
            if not trade.get(field):
                findings.append(f"{name}: missing trade.{field}")
        page_text = BeautifulSoup((ROOT / url).read_text(encoding="utf-8"), "html.parser").get_text(" ") if url and (ROOT / url).is_file() else ""
        normalized_page = re.sub(r"[^a-z0-9%]+", "", page_text.casefold())
        for key, value in product.get("s", []):
            if key in {"HS Code", "Moisture", "Purity", "Broken", "Foreign Matter", "Length", "MOQ"}:
                normalized_value = re.sub(r"[^a-z0-9%]+", "", str(value).casefold())
                if normalized_value and normalized_value not in normalized_page:
                    findings.append(f"{url}: master/page mismatch for {key}={value}")

    catalogue = (ROOT / "products.html").read_text(encoding="utf-8")
    if "fob_usd_min" in catalogue or "AggregateOffer" in catalogue or "InStock" in catalogue:
        findings.append("products.html: stale hard-coded price/availability schema remains")
    if "const PRODUCT_DATA = window.JFT_PRODUCT_DATA;" not in catalogue:
        findings.append("products.html: catalogue is not consuming the canonical product master")

    print(f"Claims/product findings: {len(findings)}")
    for finding in findings[:100]:
        print("-", finding)
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
