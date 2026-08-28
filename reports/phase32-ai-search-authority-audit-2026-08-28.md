# Phase 32 — AEO + GEO + LLMO + AI Search + E-E-A-T Authority Audit

Date: 2026-08-28
Status: **INVESTIGATION COMPLETE. AUDIT-ONLY. ZERO WEBSITE MODIFICATIONS.**

## 1. Executive Summary

JFT Agro Overseas LLP's technical, on-page, and entity-schema foundation — already exhaustively verified clean across Phases 1-31 — continues to hold up. What this phase adds is the first *direct, evidence-based measurement* of how that foundation translates into actual AI/search visibility, using live queries rather than inference.

The result is a clear, honest split:

- **Branded queries** (company name, name + product category): JFT is found, and most facts returned are accurate — but **one specific, material fabrication persists unchanged from Phase 24 through this phase, 8 phases and presumably weeks/months later**: an AI-synthesized claim that JFT is a "Star Export House since 1980," directly contradicting the website's own careful, disclaimed "Established 2016" framing. This is reconfirmed here as **AI-generated, not website-sourced** (see §14).
- **Generic, high-commercial-intent category queries** covering nearly the entire product catalog (rice, spices, herbs, animal feed, sugar, raisins) — the queries that actually drive new-buyer discovery — return **zero JFT visibility** in 8 of 9 tests run this phase, with established and even peer-scale competitors dominating instead. The one exception (an Africa-region query) reconfirms a positive finding from Phase 26.
- **Buyer-intent questions** that JFT's own trust pages (`buyer-security.html`, `export-documentation.html`) were purpose-built to answer are not returning JFT at all — generic third-party advisory content wins instead.

None of this traces to a website defect. The technical/content foundation has already been proven sound. The gap is **off-site authority**: no confirmed B2B marketplace listing (Indiamart/TradeIndia/ExportersIndia), no discoverable LinkedIn company page, and an unverifiable business-registration figure ("AAY-5952") that does not match any number on the website or the confirmed-real LEI. These are the load-bearing findings of this phase.

**No website file was modified. No fixes were implemented.** This is a strategy document for a future phase's decision-making.

## 2. Method and Tool Disclosure

Per this phase's own rules, honesty about tool access takes priority over the appearance of thoroughness.

**What was actually used:** one general-purpose, AI-summarized web-search tool (`WebSearch`), which blends organic search results with a synthesized natural-language answer. Its exact backing search index/AI model is not disclosed to this session and is **not assumed to be Google, Bing, ChatGPT, Perplexity, or Gemini specifically**.

**What was NOT tested, and is marked accordingly everywhere in this report and its companion matrix:**

| Platform | Status |
|---|---|
| Google Search (organic ranking) | Partially observable via returned links; not a verified live SERP screenshot |
| Google AI Overviews / AI Mode | **NOT TESTED — TOOL ACCESS LIMITATION** |
| ChatGPT / ChatGPT Search | **NOT TESTED — TOOL ACCESS LIMITATION** |
| Perplexity | **NOT TESTED — TOOL ACCESS LIMITATION** |
| Gemini | **NOT TESTED — TOOL ACCESS LIMITATION** |
| Microsoft Copilot / Bing Chat | **NOT TESTED — TOOL ACCESS LIMITATION** |

No result from any of the untested platforms is simulated, guessed, or implied anywhere in this report. This matches the disclosure standard Phase 26 already established for the same tool limitation.

**Query sampling:** 21 substantive queries were run this phase (full list and results in `reports/phase32-ai-visibility-matrix-2026-08-28.json`), covering all five required categories (brand/entity, generic commercial, buyer-intent, commodity-specific across 7 of JFT's 9 governed product categories, geography). This is a representative sample, not an exhaustive test of every example listed in the phase prompt — chosen to maximize evidence diversity within a realistic tool-call budget, consistent with the phase's own instruction against treating keyword volume as the only decision factor. Every category required by the phase was tested at least twice.

## 3. Baseline Confirmed Before Investigation

Re-confirmed rather than re-run in full (already exhaustively verified through Phase 31): production healthy, 1,753 renderable pages, 0 regression findings, sitemap 1,454 URLs unchanged. No technical/on-page audit was repeated in this phase — Sections 3-9, 15-19 of the phase's own instructions build on that existing, unrepeated evidence rather than re-deriving it.

## 4. AI Search Query Benchmark — Results Summary

Full row-by-row data: `reports/phase32-ai-visibility-matrix-2026-08-28.json`. Headline patterns:

### A. Brand/entity queries (4 tested)
JFT is found in all 4. Core facts (LLP status, Navi Mumbai/Vashi location, ISO 9001:2015/ISO 22000:2018/HACCP, 250 MT/day milling capacity, APEDA/Spices Board/AEO/RCMC references) are **accurate and traceable to real website content** (cross-checked directly against `about.html`, `certificates.html`, `index.html` source — see §14 methodology). One fabrication (`Since 1980` / "5 decades of experience") appears in every brand-query result and is **not present anywhere in the website's HTML** (confirmed via direct full-text search of every root-level HTML file for the string "1980" — zero matches).

### B. Generic commercial queries (5 tested: rice exporter India, IR64/parboiled rice, Middle East/UAE rice+spice, Africa rice/spice/pulses, animal feed maize/sorghum/millet)
JFT appears in **1 of 5**. The single hit (Africa-region query) reconfirms Phase 26's P26-F2 finding is still accurate and still holding, 2 phases later — a genuine, if narrow, positive signal that region-specific pages with concrete detail can earn a citation. The other 4 — including the single highest-value generic head-term, "rice exporter India" — return zero JFT presence; established competitors (LT Foods, Adani Wilmar, Sukhva Rice, Shri Lal Mahal, AMIRA Nature Foods) and category specialists (Plowexim, Ashoka Rice Mills, WGC Exports, Svara Impex) fill the results instead.

### C. Buyer-intent questions (2 tested)
JFT appears in **0 of 2**, despite owning purpose-built pages for exactly these questions (`buyer-security.html` for exporter-verification guidance, `export-documentation.html` for shipping-document guidance — both previously verified functionally and structurally correct in Phases 29-31). Generic third-party advisory blogs dominate both results.

### D. Commodity-specific questions (5 tested, spanning spices, herbs, sugar/flour, raisins, and the rice/IR64 query already counted in B)
JFT appears in **0 of 4** additional commodity tests (spices, herbs, sugar/flour, raisins). A recurring, closely-matched competitor set emerges per category (see §22).

### E. Geography-specific queries (2 tested beyond the Africa hit already counted: Middle East/UAE, Southeast Asia)
JFT appears in **0 of 2**. The Southeast Asia query in particular returned almost no exporter-brand results at all (dominated by country-level trade-statistics sites), suggesting this is a thin-competition space where a well-evidenced page could plausibly earn a citation — worth noting for Section 9's opportunity map, though this is inference, not a proven opportunity.

**Pattern, stated plainly:** JFT's AI/search visibility is effectively binary — present and mostly accurate for its own name, essentially absent for the commercial-intent queries that would introduce it to a new buyer. This is the same conclusion Phase 24-26 reached from indirect evidence; this phase confirms it directly.

## 5. Entity Understanding Audit

| Attribute | Website | External evidence found this phase | Consistent? |
|---|---|---|---|
| Legal name | JFT Agro Overseas LLP | Matches LEI registry (Phase 26, reconfirmed present) | Yes |
| Founding/establishment | "Established 2016," explicit disclaimer that any predecessor-business history requires buyer verification | AI search summaries confidently state "since 1980" with no disclaimer | **NO — see §14, classified AI-GENERATED** |
| Location | Godown N-2, APMC Market, Vashi, Navi Mumbai, 400705 | LEI registry lists postal code 400703 (open question since Phase 26, not re-resolved this phase — no new evidence found) | Partially — unresolved, business input still required |
| Registration number | Not published on the website (LEI `3358008COTZVRF8ZQE38` is the only registration figure the website's own reports have independently verified) | AI summaries repeatedly cite "AAY-5952" as a "business registration number" | **UNVERIFIED — see §6** |
| Certifications (ISO 9001:2015, ISO 22000:2018, HACCP, FSSAI, APEDA, Spices Board, AEO/RCMC) | All genuinely present in website source (spot-checked directly) | AI summaries list the same set | Yes — accurate |
| LinkedIn presence | Not linked from the website (only Facebook/Instagram appear in `sameAs`) | No JFT Agro Overseas LLP company page found; search returns unrelated companies ("JF Agro," "JFT Inc.") | **Gap — no confirmed page found** |
| B2B marketplace presence (Indiamart, TradeIndia, ExportersIndia) | Not linked from the website | No JFT listing found on any of the three largest Indian B2B export marketplaces | **Gap — no confirmed listing found** |

No fabricated historical claims, incorrect product associations, or incorrect ownership information were found on the website itself. The one confirmed misinformation vector is external (§14).

## 6. The "AAY-5952" Registration Number — Unresolved, Flagged Honestly

Multiple AI search summaries this phase repeated a specific figure, "business registration number AAY-5952," attributed to JFT Agro Overseas LLP. This number:

- Does **not** appear anywhere in the website's HTML (confirmed via direct search).
- Does **not** match the confirmed-real LEI (`3358008COTZVRF8ZQE38`).
- Could not be independently confirmed or refuted against the Ministry of Corporate Affairs' LLPIN lookup with the tools available this session (that lookup requires an interactive, likely CAPTCHA-gated government portal).

This is classified **UNKNOWN — business input required**, not corrected, not assumed false, and not published anywhere. It sits alongside the Phase 26 postal-code discrepancy as a second open entity-verification question best resolved by someone at JFT confirming the company's actual LLPIN against the MCA registry directly.

## 7. External Authority Audit

| Source | Category | Status found this phase |
|---|---|---|
| LEI (`globallei.in`, `3358008COTZVRF8ZQE38`) | **STRONG** | Reconfirmed present and ACTIVE (no change since Phase 26) |
| APEDA RCMC | **STRONG (claimed on-site, not independently re-verified)** | Website claims APEDA/Spices Board/AEO/RCMC; JFT's name did not appear in the visible excerpt of APEDA's public rice-exporter PDF list returned by search — **inconclusive**, not a proven absence (the full PDF was not parsed) |
| FIEO membership | **UNKNOWN** | No evidence found either confirming or denying FIEO membership; APEDA/Spices Board RCMC is a separate credential from FIEO membership |
| LinkedIn company page | **WEAK/ABSENT** | No confirmed page found |
| Indiamart / TradeIndia / ExportersIndia | **WEAK/ABSENT** | No confirmed listing found on any of the three; several peer-scale competitors (Rivha Traders, VLX Exports, Ashapura Exporters) do maintain a visible presence adjacent to these queries |
| Trade press / industry association mentions | **ABSENT** | None surfaced in any query this phase |
| Chamber of commerce | **UNKNOWN** | Not investigated with available tools this phase; not previously investigated in prior phases either |

No risky, spam, or paid-directory signals were found or are recommended. No backlink purchase, mass directory submission, or link scheme is recommended anywhere in this report, per the phase's explicit prohibition.

## 8. E-E-A-T Findings Summary

Full detail: `reports/phase32-eeat-evidence-map-2026-08-28.md`/`.json`. Headline:

- **Experience** — genuinely evidenced (not merely claimed): a specific, named milling facility (Balap, Raigad) with a specific, consistent 250 MT/day figure repeated identically across `index.html` and search-engine summaries; functional, previously-verified buyer tools (packing calculator, port-transit calculator, shipment tracker); real per-product specification tables across all 84 products.
- **Expertise** — genuinely evidenced: 37 articles covering real export-process topics (APEDA registration, bill of lading, certificate of analysis, HS codes), product-specific FAQ content built from governed specification data (Phase 7), and functioning trust/documentation pages.
- **Authoritativeness** — the weakest of the four, and the correct target for future work: one strong independent signal (LEI), no other confirmed independent registry/association/press signal, and two absent modern-discovery channels (LinkedIn, B2B marketplaces) that peer competitors visibly use.
- **Trustworthiness** — strong internally (consistent NAP data, an honestly-disclaimed founding narrative, a deliberate certificate-verification-gate design already assessed as sound in Phase 26) but undermined *by an external actor, not the website* — a buyer who cross-checks JFT's own careful "Est. 2016" framing against an AI summary's confident "since 1980" claim encounters a contradiction the website did not create and cannot directly fix.

## 9. AI Misinformation Audit — Full Classification

| Finding | Classification | Evidence |
|---|---|---|
| "Star Export House since 1980" / "5 decades of experience" | **AI-GENERATED** | Zero occurrences of "1980" anywhere in the website's HTML (verified this phase via direct full-repository search); website consistently and explicitly states "Established 2016" with a predecessor-history disclaimer. First found Phase 24; reconfirmed unchanged in this phase — persists across at least 8 phases. |
| Fabricated `about.html` page title ("JFT Agro Overseas \| Star Export House India Since 1980") | **AI-GENERATED** | The website's actual, current `<title>` tag is "About JFT Agro Overseas \| Company & Buyer Verification" (confirmed by direct file read this phase) |
| "7 branch offices" in Russia, Vietnam, Sri Lanka, Indonesia, Benin, Dubai, Zambia | **THIRD-PARTY/AI OVERSTATEMENT** | The website genuinely names these countries as regional trade hubs/target markets (`about.html`, `index.html`), but does not claim staffed "branch offices" in each; the AI's summary upgrades a market-relationship claim into a stronger operational claim the site does not make |
| "AAY-5952" registration number | **UNKNOWN** | Not found on the website; does not match the confirmed LEI; source cannot be established with available tools (§6) |
| "Dedicated slots with Maersk, MSC & CMA for guaranteed transit times" | **AI-GENERATED / THIRD-PARTY CONFLATION** | The website cites Maersk's public container specifications as a reference source (`packing-calculator.html`) and a *different* page (a blog article) lists generic carrier/route data for Africa-bound shipping lanes; neither claims JFT holds "dedicated slots" or "guaranteed transit" with any carrier. The AI appears to have merged two unrelated, accurately-sourced facts into a new claim the website does not make. |
| Certifications (ISO 9001:2015, ISO 22000:2018, HACCP, FSSAI, APEDA, Spices Board, AEO, RCMC) | **ACCURATE / WEBSITE-SOURCED** | All independently confirmed present in the actual website source this phase |
| Customer testimonials referenced in one AI summary | **NOT INDEPENDENTLY VERIFIED THIS PHASE** | Plausible (the website does carry testimonial-style content in some areas per prior phases) but not spot-checked against the exact wording cited; not classified either way |

**Only website-sourced errors could justify a website change. None were found.** Every confirmed misinformation vector this phase is AI-generated or unresolved-third-party, consistent with the "only website-sourced errors may potentially justify a website modification" rule — no website change is recommended from this section.

## 10. AEO Content Coverage (Summary)

Built from the governed 84-product/9-category catalog (`data/products.json`) cross-referenced against the 37-article program and the query results in §4:

- **COVERED** — most core product specification questions ("what specifications matter when importing X") across all 9 categories; export-documentation and buyer-verification guidance (content exists and is good; the gap is citation, not content — see §4C).
- **PARTIALLY COVERED** — commodity-use-case questions ("what is X used for") for the herb/spice categories, where product pages focus on trade specification more than end-use education.
- **MISSING** — no meaningful gap was found that both (a) has genuine commercial relevance and (b) JFT has first-hand evidence to answer better than existing third-party content. This is stated plainly rather than manufactured: the content layer is not the bottleneck.
- **SHOULD NOT CREATE** — any new page whose sole purpose is to chase a generic keyword without new first-hand evidence behind it; this would repeat the exact anti-pattern this phase's rules warn against (thin content, duplication, no differentiation).

## 11. Generative Answer Structure Audit

Spot-checked a sample of already-live pages (`buyer-security.html`, an africa-trade region page, a product FAQ) for AI-extractability: clear headings, explicit entity references (consistent "JFT Agro Overseas LLP" naming), concrete tables, unambiguous specification values. **No extraction/understanding problem was found in this sample.** The Africa-region query's accurate citation (§4B) is itself evidence that at least one page's structure is already being read and reused correctly by the tool tested. No restructuring is recommended.

## 12. LLMO Entity Consistency

Organization schema, About page, Contact page, and trust pages were spot-checked (not re-audited in full — Phase 24/26 already did this exhaustively) and found consistent with each other. The one inconsistency identified is between the website and *external* AI-generated text (§9), not within the website's own signals.

## 13. Author / Expert Signals

Current state, reconfirmed rather than re-derived: articles use organizational attribution, not fabricated individual identities; a governance script (`validate_editorial_governance.py`) already prevents unsupported "reviewed by [name]" claims (Phase 23/24). This is a deliberately correct, non-fabricated design. Whether real, identifiable subject-matter experts exist at JFT who could be named is unknown to this investigation and cannot be determined without asking the business. **Classified: BUSINESS INPUT REQUIRED.** No generic "JFT Editorial Team" byline is recommended — that would be exactly the manipulation this phase's rules forbid.

## 14. Structured Data — Audit Only

No schema was added or modified. Existing Organization/WebSite/LocalBusiness/BreadcrumbList/FAQPage schema was spot-checked this phase (`about.html`, `contact.html`) and found internally consistent and accurate against visible content — no contradiction found. The Phase 24 Product-schema decision (deliberately absent from quote-only pages) is **not reopened**; no new evidence this phase changes that governance call.

## 15. `llms.txt` Reassessment

**NO CHANGE — still unnecessary**, and now with materially *stronger* supporting evidence than existed at the Phase 24 decision: external research this phase found that Google's own May 2026 AI-search optimization guidance explicitly states `llms.txt` is not needed for AI Overviews, AI Mode, or other generative search features, and that major AI crawlers (GPTBot, ClaudeBot, PerplexityBot, OAI-SearchBot, Google-Extended) overwhelmingly skip the file and crawl HTML directly. Industry adoption remains partial (~10% of sites) and effectiveness evidence is genuinely mixed even among proponents. The Phase 24 reconsideration trigger ("a major AI/search vendor formally documents production consumption") has **not** been met — if anything, the opposite has been documented. Not created.

## 16. Content Quality / AI-Spam Risk Audit

No new risk pattern was found beyond what Phases 29-30 already documented (the article dual-template inconsistency, already correctly classified as redesign-scale, not an AI-spam or thin-content issue). Spot-checked articles show real specification detail, real process explanation, and genuine differentiation from generic templated writing — none were labeled "AI-generated" or "spam-risk" merely for being polished, per this phase's explicit instruction.

## 17. Competitor AI Authority Analysis

See `reports/phase32-aeo-geo-llmo-opportunity-map-2026-08-28.md` §"Competitor Landscape" for the full breakdown by category. In short: across every commodity category tested, a *different* set of specialized competitors dominates AI-search results — none of them uniformly superior to JFT in content depth, but each visibly stronger in **off-site discovery signals** (marketplace listings, category-specific microsites, or years of accumulated backlink/citation history). This is the evidence base for classifying the core gap as authority-side, not content-side.

## 18. Backlink / Citation Opportunity Map

See the companion opportunity map document for the full tiered list. No paid, automated, or spam-adjacent tactic is recommended anywhere in this list, per explicit instruction.

## 19. Off-Site vs. On-Site Classification

See `reports/phase32-aeo-geo-llmo-opportunity-map-2026-08-28.json` for the full structured table. Headline: **of every substantive finding in this phase, none require a website code/content change.** Every actionable item is either an external action (marketplace/LinkedIn/association listings) or a business-input item (registration-number confirmation, real-author decision, FIEO status).

## 20. Limitations of This Audit

- Only one AI-augmented search tool was available; five named platforms (Google AI Overviews, ChatGPT, Perplexity, Gemini, Copilot) were not independently testable and are marked as such throughout, not simulated.
- 21 queries is a representative sample, not an exhaustive test of every literal example the phase prompt listed.
- The APEDA rice-exporter PDF list was not fully parsed; JFT's absence from the visible excerpt is inconclusive, not a proven absence from the full registry.
- The postal-code discrepancy from Phase 26 was not re-investigated with new evidence this phase (no new evidence existed to add) and remains open.
- MCA/LLPIN lookup requires an interactive government portal not accessible with this session's tools; the "AAY-5952" figure could not be confirmed or refuted.

## Stop

Per this phase's explicit instruction: investigation and reporting only. Zero website modifications occurred. See `reports/phase32-ai-search-final-2026-08-28.md` for the final decision, scorecard, and answers to the phase's 10 required closing questions.
