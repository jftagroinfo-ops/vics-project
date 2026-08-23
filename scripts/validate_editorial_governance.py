#!/usr/bin/env python3
"""Prevent unsupported named-reviewer claims in controlled priority articles."""

from __future__ import annotations

import csv
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
REGISTER = ROOT / "data/editorial-review-register.csv"
STATUSES = {"pending_human_approval", "approved", "revision_required", "retired"}


def main() -> int:
    rows = list(csv.DictReader(REGISTER.open(encoding="utf-8-sig", newline="")))
    errors: list[str] = []
    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        url = row["canonical_url"].strip()
        status = row["status"].strip()
        if url in seen:
            errors.append(f"row {number}: duplicate canonical URL")
        seen.add(url)
        path = ROOT / urlsplit(url).path.lstrip("/")
        if not path.exists():
            errors.append(f"row {number}: article does not exist: {path.name}")
            continue
        source = path.read_text(encoding="utf-8")
        if "editorial-policy.html" not in source:
            errors.append(f"row {number}: article lacks editorial-policy link")
        if status not in STATUSES:
            errors.append(f"row {number}: invalid status {status!r}")
        if status == "approved":
            for field in ("named_reviewer", "reviewer_role_or_qualification", "review_scope", "human_review_date"):
                if not row[field].strip():
                    errors.append(f"row {number}: approved review missing {field}")
            try:
                reviewed = date.fromisoformat(row["human_review_date"])
                if reviewed > date.today():
                    errors.append(f"row {number}: human review date is in the future")
            except ValueError:
                errors.append(f"row {number}: invalid human_review_date")
            if row["named_reviewer"].strip() not in source or row["human_review_date"].strip() not in source:
                errors.append(f"row {number}: approved reviewer/date not visible in article")
        elif "reviewed by" in source.casefold() and "no “reviewed by” claim" not in source.casefold():
            errors.append(f"row {number}: unsupported visible reviewed-by claim")
    if errors:
        print("Editorial governance failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    approved = sum(row["status"].strip() == "approved" for row in rows)
    print(f"Validated {len(rows)} editorial records; {approved} approved, {len(rows) - approved} gated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
