# Phase 27 — AEO/GEO/LLMO + E-E-A-T Content Authority Implementation

Date: 2026-08-28
Status: Implementation complete and verified clean. **NOT DEPLOYED.**

## 1. Scope

Implemented only the opportunities that passed the Content Creation Decision Gate in `reports/phase27-aeo-eeat-opportunity-map-2026-08-28.md` (P27-O1, P27-O3, P27-O4, P27-O5). Explicitly did not touch: the 3 thin category hubs (P27-O2, correctly failed the gate), the postal-code discrepancy (P27-O6, requires business input), or off-site authority (P27-O7, out of scope for a website change).

## 2. P27-O1 — Completed the Toor Dal Article

`blog-toor-dal-export-india-2026.html` was a bare placeholder (`<p>Placeholder article — create full content as needed.</p>`, `noindex`, no header/footer includes, no Article schema). Rewrote it completely, replicating the exact template of a live, working article (`blog-groundnut-peanut-export-india-2026.html`) structurally, while sourcing every fact from material already governed on `toor-dal-split-pigeon-pea-exporter.html`'s specification table and FAQ:

- **Identity/synonym mapping** (toor dal = tur dal = arhar dal = dehulled split *Cajanus cajan*) — directly from the product page's existing FAQ.
- **Process-status distinction** (whole vs. dehulled-split vs. oily/non-oily treatment) — directly from the product page's specification table.
- **Physical-quality and food-safety parameters** (moisture, extraneous matter, broken/damaged/discoloured pieces, destination-specific residue/mycotoxin/microbiology limits) — directly from the product page's specification table.
- **One new, genuine external citation**: found via real web search and verified before use — the joint FAO/WHO **Codex Alimentarius Standard for Certain Pulses, CODEX STAN 171-1989 (Rev. 1-1995)**, linked directly to its official FAO PDF. Cited only at the safe level actually confirmed by the search result (that the standard exists and addresses safety/suitability for consumption of pulses including pigeon pea) — no specific numeric threshold was invented or quoted beyond what was genuinely found.
- Packing/container/documentation guidance restates the product page's own established facts (HS code/MOQ/container-load reference, 20ft FCL basis) without inventing new figures.

No customer, volume, certification number, employee, or superlative claim was added — fully compliant with Rule 3's fabrication ban.

**Robots meta changed from `noindex,follow` to `index,follow,max-snippet:-1,max-image-preview:large,max-video-preview:-1`** (matching every other live article) — this is the one change that makes the page genuinely discoverable, appropriate now that it has real content.

## 3. Downstream Fixes Required by P27-O1 (discovered via regression, not anticipated in the opportunity map)

Running the regression suite immediately after completing the article (per this program's established discipline of never assuming a change is clean) surfaced two real, direct consequences that needed fixing — not new content-authority findings, but correctness requirements:

- **`blog.html`'s filter-count display** read "All Articles 29" / "Buyer Guides 9" — now stale since a 30th article and 10th buyer-guide exist. Corrected both counts to 30/10 (§P27-O4).
- **`scripts/audit_website.py`'s `UNPUBLISHED_BLOGS` registry** still listed `blog-toor-dal-export-india-2026.html`, causing `audit_website.py` to report 9 false findings (`PUBLISHED_INCOMPLETE_BLOG`, `LINK_TO_UNPUBLISHED_BLOG` ×6, plus the two stale filter-count findings) even after the article was genuinely complete. Removed the single now-inaccurate entry, leaving the other 17 entries in the same set untouched (they correctly correspond to still-retired/redirected articles per `worker.js`'s `LEGACY_ARTICLE_REDIRECTS`). Re-ran: `audit_website.py` returned to **0 findings**.

## 4. Also Added: `blog.html` Card and `pulses-exporter-india.html` Guide Link

Following the exact existing template patterns (verified against the groundnut article's card and the pulses category page's existing single "Related Buyer Guide" entry) — added a matching card/link entry for the new article, so it is discoverable from both the article index and its category hub, not only via internal article-to-article links.

## 5. P27-O3 — Extended Article→Category Linking to a Second Reusable Component

Phase 25 closed this gap for the 6 articles using the `jft-related-product` aside. This phase found a **second**, independently reusable component — `<section class="seo-related"><div class="seo-related-grid">` — used by 4 additional articles that were not covered by Phase 25's fix (including the newly-written toor-dal article's own grid, which already had its category represented via the other aside — correctly detected and skipped).

Wrote `scripts/add_seo_related_category_cards.py`: for each article using this grid, derives the category **only from the grid's own first, already-existing product-type card** (no new categorization judgment), and adds one additional "Category" card — matching the exact visual/semantic pattern of the existing "Product"/"Compliance"/"Specification" cards already in that grid. Checks the **entire article source**, not just the grid, before adding — this correctly caught and skipped `blog-groundnut-peanut-export-india-2026.html`'s *aside* (which already names "Indian Animal Feed Input Exporter" via a different, oil-cake-specific product link) while still correctly adding a **second, independently accurate** category card to its *grid* ("Indian Oilseeds Exporter," derived from the grid's own `groundnuts-peanuts-exporter.html` reference) — verified this is not a duplicate or an error: the article genuinely discusses both the raw groundnut/peanut product (Oilseeds) and its oil-cake byproduct (Animal Feed), and both category associations are independently correct.

**Result**: 4 articles updated (`blog-coriander-seeds-export-india-2026.html`, `blog-groundnut-peanut-export-india-2026.html`, `blog-private-label-rice.html`, `blog-sesame-export-2026.html`). Verified idempotent (second run: 0 added, 5 already present — including the toor-dal article, correctly recognized as already covered via its other aside).

**Remaining scope, correctly not touched**: 27 articles still lack either reusable component entirely. Extending category-linking to them would require inventing a new insertion point per differently-structured article — flagged as future template-standardization work, not attempted here (matches Phase 25's identical, still-valid reasoning).

## 6. Content Quality Control (Part 31, applied to the new article)

- **Factual accuracy**: every specific claim traced to either the existing product page or the one verified external citation.
- **No keyword stuffing**: "toor dal," "tur dal," "arhar dal" are used exactly as needed for the genuine synonym-disambiguation point, not repeated artificially.
- **No unsupported claims**: no certification, volume, or superlative claim added.
- **No duplicate content**: the article provides buyer-education framing (process-status distinctions, a recognized quality framework, a pre-shipment checklist) that the product page's FAQ format does not — genuinely differentiated, matching the established pattern of every other product-page/article pair on the site.
- **Internal-link relevance**: every link (product page, specification-writing guide, certificate-of-analysis guide, sample-request) is a real, existing, contextually appropriate page.
- **Heading hierarchy**: H1 → H2 sections with `id` attributes matching the sidebar navigation exactly (verified directly, not assumed).
- **HTML/JSON-LD validity**: both JSON-LD blocks (`BlogPosting`, `BreadcrumbList`) parsed successfully; single `</head>`; all anchor IDs confirmed present.

## 7. Files Changed

| File | Change |
|---|---|
| `blog-toor-dal-export-india-2026.html` | Complete rewrite from placeholder to a full, templated, evidence-backed article; `noindex` removed |
| `blog.html` | Added one article card; corrected two stale filter counts (29→30, 9→10) |
| `pulses-exporter-india.html` | Added one "Related Buyer Guide" entry |
| `scripts/audit_website.py` | Removed one now-inaccurate entry from `UNPUBLISHED_BLOGS` |
| `scripts/generate_sitemap.py` | Added one new dated override set (`UPDATED_2026_08_28`), following the exact existing pattern of two prior such sets, so the new article's `lastmod` reflects its true publish date instead of falling back to a generic placeholder date |
| `sitemap.xml` | Regenerated (deterministic, idempotent — verified byte-identical on a second run); 1,453 → 1,454 URLs |
| `blog-coriander-seeds-export-india-2026.html`, `blog-groundnut-peanut-export-india-2026.html`, `blog-private-label-rice.html`, `blog-sesame-export-2026.html` | Added one "Category" card each to their existing `seo-related-grid` |
| `scripts/add_seo_related_category_cards.py` (new) | Governed, deterministic, idempotent script implementing the above |

## 8. Determinism Verification

- `scripts/generate_sitemap.py`: run twice after the fix; SHA-256 of `sitemap.xml` identical both times.
- `scripts/add_seo_related_category_cards.py`: run twice; second run reported `0 added, 5 already present` — fully idempotent.

## 9. Regression Results (final, complete run)

| Script | Result |
|---|---|
| `audit_website.py` | **0 findings** (was 9 immediately after completing the article, before the two downstream fixes in §3 — root-caused and fixed, not suppressed) |
| `full_site_audit.py` | 0 findings, 1,454 indexable (was 1,453 — correct +1) |
| `audit_commercial_content.py` | 0 findings |
| `audit_claims_and_products.py` | 0 findings |
| `validate_blog_navigation.py` | Passed — 260 published blog cards (was 259 — correct +1), 0 stale schema images |
| `audit_locale_ui.py` | 0 findings, determinism PASS |
| `audit_localizations.py` | 0 findings |
| `audit_coverage_gaps.py` | 0 findings |
| `audit_performance.py` | 0 findings |
| `check_unused.py` | Confirmed the new article's image is no longer in the unused-files list (correctly now referenced) |
| `check_links.py` | 0 broken links / 1,766 files |

**No pre-existing issue was suppressed or hidden.** `validate_seo_alignment.py`'s already-documented `P23-R4` finding (unrelated internal-linking gap on ~30 different product pages) was not re-run this phase since none of those pages were touched.

## 10. Build Verification

Ran `scripts/build_cloudflare_assets.py` (existing, unmodified): 2,099 public assets built successfully. Verified the new article is present in the bundle, `scripts/` and `reports/` are correctly excluded (no source/report leakage), and the bundled `sitemap.xml` correctly includes the new URL. **Deleted the temporary `.cloudflare-dist-next` artifact immediately after verification**, per established project practice.

## 11. Deployment Status

**NOT DEPLOYED.** Directly re-confirmed against production after all local changes: `https://jftagro.com/blog-toor-dal-export-india-2026.html` still returns the **old placeholder text** ("Placeholder article — create full content as needed"), proving conclusively that no deployment occurred and production remains exactly as it was at the start of this phase (plus Phase 25's still-undeployed `worker.js` redirect fix, also reconfirmed unchanged).

## 12. Full Diff Discipline

`git status --short` isolated to exactly 9 intentionally-modified tracked files (§7) plus 1 new script and this report set; every line change is accounted for in §7-§9. The `sitemap.xml` diff initially appeared large (88 lines) — investigated and confirmed to be **entirely additive** (0 deletions beyond the diff header), consistent with this repository's established pattern of cumulative uncommitted drift against a stale Phase-1 git baseline (documented in every prior phase) plus the one genuine new URL entry. No unexplained modification was found; nothing was reverted.

## 13. Limitations

- No live browser-automation tool was available to visually verify the new article's rendered layout — verification relied on exact template replication (matching a live, working article byte-for-byte in structure) plus static HTML/JSON-LD/link validation.
- The Codex Alimentarius citation was verified to exist and to cover pulses generally via a real search result; the full PDF text was not independently read in this session, so the article deliberately does not quote any specific numeric threshold from that standard — only its existence and general scope, which is what the search evidence actually supports.
- AI query testing was not re-run this phase (see the opportunity map's reasoning) — the 15 queries already run across Phases 24-26 remain the current evidence base for AI-search visibility.
