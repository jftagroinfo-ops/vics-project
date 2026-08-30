# Backlink Data Requirements — Phase 37

**Date:** 2026-08-29 · **Domain:** https://jftagro.com
**Status:** BLOCKER DOCUMENT — required before any forensic/classification work on the "44 referring domains / 61 backlinks" figures can be verified.

---

## 1. Why this document exists

Phase 37 was briefed with specific backlink figures (61 backlinks, 44 referring domains, a named set of 10 domains, a follow/nofollow split). A repository-wide search (all 5,807 files) returned **zero** matches for any of the 10 named domains, and no `*.csv`/`*.json`/`*.xlsx` containing a backlink or referring-domain dataset exists in the repo.

Phase 36 explicitly resolved the external-authority inputs as **UNKNOWN** (`ai-search-baseline-2026-08-29.json` → `external_authority.unknown_dimensions` includes `"referring_domains"`), and the project's governing contract (`seo-v3-joint-implementation-contract-2026-08-20.md` §31) forbids fabricating backlinks, credentials, prices, or company claims.

Per the Phase 37 plan §3, when the 44-domain dataset is not available locally we must **document the gap and specify the required export columns** rather than invent data.

## 2. What is MISSING

| Missing item | Source expected | Notes |
|---|---|---|
| Full referring-domain list (44) | Ahrefs / Semrush / Majestic / Moz / GSC Links report | Only 10 of 44 named in brief; 34 are unlisted. |
| Backlink-level export (61 rows) | Same tools | Needed for anchor/follow/landing-page analysis. |
| Follow / nofollow split | Tool attribute | Brief asserts "2 dofollow" — unverified. |
| Per-link landing URL | Tool attribute | Needed for authority-concentration check (brief asserts 60/61 → homepage). |
| Anchor text per link | Tool attribute | Needed for over-optimization risk. |
| First / last seen dates | Tool attribute | Needed for freshness / decay analysis. |
| Domain & page strength (DR/UR/DA/PA, or equivalents) | Tool metric | Needed for real prioritization. |
| HTTP status of each link | Live re-check | Needed to confirm links are still live. |

## 3. Required export columns (preferred)

If a backlink export is supplied later, it should include at minimum:

1. `referring_url` — exact page URL containing the link
2. `referring_domain` — root domain of the source
3. `target_url` — the jftagro.com URL being linked
4. `anchor_text` — exact anchor used
5. `link_type` — dofollow / nofollow / ugc / sponsored
6. `first_seen` — date first observed
7. `last_seen` — date last observed
8. `domain_strength` — DR/DA or equivalent (0–100)
9. `page_strength` — UR/PA or equivalent (0–100)
10. `country` — source geo
11. `tld` — source top-level domain
12. `http_status` — current live status (200/301/404…)
13. `surrounding_text` — snippet around the link (context/intent)
14. `is_spam` / `is_pbn` flag if the tool provides one

## 4. What will be done once data is provided

- Re-run the forensic audit (`backlink-forensic-audit`) against the real 44-domain set.
- Produce a verified `referring-domain-classification.csv` with all 44 rows.
- Compute a real authority-concentration and anchor-risk profile.
- Convert the current "DATA NOT PROVIDED / UNKNOWN" placeholders to PROVEN/OBSERVED records.

Until then, all 44-domain figures are labeled **USER-PROVIDED / UNVERIFIED** and the 34 unlisted domains are **DATA NOT PROVIDED**.
