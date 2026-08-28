# Phase 8 — Product FAQ Accordion Functional Repair & Interaction Regression

## Root cause

Every product page's FAQ accordion attaches **two** click listeners to each
question (`.faq-q`):

1. An inline `onclick` attribute (identical on English and locale pages) that
   toggles the `.open` CSS class on the answer panel and updates
   `aria-expanded`.
2. A separate listener, attached by a trailing `<script>` block after
   `</section>`, that reads the `.open` class and sets the answer panel's
   `max-height` accordingly.

Because the inline handler (registered first, at parse time) always fires
before the second listener, by the time the second listener runs, `.open`
already reflects the **post-toggle** state — so its branches must map
"class is now open" → "show the panel." The English root pages get this
right:

```javascript
var open = a.classList.contains('open');
a.style.maxHeight = open ? a.scrollHeight + 'px' : '0';
```

Every one of the 830 locale product pages had the two branches **reversed**:

```javascript
if (a.classList.contains('open')) { a.style.maxHeight = '0'; }
else { a.style.maxHeight = a.scrollHeight + 'px'; }
```

Net effect, confirmed by real-browser reproduction before any fix: clicking a
question correctly flips `aria-expanded` (false→true→false) but the visual
panel does the **opposite** — it stays collapsed on the click that should open
it, and pops open on the click that should close it. This is exactly the
"`aria-expanded="true"` while the answer remains visually hidden" failure mode
Part K warns against.

**Confirmed pattern, not assumed:** extracted the click-handler script from
all 830 locale files and all 83 applicable English root files — exactly one
distinct byte-identical variant on each side, and the two variants differ only
in which branch is which. No markup inversion, no `hidden`-attribute
inversion, no CSS-selector inversion, no height-calculation bug: the defect is
precisely the two assignment targets swapped inside one `if/else`.

## Scope

| | |
|---|---|
| Files affected | 830 locale product pages (83 products x 10 locales) |
| Not affected | English root pages (83/83 already correct); `sugar-s30-supplier.html` and its 10 locale copies (no generic FAQ template at all, per Phase 7) |
| Shared code impact | **None.** `faq.html` and `contact.html` (both per-locale) render FAQs via a completely different markup/JS pattern (`faq.html` uses native `<details>/<summary>`; `contact.html` uses its own `.faq-qt`/`.faq-qi` structure with no matching click handler in either file). Calculators (`packing-calculator.html`, `quote-calculator.html`, `port-transit-calculator.html`) and the shared header/mobile-nav (`header.html`) contain zero occurrences of `.faq-q`/`.faq-a`. Confirmed by direct grep across all of them — the buggy script exists nowhere outside the 830 product pages it was found in. |

## Fix

Single-line correction, applied identically to how the English root pages
already do it — swap which branch sets `scrollHeight` and which sets `'0'`.
No markup change, no CSS change, no new library, no new interaction model:

```diff
- if(a.classList.contains('open')){a.style.maxHeight='0';}
- else{a.style.maxHeight=a.scrollHeight+'px';}
+ if(a.classList.contains('open')){a.style.maxHeight=a.scrollHeight+'px';}
+ else{a.style.maxHeight='0';}
```

Applied via one new script, `scripts/fix_product_faq_accordion.py`: locates
the exact stale script string, asserts it appears exactly once per file, and
replaces it — the same "one script execution, zero hand-edited files" pattern
used for the Phase 6 CTA fix. 830 files changed, 0 files needed a second look.

## Browser reproduction (before -> after)

Real Chromium (Edge) via Playwright, local HTTP server, English + all 10
locales, `1121-basmati-rice-exporter.html`:

| | Before fix | After fix |
|---|---|---|
| English | Click 1: `aria=true`, height=100px (correct) | unchanged (was never broken) |
| Every locale (ar/es/fr/id/ms/pt/ru/si/th/vi) | Click 1: `aria=true`, height=**0px** (visually still closed); Click 2: `aria=false`, height=**100px** (visually open while ARIA says closed) | Click 1: `aria=true`, height=100px (Arabic: 74px, matching its own content); Click 2: `aria=false`, height=0px — identical shape to English |

0 console errors and 0 failed requests in every case, before and after.

## Expected behavior verification (Part C)

- Initial: answer height 0/collapsed, `aria-expanded="false"` — confirmed on all 11 languages, before and after (this part was never broken).
- After click: answer expands to its full `scrollHeight`, `aria-expanded="true"` — confirmed on all 11 languages after the fix (previously failed on all 10 locales).
- Second click: collapses back to height 0, `aria-expanded="false"`, no page corruption — confirmed on all 11 languages after the fix.

## Keyboard interaction (Part D)

The existing `onkeydown` handler (`Enter`/`Space` → `this.click()`) was
already present on both English and locale pages and was **not modified**.
Verified after the fix, on `ar/1121-basmati-rice-exporter.html`:

| Input | Result |
|---|---|
| Tab to question | Focus lands on `.faq-q` (`tabindex="0"`), visible 3px solid focus outline |
| Enter | Opens: `maxHeight=74px`, `aria-expanded=true` |
| Space | Closes: `maxHeight=0px`, `aria-expanded=false` |
| Tab again | Focus moves to the next `.faq-q` |

No new keyboard behavior was added — the existing control simply works now
that the underlying click handler is correct, since `onkeydown` invokes the
same `.click()` path.

## Multiple FAQ items (Part E)

The existing design is **multi-open**: opening one question does not close
another (the click handler only ever touches its own `nextElementSibling`,
never any other item). Verified post-fix on a 5-question page: opening
questions 1 and 3 leaves both open (`74px`, `0px`, `74px`, `0px`, `0px`) while
2/4/5 remain closed. This interaction model was not changed — it was already
the site's design and continues to be after the fix.

## RTL (Part F)

Arabic, mobile (390x844): `dir="rtl"` confirmed; chevron rotates correctly
(`matrix(-1,0,0,-1,0,0)` after click, `.rotated` class applied — chevron
mirrors along with the rest of the RTL layout, which is the existing,
unmodified behavior, not something newly mirrored by this fix); 0 horizontal
overflow after opening the panel.

## Mobile / long content (Parts G, H)

Tested `1718-golden-sella-basmati-exporter.html` (the product with the most
spec fields, hence the longest FAQ answer) at all four Phase-5 mobile
breakpoints, Arabic, after opening the first answer:

| Viewport | Overflow | Rendered height vs. content scrollHeight |
|---|---:|---|
| 430x932 | 0 | 127px / 127px (no clipping) |
| 390x844 | 0 | 154px / 154px (no clipping) |
| 375x812 | 0 | 154px / 154px (no clipping) |
| 360x800 | 0 | 154px / 154px (no clipping) |

No horizontal scrolling, no clipping, no viewport jump at any size.

## Accessibility / ARIA state consistency (Part K)

Confirmed on every tested locale, before vs. after:

| | Before | After |
|---|---|---|
| Closed | `aria-expanded=false` + visually collapsed | unchanged (already correct) |
| Open | `aria-expanded=true` + **visually collapsed** (mismatch) | `aria-expanded=true` + visually expanded (matches) |

The specific failure mode Part K names — `aria-expanded="true"` while the
answer stays visually hidden — is exactly what existed before this fix and is
exactly what is eliminated by it.

## Regression test (Part L)

New: `scripts/browser_faq_accordion_test.py` — loads English + all 10
locales' `1121-basmati-rice-exporter.html`, asserts closed-initial /
open-after-click / closed-after-second-click, with height and
`aria-expanded` checked together (not just one or the other), plus 0 console
errors. Run against a local server (`python -m http.server 8765`, matching
this repo's existing `locale_browser_audit.py` convention).

**Proven to actually catch the regression, not just pass by construction:**
1. Ran against the fixed pages — PASS on all 11.
2. Deliberately reintroduced the inverted script on
   `ar/1121-basmati-rice-exporter.html` only.
3. Re-ran — **FAIL**, isolated correctly to `ar`:
   `expected open state after click, got height=0 (scrollHeight=74) aria=true`.
4. Restored the fix.
5. Re-ran — PASS on all 11 again.

**A second, faster, CI-gating static check was also added**
(`check_faq_accordion_script()` in `scripts/audit_localizations.py`,
already part of the offline audit chain that runs on every regression pass):
compares each locale page's accordion script against the known-correct and
known-inverted patterns byte-for-byte. Verified with the same
reintroduce/detect/restore/pass cycle: correctly reported
`{"ar_faq_accordion_inverted": 1}` when the bug was reintroduced, and 0
findings once restored. This gives defense in depth: the static check runs on
every audit pass (fast, no browser needed) and the browser test provides
real, rendered-behavior proof on demand.

## Locale matrix (Part M)

| Locale | FAQ opens | FAQ closes | ARIA correct | Console clean |
|---|---|---|---|---|
| English | Yes (unchanged) | Yes | Yes | Yes |
| Arabic | Yes | Yes | Yes | Yes |
| Spanish | Yes | Yes | Yes | Yes |
| French | Yes | Yes | Yes | Yes |
| Indonesian | Yes | Yes | Yes | Yes |
| Malay | Yes | Yes | Yes | Yes |
| Portuguese | Yes | Yes | Yes | Yes |
| Russian | Yes | Yes | Yes | Yes |
| Sinhala | Yes | Yes | Yes | Yes |
| Thai | Yes | Yes | Yes | Yes |
| Vietnamese | Yes | Yes | Yes | Yes |

## Product / commodity-group matrix (Part N)

One representative per commodity group (rice, spices, herbs, feed, oilseeds,
flour, wheat, pulses, raisins — 9 groups; sugar's `sugar-s30-supplier.html`
has no generic FAQ to test, per Phase 7) x 11 languages x 2 viewports
(desktop 1440x900, mobile 390x844) = 198 page loads. **196/198 passed
directly; the 2 "failures" were a test-scope artifact, not a defect** — see
below.

**Discovery, not a Phase 8 defect, documented for transparency:** the
"raisins" representative, `indian-raisins-kishmish-exporter.html`, is one of
4 products (the others: `psyllium-husk-exporter.html`,
`yellow-peas-matar-exporter.html`, and Phase 7's already-known
`sugar-s30-supplier.html`) whose **English root page carries a bespoke,
non-interactive FAQ** (plain `<div class="faq-item"><h3>/<p></div>` pairs,
commodity-specific technical content — e.g. raisin grading standards and a
Codex reference — with no `.faq-q`/`.faq-a` accordion markup at all), while
their **locale pages carry the generic, interactive 5-question accordion**
(because their pre-Phase-7 locale copies already had 5 stale `.faq-item`
elements, so Phase 7's generator correctly matched its "5 items exist"
precondition and regenerated them, without knowing the English side had since
diverged to bespoke content for these 4 products specifically). This
predates both Phase 7 and Phase 8 — it explains why my English-vs-locale
comparison test failed for this one product (there is no accordion on its
English page to compare against), not any accordion malfunction.

**Verified directly, locale-side only, that this does not affect Phase 8's
fix:** all 3 of these products' (excluding Sugar S-30, which has no locale
FAQ at all) Arabic accordions were tested independently and open/close
correctly post-fix:

| Product | Initial height | After click | aria-expanded |
|---|---:|---:|---|
| `indian-raisins-kishmish-exporter.html` | 0 | 99.9px | true |
| `psyllium-husk-exporter.html` | 0 | 73.5px | true |
| `yellow-peas-matar-exporter.html` | 0 | 73.5px | true |

This is a content-parity question for whoever revisits Phase 7's scope (should
these 4 products' locale FAQs also switch to bespoke, translated,
non-interactive content to match English, or should English gain the generic
accordion back?) — not something Phase 8 is authorized to decide or touch
("DO NOT change the FAQ content," "DO NOT redesign the FAQ"). Flagged here,
not fixed.

The remaining 196/198 matrix cells (8 unaffected commodity-group products x 11
languages x 2 viewports, plus both viewports of the 9th group's confirmed-fine
locale side) all passed cleanly: correct closed→open→closed transitions,
correct `aria-expanded`, 0 console errors, 0 request errors, 0 horizontal
overflow.

## Visual regression (Part O)

Desktop (1440x900), mobile (390x844), and Arabic RTL mobile (390x844) all
included in the Part N matrix above. No layout shift, clipping, overlap, or
unexpected whitespace was introduced — the fix changes only a JS variable
assignment inside an inline `<script>` tag; no CSS, markup, or animation
timing was touched.

## Full regression (Part P)

| Check | Result |
|---|---|
| `audit_locale_ui.py` | PASS |
| `audit_website.py` | PASS (1,743 renderable pages, 0 findings) |
| `audit_commercial_content.py` | PASS (84 product pages, 0 findings) |
| `audit_claims_and_products.py` | PASS, 0 findings |
| `validate_blog_navigation.py` | PASS (259 blog cards, 66 legacy redirects) |
| `audit_localizations.py` (includes Phase 7's `check_product_faq_drift` and this phase's new `check_faq_accordion_script`) | PASS, 0 findings, informational cache-identity counts unchanged from Phase 6/7 |
| `audit_performance.py` | PASS, 0 findings |
| `full_site_audit.py` | PASS, numbers unchanged from baseline |
| `audit_coverage_gaps.py` | PASS, pre-existing classification-bug numbers unchanged, out of scope |
| `check_links.py` | PASS, 0 broken links across 1,756 HTML files |
| HTML validity (html5lib, fresh 60-file sample) | Valid |
| Real-browser locale matrix (Part M) | PASS, 11/11 languages |
| Real-browser product/commodity matrix (Part N) | 196/198 direct pass; 2 explained as a test-scope artifact, not a defect (see above) |
| Determinism (2 fix-script runs + hash comparison) | Byte-identical |
| Cloudflare build | 2,089 files (matches baseline), no internal-file leaks, **not deployed** |

All PASS.

## Determinism (Part Q)

`scripts/fix_product_faq_accordion.py` run twice: first run reported "Fixed
830 files," second run reported "Fixed 0 files" (nothing left to change).
MD5 hashes of 3 representative files identical before and after the second
run. No network access used or required.

## Files changed this phase

| File | Reason |
|---|---|
| `scripts/fix_product_faq_accordion.py` | New. One-time-run script: single-line correction of the inverted accordion branches, applied to all 830 affected files |
| `scripts/browser_faq_accordion_test.py` | New. Real-browser regression test (Part L) |
| `scripts/audit_localizations.py` | Added `check_faq_accordion_script()` — fast, static, CI-gating regression check |
| 830 locale product HTML files | One line changed per file: the two branch bodies inside the accordion click handler swapped |
| `reports/product-faq-accordion-fix-2026-08-27.md` / `.json` | This report |

No FAQ content, translations, product data, SEO/URL architecture, CSS, or
other JavaScript was changed. No accordion library was added. No animation,
color, or typography was changed.
