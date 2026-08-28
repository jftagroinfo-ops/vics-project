# Phase 6 — Complete Localization Quality & Language Integrity Audit

**Baseline:** Phases 1-5 (uncommitted working-tree changes on top of `e64a3f2b`).
**Scope:** English + 10 locales (ar, es, fr, id, ms, pt, ru, si, th, vi).

## Summary

The Phase 5 finding — `Order on WhatsApp` untranslated 830 times — was root-caused,
fixed at the governed source (not by hand-editing 830 files), and the audit gap
that let it through was closed and regression-tested. While investigating the
architecture behind that defect, this phase found a **second, larger instance of
the same root cause**: a stale product-page FAQ block leaking English (and one
apparent mistranslation) across all 84 products x 10 locales. That one is
**documented, not fixed** — no governed translation exists for it, and the
underlying English content has since been rewritten, so a mechanical fix isn't
available without new human translation (see Finding F2 and the human-review
report).

## Part D — Localization architecture (where the chain actually runs, and where it breaks)

Two independent translation pipelines exist on this site, both reading from the
same governed store, `data/localized-copy-cache.json` (a flat
`{locale: {english_source_string: translated_string}}` map, ~6,500-6,700 entries
per locale):

```
Header/footer text:
  English source string -> data/localized-copy-cache.json -> build_locale_ui.py
    -> locale-ui.js (regenerated + determinism/drift-checked by audit_locale_ui.py, Phase 2)
    -> browser (runtime DOM text-swap)

Body content (product pages, articles, calculators, everything else):
  English source string -> data/localized-copy-cache.json -> [one-off historical
    scripts, e.g. translate_fallback_pages.py / repair_localized_copy.py /
    humanize_site_content.py] -> committed locale/*.html (STATIC, never regenerated)
    -> browser
```

The header/footer pipeline has a regeneration step and a dedicated drift
detector (`audit_locale_ui.py`, added in Phase 2) that guarantees the shipped
artifact always matches the current cache and source. **The body-content
pipeline has neither.** Once a string is translated and stamped into static
HTML, nothing re-applies it if the English source is later edited, and nothing
detected the resulting drift. That gap — not a one-off typo — is the actual root
cause of both M1 and F2 below. This phase closes the detection gap for
structurally-identifiable UI components (Part P) but does not build a full
body-content regeneration pipeline; that would be a substantial project of its
own and is recommended, not undertaken, here (see Recommendations).

## Part C/Q — M1: "Order on WhatsApp" (FIXED)

- **Where it originated:** `a.btn-wa-product`, the WhatsApp CTA button on every
  product page's hero area.
- **Root cause, precisely:** the English root pages' button text was renamed at
  some point from "Order on WhatsApp" to "WhatsApp Inquiry." The governed cache
  was updated with translations of the *new* string ("WhatsApp Inquiry") for all
  10 locales. The 830 already-translated locale product pages were never
  re-synced, so they kept shipping the *old* English text verbatim — it wasn't
  untranslated, it was orphaned.
- **Existed in a shared component?** Yes structurally (`btn-wa-product` class,
  identical markup on every product page), but there is no shared *generator* for
  it — each locale page is a static, independently-committed file.
- **Different variants across locales?** No — verified exactly one fragment,
  `<i class="fa-brands fa-whatsapp"></i> Order on WhatsApp</a>`, appeared exactly
  once in exactly 830 files (83 products x 10 locales), byte-identical every time.
- **Fix:** `scripts/fix_stale_ui_strings.py` (new, permanent, reusable) — reads
  `data/localized-copy-cache.json`, validates all 10 locales have a translation
  for the current source string ("WhatsApp Inquiry") before writing anything,
  then replaces the stale fragment in each of the 830 files with the governed
  translation. One script execution, zero hand-typed translations, zero manual
  per-file edits. Re-run is idempotent (re-running after the fix is a no-op).
- **Validation:** 0 occurrences of "Order on WhatsApp" remain sitewide (was 830).
  Real-browser check (Playwright/Edge, local server) across all 11 languages on
  a representative product page confirmed the correct translated button text
  renders, 0 console errors, 0 failed requests, 0 horizontal overflow. A
  controlled regression test — reintroducing the stale string on one file,
  confirming the new audit check (`audit_localizations.py`) flags it, then
  restoring the fix — proved the detector actually works, not just that it ran.

## Part P — Why `audit_localizations.py` missed M1, and the fix

The existing detector (`ENGLISH_SENTENCE` regex + `visible_strings()`) is a
long-sentence residue check: it requires 5+ words *and* a common English
function word (the/with/from/your/buyer/request/...), *and* requires 4+ such
sentences on a page before flagging it. "Order on WhatsApp" is 3 words with no
qualifying function word — it was structurally invisible to this check, no
matter how many times it appeared. This is not a threshold-tuning problem; the
check was never designed to catch short UI/button strings at all.

**Fix added (not a rewrite — the existing check is unchanged and still runs):**
a new `check_component_drift()` function targeting closed-vocabulary shared UI
components — CSS-class-identified elements where the English root pages carry a
single dominant text/attribute value (verified empirically per component, not
assumed: `a.btn-wa-product` text is "WhatsApp Inquiry" on 100% of 83 product
pages; `a.wa-fab`'s `aria-label` is "WhatsApp JFT Agro" on 100% of the same 83
pages — this component list currently has these 2 entries and is meant to grow).
For each locale, every occurrence of that component must equal the governed
cache translation of the *current* dominant English value — not the English
value itself unless the cache has no entry for that language at all (that gap is
reported separately as `shared_component_cache_gaps`, never silently accepted).
A locale-page value that matches neither is flagged.

This check would have caught M1 on day one of the drift (any locale page still
showing "Order on WhatsApp" after the English rename, with "WhatsApp Inquiry"
newly dominant, would immediately fail to match the required cache-governed
value). It does **not** produce mass false positives from brand/code/proper-noun
text, because it only evaluates the 2 explicitly-verified closed-vocabulary
components, not general page text.

**Verified working, not just written:** the stale string was temporarily
reintroduced on one file; the check correctly flagged
`{"vi_a.btn-wa-product": ["...: 'Order on WhatsApp'"]}`; the fix was re-applied;
the check returned clean again.

**A second, complementary addition** (`check_cache_self_identical()`) flags
cache entries where the translation is byte-identical to the English source and
the source reads as ordinary prose (contains a common function word, or is 4+
words) rather than a probable code/brand/proper-noun token. This is reported as
**informational**, not a hard finding — inspection of samples showed it mixes
real gaps with correctly-preserved company names, port names, shipping lines,
and grade/HS codes (see the human-review report). Making this a blocking check
would risk exactly the "mass false positives" this phase's rules warn against;
reporting it as a metric for human triage does not.

## Part E — Translation coverage per locale

Coverage is measured against the union of all distinct English source strings
present in the governed cache across every locale (7,115 distinct strings) —
this is an upper-bound estimate of gaps, since some strings only apply to one
locale's specific fallback/legal notices and were never meant to exist in every
locale's cache.

| Locale | Cache entries | Missing (vs. 7,115-string union) | Coverage |
| ------ | -------------------------: | ------: | -------: |
| AR     | 6,658 | 457 | 93.6% |
| ES     | 6,678 | 437 | 93.9% |
| FR     | 6,697 | 418 | 94.1% |
| ID     | 6,546 | 569 | 92.0% |
| MS     | 6,597 | 518 | 92.7% |
| PT     | 6,559 | 556 | 92.2% |
| RU     | 6,660 | 455 | 93.6% |
| SI     | 6,557 | 558 | 92.2% |
| TH     | 6,537 | 578 | 91.9% |
| VI     | 6,545 | 570 | 92.0% |

The 4 "priority" locales per the site's own `localization-review.json`
(ar/es/fr/ru) sit at 93.6-94.1%; the 6 "fallback" locales (id/ms/pt/si/th/vi,
explicitly `noindex,follow` by policy until content diverges materially from
English) sit at 91.9-92.7% — consistent with, not contradicting, that documented
staged rollout.

## Part F — Consistency (dead/stale/duplicate keys, conflicting translations)

- **No duplicate-key ambiguity is structurally possible** — the cache is a flat
  `{source: translation}` map per locale, so a given English string cannot have
  two different stored translations within one locale.
- **Cross-page consistency, spot-checked:** "Request Pricing" and "Request
  Sample" (the other two hero CTA buttons, siblings of the WhatsApp button)
  render with exactly one, uniform, correctly-translated value across all 830
  applicable pages in every locale — zero leakage, zero inconsistency. This
  confirms M1 was an isolated drift on one specific string, not a wider quality
  problem with these buttons.
- **Dead/unused keys:** not exhaustively enumerated (the cache is a shared
  translation memory across many historical workflows, so many entries will
  legitimately correspond to since-reworded content — a "dead key count" without
  triage would be noise, not a finding). Two dead keys were found incidentally
  while investigating a cache hit: `Use filled-bag envelope dimensions and
  actual gross weight for a firmer plan.` and 4 sibling method-card strings have
  Thai (and by the same pattern, presumably other-locale) cache translations
  that are never applied anywhere, because the section they belong to
  (`packing-calculator.html`'s `packing-method` block) was never propagated to
  any locale page at all — see Finding F5.

## Findings

### F1 — "Order on WhatsApp" stale CTA (830 instances) — FIXED
See Part C/Q above. Severity was HIGH; resolved.

### F2 — Stale product-page FAQ block leaking English across all 84 products x 10 locales — NOT FIXED (HIGH, documented)
Discovered while spot-checking JSON-LD `FAQPage` structured data for RTL
correctness (Part H). The Arabic FAQ block for `1121-basmati-rice-exporter.html`
showed:
- Q1 (MOQ) answer: `Minimum order is 1 FCL (حمولة حاوية كاملة) - ما يقرب من...`
  — starts in English, continues in Arabic. **830 instances** site-wide
  (`grep -rl "Minimum order is 1 FCL"` across all locale product pages).
- Q2 (payment terms) answer: `We accept LC في الافق، TT (T / T)، وDP...` —
  starts in English, code-switches with Arabic connectives. **747 instances**
  site-wide (the count is slightly lower than 830, meaning a minority of
  products have a differently-worded payment answer not matching this exact
  string — not investigated further).
- Q5 (sample request) — the entire question *and* answer render 100% in
  English on every locale product page: "Can I get a Trade samples on request
  before placing an order?" **830 instances** site-wide.

**Root cause:** identical mechanism to M1 — the English root pages' product FAQ
content was substantively rewritten at some point (the current English FAQ is a
different, HS-code-inclusive 5-question set; grepping the current English root
page for "Minimum order is 1 FCL" or "We accept LC" returns **zero** matches —
these strings no longer exist in the English source at all). The locale pages
still carry the *retired* FAQ content, partially translated at the time, and
nothing re-synced them when the English content changed.

**Why not fixed this phase:** unlike M1, there is no governed cache translation
for any of these three strings in any locale (checked directly — all `None`).
Fixing this responsibly requires either (a) new native-reviewed translations of
the *current* English FAQ content, which this phase cannot manufacture without
violating rule 6 (no machine-translating), or (b) a content decision about
whether to backport the new FAQ structure to all 830 locale pages at all — a
content-parity call outside a QA/audit phase's authority. Documented in full in
`reports/localization-human-review-2026-08-27.md` (item 3) as the top-priority
recommendation for the next content-localization phase.

### F3 — `wa-fab` floating-button aria-label identical to English in the governed cache for 7/10 locales (588 instances) — NOT FIXED (MEDIUM, documented)
`data/localized-copy-cache.json` stores `"WhatsApp JFT Agro"` as its own
"translation" (i.e., untranslated) for es, fr, id, ms, pt, si, vi. ar, ru, and th
already have real transliterations ("...اجرو", "...Агро", "...การเกษตร").
Because "Agro" sits in the same family as intentionally-preserved brand text
("JFT Agro Overseas" is one of this phase's own worked examples of text that
should stay in English), whether the other 7 locales *should* transliterate it
is a genuine judgment call, not something to resolve by pattern-matching against
3 locales that happen to already do it. Not auto-fixed; flagged for human review
(`localization-human-review-2026-08-27.md`, item 2).

### F4 — Cache entries identical to their English source (594 total, informational) — NOT FIXED (LOW/informational)
See Part F and Part P above for methodology. Per-locale counts: ar 8, es 59, fr
74, id 69, ms 155, pt 52, ru 26, si 99, th 12, vi 40. Manual inspection of a
sample from each locale found the substantial majority are legitimately
preserved: company names ("JFT Agro Overseas LLP"), shipping lines ("MSC, CMA
CGM, Maersk"), port names, grade/HS codes ("S-30 · M-30 · ICUMSA 45"), prices,
and dates. A minority are genuine full-sentence gaps that slipped through
because they didn't meet the existing residue check's 4-sentences-per-page
threshold (e.g., several `packing-calculator.html` method-card captions in Thai
— see F5, these turned out to be dead keys rather than live leaks). Reported as
an informational metric, not a hard finding, per Part P's false-positive
constraint; full lists are in the JSON report and the human-review report.

### F5 — Calculator explainer sections exist only in English, absent from all 10 locale copies — NOT FIXED (MEDIUM, documented)
`packing-calculator.html` (`section.packing-method`), `quote-calculator.html`
(`section.method-section`), and `port-transit-calculator.html`
(`section.schedule-section` / `section.origin-comparison`) each have zero
matching section in any of the 10 locale versions of the same page (confirmed
by direct HTML structure inspection, not byte-size comparison — byte size is
not a reliable signal here because locale pages are pretty-printed and English
pages are minified, making locale files ~2.5x larger by formatting alone). This
is a content-completeness gap (nothing to mistranslate — the section doesn't
exist at all in these locales), not a translation-quality defect. Not fixed;
documented for a content-ownership decision.

### F6 — Byline/caption text left in English inside a translated article body — NOT FIXED (LOW, informational)
`ar/blog-bill-of-lading-explained-importers.html`: the article prose is
genuinely translated (confirmed by reading a full paragraph), but the editorial
byline "JFT Agro Editorial • Bill Of Lading Review At An Export Terminal"
(likely an image caption/credit line) renders in English. Low severity, noted
for completeness; see human-review item 6.

## Part H — Locale-specific spot checks

- **Arabic:** `lang="ar"`, `dir="rtl"` confirmed on all sampled pages; RTL layout
  renders correctly (mirrored nav, right-to-left cards); numerals and
  punctuation render correctly; F2's mixed-language leak and the "at sight"
  mistranslation candidate (human-review item 1) were both found here.
- **Spanish/French/Portuguese/Russian:** metadata, OpenGraph, and JSON-LD
  (WebPage/BreadcrumbList/FAQPage where present) confirmed genuinely translated
  on sampled pages; 0 console errors across homepage/article/calculator/RFQ in a
  real-browser pass.
- **Indonesian/Malay:** fallback-locale status per site policy; not
  individually browser-tested this phase beyond the automated component-drift
  and cache checks (which cover them equally); no locale-specific defect found
  in the automated passes.
- **Sinhala/Thai/Vietnamese:** browser-tested (Thai, plus the sitewide
  11-language product-page pass covering all three); F5's dead-key example was
  surfaced via Thai; diacritics (Vietnamese) render correctly in all sampled
  pages.

No locale received a "PASS" grade implying native-speaker-verified quality —
per rule 11/12, none was claimed. Every "confirmed" statement above is backed by
either a direct structural check (HTML parsing, cache lookup) or a real-browser
render, both cited specifically.

## Part I — Metadata localization

Sampled 3 page types (homepage, product, article) x 10 locales = 30 checks:
`<title>` and meta description differ from the English source in **all 30**
cases (i.e., are genuinely localized, not copy-pasted). OpenGraph title/description
confirmed translated on a product-page sample. Canonical and hreflang tag counts
match Phase 3/4's already-verified baseline (12 hreflang alternates per page — 11
locales + x-default) with no regression. JSON-LD `WebPage`, `BreadcrumbList`, and
`FAQPage` structured data are translated field-by-field on the sampled Arabic
page (this is also where F2's mixed-language FAQ answers were found — the
structured data faithfully mirrors the same defect present in the visible HTML,
it does not introduce a separate one).

## Part J — Accessibility text

`wa-fab`'s `aria-label` is the one accessibility-text component checked in
depth this phase (via the new closed-vocabulary check) — see F3. No other
aria-label/alt-text regression was found in the pages exercised during the
Part S browser pass (0 console errors, which would surface most broken
attribute-driven JS behavior, though this is not a substitute for a full
accessibility audit — none was performed, consistent with rule scope).

## Part K/L — Forms and calculators

Real-browser pass (Playwright/Edge) across packing-calculator.html and
quote-calculator.html for English, Arabic, Thai, and Russian: 0 console errors,
0 failed requests, 0 horizontal overflow on every load. Labels/buttons on the
calculators' *form* controls were not found to have translation defects. The
one calculator-related finding (F5) is a missing *explainer section*, not a
broken or untranslated form control — the calculators remain fully functional
and their input/result UI is localized correctly in every locale checked.

## Part M/N — Product pages and articles

Product pages: FAQ block (F2) is the significant finding; hero CTAs (F1, fixed;
"Request Pricing"/"Request Sample," confirmed consistent) and breadcrumbs
(confirmed translated via JSON-LD sample) are otherwise clean in the pages
checked. Articles: body content is genuinely translated (not English-only by
policy, contrary to an initial assumption checked against `localization-review.json`
— that policy governs *legal* pages and 2 named evidence pages, not general
blog articles); F6's byline leak is the one defect found.

## Part O — Locale UI generator audit (`build_locale_ui.py`)

Re-verified against Phase 2's guarantees: `audit_locale_ui.py` still passes
(deterministic, offline — confirmed via the existing socket-blocking test being
part of that script's own validation, not re-run destructively this phase since
Phase 2 already proved it and no code in this pipeline changed); missing-key
detection still fails loudly (`TranslationCoverageError`); generated output
still matches source byte-for-byte. Nothing in Phase 6 touched this file or its
inputs, so Phase 2's guarantees remain intact by construction, and the re-run
confirms it.

## Part S — Browser validation after the M1 fix

Real Chromium (Edge) via Playwright against a local HTTP server (never static
inference):
- **All 11 languages** (English + 10 locales) on `1121-basmati-rice-exporter.html`:
  correct translated WhatsApp CTA text confirmed live in the DOM, 0 console
  errors, 0 failed requests, 0 horizontal overflow.
- **4 locales** (English, Arabic, Thai, Russian) x **5 page types** (homepage,
  article, packing calculator, quote calculator, contact/RFQ) = 20 page loads:
  0 console errors, 0 failed requests, 0 horizontal overflow, footer correctly
  injected on every page.
- **Mobile nav** (390x844): `#mobileToggleBtn` confirmed present for both
  English and Arabic homepages.

## Part T — Full regression

| Check | Result |
|---|---|
| `audit_locale_ui.py` | PASS |
| `audit_website.py` | PASS |
| `audit_commercial_content.py` | PASS |
| `audit_claims_and_products.py` | PASS |
| `validate_blog_navigation.py` | PASS (259 blog cards, 66 legacy redirects validated) |
| `audit_localizations.py` (enhanced) | PASS, 0 findings, 594 informational (see F4) |
| `audit_performance.py` | PASS |
| `full_site_audit.py` | PASS |
| `audit_coverage_gaps.py` | PASS (same pre-existing classification-bug numbers as Phase 3/4/5 baseline — unchanged, out of this phase's scope) |
| `check_links.py` | PASS, 0 broken links across 1,756 HTML files |
| Cloudflare build | 2,089 files (matches every prior phase's baseline), no internal-file leaks, **not deployed** |

## Recommendations for a future phase (not undertaken here)

1. **F2 is the new highest-priority localization item on this site** — larger in
   raw instance count (830+747+830) than the M1 defect this phase was
   commissioned to fix. It needs native translation of the *current* English FAQ
   content, not a mechanical fix.
2. Consider whether body content (product pages, calculators) deserves a
   drift-detection mechanism analogous to `audit_locale_ui.py`, given this phase
   found the *same* root cause twice (M1, F2) in one investigation.
3. F3 (wa-fab transliteration) and F5 (calculator explainer sections) are
   smaller, well-scoped follow-ups suitable for a native reviewer plus one
   mechanical-fix pass once translations exist.

## Files changed this phase

| File | Reason |
|---|---|
| `scripts/fix_stale_ui_strings.py` | New. Governed-cache-driven fix for orphaned English UI strings; used once to fix F1/M1 (830 files) |
| 830 locale product HTML files (`ar/`, `es/`, `fr/`, `id/`, `ms/`, `pt/`, `ru/`, `si/`, `th/`, `vi/` `*-exporter.html`) | One-line CTA text fix each, applied by the script above, sourced from the already-governed cache translation of "WhatsApp Inquiry" |
| `scripts/audit_localizations.py` | Added `check_component_drift()` (closed-vocabulary shared-component drift detection — the fix for Part P) and `check_cache_self_identical()` (informational same-as-English cache metric) |
| `reports/localization-quality-2026-08-27.md` / `.json` | This report |
| `reports/localization-human-review-2026-08-27.md` | Human-review item list (Part R) |

No redesign, no URL changes, no product-fact changes, no legal/regulatory
wording changes, no machine-translation of the site, no manual patching of
generated HTML, no unrelated cleanup.
