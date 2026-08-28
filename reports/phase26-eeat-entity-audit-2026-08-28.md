# Phase 26 — E-E-A-T, Entity Authority & AI Search Trust Audit

Date: 2026-08-28
Status: Investigation complete. **ZERO WEBSITE SOURCE FILES MODIFIED.** No production change. No deployment.

## 1. Executive Summary

Phase 26 conducted a deeper E-E-A-T/entity/trust audit than Phases 24-25, specifically targeting trust pages not yet directly audited (`buyer-security.html`, `export-documentation.html`, `privacy.html`, `terms.html`), JS-extraction risk, expanded AI query testing, and — most significantly — genuine external (off-site, third-party) entity verification, which had not been attempted in any prior phase. This surfaced one real, well-evidenced, but genuinely **unresolvable-without-human-input** discrepancy (a postal-code mismatch between JFT's own site and an official third-party LEI registry, where independent research shows both codes are legitimately used within the same market complex). Every other candidate investigated either confirmed existing work is sound (several false positives from my own extraction methods were caught and dismissed before being reported) or was correctly left undocumented-but-unfixed per the Fix Decision Gate's evidence and root-cause requirements. **No website file was modified this phase — a fully valid, deliberate outcome given the evidence, not an absence of effort.**

## 2. Phase 25 Baseline

| Item | Value |
|---|---|
| Git commit | `e64a3f2ba03c114a94ef61db20fbff486dab2a2b` (unchanged) |
| Production | `HTTP 200`, sitemap 1,453 URLs |
| Phase 25's `worker.js` redirect fix | Confirmed still **local-only, not deployed** — `curl https://jftagro.com/spices/` still returns `404` in production, exactly as Phase 25 documented |
| `legalName` fix (Phase 24) | Confirmed still in place |
| Article-category links (Phase 25) | Confirmed still in place |

No regression. No unexpected difference.

## 3. Entity Identity Audit

Re-verified (not assumed) across `index.html`, `about.html`, `contact.html`, `footer.html`, `privacy.html`:

- **Name**: "JFT Agro Overseas" consistently used as the brand/display name.
- **Legal name**: "JFT Agro Overseas LLP" consistently used in legal contexts (`privacy.html`'s data-controller clause, `about.html`'s `legalName` schema property and prose) — correctly distinct from the brand name, not contradictory.
- **Address**: `Godown N-2, APMC Market, Danabunder, Phase II, Sector 19, Vashi, Navi Mumbai, Maharashtra 400705, IN` — consistent across every internal page checked. `privacy.html`'s legal notice uses a shortened form (`APMC Market, Phase II, Sector 19, Vashi, Navi Mumbai, Maharashtra`) omitting "Godown N-2" and "Danabunder" — a normal legal-notice abbreviation, not a contradiction.
- **Phone/email**: consistent (see Phase 24/25 findings, reconfirmed unchanged).
- **A false positive caught and dismissed**: `privacy.html`'s and `terms.html`'s H1 text initially appeared to read "PrivacyPolicy" and "Terms ofTrade" (missing spaces) via a naive tag-stripping check. Reading the raw HTML showed this is a `<br>`-separated two-line stylized hero heading (`Privacy<br><em>Policy</em>`) — the exact same deliberate pattern used on the homepage and `about.html`. **Not a defect** — correctly investigated before being reported, per Rule 1's root-cause requirement.

**Entity Consistency Matrix (internal)**:

| Attribute | Homepage | About | Contact | Footer | Privacy | Product pages (sample) | Consistent? |
|---|---|---|---|---|---|---|---|
| Brand name | JFT Agro Overseas | JFT Agro Overseas | JFT Agro Overseas | JFT Agro Overseas | JFT Agro Overseas LLP (legal context) | JFT Agro Overseas | Yes |
| Address | Full | Full | Full | Full | Shortened (legal notice) | N/A | Yes (abbreviation, not conflict) |
| Phone (primary) | `+91 84250 57274` | Same | Same | Same | N/A | Same | Yes |
| `@id` | `#organization` | `#organization` | (no full block) | (no full block) | N/A | `#organization` | Yes |

**No internal entity fragmentation found.**

## 4. Organization Schema Audit

Building on Phase 24's `legalName` fix (1,326 files) and Phase 24's confirmation that Product schema is correctly absent: re-checked `sameAs` URLs are genuinely live, not dead links.

| Property | Value | Verified |
|---|---|---|
| `name` | JFT Agro Overseas | Consistent everywhere |
| `legalName` | JFT Agro Overseas LLP | Present on 1,327 declarations (Phase 24) |
| `url` | `https://jftagro.com/` | Consistent |
| `logo` | `https://jftagro.com/images/jft%20logo.png` | Present |
| `sameAs` | `facebook.com/jftagro` (HTTP 200, live), `instagram.com/jftagro` (HTTP 200, live) | **Verified live this phase, not assumed** |
| `address` | Consistent `PostalAddress` | See §6 for one external discrepancy |
| `@id` | `https://jftagro.com/#organization` | Single canonical entity, no duplicates found |

**No conflicting Organization schema, no duplicate entities, no unsupported `sameAs` found.**

## 5. E-E-A-T Experience Audit

Consistent with Phase 24's findings, reconfirmed: `about.html` states a specific, checkable registration year (2016) with an explicit caveat that predecessor-business history requires independent verification — genuine, honest experience signaling rather than a vague "decades of experience" claim. Product-page FAQ content (Phase 24's 84-page audit) demonstrates real operational knowledge (container-load math, HS codes, documentation lists) rather than generic filler. `export-documentation.html` and `buyer-security.html` (newly read in full this phase) both provide specific, practical process explanations (LC vs. TT payment safety mechanics, a defined export-document set) rather than abstract claims.

**Distinguishing demonstrated experience from generic knowledge**: the container-load figures, HS codes, and packaging specifics on product pages are demonstrated (specific to JFT's actual catalog); the LC/TT payment-mechanics explanation on `buyer-security.html` is more general trade knowledge (correct and useful, but not JFT-specific first-hand experience) — this distinction matters for E-E-A-T evaluation and is recorded honestly rather than credited as "experience" where it is really "expertise."

## 6. External Entity Authority — A Genuine New Finding

This is the one substantively new investigation this phase performed that Phases 1-25 had not: checking whether a real, independent, authoritative third party confirms JFT's identity.

**Found**: a Legal Entity Identifier (LEI) registration — `globallei.in/lei/3358008COTZVRF8ZQE38/jft-agro-overseas-llp` — a legitimate, internationally-recognized corporate identifier issued under the Global LEI Foundation framework (used for financial/regulatory identification, not a spammy directory). It confirms: entity name "JFT Agro Overseas LLP", LLP registration, **ACTIVE** status, business registration number **AAY-5952**, LEI status **ISSUED**, registered **2021-11-15**, next renewal **2026-11-14**. **This is a strong, genuine, verifiable external authority signal** — classified as **STRONG** per Part K's scale, not moderate/weak (an LEI is a formal regulatory credential, materially more authoritative than a business directory listing).

**One discrepancy found**: the LEI registry lists the postal code as **400703**; JFT's own website consistently uses **400705** everywhere (Organization schema, `contact.html`, `footer.html`, confirmed across Phases 21-25).

**Investigated before concluding anything** (per Rule 1/Rule 3): searched independently for the correct postal code of "APMC Market, Sector 19, Vashi, Phase II, Navi Mumbai." Result: **both codes are genuinely, legitimately in use within the same market complex** — one source shows "APMC Market 2, Phase 2, Sector 19" as `400703`, while a different, verifiable government-affiliated source (National Medicinal Plants Board, a Government of India body) lists a specific unit at "APMC Market-1, Phase-II, Sector-19, Vashi" as `Navi Mumbai-400 705`. This is a large, subdivided market complex where adjacent buildings/godowns can legitimately carry different postal codes.

**Conclusion, per Rule 3's explicit instruction**: this cannot be resolved from available evidence — **classified as UNKNOWN / REQUIRES HUMAN VERIFICATION**, not silently assumed correct in either direction. **No change was made to JFT's website's postal code.** Changing it based on an external registry entry that itself might reflect a different building within the same complex would risk replacing a correct, long-standing, internally-consistent fact with an unproven one — exactly the outcome Rule 3 and the Fix Decision Gate (condition 3, "root cause is proven") are designed to prevent. **Recommendation for the business**: confirm with JFT directly (or via their own LEI-issuing/registration paperwork) which postal code is correct for their specific Godown N-2 address, and update whichever source (website or LEI registry) is wrong — this phase does not and should not guess.

## 7. E-E-A-T Expertise Audit

No new full re-audit performed (Phase 24's 84-product and Phase 25's 37-article delegated audits already cover this exhaustively and remain valid, unchanged). This phase's incremental contribution: read `buyer-security.html` (507 words, LC/TT payment-safety specifics, correct and useful) and `export-documentation.html` (755 words, defined export-document set) in full — both substantive, specific, non-generic. No new expertise gap found beyond what Phase 25 already documented (3 thin category hubs, 1 placeholder article).

## 8. Author / Editorial Responsibility Audit

Unchanged from Phase 24/25's confirmed-correct finding: articles use organizational authorship (`"author":{"@type":"Organization","name":"JFT Agro Overseas",...}`), which is the honest choice for a company blog with no named individual subject-matter authors on record. Classification per Part E's own categories: **company attribution sufficient** for all 30 substantive articles — none require an invented individual author identity, and none currently claim one falsely.

## 9. Trust Architecture Audit

Newly read in full this phase: `buyer-security.html`, `export-documentation.html`, `privacy.html`, `terms.html`. All four are substantive (507-755 words), specific to JFT's actual commercial process, internally consistent with the rest of the site's entity/address/contact information, and free of unsupported claims. `certificates.html` (already investigated in Phase 25) confirmed to deliberately withhold certificate numbers behind a buyer-request flow — a sound anti-fraud design, reconfirmed.

**Answering the phase's own question** ("Can a cautious international buyer independently understand who they are dealing with and how the company operates?"): **yes, substantially** — legal entity, address, registration year, certification types, payment-safety mechanics, and the full export-document set are all disclosed; exact certificate numbers and precise operational scale figures are appropriately gated behind a genuine buyer inquiry rather than either published risk-lessly or fabricated.

## 10. Commercial Credibility Audit

Consistent with Phase 24/25: product specificity (moisture/purity/broken%/HS codes), packaging options, MOQ (1 FCL), container-load math, and documentation lists are all present, specific, and internally consistent across the 84 product pages. No claim was found that reads as stronger than its evidence — the certificates.html "not published, request for verification" pattern (§9) is itself evidence of appropriate claim calibration rather than overclaiming.

## 11. Evidence Graph

| Claim | Page(s) | Evidence source | Visible? | Structured? | Internally supported? | External support? | Risk |
|---|---|---|---|---|---|---|---|
| Company identity (JFT Agro Overseas / LLP) | Homepage, About, Contact, Footer, Privacy | Consistent prose + Organization JSON-LD | Yes | Yes | Yes | Yes — LEI registry confirms ACTIVE LLP status | LOW |
| Registered 2016 | About | Prose + explicit predecessor-history caveat | Yes | No (not a schema property) | Yes | Not independently checked (out of scope to verify a specific date via LEI, which shows 2021 LEI issuance, not company founding) | LOW |
| ISO 9001:2015 / ISO 22000:2018 / HACCP / APEDA / FSSAI / Star Export House | Homepage, About, Contact, product pages | Consistent prose across every page checked | Yes | No | Yes (internally consistent) | Not independently verified against the certifying bodies' own registries this phase (would require contacting APEDA/ISO certifying bodies directly — out of this session's safe scope) | MEDIUM (internally consistent but not third-party-verified) |
| Address (400705) | Homepage, About, Contact, Footer | Consistent | Yes | Yes | Yes | **Contradicted by one external source (LEI: 400703)**; both codes legitimately used in the same complex per independent research | MEDIUM — genuine open question, not a proven defect |
| Export to 25+ countries / specific African nations | Homepage, About, `africa-trade.html` | Prose | Yes | No | Yes | AI-search summary using JFT's own `africa-trade.html` as a source produced an **accurate** restatement this phase (§13) | LOW |
| Certificate numbers | `certificates.html` | Explicitly marked "Not published," request-gated | Yes (as a gate, not the number) | No | Yes (consistent policy) | N/A by design | LOW (deliberate design, not a gap) |

## 12. AEO Query Testing (continuing Phases 24-25's methodology)

Tool: the single web-search tool available this session — explicitly not Google AI Overviews, Bing Copilot, ChatGPT search, Perplexity, or Gemini. 5 new queries this phase (in addition to the 10 already tested across Phases 24-25):

| # | Query | Type | JFT appears? | Notes |
|---|---|---|---|---|
| 1 | `rice supplier India for Africa export` | Geography/commercial | **Yes, accurately** | `africa-trade.html` cited directly; the AI summary's restatement of JFT's African market coverage matched the site's own content, no fabrication detected this time |
| 2 | `documents required from Indian rice exporter` | Buyer-intent/trust | No | Dominated by APEDA's own official page and generic export-guide blogs |
| 3 | `Indian parboiled rice supplier` | Commodity | No | Competitors: Pramoda Exim, Ashoka Rice Mills, SKRM Foods |
| 4 | `how to inspect rice before shipment quality` | Trust | No | Dominated by third-party inspection-service providers (HQTS, Alex Stewart Agriculture) and academic sources |
| 5 | `globallei.in JFT Agro Overseas LLP LEI ...` | External verification | Yes | Confirmed the LEI registration details in §6 |

**Refined pattern**: JFT is not merely invisible for all non-branded queries — it appears **accurately** for at least one geography-specific commercial query that directly matches a dedicated page (`africa-trade.html`), suggesting the site's regional trade pages have some real external traction that its generic commodity/category pages do not yet have. This is a more precise, nuanced finding than Phase 24/25's broader "absent from generic queries" conclusion, and points toward regional/geography-specific content as a comparatively stronger existing asset than category-generic content for AI-search visibility.

## 13. GEO / LLMO Citation Readiness

Checked whether critical page content depends on JavaScript execution to be extractable: `1121-basmati-rice-exporter.html`'s FAQ content (5 Q&A pairs, matching its `FAQPage` schema) is present directly in static HTML, not JS-rendered-only. `quote-calculator.html` has 671 words of static visible text before any script executes — the page is not a blank shell requiring JS. **No JS-dependency extraction problem found** on the pages checked — consistent with the site's established static-HTML architecture.

## 14. AI Misinformation / Entity Confusion (continuing Phase 25)

Reconfirmed, not re-investigated from scratch: the "Since 1980" fabrication's root cause (stale, still-indexed legacy WordPress URLs) was identified in Phase 25 and a fix was written into `.cloudflare/worker.js` — **confirmed this phase still not deployed** (`/spices/` on production still returns `404`). No new misinformation pattern was found this phase beyond what Phase 25 already documented; the query in §12 row 1 is a positive counter-example (accurate AI representation), not a new misinformation instance.

## 15. External Entity Authority — Classification

Per Part K's requested scale: **STRONG** (LEI registration, a formal international regulatory credential, ACTIVE status, verifiable business registration number). This is a materially better external-authority signal than a typical business directory listing, and its existence was not previously documented in any prior phase's reports — recorded here for the first time.

## 16. Entity Consistency Outside the Website (Part L)

| Attribute | JFT's website | LEI registry | Consistent? |
|---|---|---|---|
| Legal name | JFT Agro Overseas LLP | JFT Agro Overseas LLP | Yes |
| Entity type | LLP | LLP | Yes |
| City | Navi Mumbai | Navi Mumbai | Yes |
| Postal code | 400705 | 400703 | **No — genuine, unresolved discrepancy (§6)** |
| Status | (implied active, operating) | ACTIVE | Yes |

Per Part L's explicit instruction, no attempt was made to correct the third-party LEI profile, and no assumption was made that either source is authoritative over the other.

## 17. Topical Authority (building on Phase 25's mapping)

No new mapping performed — Phase 25's `Entity → Category → Product → Article` graph (7/10 strong-or-adequate category hubs, 3/10 thin; 18/30 articles linking to products, 5/30 now linking to categories) remains the current, valid state. No new disconnected cluster or unsupported claim was found this phase.

## 18. Content Quality / Originality

Spot-checked `buyer-security.html` and `export-documentation.html` (read in full this phase, §9): both specific and non-generic, no repeated-boilerplate or "why choose us" filler found. No evidence of AI-generated-sounding prose was found in either page — consistent with the specific, factual, non-generic tone Phase 24/25 already documented across product pages and articles.

## 19. Source / Citation Quality

The pages read this phase (`buyer-security.html`, `export-documentation.html`, `privacy.html`, `terms.html`) present company-specific process information (correctly, without external citation needed — this is first-party operational description, not a claim requiring a third-party source) and general trade-mechanics information (LC/TT payment terms, documentation types) that is common professional knowledge, correctly presented without false attribution to JFT-specific research. No citation-quality defect found.

## 20. Schema ↔ Visible Content Consistency

Cross-checked: `about.html`'s `legalName: "JFT Agro Overseas LLP"` is directly supported by adjacent visible prose stating the same fact with a registration year. Homepage's `Organization` schema properties (name, address, contact, logo) all correspond to genuinely visible homepage/footer content — no schema property was found asserting something the visible page does not support.

## 21. Findings Register

| ID | Severity | Evidence | Affected pages | Root cause | On-site/off-site | Recommendation | Decision |
|---|---|---|---|---|---|---|---|
| P26-F1 | MEDIUM | LEI registry postal code (400703) vs. site-wide postal code (400705); independent research shows both codes legitimately used in the same market complex | All pages with the Organization address (127+ files) | Genuinely ambiguous — cannot be resolved without confirming JFT's exact building/godown assignment | Both (external record vs. internal fact) | Business should confirm the correct code directly and update whichever source is wrong | **DOCUMENTED, NOT MODIFIED** — root cause not proven (Gate condition 3 fails) |
| P26-F2 | INFORMATIONAL (positive) | `africa-trade.html` surfaced accurately in a geography-specific AI query | `africa-trade.html` | Regional trade pages have some real external traction | N/A | Consider (in a future phase, not now) whether similar page-level specificity could help other underperforming category queries | No action — informational only |
| P26-F3 | INFORMATIONAL (false positive, dismissed) | Apparent "PrivacyPolicy"/"Terms ofTrade" missing-space text | `privacy.html`, `terms.html` | Artifact of naive tag-stripping; real HTML uses a deliberate `<br>` two-line heading pattern | N/A | None — not a defect | No action |
| P26-F4 | INFORMATIONAL | ISO/APEDA/FSSAI/HACCP claims are internally consistent but not independently verified against certifying bodies' own registries this session | Homepage, About, Contact, product pages | Verifying would require contacting external certifying bodies, outside this session's safe scope | Off-site | None recommended — no evidence of falsity, only unverified-by-this-session | No action, classified UNKNOWN (not converted to a false PASS or FAIL) |

**No CRITICAL or HIGH severity finding exists.**

## 22. Fix Decision Gate

| Candidate | Gate result |
|---|---|
| Correct the website's postal code to match the LEI registry | **FAILS condition 3** (root cause not proven — both codes are legitimately in use nearby; no evidence the LEI registry, rather than the website, is the correct source) |
| Correct the LEI registry's postal code | **Out of scope entirely** — Part L explicitly forbids attempting to correct third-party profiles |
| Any other candidate | No other candidate reached the gate — all other investigation this phase either confirmed existing correctness or produced informational-only findings |

## 23. Changes Made

**ZERO WEBSITE SOURCE FILES MODIFIED.**

## 24. Regression Results

Not applicable — no file was changed, so no regression suite run was required to detect drift. `git status --short` confirmed unchanged before and after this phase's entire investigation.

## 25. Build Verification

Not applicable — no source change means no new build was required. The Phase 25 `worker.js` change remains local and unbuilt-into-a-fresh-bundle since Phase 25; no new bundle was built this phase (nothing changed to verify).

## 26. Deployment Status

**NOT DEPLOYED.** No deployment was performed or attempted this phase. The Phase 25 `worker.js` redirect fix also remains undeployed, confirmed via direct production testing (§2).

## 27. Limitations

- No live browser-automation tool available this session (consistent with every prior phase).
- AI query testing used the one general web-search tool available in this session — not Google AI Overviews, Bing Copilot, ChatGPT search, Perplexity, or Gemini specifically; none of those systems were independently testable, and no claim is made about their behavior.
- Certification claims (ISO/APEDA/FSSAI/HACCP) were checked for internal consistency only — this session did not and could not safely contact the certifying bodies' own verification registries to independently confirm validity; this is disclosed as UNKNOWN, not silently assumed true.
- The postal-code discrepancy (§6) could not be resolved with available evidence; this is explicitly left as an open question for the business, not guessed at.
- No external profile was created, contacted, or modified, per Part K/L's explicit instructions.

## 28. Open Risk Register

| Severity | Item |
|---|---|
| MEDIUM | P26-F1 — postal code discrepancy (400705 vs. 400703), genuinely unresolved, requires business confirmation |
| MEDIUM | P25 (carried forward) — TLS 1.0/1.1 acceptance, requires Cloudflare dashboard access outside this session |
| UNKNOWN | P25 (carried forward) — Cloudflare rate-limiting status for `/api/lead` |
| UNKNOWN | P26-F4 — certification claims not independently verified against issuing bodies |
| LOW-MEDIUM | P24 (carried forward) — Turnstile absent, deliberate, re-evaluation triggers documented |
| LOW | P25 (carried forward) — 3 thin category hubs, 1 placeholder article, both require future content authorship |
| INFORMATIONAL | P24/P25 (carried forward) — off-site/generic-query AI visibility gap, strategic not technical |

## 29. Phase 27 Recommendation

Based on the evidence gathered across Phases 24-26, the highest-value next steps are **not** another audit-style AI-search phase (the site's on-page technical/entity/trust foundation has now been examined from essentially every angle this program's methodology supports, with diminishing new findings each phase). The recommended next phase, if authorized, should be one of:

1. **A content-authorship phase**, narrowly scoped to the 4 already-identified, well-documented gaps: the `blog-toor-dal-export-india-2026.html` placeholder, light buyer-subtopic depth for the 3 thin category hubs (Wheat, Sugar, Raisins), and a decision on category-level FAQ — all already scoped in Phase 25's report.
2. **A deployment phase**, to actually ship Phase 25's `worker.js` redirect fix to production (with the standard pre/post-deployment verification this program has established) — this is the one change with a demonstrated, direct GEO/misinformation benefit that has been sitting implemented-but-undeployed for two phases.
3. **A business-input item**, not a technical phase at all: resolving the postal-code discrepancy found this phase requires someone at JFT to confirm the correct code — no further website investigation can resolve it.

## Stop

Per Phase 26's explicit instruction: **AUDIT COMPLETE — ZERO WEBSITE SOURCE FILES MODIFIED.** Do not begin Phase 27 without explicit authorization.
