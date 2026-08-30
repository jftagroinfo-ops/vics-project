# Phase 38 — Full Backlink Forensic Audit & Authority Acquisition Gate (PRE-GATE SPECIFICATION)
**Domain:** https://jftagro.com · **Date:** 2026-08-29 · **Baseline SHA:** 4535656d
**Status:** PRE-GATE — specification only. NOT yet executed. No backlink export provided yet.
**Hard constraints:** NO link acquisition. NO disavow. NO outreach. This phase is purely *validation + gating*.

---

## 0. Why Phase 38 exists (sequencing decision)
Phase 37 produced a strategy but the **actual backlink profile is still UNKNOWN**. Per the agreed sequence, Phase 38 is the **data-validation gate**, not link acquisition. We must obtain a real backlink export and audit it *before* creating or pursuing any links.

---

## 1. Baseline correction (must be honored everywhere)
The Phase 36 `external_authority` figures must NOT be read as a definitive backlink score:

- `external-authority-baseline-2026-08-29.json` → `observed_values: null`, `observed_score: 40.0`, `coverage_adjusted_score: 17.8`, with 5 UNKNOWN dimensions (`referring_domains`, `institutional_presence`, `trade_portals`, `marketplace_presence`, `publications`).
- Stage-K AI input `external_authority = 30` was derived only from social `sameAs` presence (LinkedIn company page 404; directories/certifications UNKNOWN).

**Clean baseline (corrected):**
- **External authority:** *provisional / coverage-limited* (backlink component UNKNOWN; only social sameAs observed).
- **Backlink profile:** **UNKNOWN pending a real backlink export.**

This is more trustworthy than inflating a score on incomplete data. Any future score must be recomputed only after the export is ingested.

---

## 2. Required input — real backlink export
Obtain a CSV/JSON from a credible backlink index (Ahrefs, Semrush, Moz, or equivalent) for `jftagro.com`. Preferred columns (see `reports/phase37/backlink-data-requirements.md`):
referring_url, referring_domain, target_url, anchor_text, link_type (dofollow/nofollow/ugc/sponsored), first_seen, last_seen, domain_strength (DR/DA), page_strength (UR/PA), country, tld, http_status, surrounding_text, is_spam/is_pbn.

Place the file under `reports/phase38/` (e.g. `reports/phase38/backlinks-export.csv`) when available. **Phase 38 execution begins only once this exists.**

---

## 3. Phase 38 execution plan (to run once export is provided)
1. **Ingest & validate** the export; reconcile against the brief's claims (61 backlinks / 44 referring domains / 59 nofollow / 2 dofollow). Flag any mismatch as USER-PROVIDED-vs-OBSERVED.
2. **Per-domain forensic audit** of all 44 referring domains individually:
   - Actual referring URLs + target pages (confirm which jftagro page each link hits).
   - Genuine vs low-quality vs spam-like classification using referring URL + surrounding text, not homepage guess.
   - Verify the 10 preliminary-suspicious domains (seo-tip.com, wants.cfd, takes.sbs, quero.party, urls-shortener.eu, bye.fyi, domains.com.bz, drjack.world, backlink.wiki, atomizelink.icu) with their **actual referring URLs** before any removal/disavow decision.
3. **Follow/nofollow verification** — confirm whether 59 nofollow / 2 dofollow is accurate.
4. **Authority-concentration check** — confirm true landing-page distribution (brief claims 60/61 → homepage).
5. **Disavow decision:** **NONE in this phase.** Only produce an *investigate/watch* list. Removal/disavow requires a later, evidence-backed decision.
6. **Recompute** external-authority score from OBSERVED backlink data only (no imputation).
7. **Emit gate outputs** under `reports/phase38/` + `scripts/phase38/` (forensic-audit.md/.json, referring-domain-classification.csv, follow-split-verification, authority-recompute.json, PHASE-38-GATE.md).

---

## 4. Authority-target selection (from Phase 37, prioritized — legitimate only)
Once the profile is validated, pursue ONLY legitimate targets (no automated-SEO domains):
1. Indian export/trade organizations (APEDA, FIEO, DGFT)
2. Agriculture / commodity organizations (commodity boards)
3. Rice / spice industry publications
4. International trade publications
5. Credible B2B resources (verified directories, not link networks)
6. Genuine buyer / importer references (REAL, approved)
7. Logistics / trade resources

---

## 5. Linkable assets — build ONLY after targets selected
Prioritize assets that can genuinely earn citations (not generic SEO articles):
- Export documentation guide (REAL HS codes / Incoterms / procedures)
- Container / packing calculator (REAL specs)
- India commodity export data (published government datasets, attributed)
- Rice export guide
- Spice market research (published data)
- Practical FOB / CIF resources

---

## 6. Keep Phase 36 monitoring active
Continue `monitor_template.py` (AI-search monitoring). Once authority-building begins, track:
- referring-domain **quality** increases
- commercial **rankings** improvement
- **branded** visibility improvement
- **product pages** receiving external references
- AI-search **citations** eventually observable

---

## 7. Change-control (Phase 38 will honor)
- Only `?? reports/phase38/` + `?? scripts/phase38/` may appear untracked.
- `git diff` empty; no website / worker / schema / sitemap / robots changes; no deploy / push / commit.
- No backlinks created; no outreach; no disavow.

---

## 8. Current state
- **Phase 38 NOT executed** — awaiting the real backlink export.
- This specification is the agreed gate. Provide the Ahrefs/Semrush/Moz CSV and Phase 38 will run end-to-end before any link is created or pursued.
