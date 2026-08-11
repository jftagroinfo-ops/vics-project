"""Refresh the quote calculator feed from a verified commercial endpoint.

The endpoint must return the same schema as data/quote-market-rates.json.
No update is made when the endpoint is not configured or validation fails.
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

import requests


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "quote-market-rates.json"


def require_number(value: object, label: str, allow_zero: bool = False) -> float:
    if not isinstance(value, (int, float)) or isinstance(value, bool):
        raise ValueError(f"{label} must be numeric")
    if value < 0 or (value == 0 and not allow_zero):
        raise ValueError(f"{label} is outside the accepted range")
    return float(value)


def parse_timestamp(value: object, label: str) -> datetime:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be an ISO timestamp")
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError(f"{label} must include a timezone")
    return parsed.astimezone(timezone.utc)


def validate(feed: object) -> dict:
    if not isinstance(feed, dict) or feed.get("schemaVersion") != 1:
        raise ValueError("Unsupported quote-feed schema")
    if feed.get("currency") != "USD" or feed.get("mode") not in {"live", "reference"}:
        raise ValueError("Feed must use USD and declare live or reference mode")

    updated = parse_timestamp(feed.get("updatedAt"), "updatedAt")
    valid_until = parse_timestamp(feed.get("validUntil"), "validUntil")
    if valid_until <= updated:
        raise ValueError("validUntil must be later than updatedAt")
    if updated > datetime.now(timezone.utc):
        raise ValueError("updatedAt cannot be in the future")

    products = feed.get("products")
    freight = feed.get("freight")
    packing = feed.get("packing")
    assumptions = feed.get("assumptions")
    sources = feed.get("sources")
    if not isinstance(products, dict) or len(products) < 10:
        raise ValueError("Feed does not contain the expected product coverage")
    if not isinstance(freight, dict) or len(freight) < 10:
        raise ValueError("Feed does not contain the expected freight coverage")
    if not isinstance(packing, dict) or not isinstance(assumptions, dict) or not isinstance(sources, dict):
        raise ValueError("Feed is missing packing, assumption or source metadata")

    for key, product in products.items():
        if not isinstance(product, dict) or not product.get("name") or not product.get("hs"):
            raise ValueError(f"Invalid product metadata: {key}")
        require_number(product.get("fob"), f"products.{key}.fob")
        require_number(product.get("load20"), f"products.{key}.load20")
        require_number(product.get("load40"), f"products.{key}.load40")
        require_number(product.get("rangePct"), f"products.{key}.rangePct", allow_zero=True)

    for key, lane in freight.items():
        if not isinstance(lane, dict) or not lane.get("name"):
            raise ValueError(f"Invalid freight metadata: {key}")
        allow_zero = key == "ex_mill"
        require_number(lane.get("20ft"), f"freight.{key}.20ft", allow_zero=allow_zero)
        require_number(lane.get("40ft"), f"freight.{key}.40ft", allow_zero=allow_zero)
        require_number(lane.get("rangePct"), f"freight.{key}.rangePct", allow_zero=True)

    return feed


def main() -> None:
    endpoint = os.environ.get("QUOTE_RATE_FEED_URL", "").strip()
    token = os.environ.get("QUOTE_RATE_FEED_TOKEN", "").strip()
    if not endpoint:
        print("QUOTE_RATE_FEED_URL is not configured; keeping the current reference feed.")
        return

    headers = {"Accept": "application/json", "User-Agent": "JFT-Agro-Rate-Sync/1.0"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    response = requests.get(endpoint, headers=headers, timeout=45)
    response.raise_for_status()
    feed = validate(response.json())

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(feed, indent=2, ensure_ascii=True) + "\n", encoding="utf-8")
    temporary.replace(OUTPUT)
    print(f"Updated {OUTPUT.relative_to(ROOT)} from the configured verified feed.")


if __name__ == "__main__":
    main()
