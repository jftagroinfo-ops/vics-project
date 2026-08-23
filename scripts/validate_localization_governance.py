#!/usr/bin/env python3
"""Validate native-language commercial review and search-demand governance."""

from __future__ import annotations

import csv
import json
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
POLICY = ROOT / "localization-review.json"
REGISTER = ROOT / "data" / "localization-review-register.csv"
LOCALES = {"ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"}
STATUSES = {"pending_native_commercial_review", "approved", "hold", "retired"}
DEMAND_DECISIONS = {"proceed", "maintain", "hold", "retire"}


def main() -> int:
    policy = json.loads(POLICY.read_text(encoding="utf-8"))
    if policy.get("review_register") != "data/localization-review-register.csv":
        raise SystemExit("Policy does not point to the controlled localization review register.")

    rows = list(csv.DictReader(REGISTER.open(encoding="utf-8-sig", newline="")))
    errors: list[str] = []
    seen: set[str] = set()
    for number, row in enumerate(rows, start=2):
        locale = row["locale"].strip()
        status = row["status"].strip()
        decision = row["demand_decision"].strip()
        if locale not in LOCALES:
            errors.append(f"row {number}: unsupported locale {locale!r}")
        if locale in seen:
            errors.append(f"row {number}: duplicate locale {locale!r}")
        seen.add(locale)
        if status not in STATUSES:
            errors.append(f"row {number}: invalid status {status!r}")
        if decision not in DEMAND_DECISIONS:
            errors.append(f"row {number}: invalid demand decision {decision!r}")
        if status == "approved":
            required = (
                "native_reviewer", "reviewer_language", "reviewer_qualification",
                "commercial_review_date", "source_batch", "gsc_evidence_period",
            )
            for field in required:
                if not row[field].strip():
                    errors.append(f"row {number}: approved record missing {field}")
            try:
                reviewed = date.fromisoformat(row["commercial_review_date"])
                if reviewed > date.today():
                    errors.append(f"row {number}: review date is in the future")
            except ValueError:
                errors.append(f"row {number}: invalid commercial_review_date")
            if decision not in {"proceed", "maintain"}:
                errors.append(f"row {number}: approved record requires proceed/maintain demand decision")
        if decision == "proceed":
            try:
                if int(row["gsc_nonbrand_impressions"]) <= 0:
                    errors.append(f"row {number}: proceed decision requires positive non-brand impressions")
            except ValueError:
                errors.append(f"row {number}: invalid gsc_nonbrand_impressions")

    if seen != LOCALES:
        errors.append(f"register locale mismatch: expected {sorted(LOCALES)}, found {sorted(seen)}")
    if errors:
        print("Localization governance failed:")
        for error in errors:
            print(f"- {error}")
        return 1
    approved = sum(row["status"].strip() == "approved" for row in rows)
    print(f"Validated {len(rows)} locale governance records; {approved} approved, {len(rows) - approved} gated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
