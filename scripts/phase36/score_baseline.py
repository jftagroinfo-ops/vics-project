#!/usr/bin/env python3
"""Phase 36 - Stage K/L: Evidence-based scoring with explicit UNKNOWN handling.

Computes two AI-visibility scores and an external-authority score from available evidence.
Dimensions that cannot be measured (AI-answer platforms, GSC live API, backlink tools) are
kept as UNKNOWN and NEVER scored as zero. Produces OBSERVED score and COVERAGE-ADJUSTED score.

Outputs reports/phase36/ai-search-baseline-2026-08-29.json (augmented) and prints a summary.
Read-only; does not modify website/source/config.
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
REP = ROOT / "reports" / "phase36"
BASE = "4535656d830c4fb5ede7928cab7f6920597aaa67"

# ---- AI VISIBILITY SCORING MODEL (Stage K) ----
WEIGHTS = {
    "branded_visibility": 0.15,
    "commercial_query_visibility": 0.20,
    "product_visibility": 0.15,
    "ai_citation_rate": 0.20,
    "official_page_citation_rate": 0.10,
    "competitor_share": 0.10,
    "external_authority": 0.10,
}

OBSERVED = {
    "branded_visibility": 70,
    "commercial_query_visibility": 25,
    "product_visibility": 45,
    "ai_citation_rate": None,            # AI-answer platforms inaccessible -> UNKNOWN
    "official_page_citation_rate": None,  # UNKNOWN
    "competitor_share": None,             # UNKNOWN
    "external_authority": 30,
}


def score(observed: dict):
    # Renormalize weights over KNOWN dimensions for the OBSERVED score (0-100).
    known = {k: v for k, v in observed.items() if v is not None}
    known_w = sum(WEIGHTS[k] for k in known)
    obs_score = round(sum(WEIGHTS[k] * known[k] for k in known) / known_w, 1) if known_w else 0.0
    # COVERAGE-ADJUSTED: apply original fixed weights across ALL dimensions (UNK counts as 0).
    adj_score = round(sum(WEIGHTS[k] * (observed[k] or 0) for k in WEIGHTS), 1)
    unknown_dims = [k for k in WEIGHTS if observed[k] is None]
    coverage_pct = round(100 * known_w / sum(WEIGHTS.values()), 1)
    return obs_score, adj_score, unknown_dims, coverage_pct


def authority_score():
    comp = {
        "referring_domains": None,        # backlink tool access unavailable
        "institutional_presence": None,    # APEDA 404 / FIEO timeout / DGFT generic -> UNKNOWN
        "business_directories": 20,        # most guessed dir URLs 404/403 -> weak observed
        "trade_portals": None,             # directory login needed
        "linkedin_presence": 0,            # company page 404 (no verified company page)
        "marketplace_presence": None,      # UNKNOWN
        "publications": None,              # UNKNOWN
        "branded_mentions": 60,            # Bing/Google brand SERP observed; FB/IG present
        "entity_consistency": 80,          # on-site consistent (2016 registration claim)
    }
    weights = {k: 1 for k in comp}
    known = {k: v for k, v in comp.items() if v is not None}
    tw = sum(weights.values())
    kw = sum(weights[k] for k in known)
    obs = round(sum(known[k] for k in known) / kw, 1) if kw else 0.0
    adj = round(sum((comp[k] or 0) for k in comp) / tw, 1)
    unknown = [k for k in comp if comp[k] is None]
    return obs, adj, unknown, round(100 * kw / tw, 1)


def main() -> int:
    REP.mkdir(parents=True, exist_ok=True)
    obs_ai, adj_ai, unk_ai, cov_ai = score(OBSERVED)
    obs_auth, adj_auth, unk_auth, cov_auth = authority_score()

    doc = {
        "audit_date": "2026-08-29",
        "repository_sha": BASE,
        "production_url": "https://jftagro.com",
        "ai_visibility": {
            "methodology": "Weighted average of 7 dimensions (Stage K). UNKNOWN dims excluded from OBSERVED score, scored 0 in COVERAGE-ADJUSTED.",
            "weights": WEIGHTS,
            "observed_values": OBSERVED,
            "observed_score": obs_ai,
            "coverage_adjusted_score": adj_ai,
            "unknown_dimensions": unk_ai,
            "measured_coverage_pct": cov_ai,
        },
        "external_authority": {
            "methodology": "Equal-weight average of 9 components (Stage L). UNKNOWN != ZERO.",
            "observed_values": None,
            "observed_score": obs_auth,
            "coverage_adjusted_score": adj_auth,
            "unknown_dimensions": unk_auth,
            "measured_coverage_pct": cov_auth,
        },
        "scoring_assumptions": [
            "Branded_visibility=70 because brand-name SERP returns jftagro.com (Bing observed True; Google reachable).",
            "Commercial_query_visibility=25 based on local GSC export (low nonbrand impressions, avg position ~9-10).",
            "Product_visibility=45: full product catalogue indexed with correct canonical/hreflang but weak query coverage.",
            "ai_citation_rate / official_page_citation_rate / competitor_share = UNKNOWN (AI-answer platforms inaccessible).",
            "External_authority=30: social sameAs present; directories institutional presence UNKNOWN; LinkedIn company page 404.",
            "All UNKNOWN dimensions are recorded and excluded from OBSERVED score; never imputed as zero without label.",
        ],
    }
    (REP / "ai-search-baseline-2026-08-29.json").write_text(
        json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print("AI visibility  OBSERVED=%s  COVERAGE-ADJUSTED=%s  measured_coverage=%s%%" % (obs_ai, adj_ai, cov_ai))
    print("Authority      OBSERVED=%s  COVERAGE-ADJUSTED=%s  measured_coverage=%s%%" % (obs_auth, adj_auth, cov_auth))
    print("UNKNOWN ai dims:", unk_ai)
    print("UNKNOWN auth dims:", unk_auth)
    print("-> reports/phase36/ai-search-baseline-2026-08-29.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

