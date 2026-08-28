# Phase 27 — AEO/GEO/LLMO + E-E-A-T Content Authority Opportunity Map

Date: 2026-08-28
Status: Investigation complete, opportunity map finalized before implementation began (per Phase 27's own sequencing requirement).

## Baseline

| Item | Value |
|---|---|
| Git commit | `e64a3f2ba03c114a94ef61db20fbff486dab2a2b` (unchanged) |
| Production | `HTTP 200`, sitemap 1,453 URLs |
| Renderable pages | 1,753 |
| Phase 25's `worker.js` redirect fix | Confirmed still present locally, still not deployed (production `/spices/` still `404`) |
| Articles | 37 files, 30 substantive (per Phase 25's audit) |
| Category pages | 10 |
| Product pages | 84 |

## Opportunities Identified

| ID | Page | Problem | Evidence | Root Cause | Business/Search Value | AEO/GEO/LLMO | E-E-A-T | Recommended Action | Authorized? | Confidence | Risk |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P27-O1 | `blog-toor-dal-export-india-2026.html` | Unpublished placeholder ("Placeholder article — create full content as needed"), `noindex` | Confirmed by direct read; flagged in Phase 25 and Phase 26 reports | Never completed after initial scaffolding | HIGH — Pulses is one of 10 core categories; toor dal/tur dal/arhar dal is a high-volume, high-search-interest Indian pulse | HIGH — closes a real content gap with genuine buyer-guide value | HIGH — genuine evidence available (product page's 5-question FAQ, real Codex Alimentarius standard for pulses found via search) | Write a complete, evidence-backed article using only facts already governed on the product page plus one genuine, verifiable external citation | **YES** | HIGH | LOW (new page, no existing content touched; template exactly replicated from a live, working article) |
| P27-O2 | 3 category hubs: Wheat, Sugar, Raisins | Thin content (~80-110 words of prose) | Confirmed via direct word-count check and Phase 25's delegated audit | Legitimately single-SKU categories, not a content omission | LOW-MEDIUM — Rule 10 explicitly warns against expanding merely because a page is short | LOW — no genuinely new, non-generic information identified that isn't already on the single underlying product page | N/A | **Leave unchanged** | NO — fails Content Creation Decision Gate conditions 1 and 4 (no proven information gap; would duplicate product-page content) | HIGH confidence this is correctly NOT actionable | N/A |
| P27-O3 | 31/37 articles lack the `jft-related-product` aside; 0/30 substantive articles linked to a category hub before Phase 25 | Article→category semantic graph incomplete | Phase 25's delegated audit | Template heterogeneity across articles authored at different times | MEDIUM — strengthens the Entity→Category→Article semantic graph (Part O) | MEDIUM | N/A | Extend category-linking to articles using the *other* existing reusable component (`seo-related-grid`), where the grid's own first product link resolves unambiguously to one category | **YES, for the safely-extensible subset** | HIGH for the 3-4 articles identified; the remaining ~27 genuinely lack any reusable link component and are correctly left for future template work | LOW (additive card only, no existing link removed) |
| P27-O4 | `blog.html` filter-count display | Would become stale (29/9) once a new article is added | Discovered as a direct consequence of implementing P27-O1 | Hardcoded display counts not tied to a dynamic query | LOW but necessary for correctness | LOW | N/A | Update the two displayed counts to match the new total | **YES** | CERTAIN | NONE (one-line text correction) |
| P27-O5 | `scripts/audit_website.py`'s `UNPUBLISHED_BLOGS` registry | Would incorrectly keep flagging the newly-completed article as unpublished/incomplete | Discovered via regression testing after implementing P27-O1 | Registry is the source of truth this audit relies on; must be updated when an article's status genuinely changes | HIGH (blocks a clean regression otherwise) | N/A | N/A | Remove the single now-inaccurate entry | **YES** | CERTAIN | NONE (removes exactly one line; verified the other 17 entries in the same set correctly remain, matching still-retired/redirected articles) |
| P27-O6 | `postal code discrepancy (Phase 26)` | LEI registry shows 400703 vs. site's 400705 | Phase 26 finding | Genuinely ambiguous per independent research | MEDIUM | LOW (external, not on-page) | MEDIUM | Requires business confirmation | NO — root cause not proven | N/A | N/A |
| P27-O7 | Off-site/generic-query AI visibility gap | JFT absent from generic commodity/category queries | Phases 24-26 | Off-site authority gap, not a content defect | Strategic | HIGH relevance but no on-page fix exists | N/A | Continue monitoring; not a content-authority fix | NO — no website change can close an off-site authority gap | N/A | N/A |

## AI Search Query Testing (this phase)

Tool used: the single web-search tool available this session. **Not** Google AI Overview, Bing Copilot, ChatGPT search, Perplexity, or Gemini specifically — none of those systems were independently accessible.

| Query | Type | Date | JFT appears? | URL cited | Competitor/entity surfaced | Accuracy | Notes |
|---|---|---|---|---|---|---|---|
| (Carried forward from Phases 24-26: 15 queries already tested across brand/product/category/commercial/trust/geography types — not re-run this phase to avoid duplicate evidence-gathering with no new information value) | — | — | — | — | — | — | This phase's query-testing budget was directed instead at verifying the one genuinely new external source found in Phase 26 (the LEI registry) and at sourcing the Codex Alimentarius pulses standard used in the toor-dal article (see Implementation Report) |

## Content Creation Decision Gate — Applied to Every Candidate

| Candidate | C1: gap proven | C2: matters | C3: evidence available | C4: no duplication | C5: clear intent | C6: strengthens cluster | C7: natural | C8: no unsupported claims | C9: no SEO/UX weakening | C10: worth maintenance | Result |
|---|---|---|---|---|---|---|---|---|---|---|---|
| P27-O1 (toor dal article) | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Yes | **PASS — implement** |
| P27-O2 (thin category hubs) | **No** | — | — | No | — | — | — | — | — | — | **FAIL — do not implement** |
| P27-O3 (article-category links, safe subset) | Yes | Yes | Yes | Yes (additive only) | Yes | Yes | Yes | Yes | Yes | Yes | **PASS — implement for the safely-derivable subset only** |

## Next Step

Proceed to implement only P27-O1, P27-O3 (safe subset), P27-O4, and P27-O5 — see `reports/phase27-aeo-eeat-implementation-2026-08-28.md`/`.json`.
