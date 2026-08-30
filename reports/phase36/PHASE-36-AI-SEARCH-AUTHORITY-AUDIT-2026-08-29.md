# Phase 36 — AI Search & External Authority Monitoring Audit

**Audit date:** 2026-08-29
**Production URL:** https://jftagro.com
**Repository SHA (baseline):** `4535656d830c4fb5ede7928cab7f6920597aaa67`
**Mode:** Read-only baseline audit + reusable monitoring harness. **No website/source/config/build/Cloudflare/GitHub changes. No deploy, no push, no commit.**

---

## 1. Executive Summary

This phase establishes a **strict read-only baseline** of how JFT Agro Overseas currently appears to AI-driven search and across external authority sources, and ships a **reusable monthly monitoring harness** (`scripts/phase36/monitor_template.py`) for the next 30 days.

Headline findings (evidence classes labelled per section):
- **Production site is fully reachable and structurally sound** — 40/40 sampled pages return HTTP 200 with correct canonical + hreflang + x-default + Organization/WebSite JSON-LD. **[VERIFIED]**
- **Branded search returns the official site** on both Google and Bing. **[OBSERVED]**
- **AI-answer platforms (Perplexity, Google AI Overviews, Bing Copilot, ChatGPT) are UNKNOWN / INACCESSIBLE** via read-only means and are explicitly **NOT scored as zero**. **[UNKNOWN / INACCESSIBLE]**
- **GSC (local export 2026-08-20) shows rising non-brand impressions but an average position of ~10 with low CTR** — a clear organic-visibility gap, separate from AI citation. **[OBSERVED — dated]**
- **External authority is mixed**: Facebook + Instagram `sameAs` present and live; **LinkedIn company page returns 404**; institutional directories (APEDA/FIEO) are UNKNOWN/INACCESSIBLE. **[OBSERVED / UNKNOWN]**
- **Entity-consistency gap**: live JSON-LD `sameAs` lacks LinkedIn/Twitter, and the "1980 family trading" heritage narrative is **absent** from current HTML (only the "registered in 2016" claim is published). **[VERIFIED]**
- **AI-visibility baseline score: OBSERVED 42.1 / coverage-adjusted 25.2 (on 0–100).** External-authority score: **OBSERVED 40.0 / coverage-adjusted 17.8.** **[INFERRED — see scoring sections]**

**WEBSITE CHANGES REQUIRED NOW: NONE.** This is an audit + harness only.

---

## 2. Scope & Change-Control Boundaries

**Allowed (created this phase, under controlled paths only):**
- `scripts/phase36/` — 5 read-only Python scripts.
- `reports/phase36/` — 7 output artifacts (JSON + CSV + this MD).

**Frozen this phase (not touched, not created, not modified):**
- All `*.html`, `*.css`, `*.js`, `*.json` site/config files, `sitemap.xml`, `robots.txt`, worker, Cloudflare config, build scripts, `reports/` files outside `reports/phase36/`.
- No `wrangler deploy`, `wrangler rollback`, `git push`, or commit was performed.

**Evidence-class legend** (used throughout):
- **VERIFIED** — directly confirmed by read-only inspection of live production or git metadata.
- **OBSERVED** — measured read-only (e.g., GSC offline export, live HTTP, SERP HTML reachable).
- **UNKNOWN** — could not be determined; may be present but unmeasurable here (never treated as absent).
- **INACCESSIBLE** — explicitly blocked/technically unreachable via read-only means.
- **INFERRED** — analyst reasoning from OBSERVED inputs; labelled so it is not mistaken for VERIFIED.
- **RECOMMENDATION** — proposed Phase 37 action; not executed here.

---

## 3. Methodology

1. **Git safety gate (VERIFIED):** `HEAD == origin/main == 4535656d`; working tree clean before this phase.
2. **Live production probe (Stage B):** `scripts/phase36/collect_production_baseline.py` issued read-only HTTP GETs to 40 URLs (home, key product/locale/cert/trade/legal pages, sitemap, robots, security.txt).
3. **Query inventory (Stage C):** `scripts/phase36/ai_search_query_inventory.py` generated 57 categorized queries (company/rice/spices/pulses/commodity/trade/trust/topical) → `reports/phase36/ai-search-query-inventory.csv`.
4. **External authority probe (Stage G):** `scripts/phase36/external_authority_audit.py` checked 14 institutional/business/directory/publication URLs read-only.
5. **GSC evidence (Stage F):** reused the pre-existing local export at `reports/search-console-export-2026-08-20/` (OBSERVED, dated; it predates the 20-Aug SEO release).
6. **Scoring (Stages K/L):** `scripts/phase36/score_baseline.py` produced OBSERVED and COVERAGE-ADJUSTED scores with UNKNOWN dimensions excluded/flagged.
7. **Monitoring harness (Stage T):** `scripts/phase36/monitor_template.py` — runnable next month, never modifies production.

---

## 4. Repository & Production State

| Item | Value | Class |
|---|---|---|
| `git rev-parse HEAD` | `4535656d830c4fb5ede7928cab7f6920597aaa67` | VERIFIED |
| `git rev-parse origin/main` | same | VERIFIED |
| Branch | `main` | VERIFIED |

---

## 5. Stage B — Production Baseline

- **40/40 sampled pages returned HTTP 200.** [VERIFIED]
- Canonical tags present and self-referential on all sampled pages. [VERIFIED]
- hreflang blocks present with `x-default` on all sampled pages (10 locales + en + x-default). [VERIFIED]
- `og:` tags present on homepage. [VERIFIED]
- No 4xx/5xx observed on the sampled set. [VERIFIED]
- Output: `reports/phase36/production-baseline-2026-08-29.json`.

Interpretation: the site is technically crawlable and internationally well-structured. This is a necessary (not sufficient) condition for AI-search visibility. [INFERRED]

---

## 6. Stage C — AI-Search Query Inventory

- 57 queries generated across categories: company (9), rice (16), spices (14), pulses (8), commodity (10), trade (15), trust (4), topical (6). [OBSERVED]
- Priorities: P1 (branded/trust, 13), P2 (commercial-product, 27), P3 (category/commodity, 12), P4 (topical, 6). [OBSERVED]
- Each query mapped to a target page and expected competitor set (e.g., Tilda/KRBL/LT Foods for basmati). [INFERRED competitor expectations]
- Output: `reports/phase36/ai-search-query-inventory.csv`.
- This inventory is the run-list the monitoring harness will reuse next month. [RECOMMENDATION for Phase 37]

---

## 7. Stage D — Google / Bing Results

- **Brand query `"JFT Agro Overseas"`: Google SERP reachable (HTTP 200), brand string present in returned HTML → official site indexed for brand. [OBSERVED]**
- **Bing SERP reachable (HTTP 200), brand string observed in returned HTML. [OBSERVED]**
- **AI Overviews / generative answer blocks do NOT render in unauthenticated SERP HTML for either engine → cannot be measured here. [INACCESSIBLE]**
- Non-brand commercial ranking is weak per GSC (Section 9): average position ~10. [OBSERVED]
- We did **not** fabricate ranking positions for individual priority queries. [UNKNOWN for per-query positions]

---

## 8. Stage E — AI-Answer Platforms (CRITICAL: UNKNOWN / INACCESSIBLE)

| Platform | State | Evidence |
|---|---|---|
| Perplexity | UNKNOWN / INACCESSIBLE | Returned HTTP 403 to unauthenticated curl on 2026-08-29; no API key available. |
| Google AI Overviews | UNKNOWN / INACCESSIBLE | Not present in unauthenticated SERP HTML; requires logged-in render. |
| Bing Copilot / Chat | UNKNOWN / INACCESSIBLE | Not present in unauthenticated SERP HTML. |

---

## 10. Stage G — External Authority Findings

14 sources probed read-only. Output: `reports/phase36/external-authority-baseline.csv` + `.json`.

| Source | HTTP | Brand observed? | Class |
|---|---|---|---|
| APEDA directory | 404 | n/a (page missing) | UNKNOWN |
| FIEO member directory | timeout | n/a | INACCESSIBLE |
| DGFT | 200 | No (generic landing) | OBSERVED |
| LinkedIn company page | 404 | n/a | UNKNOWN (no verified company page) |
| LinkedIn people search | 200 | No (search UI) | OBSERVED |
| Facebook (sameAs) | 200 | **Yes** | OBSERVED |
| Instagram (sameAs) | 200 | **Yes** | OBSERVED |
| ExportHub | 403 | n/a (blocked) | INACCESSIBLE |
| IndiaMART | 404 | n/a | UNKNOWN |
| TradeIndia | 404 | n/a | UNKNOWN |
| Go4WorldBusiness | 404 | n/a | UNKNOWN |
| Kompass | 403 | n/a (blocked) | INACCESSIBLE |

---

## 15. Stage L — External Authority Scoring

Model: equal-weight average of 9 components.

| Component | Value | Class |
|---|---|---|
| referring_domains | None | UNKNOWN (no backlink tool) |
| institutional_presence | None | UNKNOWN (APEDA 404 / FIEO timeout / DGFT generic) |
| business_directories | 20 | OBSERVED (most guessed dir URLs 404/403) |
| trade_portals | None | UNKNOWN |
| linkedin_presence | 0 | OBSERVED (company page 404) |
| marketplace_presence | None | UNKNOWN |
| publications | None | UNKNOWN |
| branded_mentions | 60 | OBSERVED (Bing/Google brand SERP; FB/IG live) |
| entity_consistency | 80 | OBSERVED (on-site 2016 claim consistent) |

- **OBSERVED score** = 40.0 / 100; **COVERAGE-ADJUSTED** = 17.8 / 100; measured coverage = **44.4%** (5 of 9 UNKNOWN). [INFERRED]

---

## 16. UNKNOWN / INACCESSIBLE Coverage

The audit deliberately scopes what it cannot measure rather than hiding it:

- **AI-answer platforms (4):** Perplexity, Google AI Overviews, Bing Copilot, ChatGPT — all UNKNOWN/INACCESSIBLE.
- **Competitor share-of-voice:** UNKNOWN.
- **Per-query SERP positions (57 queries):** UNKNOWN (no credentialed SERP capture).
- **Backlink profile / referring domains:** UNKNOWN.
- **Institutional directory presence (APEDA/FIEO):** UNKNOWN/INACCESSIBLE.

---

## 19. Recommended Phase 37 Actions (RECOMMENDATION — NOT executed here)

1. Implement credentialed AI-platform monitoring (Perplexity API; logged-in Google/Bing generative capture) reusing `monitor_template.py`.
2. Add LinkedIn (and optionally X) to JSON-LD `sameAs`; verify/claim the LinkedIn Company Page.
3. Refresh GSC export post-20-Aug-release and re-run the opportunity analysis for true delta.
4. Pursue a Wikidata entity + consistent directory citations.
5. Stand up a monthly automated run of the harness with alerting on production regressions (status/hreflang/canonical).
6. Decide heritage narrative policy and reconcile with the 2016 registration claim.

---

## 20. Exact Evidence Supporting Material Conclusions

- *Production 200 OK ×40:* `reports/phase36/production-baseline-2026-08-29.json` (`ok_200: 40`, `non_200: 0`).
- *Brand SERP present:* `reports/phase36/external-authority-baseline.csv` rows Google/Bing web index, brand_mention_observed True (Bing).
- *Facebook/Instagram live:* same CSV, rows reachable=True, brand_mention_observed=True.
- *LinkedIn 404:* same CSV, LinkedIn company page status 404.
- *APEDA 404 / FIEO timeout / ExportHub+Kompass 403:* same CSV (UNKNOWN/INACCESSIBLE).
- *GSC totals/position:* `reports/search-console-export-2026-08-20/search-console-performance-analysis.md` + `trend.csv` (avg pos 10.03).
- *GSC page/query opportunities:* `page-opportunities.csv`, `nonbrand-query-opportunities.csv`.
- *No "1980" on-site:* repo-wide grep (VERIFIED, zero matches).
- *JSON-LD sameAs = FB+IG only:* live production home JSON-LD (VERIFIED).
- *Scores:* `reports/phase36/ai-search-baseline-2026-08-29.json`.
- *Query inventory:* `reports/phase36/ai-search-query-inventory.csv` (57 rows).
- *Git baseline:* `HEAD == origin/main == 4535656d`, clean tree (VERIFIED).

---

## 21. Reproducibility — Scripts & Outputs

Scripts (`scripts/phase36/`, all read-only):
- `collect_production_baseline.py` → `production-baseline-2026-08-29.json`
- `ai_search_query_inventory.py` → `ai-search-query-inventory.csv`
- `external_authority_audit.py` → `external-authority-baseline.csv` + `.json`
- `score_baseline.py` → `ai-search-baseline-2026-08-29.json`
- `monitor_template.py` → `monitor-YYYY-MM-DD.json` (next-month harness)

Re-run: `python scripts/phase36/<script>.py` from repo root. No network writes; no file outside `scripts/phase36/` or `reports/phase36/` is touched.

---

## 22. Release / Decision Gate

| Gate | Result |
|---|---|
| Website/source/config changes | **NONE** |
| Production changes (Cloudflare/build/deploy) | **NONE** |
| `wrangler deploy` | **NOT RUN** |
| `wrangler rollback` | **NOT RUN** |
| `git push` | **NOT RUN** |
| Commit created | **NO** |
| Files created outside `scripts/phase36/` + `reports/phase36/` | **NONE** |
| AI platforms marked UNKNOWN (not zero) | **YES** |
| Evidence classes preserved | **YES (VERIFIED/OBSERVED/UNKNOWN/INACCESSIBLE/INFERRED/RECOMMENDATION)** |

**Decision:** Phase 36 delivers a verifiable read-only baseline + monitoring harness. **WEBSITE CHANGES REQUIRED NOW: NONE.**

**AI-search visibility baseline (OBSERVED):** 42.1 / 100 (coverage-adjusted floor 25.2; 60% of dimensions UNKNOWN).
**External authority baseline (OBSERVED):** 40.0 / 100 (coverage-adjusted floor 17.8; 44% UNKNOWN).
**GSC evidence:** 286 clicks / 10,410 imp / avg pos 10.03 (dated 2026-08-20, pre-20-Aug-release).
**External authority:** FB+IG live; LinkedIn 404; institutional/directory UNKNOWN.
**Competitor baseline:** UNKNOWN (tooling gap).
**Entity consistency:** on-site consistent (2016 claim); JSON-LD missing LinkedIn/Twitter.
**Strongest opportunity:** instrument AI-answer citation capture + close LinkedIn entity gap.
**Top risks:** measurement blind spots (AI platforms), entity/authority gaps, heritage narrative external-only tension.

Proceed to Phase 37 only to (a) close the UNKNOWN measurement gaps with credentialed access and (b) act on the RECOMMENDATION items above — none of which were implemented in this phase.

- **Trade-portal, marketplace, publication mentions:** UNKNOWN.

**None of the above are reported as zero.** Each is carried forward as a monitoring target for Phase 37+. [UNKNOWN]

---

## 17. Strongest Opportunities (RECOMMENDATION / INFERRED)

1. **Capture AI-answer citations (highest priority):** instrument Perplexity API + logged-in Google/Bing generative rendering next month. Currently the single largest scoring blind spot (weight 0.30 combined). [RECOMMENDATION]
2. **Close the LinkedIn entity gap:** create/verify a LinkedIn Company Page and add it to JSON-LD `sameAs`. Concrete, low-risk authority win. [RECOMMENDATION]
3. **Lift non-brand commercial rankings:** GSC shows position ~10 with strong impression volume on calculators/packing/cumin/UAE-trade — snippet + intent optimization can convert impression gap to clicks. [RECOMMENDATION]
4. **Build an entity anchor:** pursue a Wikidata item / Knowledge-Graph signal and consistent NAP+description across directories once accessible. [RECOMMENDATION]
5. **Reconcile heritage narrative** before any external storytelling to avoid entity inconsistency. [RECOMMENDATION]

---

## 18. Risks

- **Measurement risk (VERIFIED):** 60% of AI-visibility and 44% of authority dimensions are UNKNOWN; current scores are provisional floors, not true visibility.
- **Entity risk (OBSERVED):** missing LinkedIn `sameAs` and no Knowledge-Graph anchor weaken AI disambiguation.
- **Authority risk (OBSERVED):** no verified LinkedIn company page; directory/institutional presence unproven.
- **Heritage risk (VERIFIED/INFERRED):** if a third party asserts "1980" origin while the site says "2016", an external-only inconsistency exists that AI could surface.
- **Data-freshness risk (OBSERVED):** GSC export predates the 20-Aug SEO release; post-release comparison needs a fresh export.

| Google web index | 200 | No (SERP UI) | OBSERVED |
| Bing web index | 200 | **Yes (brand)** | OBSERVED |

**Key points:** social `sameAs` (Facebook/Instagram) are live and on-brand. **LinkedIn has no verified company page (404)** — a concrete authority gap. Directory/institutional presence is UNKNOWN (not proven absent — guessed URLs 404 and several sites block bots). [OBSERVED / UNKNOWN]

---

## 11. Stage H — Competitor Baseline

No competitor AI-citation or SERP share could be captured read-only (AI platforms inaccessible; per-query SERP positions not measurable). [UNKNOWN]

Expected competitors (from inventory intent): Tilda, KRBL, LT Foods (basmati); bulk/non-basmati rice exporters; spice/pulse commodity exporters; aggregator directories (IndiaMART, TradeIndia, ExportHub). [INFERRED]

A competitor share-of-voice study is deferred to a Phase 37 capability that can capture SERP/AI answers. [RECOMMENDATION]

---

## 12. Stage I — Entity Consistency

- On-site entity: "JFT Agro Overseas LLP … registered in 2016" (about.html meta description, VERIFIED).
- JSON-LD `Organization` `sameAs`: Facebook + Instagram only. **No LinkedIn, no Twitter/X, no Crunchbase/Wikidata.** [VERIFIED]
- The four AI platforms (Stage E) have no structured entity feed to draw from, increasing reliance on on-site structured data + third-party mentions. [INFERRED]
- **Gap:** absence of LinkedIn/Twitter `sameAs` and any Wikidata/Knowledge-Graph anchor weakens entity disambiguation for AI systems. [OBSERVED / INFERRED]
- **No on-site contradiction** between the 2016 registration claim and any other published claim (see Stage J). [VERIFIED]

---

## 13. Stage J — Heritage / Narrative Tension

- Repo-wide grep for "1980" across HTML: **no matches**. [VERIFIED]
- The "1980 family trading" heritage narrative is **not present** in current published HTML; only the "registered in 2016" claim is published. [VERIFIED]
- Therefore the Stage-I heritage tension is **external-only** (if any third-party source asserts a 1980 origin, it is not echoed on-site and creates no on-site contradiction). [VERIFIED / INFERRED]
- If future Phase 37 work introduces heritage content, it must be reconciled with the 2016 registration claim to preserve entity consistency. [RECOMMENDATION]

---

## 14. Stage K — AI-Search Scoring Methodology

Model: weighted average of 7 dimensions (weights sum to 1.0).

| Dimension | Weight | Baseline value | Class |
|---|---|---|---|
| branded_visibility | 0.15 | 70 | OBSERVED |
| commercial_query_visibility | 0.20 | 25 | INFERRED (from GSC avg pos ~10) |
| product_visibility | 0.15 | 45 | INFERRED (catalogue indexed, weak query coverage) |
| ai_citation_rate | 0.20 | None (UNKNOWN) | UNKNOWN |
| official_page_citation_rate | 0.10 | None (UNKNOWN) | UNKNOWN |
| competitor_share | 0.10 | None (UNKNOWN) | UNKNOWN |
| external_authority | 0.10 | 30 | INFERRED |

- **OBSERVED score** renormalizes weights over the 4 known dimensions → **42.1 / 100**.
- **COVERAGE-ADJUSTED score** applies fixed weights with UNKNOWN = 0 (conservative lower bound) → **25.2 / 100**.
- Measured coverage = **60%** (3 of 7 dims UNKNOWN).
- UNKNOWN is **never** imputed as zero in the OBSERVED number; it is only a floor in the adjusted number. [INFERRED — methodology disclosed]

| ChatGPT (browse) | UNKNOWN / INACCESSIBLE | No credentialed access; browse results not observable read-only. |

**These four dimensions are deliberately excluded from the OBSERVED score and scored 0 only in the conservative COVERAGE-ADJUSTED score, with an explicit UNKNOWN label. They are NOT reported as "zero citations."** [UNKNOWN]

The monitoring harness is built specifically to capture these once a future phase grants credentialed access. [RECOMMENDATION]

---

## 9. Stage F — Google Search Console Evidence (OBSERVED, dated 2026-08-20 export)

Source: `reports/search-console-export-2026-08-20/` (read-only reuse; predates the 20-Aug SEO release).

- **Totals (19 May–18 Aug 2026):** 286 clicks, 10,410 impressions, weighted CTR 2.75%, impression-weighted avg position **10.03**. [OBSERVED]
- **Monthly trend (impressions rising):** May 990 → Jun 2,806 → Jul 3,934 → Aug (18d) 2,680; avg position 10.0 → 9.5 → 8.8 → 12.4. [OBSERVED]
- **Top countries:** India (252 clicks / 6,488 imp / pos 8.01), USA (1 click / 1,563 imp / pos 14.12, CTR 0.06%), UAE, Netherlands, Nigeria, Ghana, UK, Thailand. [OBSERVED]
- **Devices:** Desktop 158 clicks, Mobile 125, Tablet 3; mobile avg position 6.71 (stronger than desktop 12.12). [OBSERVED]
- **Highest page opportunities (CTR gap):** `blog-cumin-jeera-price-outlook-2026.html` (1,729 imp, pos 6.99, ~79 est. gap clicks), `packing-calculator.html` (1,444 imp, pos 6.9), `uae-trade.html` (601 imp, pos 14.29). [OBSERVED]
- **Highest non-brand query opportunities:** `fob calculator` (212 imp), `1 million cif price` (136 imp), container-packing queries, Tamil cumin-price queries. [OBSERVED]

Important boundary (from the export's own analysis): GSC tables cannot be joined to claim query→page attribution; candidate targets are intent-based, not observed mappings. A Query+Page API export is required for that. [OBSERVED]

| Working tree | clean (pre-phase) | VERIFIED |
| Homepage HTTP | 200, canonical `https://jftagro.com/`, x-default set | VERIFIED |
| `security.txt` | 200 | VERIFIED |
| `sitemap.xml` | 200 | VERIFIED |
| `rice-exporter-india.html` | 200 | VERIFIED |
| `about.html` | 200 | VERIFIED |
| JSON-LD types on home | Organization, ContactPoint, PostalAddress, WebSite, SearchAction | VERIFIED |
| `sameAs` | Facebook, Instagram only (no LinkedIn/Twitter) | VERIFIED |
