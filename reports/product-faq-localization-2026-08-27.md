# Phase 7 — Product FAQ Localization & Translation Governance

Resolves Phase 6 finding F2.

## Root cause

`scripts/remediate_production_claims.py` rewrote the product-page FAQ into a
data-driven, 5-question design (spec values, HS code/MOQ/packing, container
capacity, documents, sample request) sourced live from `data/products.json`
— but its `main()` applies that regeneration **only to the English root page**
(`root_path = ROOT / product["u"]`). Its locale loop applies unrelated
claim-normalization regexes and never touches the FAQ section. Locale pages
therefore kept shipping an **earlier, retired 5-question FAQ design**
(MOQ / payment terms / certificates / shipping time / sample request),
partially translated at the time it was written, with:

- 2 of those 5 old questions' answers starting with an untranslated English
  clause ("Minimum order is 1 FCL...", "We accept LC...") before continuing
  in the target language — 830 and 747 instances respectively
- 1 of those 5 old questions ("Can I get a Trade samples on request before
  placing an order?") never translated at all, question and answer both fully
  English — 830 instances

This is the exact same systemic gap identified in Phase 6 for the "Order on
WhatsApp" CTA: **body content on product pages has no regeneration or
drift-detection mechanism**, unlike header/footer text (which has
`build_locale_ui.py` + `audit_locale_ui.py`, Phase 2). Once the English FAQ was
rewritten, nothing re-synced or even flagged that locale copies had fallen
behind.

**A second manifestation of the same defect was found and fixed as a
consequence of this pipeline being traced**: the FAQPage JSON-LD structured
data mirrors the visible HTML (via `scripts/sync_faq_schema.py`, a pre-existing
script), so it carried the same stale content. Regenerating the visible HTML
and re-running `sync_faq_schema.py` resolved both simultaneously.

## Scope

| | Count |
|---|---:|
| Products affected | 83 of 84 (`sugar-s30-supplier.html` uses a bespoke, non-templated regulatory FAQ and is out of scope — see below) |
| Locales affected | 10 (ar, es, fr, id, ms, pt, ru, si, th, vi) |
| Pages regenerated | 830 |
| "Minimum order is 1 FCL" instances (before -> after) | 830 -> 0 |
| "We accept LC" instances (before -> after) | 747 -> 0 |
| "Can I get a Trade samples on request..." instances (before -> after) | 830 -> 0 |
| New governed template keys created | 5 (`product_faq.spec`, `.hs_moq_packing`, `.container`, `.documents`, `.sample`) |
| New translations created | 50 (5 keys x 10 locales), all `status: draft_pending_native_review` |
| New governed vocabulary entries added to `data/localized-copy-cache.json` | 7 (4 document-type phrases, 2 spec-label words, 1 product name) |

**Out of scope, documented not fixed:** `sugar-s30-supplier.html`'s locale
pages have no FAQ section at all (not even the retired one) — its English page
carries a bespoke FAQ about DGFT export-policy restrictions, dated claims, and
regulatory specifics that would need dedicated legal/native review, not a
mechanical template fill. See the human-review report.

## Translation governance — where translations now live

```
data/products.json (product facts: spec values, HS code, MOQ, packing, documents)
    +
data/localized-copy-cache.json (governed vocabulary: product names, spec
    labels, document-type names -- reused, 7 new entries added this phase)
    +
data/product-faq-templates.json  <-- NEW governed source: the 5 question/answer
    sentence templates, per locale, each with a `status` field
    |
    v
scripts/build_product_faq_locale.py  <-- NEW deterministic, offline generator
    |
    v
locale/<product>.html (830 files: the 5 .faq-item elements)
    |
    v
scripts/sync_faq_schema.py (pre-existing) re-derives the FAQPage JSON-LD from
    the now-correct visible HTML
```

Every translation in `data/product-faq-templates.json` carries
`"status": "draft_pending_native_review"` — consistent with, not overriding,
the site's pre-existing `localization-review.json` /
`data/localization-review-register.csv` policy, which already records all 10
locales as `pending_native_commercial_review`. No translation in this phase is
marked approved; that determination remains with a qualified native reviewer,
per the site's own governance and this phase's rule 19.

**No blind machine translation was used.** Where a governed cache translation
already existed for a needed piece of vocabulary (product names, most spec
labels, most document names — the large majority of what the templates need),
it was reused verbatim. Where it did not exist (4 document-type phrases, 2
spec-label words, 1 product name, and the 10 sentence templates themselves),
a careful, terminology-consistent draft translation was written and recorded
with its review status — not silently guessed, not auto-published as
approved, and not applied via 830 individual manual file edits.

## Translation coverage

| Locale | Template keys translated | Status |
|---|---:|---|
| ar | 5/5 | draft_pending_native_review |
| es | 5/5 | draft_pending_native_review |
| fr | 5/5 | draft_pending_native_review |
| id | 5/5 | draft_pending_native_review |
| ms | 5/5 | draft_pending_native_review |
| pt | 5/5 | draft_pending_native_review |
| ru | 5/5 | draft_pending_native_review |
| si | 5/5 | draft_pending_native_review |
| th | 5/5 | draft_pending_native_review |
| vi | 5/5 | draft_pending_native_review |

100% structural coverage (every locale has all 5 keys); 0% marked "approved"
(by design, per the site's own governance policy — see above).

## Human review

Full detail in `reports/product-faq-human-review-2026-08-27.md`. Headline
items:

- **Part O / Arabic "at sight"**: the disputed phrase ("في الافق," a likely
  mistranslation of "at sight") lived only in the now-retired payment-terms
  question, which the current English FAQ design does not include. Regenerating
  to parity **removes** the phrase from every page it appeared on (verified: 0
  occurrences remain) rather than correcting it in place — there is nothing left
  to mark `HUMAN_REVIEW_REQUIRED` for this specific phrase, since no replacement
  text was written. The intended meaning ("at sight" = payment on presentation
  of complying documents; standard Arabic banking term "عند الاطلاع") is
  documented for whoever reintroduces a payment-terms question in a future
  phase.
- All 50 new template translations are `draft_pending_native_review` by
  default, per the site's own policy — none is claimed correct at
  native-speaker fidelity.
- "Chromate," "Radiation" (spec labels) and "Turmeric Finger & Powder" (a
  product name that was missing from the cache entirely, discovered as a
  generator-blocking gap, unrelated to F2 itself) are flagged for a reviewer's
  second look.

## Audit protection (Part L)

`scripts/audit_localizations.py` gained `check_product_faq_drift()`: for every
product x locale, it **regenerates** the expected FAQ markup in-memory from the
same governed source the real generator uses, and byte-compares it against
what the live page actually ships — the same determinism-check pattern
`audit_locale_ui.py` established in Phase 2. This catches missing translation,
English leakage, and stale content generically (by detecting *any* deviation
from the governed source), not by matching specific strings — so it does not
need updating if the template wording changes later, and it would have caught
the original F2 defect on day one.

**Regression test performed, per this phase's own instruction:**
1. Deliberately replaced one Arabic FAQ question's visible text with its
   English source text.
2. Ran `audit_localizations.py` — result: **FAIL**, exit code 1,
   `{"ar_product_faq_drift": ["1121-basmati-rice-exporter.html"]}`.
3. Restored the correct Arabic translation.
4. Re-ran the audit — result: **PASS**, exit code 0, 0 findings.

(A first attempt at this test accidentally edited the JSON-LD copy of the
string instead of the visible HTML copy, since both exist in the file; the
audit correctly did *not* flag that, because `check_product_faq_drift()` checks
the visible-HTML source of truth, not its JSON-LD mirror, which is
kept in sync by the separate, pre-existing `sync_faq_schema.py` step that is
now part of this fix's regeneration procedure. Noted here for transparency
about how the test was actually run, not glossed over.)

## Determinism (Part K)

`scripts/build_product_faq_locale.py` was run twice in sequence (with
`sync_faq_schema.py` after each run). The second run reported "0 locale pages"
changed, and MD5 hashes of 3 representative files were confirmed identical
before and after the second run. No network access is used or required by
either script.

## Browser validation (Part N, Part M)

Real Chromium (Edge) via Playwright, local HTTP server, 130 page loads: 13
representative products (one per commodity group — rice, spices, herbs, feed,
oilseeds, flour, wheat, sugar, raisins, pulses — plus the shortest product
name, the longest product name, and the product with the most spec
fields/largest FAQ) x 10 locales.

| Check | Result |
|---|---|
| Page load errors | 0 / 130 |
| FAQ item count (expected 5, or 0 for the out-of-scope Sugar S-30) | correct on all 130 |
| English leakage in visible FAQ text (4 known stale-string markers) | 0 / 130 |
| Console errors | 0 / 130 |
| Failed requests | 10 — all the same external Wikimedia image (`upload.wikimedia.org/.../Monocrystals_of_sucrose.jpg`) on `sugar-s30-supplier.html`'s 10 locale copies, unreachable from this sandboxed test environment; not a same-origin or FAQ-related failure, and not evidence of a live-site defect |
| Horizontal overflow | 0 / 130 |
| RTL (`dir="rtl"` on Arabic pages) | confirmed correct |

**New finding, not caused by this phase, discovered by this phase's own
testing requirement (Part N: "accordion open/close"):** clicking a FAQ
question on any of the 830 locale product pages toggles the `open` CSS class
and `aria-expanded` correctly, but the answer panel's `max-height` is
immediately reset to `0` by a second, independently-registered click listener
whose open/closed branches are inverted relative to the equivalent listener on
the English root pages (English: `open ? scrollHeight : '0'`; locale:
`if(open){maxHeight='0'}else{maxHeight=scrollHeight}` — logically the reverse).
Net effect: the accordion visually never opens on any locale product page,
while the underlying ARIA state (`aria-expanded`) correctly reflects open/closed
— a real accessibility/UX defect, but **not part of F2** (it is an
interactivity bug in a `<script>` block outside the FAQ text content, present
before this phase and structurally unrelated to translation). Confirmed
pre-existing via `git diff`: zero lines of this script appear in this phase's
changes, and the bug is identical across every locale page checked (ar, th,
vi spot-checked in detail; the full 130-page automated sweep shows the same
"opened: false" symptom on all 120 non-Sugar-S30 pages, i.e. universally, not
selectively). **Not fixed this phase** — fixing it would mean editing the
shared accordion `<script>` block, which is outside this phase's authorized
scope (Part S: "only modify... required generated locale outputs" for the FAQ
fix; this is a pre-existing, unrelated JS defect, not a locale output of the
FAQ governance system). Recommended for a focused follow-up phase given its
reach (all 830 product pages, all 10 locales).

## SEO / structured data (Part P)

- Title, meta description, canonical, hreflang count (12: 11 locales +
  x-default) confirmed **unchanged** on sampled pages — this phase only
  touches the FAQ section.
- FAQPage JSON-LD validated as parseable JSON on all 2,510 `<script
  type="application/ld+json">` blocks across the 830 regenerated pages (0
  parse errors) — no duplicate schema introduced (still exactly 3 script
  blocks per page: WebPage, BreadcrumbList, FAQPage, matching the pre-Phase-7
  baseline).
- FAQPage `mainEntity` now semantically matches the visible FAQ content
  (previously it matched the *retired* content, since `sync_faq_schema.py` had
  synced it from the stale HTML) — confirmed on a sampled Arabic page.

## Visual regression (Part Q)

HTML validity (html5lib) confirmed on a 60-file sample (6 products x 10
locales, 0 errors). No CSS, no component markup, no accordion JS was changed —
only the 5 `.faq-item` elements' *text content* and their embedded product
variables. The FAQ component itself was not redesigned.

## Full regression (Part R)

| Check | Result |
|---|---|
| `audit_locale_ui.py` | PASS |
| `audit_website.py` | PASS (1,743 renderable pages, 0 findings) |
| `audit_commercial_content.py` | PASS (84 product pages, 0 findings) |
| `audit_claims_and_products.py` | PASS, 0 findings |
| `validate_blog_navigation.py` | PASS (259 blog cards, 66 legacy redirects) |
| `audit_localizations.py` (enhanced, Part L) | PASS, 0 findings, informational cache-identity counts unchanged from Phase 6 |
| `audit_performance.py` | PASS, 0 findings |
| `full_site_audit.py` | PASS, numbers unchanged from baseline |
| `audit_coverage_gaps.py` | PASS, pre-existing classification-bug numbers unchanged, out of scope |
| `check_links.py` | PASS, 0 broken links across 1,756 HTML files |
| HTML validity (html5lib, 60-file sample) | Valid |
| JSON-LD validity (all 2,510 script blocks across 830 pages) | Valid |
| Determinism (2 generator runs + hash comparison) | Byte-identical |
| Cloudflare build | 2,089 files (matches baseline), no internal-file leaks, **not deployed** |

All PASS. Technical crawl was not re-run in full this phase (Phase 3's crawl
scope is broader than this phase's changes warrant); `check_links.py` (0 broken
links) and the metadata/hreflang/canonical spot-checks above cover the surface
area this phase actually touched.

## Files changed this phase

| File | Reason |
|---|---|
| `data/product-faq-templates.json` | New. Governed source: 5 FAQ question/answer templates x 10 locale translations, each with review status |
| `scripts/build_product_faq_locale.py` | New. Deterministic, offline generator: renders the governed templates + product variables into each locale page's 5 `.faq-item` elements |
| `data/localized-copy-cache.json` | Additive: 7 new entries (4 document-type phrases, "Chromate", "Radiation", "Turmeric Finger & Powder") needed by the new templates. Also re-serialized (alphabetically re-sorted, LF line endings) as a side effect of the update script used — no data lost or altered, verified by entry-count reconciliation and the full audit suite passing; disclosed here for transparency since the resulting diff is large. |
| `scripts/audit_localizations.py` | Added `check_product_faq_drift()` — regeneration-diff based detection of FAQ source/output drift, wired into the existing gating audit |
| 830 locale product HTML files | The 5 `.faq-item` elements replaced with governed, translated, product-correct content; heading/brand-tag left untouched |
| (same 830 files) FAQPage JSON-LD | Re-synced from the now-correct visible HTML via the pre-existing `scripts/sync_faq_schema.py` |
| `reports/product-faq-localization-inventory-2026-08-27.md` / `.json` | Part A inventory |
| `reports/product-faq-human-review-2026-08-27.md` | Part H/R human-review list |
| `reports/product-faq-localization-2026-08-27.md` / `.json` | This report |

No redesign of the FAQ component. No URL changes. No product facts changed
(all spec values, HS codes, MOQ, packaging, container capacities are read
verbatim from the existing `data/products.json` — none were altered). No
unrelated cleanup.
