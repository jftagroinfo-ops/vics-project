#!/usr/bin/env python3
"""Phase 37 — read-only authority-target scorer.

Reads reports/phase37/authority-opportunity-database.csv and writes
reports/phase37/phase37-score-model.json describing the priority model and
per-row scores. READ-ONLY: does not fetch the web or mutate any website.
"""
import csv
import json
import os

BASE = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CSV_PATH = os.path.join(BASE, "reports", "phase37", "authority-opportunity-database.csv")
OUT_PATH = os.path.join(BASE, "reports", "phase37", "phase37-score-model.json")

# §15 priority model weights (sum = 100)
WEIGHTS = {
    "topical_relevance": 25,
    "authority": 20,
    "editorial_legitimacy": 20,
    "business_relevance": 15,
    "ai_entity_value": 10,
    "feasibility": 10,
}

def band(score):
    if score >= 75:
        return "P1"
    if score >= 65:
        return "P2"
    if score >= 55:
        return "P3"
    return "DEPRIORITIZE"

def main():
    rows = []
    with open(CSV_PATH, newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            # ratings are 1-5; normalize to 0-100 weighted by percent weights
            comp = sum((int(r[k]) / 5.0) * WEIGHTS[k] for k in WEIGHTS)
            comp = round(comp, 1)
            rows.append({
                "category": r["category"],
                "opportunity": r["opportunity"],
                "composite_score": comp,
                "model_priority": band(comp),
                "csv_priority": r["priority"],
                "evidence_class": r["evidence_class"],
                "required_evidence": r["required_evidence"],
            })

    model = {
        "model": "phase37-authority-priority",
        "weights_percent": WEIGHTS,
        "scale": "each dimension 1-5; composite 0-100",
        "bands": {"P1": ">=75", "P2": "65-74", "P3": "55-64", "DEPRIORITIZE": "<55"},
        "backlink_profile_status": "UNKNOWN (no local export; see backlink-data-requirements.md)",
        "ai_platforms_status": "UNKNOWN/INACCESSIBLE (Phase 36)",
        "disclaimer": "All scores are MODELED/INFERRED — NOT GUARANTEED. No backlink/credential fabricated.",
        "scored_opportunities": rows,
    }
    with open(OUT_PATH, "w", encoding="utf-8") as f:
        json.dump(model, f, indent=2, ensure_ascii=False)
    print(f"Wrote {OUT_PATH} with {len(rows)} scored opportunities.")

if __name__ == "__main__":
    main()
