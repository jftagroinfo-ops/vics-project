# Phase 32 — AEO/GEO/LLMO Opportunity Map

Date: 2026-08-28
Status: Audit-only deliverable. No fixes authorized or implemented this phase.

## Off-Site vs. On-Site Classification

| Finding | Root Cause | Website Can Fix? | External Action | Business Input |
|---|---|---:|---|---:|
| "Since 1980"/"5 decades" AI fabrication | AI-generated; no identifiable website or third-party source | **No** — website already correct and disclaimed | Low-confidence, likely-impractical correction request to search platforms | No |
| Fabricated `about.html` title in AI summaries | Same as above | No | Same as above | No |
| "7 branch offices" overstatement | AI reinterprets trade-hub/market wording as literal offices | Marginal — not recommended (single AI's paraphrase, not evidence of real ambiguity) | No | No |
| "AAY-5952" unverifiable registration number | Unknown | No | Confirm true LLPIN via MCA portal | **Yes** |
| Postal code discrepancy (400705 vs. 400703, carried from Phase 26) | Unresolved, no new evidence this phase | No | N/A | **Yes** (unchanged from Phase 26) |
| Zero AI visibility on generic high-intent category queries (8/9 categories tested) | Off-site authority/citation deficit vs. established and peer-scale competitors — not a content or technical defect | **No** | Authority-building (marketplaces, associations, press) | Partially |
| Buyer-intent pages not surfacing for matching questions | Content is good and previously verified; lacks external citation authority | No — no extraction/structure defect found | Authority-building | No |
| No confirmed LinkedIn company page | Never created, or exists but unindexed | No | Create/claim a company page | **Yes** |
| No confirmed B2B marketplace listing (Indiamart/TradeIndia/ExportersIndia) | Never created | No | Create and maintain listing(s) | **Yes** |
| FIEO membership status unknown | Not investigated/confirmed previously | No | Confirm status; pursue if not held | **Yes** |
| `llms.txt` absence | Reasoned prior decision, reconfirmed this phase with stronger evidence | No — do not create | N/A | No |
| Product schema on quote-only pages | Deliberate governance decision (Phase 24), not reopened | No | N/A | No |

## Competitor Landscape (by category, from this phase's query testing)

| Category | Competitors observed in AI/search results | Observation |
|---|---|---|
| Rice (generic) | LT Foods, Adani Wilmar, Sukhva Rice, Shri Lal Mahal, AMIRA Nature Foods | Large, established national brands dominate the highest-intent head-term |
| Rice (IR64/parboiled) | Plowexim, Pitambar Foods, Ashoka Rice Mills, Eco Export, Tizara Group, A-1 Overseas | Mid-size specialist exporters, closer to JFT's scale |
| Rice + spices + pulses (multi-commodity, Africa-adjacent) | Global Pulse Farm, Rivha Traders, Ashapura Exporters, VLX Exports | Peer-scale multi-commodity exporters most comparable to JFT's own positioning; several visibly maintain marketplace/LinkedIn presence JFT lacks |
| Spices | Shri Sagas Connect, Sai Shagun Food Industries, Vora Spice Mills | — |
| Herbs | Kinal Global Care, Apexherbex, Apex International, Koreagro | — |
| Sugar/flour/wheat | Savaliya Exports, ABZ Frozen Food, A-1 Overseas, Aroma Valley Trade | Aroma Valley Trade is a direct S-30 sugar competitor |
| Raisins | AgroX Organic Exports, Nature to Home Agro, Chau Foods | — |
| Animal feed | Svara Impex, WGC Exports, Bhimani Exports, Om Shree International, Yembroos | — |
| UAE/Middle East | Meridian MPF, Al Arza Al Dhahbi, Al Turab Foodstuff Trading | Local UAE-based trading companies, different business model (import/redistribution) than JFT's export model |

**What competitors have that JFT does not, based on direct evidence (not assumption):** visible marketplace presence, in several cases; longer accumulated web history. **What competitors do not have that JFT does:** a verified LEI registration (none of the competitors surfaced in this phase's searches showed an equivalent independent credential), and — per Phases 1-31 — a materially stronger, already-verified technical/on-page/UX foundation. The gap is specifically in off-site discovery signals, not content quality or technical execution.

## Backlink / Citation Opportunity Tiers

**Tier 1 — highly valuable, not pursued this phase (business decision required):**
- Confirmed FIEO membership listing (status currently unknown — §7 of main audit)
- Government/APEDA public exporter registry confirmation

**Tier 2 — relevant industry sources:**
- Rice/spice trade association mentions (e.g., All India Rice Exporters' Association, Indian Rice Exporters Federation) if membership is pursued
- Genuine trade-publication coverage, contingent on a real newsworthy event (not manufactured)

**Tier 3 — useful business references:**
- LinkedIn company page (foundational, low-cost, high-leverage for entity verification and professional-network signal)
- Indiamart / TradeIndia / ExportersIndia listing(s), matching the pattern several peer competitors already use

**Explicitly rejected — not recommended under any circumstance:**
- Paid spam links, PBNs, automated mass directory submission, mass guest-post campaigns, fake reviews, fabricated citations, or AI-generated "authority" microsites.

## Prioritized Opportunity Matrix

| ID | Opportunity | Area | Evidence | Impact | Effort | Risk | Website Change? | Priority | Track |
|---|---|---|---|---|---|---|---|---|---|
| O1 | Confirm true LLPIN/registration number via MCA; resolve "AAY-5952" | Entity/Trust | §6, main audit | Medium | Low | Low | No | **P1** | BUSINESS DECISION REQUIRED |
| O2 | Create/claim a verifiable LinkedIn company page | Authority | §7, §5 | Medium-High | Low | Low | No | **P1** | BUSINESS DECISION REQUIRED |
| O3 | Establish presence on at least one major B2B marketplace (Indiamart/TradeIndia/ExportersIndia) | Authority | §7, competitor landscape | Medium-High | Medium | Low | No | **P1** | BUSINESS DECISION REQUIRED |
| O4 | Confirm FIEO membership status; pursue if not held | Authority | §7 | Medium | Low-Medium | Low | No | **P1** | BUSINESS DECISION REQUIRED |
| O5 | Continue monitoring the "since 1980" AI misinformation across future phases | Trust/Misinformation | §9 | Low (tracking only) | Low | None | No | **P1** | DO NOW (monitoring only) |
| O6 | Pursue genuine trade-press/association mentions as real opportunities arise | Authority | §7, Tier 2 | Medium | Medium-High | Low | No | **P2** | FUTURE PHASE |
| O7 | Independently confirm JFT's entry in APEDA's full public exporter-list PDF | Authority (clerical) | §7 | Low | Low | None | No | **P2** | DO NOW (verification only, no site change) |
| O8 | Real, named subject-matter-expert authorship, only if business identifies willing individuals | E-E-A-T | §13, main audit | Medium | Low (if names exist) | Low | Possibly (byline addition) | **P2** | BUSINESS DECISION REQUIRED |
| O9 | Consider whether "trade hub" wording on about.html/index.html could be tightened to preempt AI overstatement | Content clarity | §9, P32-F3 | Low | Low | Low | Possibly (minor copy) | **P3** | FUTURE PHASE (optional, low confidence) |
| O10 | Establish a lightweight recurring AI-visibility monitoring check (quarterly) | Process | §4, whole audit | Low-Medium | Low | None | No | **P3** | FUTURE PHASE |

## DO NOT DO

- Do not create `llms.txt`.
- Do not buy backlinks, use PBNs, or run automated mass-directory submissions.
- Do not fabricate author bios or a generic "JFT Editorial Team" byline.
- Do not attempt to unilaterally "correct" the LEI registry or any third-party profile.
- Do not reopen the Product-schema-on-quote-pages decision.
- Do not create new pages solely to chase generic keywords without new first-hand evidence behind them.
- Do not treat a single AI tool's paraphrase ("branch offices") as proof of a real website ambiguity requiring a copy change.

## Stop

Audit-only. No implementation authorized. See `reports/phase32-ai-search-final-2026-08-28.md` for the final decision and recommended Phase 33 scope.
