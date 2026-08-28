# Phase 15 — Analytics, Conversion Measurement & Real-World Performance Audit

Date: 2026-08-28
Status: Investigation complete. One evidence-backed fix implemented (documented at the end); everything else reflects direct source inspection.

## 1. Executive Summary

JFT Agro Overseas has a single, coherent, already-thoughtful analytics implementation (`jft-conversion.js`, one GA4 property, `G-MWZ2ZWZP4G`) that correctly distinguishes intent from conversion, keeps personal data out of Google Analytics, and is consent-gated before anything fires. Tracing its actual delivery mechanism (not just its source code) surfaced one genuine, well-scoped defect: two trust-critical pages (`buyer-security.html`, `export-documentation.html`) and their 10 locale copies each — 22 pages total — loaded the analytics script twice, causing every click-based event and the RFQ/sample "form start" intent event to double-fire on those specific pages. This has been fixed at the source. No GA4 export data exists in this repository (there is no live account access in this session), so no live traffic/conversion numbers are reported anywhere in this document — only what the code proves is measurable. A real, dated Google Search Console export (19 May–18 Aug 2026) does exist and was analyzed on its own terms.

## 2. Repository Baseline

- Commit: `e64a3f2b` (branch `main`), unchanged — nothing has been committed during this entire multi-phase engagement.
- Working-tree diff before this phase's fix: 1,132 changed paths.
- Phase 14 end-state confirmed intact: 0 website files had been modified by Phase 14 (audit-only phase, as recorded in its own report).
- No unrelated changes were present; no reset/discard/clean operation was performed.

## 3. Analytics Inventory

A repository-wide search for GA4/GTM/gtag/dataLayer/UTM/conversion-event patterns found exactly **one** analytics implementation: `jft-conversion.js` (325 lines, plain JS, no framework, no third-party analytics platform beyond Google Analytics). It is referenced by name in exactly 3 English root files (`404.html`, `header.html`, `index.html`) plus, before this phase's fix, `buyer-security.html` and `export-documentation.html` and their 10 locale copies (now removed — see §26). No Google Tag Manager container, no Meta/LinkedIn/TikTok pixel, no heatmap or session-recording script, and no second analytics ID were found anywhere in the codebase.

## 4. GA4 Implementation

- **Measurement ID**: `G-MWZ2ZWZP4G`, hardcoded in exactly one place (`jft-conversion.js`'s `CONFIG` object) — confirmed via a repository-wide search for any other `G-XXXXXXXX`-shaped string; none found. Single source of truth, correctly governed.
- **Delivery mechanism**: every page injects `header.html` via `fetch()` + a script-recreation routine (`querySelectorAll('script').forEach(...)` that clones and re-inserts each `<script>` tag so the browser actually executes it — the standard, correct technique for dynamically-injected scripts). `header.html` itself contains `<script src="/jft-conversion.js"></script>`, so every page that successfully injects the header receives the analytics script exactly once — **this was verified, not assumed**, by tracing the actual injection code rather than just finding the script tag in source (see Phase 14's own false-positive-and-resolution for the article buyer-path, which used the same verification method).
- `index.html` bakes the header (and therefore the script tag) directly into its own static HTML for performance (no fetch, no FOUC) — confirmed this does not double-load, since it contains exactly one `jft-conversion.js` reference and no `loadComponent('header-placeholder', ...)` call.
- **Duplicate initialization found and fixed**: `buyer-security.html` and `export-documentation.html` (+ 10 locale copies each = 22 files) had their own *direct* `<script src="jft-conversion.js">` tag *in addition to* the header-injection delivery — meaning the script's top-level code ran twice on these specific pages. See §12/§26.
- Pageviews rely on GA4's own automatic `page_view` (Enhanced Measurement), not a custom implementation — appropriate, standard practice, not a gap.
- Custom events exist for: form intent, form success, product/article views, WhatsApp/phone/email clicks, outbound/file-download clicks, and diagnostic events (404, CSP violations) — full taxonomy in §6.
- Locale pages, product pages, category pages, contact/sample forms, and all three calculators all load the identical shared script via the identical header-injection mechanism — one implementation, not 11 or 84 separate ones (matches the phase's own "prefer one reusable implementation" instruction; nothing needed to be built here, it already exists).

## 5. Consent / Privacy

**Technical finding, not a legal conclusion**: `loadAnalytics()` checks `localStorage.getItem('jft_cookie_choice') !== 'accepted'` and returns immediately if consent has not been explicitly recorded as accepted — the GA4 script tag is not created, `gtag('js', ...)` and `gtag('config', ...)` are not called, and no `dataLayer` push reaches Google's servers until this flag is set. The cookie bar (`#jft-cookie-bar`) is shown after a 700ms delay only when no prior choice exists (`if (bar && !choice) setTimeout(...)`), and `jftCookieDecline()` sets `'essential'` (not `'accepted'`), which correctly keeps analytics off. Consent withdrawal (`jftCookiePreferences()`) clears the stored choice and re-shows the bar, and additionally calls `gtag('consent', 'update', { analytics_storage: 'denied' })` if `gtag` already exists. **Classification: TECHNICAL — verified as implemented; no GDPR/DPDP/ePrivacy legal-compliance conclusion is offered, as that requires legal review this session cannot provide.**

## 6. Event Taxonomy

| Event | Trigger | Represents |
|---|---|---|
| `form_start` / `rfq_start` / `sample_request_start` | first `focusin` on any form | INTENT |
| `rfq_click` / `sample_request_click` | click on a link to `contact.html`/`sample-request.html` | INTENT |
| `generate_lead`, then `rfq_submit` / `sample_request` / `enquiry_submit` | **only after** the `/api/lead` backend returns `{success:true}` | CONVERSION |
| `view_item` / `product_view` | first render of a `-exporter.html`/`-supplier.html`/`products.html` page (deduped via `trackOnce`) | INTENT (product interest) |
| `article_view` / `article_read_depth` | first render / 50%+90% scroll of a `blog-*.html` page | INTENT (content engagement) |
| `whatsapp_click` / `contact_whatsapp` | click on any `wa.me`/`api.whatsapp.com` link | INTENT (high-value) |
| `contact_phone` / `contact_email` | click on `tel:`/`mailto:` links | INTENT |
| `file_download` / `brochure_download` | click on a `.pdf` link | INTENT |
| `outbound_click` / `conversion_link_click` | click on external / conversion-path links | diagnostic/INTENT |
| `page_not_found` | body has `data-page-type="404"` | diagnostic |
| `csp_violation` | `securitypolicyviolation` event | diagnostic |
| `rfq_prefill_loaded` | `contact.html?source=quote_calculator` loads | diagnostic (funnel-bridge confirmation) |

No event was found to be misleadingly named, and none needed renaming.

## 7-9. RFQ / Sample / WhatsApp Measurement

All three are measurable and, critically, **correctly distinguish intent from success**: `submitLead()` only calls `track('generate_lead', ...)` and the completion event (`rfq_submit`/`sample_request`) *after* `if (!response.ok || !result.success) throw new Error(...)` has already passed — a failed or invalid submission never reaches the tracking call. This is exactly the intent-vs-conversion discipline Part F of this phase demands, and it was already correctly built (Phases 6-13 did not need to touch this). WhatsApp clicks carry product/page context (`Product/page: <H1>`, `Source page: <path>`) in the *link's own href* (visible to the buyer, not sent to analytics) and separately fire `whatsapp_click`/`contact_whatsapp` with only `page_path` and a truncated page-title string as parameters — **no message content, no phone number, and no personal data is sent to GA4** (verified by reading every parameter object passed to every `track()` call in the file; see §22).

## 10-14. Product / Category / Article / Regional / Calculator Measurement

Product identity for `view_item`/`product_view` comes from `document.querySelector('h1').textContent` and `document.body.dataset.category` — a deterministic, governed mechanism requiring zero per-product hardcoding (84 products need no individual configuration). **Category pages do not receive this same custom event**: the triggering regex (`/-exporter\.html$|-supplier\.html$|products\.html$/i`) does not match category-page filenames (e.g. `rice-exporter-india.html` ends in `-india.html`, not `-exporter.html`), so category pages get GA4's automatic `page_view` but no custom "category viewed" event with commodity identity as a parameter. **Classification: TRACKING GAP, P2** — GA4 can still answer "how many pageviews did each category page get" via the standard `page_path` dimension (this is not a total gap), but "which commodity group attracts commercial interest" as a single structured metric is not currently a first-class event. Not implemented this phase: adding a new event type is a taxonomy expansion, not a bug fix, and the phase brief explicitly instructs not to add event tracking without a demonstrated business need beyond what already exists. Calculators (`quote-calculator.html`, `packing-calculator.html`, `port-transit-calculator.html`) are tracked only via automatic pageview plus their own `data-track="quote_to_rfq_click"`/`data-track="quote_to_whatsapp_click"` attributes (picked up by `jft-conversion.js`'s generic `link.dataset.track` handler) — a tool-to-RFQ bridge event exists; a `tool_complete`/`tool_start` distinction does not. **Classification: TRACKING GAP, P2/P3** — not implemented, same reasoning. Regional pages (Africa/Asia/Europe/UAE) inherit the same product-page and pageview mechanisms; no regional-specific event exists, and none is recommended without a demonstrated need beyond page-path analysis, which is already possible.

## 15-16. GSC Data Validation & Search Performance

**Data classification: REAL PRODUCTION DATA.** `reports/search-console-export-2026-08-20/search-console-performance-analysis.md` states an explicit export date range (19 May 2026–18 Aug 2026), real totals (286 clicks, 10,410 impressions, 2.75% weighted CTR, 10.03 average position), and real per-page/per-query/per-country/per-device row counts (327 page rows, 141 country rows, 3 device rows, 188 non-brand query rows) — this is a genuine, dated GSC export, already analyzed in Phase 9, and is re-confirmed here as real rather than assumed. By contrast, `reports/seo-opportunities-top-100-2026-08-20.csv` is confirmed, again, to be **PLACEHOLDER / estimated keyword research**, not real GSC data — every row's "Current Rank" column literally reads "Requires GSC query export." **No GA4 export of any kind exists in this repository** — there is no traffic, session, or conversion count anywhere in the repo that reflects real visitor behavior; every number in this report about *what visitors did* is a statement about what the code *would* measure, not what has been observed, and is labeled as such throughout.

Within the real GSC dataset's 3-month window, the highest-opportunity pages by the export's own CTR-gap scoring were `blog-cumin-jeera-price-outlook-2026.html` (1,729 impressions, 0.4% CTR, position 6.99) and `packing-calculator.html` (1,444 impressions, 0.76% CTR, position 6.9) — both already identified in the Phase 9 opportunity map; nothing new is added here since Phase 15's mandate is measurement architecture, not re-running the SEO audit.

## 17. UTM / Campaign Attribution

`getAttribution()` captures `utm_source/medium/campaign/id/term/content` plus `gclid/gbraid/wbraid/msclkid/fbclid/ttclid/li_fat_id` from the landing URL, persists them in `sessionStorage` (surviving the whole browsing session, not just one page), and `enrichForms()` auto-injects them as hidden fields on every form the buyer eventually submits — meaning a buyer who lands via a campaign link and later submits an RFQ several pages later still has that first-touch attribution attached to the lead. This was traced and confirmed working as designed; no gap found.

## 18. Locale Measurement

`page_path` (captured automatically on every event via `track()`'s `Object.assign({page_path: location.pathname, ...})`) includes the locale directory prefix (e.g. `/ar/1121-basmati-rice-exporter.html`), so every event is locale-attributable without any locale-specific code — one governed mechanism, not 11 separate ones. Confirmed the duplicate-script bug (§12) affected all 10 locale copies of the 2 pages identically and has now been fixed identically across all of them.

## 19. Device Measurement

GA4's own automatic device-category dimension applies to every event, since it is derived by Google's servers from the request's user agent, not from anything the site's own code needs to implement. No gap.

## 20. Conversion Quality

The three-tier intent/medium/high-intent structure the phase brief asks for already exists in substance: pageviews and scroll depth are low-intent (automatic/read-depth events); product views, form starts, and WhatsApp clicks are medium-intent; `rfq_submit`/`sample_request`/`enquiry_submit` are the only high-intent, success-gated conversions. Nothing was recommended to be marked as a GA4 "conversion" beyond what already functions as one, and no change was made to conversion definitions (that requires GA4 account access this session does not have — see §31 Limitations).

## 21. Duplicate / Faulty Event Audit — the phase's central finding

**FINDING (fixed)**: `buyer-security.html`, `export-documentation.html`, and all 10 locale copies of each (22 files total) contained a redundant, direct `<script src="jft-conversion.js">` tag *in addition to* the header-injection delivery that already exists correctly on every other page of the site. Consequence, precisely traced: the script's IIFE runs twice, so `document.addEventListener('click', ...)` and `document.addEventListener('securitypolicyviolation', ...)` are each registered twice, meaning every click-based event (`whatsapp_click`, `contact_phone`, `contact_email`, `file_download`, `outbound_click`, `conversion_link_click`, and any `data-track` attribute) fires **twice** for a single real click on these 22 pages. `enrichForms()`'s per-form `focusin` listener is likewise registered twice (each instance removes only itself, not the other), so `form_start`/`rfq_start` also double-fires once. `loadAnalytics()`'s own-closure `analyticsLoaded` guard does not survive a second, separate IIFE execution (it is a `let` variable inside the function scope, not a global), so the `gtag.js` library script is fetched and `gtag('config', ...)` is called a second time. The one-time, success-gated `rfq_submit`/`sample_request` conversion events themselves were **not** at risk of double-firing (they depend on a single form submission, not on how many click listeners exist), so this was never a lead-count-inflation risk — but it was a real, confirmed source of inflated click-event and intent-event counts on two trust-critical pages.

## 22. Data-Minimization Review

Read every parameter object passed to every `track()`/`trackOnce()` call in `jft-conversion.js` (12 distinct call sites): none pass raw form field values, names, emails, phone numbers, company names, or free-text enquiry content. The only data sent to `CONFIG.leadEndpoint` (the site's own `/api/lead` backend, not Google Analytics) includes the actual PII a buyer submits — that endpoint is JFT's own lead-storage/CRM integration, a different system from GA4, and out of this phase's scope (no source for it exists in this repository to audit). **Classification: NO ISSUE for the GA4 path specifically.**

## 23. Performance Impact

One script, no framework, no additional third-party analytics platform, `defer`-loaded, gated behind consent so the GA4 library itself (the heavier of the two scripts) does not load at all for visitors who decline. The duplicate-load bug (§21) was also a minor, real performance cost on the 22 affected pages (a second, unnecessary fetch of both `jft-conversion.js` and, post-consent, `gtag.js`) — now eliminated by the fix, a small but genuine performance improvement alongside the measurement-integrity fix.

## 24. Measurement Gap Matrix

| Gap | Severity | Status |
|---|---|---|
| Duplicate script execution on 22 pages | P0/P1 | **FIXED** |
| Category pages lack a structured "category viewed" event | P2 | Documented, not implemented (no demonstrated need beyond existing page-path analysis) |
| Calculators lack `tool_start`/`tool_complete` granularity | P2/P3 | Documented, not implemented |
| No GA4 export data available to this session | LIMITATION | Cannot be fixed from the repository; requires external account access |
| GA4 conversion-event marking (in the live GA4 property) | BUSINESS/EXTERNAL | Out of scope — Part AG forbids live account changes |

## 25. Fix Decision Gate

The duplicate-script finding satisfied all twelve required conditions in Part AA: genuine gap confirmed (traced precisely, not assumed), current implementation fully understood, root cause confirmed (redundant legacy tag pre-dating universal header-delivery), measurable business value (eliminates inflated click/intent event counts on 2 trust-critical pages × 11 locales), no personal data involved, no invented business logic, the fix *removes* a duplicate rather than adding one, deterministic (exact-string, count-guarded), low performance impact (net improvement), low regression risk, fully reversible, and testable (HTML5-validated, script-count-verified, idempotency-verified). **Implemented.** No other finding this phase satisfied all twelve simultaneously.

See `reports/phase15-analytics-measurement-final-2026-08-28.md` for implementation, verification, and regression detail.
