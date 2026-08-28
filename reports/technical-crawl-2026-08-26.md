# Phase 3 — Complete Technical Crawl & Link Integrity Audit

**Baseline:** Phase 1 `e64a3f2b` + Phase 2 (localization determinism, uncommitted working-tree changes).
**Scope:** audit + targeted repair of *confirmed* technical defects only. No redesign, no product/content/translation changes.
**Result: zero website source files were modified.** Every finding either resolved to "not a defect" under investigation, or requires judgment/authorization beyond this phase's low-risk-fix rule — both are documented below rather than acted on.

---

## Crawl statistics

| Item | Count |
|---|---|
| HTML files crawled | 1,789 (100%) |
| Internal links checked | all `<a>`/`<link>` hrefs across all 1,789 files |
| Local assets checked | all `<img>`, `srcset`, `<script src>`, downloadable-document refs |
| Redirects inventoried | 97 |
| Canonical URLs checked | all pages with a `<link rel="canonical">` |
| Hreflang URLs checked | every `<link rel="alternate" hreflang>` on every indexable/utility page |
| Sitemap URLs checked | 1,443 (100% of sitemap.xml) |
| Downloadable files checked | 138 (PDF/doc/xlsx/csv/zip links) |
| Unique external domains checked | 64 |
| Pages given a real-browser console/resource check | 28 (representative — every major template × 6 locales spanning both completeness groups; **not** all 1,789 — see Section 8) |

---

## 0. A correction to the Phase 1 baseline (found while building this crawl)

While cross-checking my own crawl script's page counts against Phase 1's numbers, I found the two disagreed, traced it to two real bugs in **`scripts/audit_coverage_gaps.py`** (the site's own CI-gating classification logic, which Phase 1's inventory script had copied verbatim), and verified the corrected numbers three independent ways (my own crawl, a direct regex check, and cross-referencing `sitemap.xml`, which matches the corrected numbers exactly).

| Classification | Phase 1 reported | Actual (corrected) |
|---|---|---|
| Indexable | 1,438 | **1,443** |
| Utility/noindex | 293 | **203** |
| Legacy redirect | 7 | **97** |
| Locale fallback | 5 | **0** |
| Helper | 46 | 46 (unchanged) |

**Bug 1 — redirect misdetection.** `audit_coverage_gaps.py` detects a redirect page with `re.search(r'<meta\s+http-equiv=["\']refresh["\']', text)`, which only matches when `http-equiv` is the *first* attribute on the tag. 90 legacy-redirect pages (mostly locale blog-post redirects) write the tag as `<meta content="0;url=..." http-equiv="refresh"/>` — attribute order reversed — so the regex misses them and they fall through to `utility_noindex` instead. Confirmed with a direct BeautifulSoup parse (attribute-order-independent) against all 1,789 files.

**Bug 2 — fallback misdetection.** `audit_coverage_gaps.py` detects an English-fallback page with a crude substring check: `"jft-localization" in text and "english-fallback" in text`. Five pages (`index.html`, `ar/index.html`, `es/index.html`, `fr/index.html`, `ru/index.html`) contain a `showLocalizationFallbackNotice()` JavaScript helper that **mentions** these two strings as text inside a `document.querySelector(...)` call — there is no actual `<meta name="jft-localization" content="english-fallback">` tag on any of these 5 pages. A repository-wide search for the real tag returns **zero matches anywhere on the site** — there are currently no active English-fallback pages at all (pages the earlier "5 intentional fallbacks" baseline figure referred to, e.g. `editorial-policy.html`, are handled by being *excluded from locale generation entirely*, not by this marker mechanism).

**Impact:** both bugs are purely in the audit's own bookkeeping — the actual redirects work correctly (verified below) and the 5 homepages are fully indexed and correctly served; nothing user-facing is affected. **Not fixed in this phase** (`audit_coverage_gaps.py` is CI-gating audit infrastructure, not a website page, and Phase 3's authorization is to fix confirmed defects on the *website* — recommend a short, low-risk, dedicated future phase to patch these two checks in `audit_coverage_gaps.py`, since they affect the reliability of the daily CI gate itself).

---

## 1. Redirects — clean

All 97 redirect pages checked for target existence, self-redirects, loops, and chains.

| Check | Result |
|---|---|
| Broken redirect (target missing) | 0 |
| Self-redirect (A → A) | 0 |
| Redirect loop | 0 |
| Redirect chain (>1 hop) | 0 |
| Malformed redirect content | 0 |
| External redirect | 0 |

## 2. Canonicals

| Check | Result |
|---|---|
| Indexable page missing canonical | 0 |
| Canonical target missing (404) | 0 |
| Indexable canonical pointing to an unintended noindex page | 0 |
| **Canonical self-references on a redirect stub (90)** | see below |
| **"Duplicate" canonical targets (6)** | see below — all verified correct |

**Finding (MEDIUM, not fixed):** all 90 locale legacy-redirect stubs (the same set from the Bug 1 misclassification above) set their own `<link rel="canonical">` to *themselves*, even though the page also meta-refreshes elsewhere. Compare this to the English-root pattern: the 7 English legacy-redirect stubs correctly set canonical *to their redirect target* (e.g. `blog-cif-fob-explained.html`'s canonical points to `blog-bill-of-lading-explained-importers.html`, the live replacement), consolidating SEO signal properly. The 90 locale stubs don't follow this same, better pattern. Not broken, but inconsistent with the site's own established best practice — flagged for a future phase rather than fixed here, since correcting 90 files' canonical target requires deciding whether to also touch `create_missing_locale_pages.py`'s stub-generation template (an architectural call, not a mechanical one-line fix).

**"Duplicate canonical target" (6 cases) — investigated, all correct:** every case is a legacy-redirect stub whose canonical correctly points to its live replacement page, which itself also canonicalizes to the same URL (e.g. `products/20325959/index.html` and `products.html` both canonicalize to `products.html`). This is the intended, correct SEO-consolidation pattern, not an error.

## 3. Hreflang — fully clean

Checked every `hreflang` URL on every indexable/utility page for: valid language code, target existence, target not a redirect, and reciprocity (does the target page declare this page's language back).

**0 findings in every category.**

## 4. Sitemap — fully clean

| Check | Result |
|---|---|
| Valid XML | Yes |
| Total URL entries | 1,443 |
| Duplicate URLs in sitemap | 0 |
| Sitemap URL → missing file | 0 |
| Sitemap URL → noindex page | 0 |
| Sitemap URL → redirect page | 0 |
| Sitemap-only URLs (not classified indexable) | 0 |
| Indexable pages missing from sitemap | 0 |

1,443 sitemap entries match the corrected 1,443-indexable-page count exactly — confirms `scripts/generate_sitemap.py` already uses correct classification logic (unlike `audit_coverage_gaps.py` — see Section 0), so this discrepancy never affected real SEO output, only one audit script's internal reporting.

## 5. Robots.txt — clean, with one cosmetic note

Valid syntax, sitemap declared correctly, zero indexable pages blocked, zero CSS/JS blocked, zero dev-path leaks.

**Note (LOW, not fixed):** `robots.txt` explicitly disallows several individual `.py` filenames at the root (`/generate_hreflang.py`, `/propagate_products_fix.py`, `/thorough_fix.py`, `/audit_website.py`, `/fetch_agro_news.py`, `/jft_ai_engine.py`, `/final_polish.py`, `/fix_image_typos.py`, `/generate_sitemap.py`). None of these files are actually present in the deployed Cloudflare bundle (confirmed in Phase 1's and this phase's bundle inspection) — these rules block URLs that were never reachable, so they're dead weight, not a security gap.

## 6. Orphan pages

Built a directed internal-link graph from every `<a>` tag on every page (see Section 8 for a stated limitation of this method).

**Legitimate orphan:** `legal.html` — reachable only via the shared footer's "Legal" link (which lives in `header.html`/`footer.html`, injected client-side and therefore invisible to a static crawl of the page source files, not because it's actually unlinked). Standard, expected pattern for a legal/terms-style page.

**Accidental orphans (36, MEDIUM, not fixed) — a real, verified content-parity gap:**

| Locale | Pages with zero in-page inbound link |
|---|---|
| id, ms, pt, si, th, vi (6 locales) | `export-documentation.html`, `faq.html`, `packing-calculator.html`, `port-transit-calculator.html`, `product-catalogue.html`, `whatsapp-catalog.html` (6 pages each = 36) |
| ar, es, fr, ru | **0** — none of these 6 pages are orphaned |

Directly verified the root cause: `ar/index.html` (and es/fr/ru) contains an in-page workflow-diagram block linking to `quality-control.html`, `certificates.html`, `buyer-security.html`, and `export-documentation.html`, plus tools-menu entries for the other pages — content that `id/index.html` (and ms/pt/si/th/vi) simply does not have. This lines up exactly with this project's earlier, separate finding that only 4 of the 10 locale homepages (ar/es/fr/ru) were fully rebuilt to the current template; the other 6 still run an older homepage structure lacking this content block. **Not fixed here** — per this phase's own Step 10 instruction ("do not automatically add links yet, document them") and because closing the gap means either porting content into 6 homepages or deciding on a different fix, both real internal-linking/content decisions for a dedicated phase, not a mechanical link repair.

## 7. Crawl depth

| Locale | Max depth found | Pages >3 clicks deep |
|---|---|---|
| en, ar, es, fr, ru | 2 | 0 |
| id, ms, pt, si, th, vi | 4 | 2 (`buyer-security.html`, `shipment-tracker.html`) |

The deeper reach in 6 locales is the same homepage-content gap as Section 6 — those 2 pages simply need an extra hop through a different page to reach, since the direct homepage links Section 6 describes aren't present. Not a broken-link issue.

## 8. Stated method limitation (Step 10/17 honesty requirement)

`header.html` and `footer.html` are fetched and injected into every page **client-side via JavaScript**, not statically present in each page's source file. A static crawl of the HTML on disk — the method used for Sections 6–7 — cannot see links that exist only inside these two shared fragments (e.g. the footer's "Legal" link, or any header dropdown-menu entry that isn't also duplicated in a page's own body). This means the true orphan/depth picture is *better* than what a static crawl alone can show (some "orphans" are actually reachable via the shared nav) — I do not claim otherwise. Where I could directly verify a real content difference between locale groups (Section 6), I did so with an independent, targeted `grep` rather than relying on the graph alone. Anything not independently spot-checked this way should be read as **NOT FULLY VERIFIED** by this method, not as confirmed orphaned.

## 9. Query-parameter / legacy URL patterns — investigated, both confirmed non-issues

- `contact.html?product=<name>#inquiry-form` — an intentional, working mechanism to pre-fill the enquiry form's product field (used on 2 blog posts and generated dynamically by `products.html`'s own JS for every product card). Not a broken dynamic route.
- `products/20325959/index.html` — the previously-identified (Phase 1) legacy numeric product archive. Confirmed to have zero internal inbound links (correct — it exists only to catch old external bookmarks/backlinks) and its meta-refresh target resolves correctly (Section 1).

## 10. URL normalization

| Check | Result |
|---|---|
| Uppercase internal URLs | 0 |
| Duplicate trailing-slash variants | 0 |
| `../../` traversal | 0 |
| Empty `href` | 0 |
| Empty `src` | 10 — all one confirmed pattern: `<img id="m-img" src="">` in every locale's `products.html`, a JS-controlled modal preview image populated on click. Working as intended, not broken. |
| `javascript:` hrefs (non-void) | 0 |
| `href="#"` (no real navigation) | 22 — all confirmed JS-action buttons styled as links (e.g. "Confirm via WhatsApp", "Read Buyer's Guide"). Functionally fine; semantically these would ideally be `<button>` elements. LOW/cosmetic, not fixed. |
| URL-encoded characters in href | 77 — all legitimate external URLs (FAO/government portal query strings, a `mailto:` subject line). Not a defect. |
| Wrong-case document extensions (`.PDF` etc.) | 0 |

**Separately noted (LOW, not fixed):** 891 references across ~84 product pages use image filenames containing literal, unencoded spaces and parentheses (e.g. `images/products/10 Parboiled Rice (IR-64).webp`). Unconventional, but every one of these resolves correctly (confirmed: zero broken-asset findings for any of them) — browsers and Cloudflare's asset server both handle this filename style without issue. Renaming ~84+ files and updating every reference would be a large, non-trivial change to fix a purely cosmetic naming-convention preference on an already-working pattern, so it wasn't touched.

## 11. Downloadable files — clean

138 PDF/document links checked; all resolve to an existing file. 0 broken.

## 12. External links

64 unique external domains checked (one representative URL per domain, HEAD then GET fallback). 15 did not return a clean 200:

| Domain | Result | Likely explanation |
|---|---|---|
| fonts.googleapis.com, fonts.gstatic.com | 404 on bare domain root | **False positive** — these are asset/CSS hosts, not meant to serve a homepage at `/`; the site's actual usage (specific font CSS URLs) is unaffected. |
| www.fda.gov | 404, redirected to an "abuse-detection" page | Bot-protection response to an automated client, not evidence the real page is gone. |
| www.iso.org, unece.org, www.mca.gov.in, portdecotonou.bj, www.fao.org | 403 Forbidden | Same — common WAF behavior against non-browser user agents on government/standards sites. |
| kephis.go.ke | 500 | Possibly transient server error on their end. |
| www.food.gov.uk | 503 | Possibly transient (rate-limit/maintenance). |
| trade.gov.ng | DNS resolution failed | **Most likely genuinely dead/moved** — the domain doesn't resolve at all right now. |
| icar.gov.in, www.container-tracking.org, www.dft.go.th, www.icegate.gov.in | SSL certificate verification error | Could reflect a real certificate problem on the target site, or a local trust-store mismatch — **NOT VERIFIED** either way from this environment. |

Per this phase's rule against changing an external link "merely because it cannot be automatically checked," **none of these were modified.** `trade.gov.ng` is the one worth a human look in a future phase; the rest are most plausibly automated-client friction rather than real breakage.

## 13. Browser console/resource check

28 representative pages (every major template — homepage, about, certificates, contact, product page, blog index, blog article, infrastructure, 3 calculators, product-catalogue, faq, buyer-security, export-documentation — across en, ar (RTL), es, id, ru, vi, spanning both the "fully rebuilt" and "not yet rebuilt" locale groups) were loaded in a real headless browser against a local HTTP server.

**Result: 0 console errors, 0 uncaught page exceptions, 0 failed resource requests, all 200 status.**

This is a representative sample, **not** all 1,789 pages — stated explicitly per this phase's honesty requirement rather than claimed as exhaustive.

---

## Fixes made this phase

**None to website content or pages.** Every finding investigated either (a) resolved to "not a defect" (query params, empty src/href patterns, encoded external URLs, duplicate canonicals, the space-in-filename convention), or (b) is real but requires judgment/architectural decision or separate authorization beyond a mechanical, low-risk fix (the two `audit_coverage_gaps.py` bugs, the 90 locale-stub canonical pattern, the 36-page locale content-parity gap, the one likely-dead external domain). Per Step 18's explicit condition — fix only what's "objectively proven... deterministic... minimal" — none of these qualified, so all are reported rather than acted on.

## Cloudflare build verification

Ran `scripts/build_cloudflare_assets.py`: succeeded, 2,089 files (matches the Phase 1/2 baseline exactly), `locale-ui.js` in the bundle byte-identical (same MD5) to the source copy, zero scripts/reports/docs/`.py`/secret files leaked. Local build artifact deleted after inspection. **Not deployed.**
