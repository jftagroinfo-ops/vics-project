# Localization Human Review — Phase 6

This is a list of items automated validation cannot reliably resolve. It does not
duplicate the site's own native-review governance system — it feeds into it.

## The site already has a more rigorous process than this phase can run

`localization-review.json` + `data/localization-review-register.csv` (dated
2026-08-20, pre-existing this phase) already record that **every one of the 10
non-English locales is `pending_native_commercial_review` / `hold`** — no locale
has a named native reviewer, a recorded commercial-review date, or Search Console
demand evidence on file yet. That policy also explicitly distinguishes:
- **priority locales** (ar, es, fr, ru) — homepage published, native legal review required
- **fallback locales** (id, ms, pt, si, th, vi) — pages stay `noindex,follow` until
  translated content is materially different from the English source

Everything below is additive to that existing register, not a replacement for it.
Nothing in this phase should be read as native-speaker sign-off.

## Items for native-reviewer attention

### 1. Payment-terms FAQ contains a likely mistranslation (Arabic)
- **File:** `ar/1121-basmati-rice-exporter.html` and other Arabic product pages sharing this FAQ answer
- **Text:** "...We accept LC **في الافق**، TT (T / T)، وDP..."
- **Concern:** "في الافق" translates literally to "on the horizon" — this reads like a
  mistranslation of the trade term "at sight" (as in "LC at sight", a standard
  payment-term phrase). A native Arabic trade-fluent reviewer should confirm
  whether "في الافق" is a recognized idiom for "at sight" in this context or an
  error that should read something like "عند الاطلاع" (the standard Arabic term
  for "at sight" in banking/LC usage).
- **Why automated validation can't resolve this:** correctness here depends on
  trade/banking terminology fluency, not just grammar — exactly the category of
  judgment call this phase's rules reserve for a native reviewer.

### 2. Whether "Agro" should transliterate in the WhatsApp floating-button label
- **Scope:** `a.wa-fab` `aria-label="WhatsApp JFT Agro"` — identical to English in the
  governed cache for es/fr/id/ms/pt/si/vi (588 page instances); already
  transliterated as "اجرو" (ar), "Агро" (ru), "การเกษตร" (th) for the other 3.
- **Concern:** the site's own brand-preservation convention (see Phase 6 report,
  "JFT Agro Overseas" listed as an intentionally-preserved brand string) is in
  tension with the precedent that 3 of 10 locales already transliterate "Agro."
  Whether the other 7 should follow suit, and with what transliteration, is a
  brand/linguistic decision, not something to infer automatically.
- **Why flagged, not fixed:** picking a transliteration for 7 locales without a
  native reviewer would itself be an unreviewed translation decision.

### 3. Stale product-page FAQ content block (all 84 products x 10 locales)
- See the main report's Finding F2 for full detail. The locale FAQ block predates
  a content rewrite that has since shipped on the English root pages (which now
  carry a different, HS-code-inclusive 5-question FAQ). Restoring parity requires
  a content decision (translate the *current* English FAQ, not the retired one)
  plus new human translation — squarely outside what an automated audit or a
  cache-driven mechanical fix can responsibly do.
- Recommended as the top-priority item for whichever phase takes on locale
  content-parity work next, given its scale (830 product pages carry at least
  one fully- or partially-untranslated FAQ answer).

### 4. Cache entries flagged as "identical to English" (594 total, by locale below)
`scripts/audit_localizations.py`'s new `check_cache_self_identical` check is a
heuristic (see its docstring) — it deliberately reports these as informational,
not findings, because most inspected examples are legitimately-preserved brand
names, shipping-line names, port names, grade/HS codes, and prices. A sample
was manually inspected for this report and the large majority were confirmed
correct-as-is. A native reviewer going through the full lists in
`reports/localization-quality-2026-08-27.json` (`informational.cache_self_identical_translations`)
would be able to separate the small remaining minority of genuine gaps (if any)
from correct brand/code preservation faster and more reliably than further
automated heuristics could.

| Locale | Flagged (heuristic) |
|---|---:|
| ar | 8 |
| es | 59 |
| fr | 74 |
| id | 69 |
| ms | 155 |
| pt | 52 |
| ru | 26 |
| si | 99 |
| th | 12 |
| vi | 40 |

### 5. Calculator explainer sections exist only in English (all 3 calculators, all 10 locales)
`packing-calculator.html`'s "What Makes a Packing Plan Reliable?" section,
`quote-calculator.html`'s `method-section`, and `port-transit-calculator.html`'s
`schedule-section`/`origin-comparison` sections have no counterpart at all in any
of the 10 locale calculator pages. This is a content-completeness decision (add
translated content, or explicitly scope it as an English-only enhancement) that
needs a call from whoever owns the calculator content, not an automated fix.

### 6. Byline metadata left in English inside otherwise-translated articles
Spot-checked on `ar/blog-bill-of-lading-explained-importers.html`: the article
body is genuinely translated, but the editorial byline/image-caption text ("JFT
Agro Editorial • Bill Of Lading Review At An Export Terminal") renders in
English mid-Arabic-page. Low severity (metadata, not reader-facing prose), but
worth a native reviewer's call on whether image captions/bylines are in scope
for translation at all.
