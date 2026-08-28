# Phase 2 — Localization Build Determinism & Stale Dictionary Fix

**Baseline:** `e64a3f2b` (Phase 1 report: `reports/production-baseline-2026-08-26.md`)
**Scope:** the localization UI-dictionary generation system only. No website redesign, no product data, no unrelated content/SEO/JS/CSS/Cloudflare config was touched.

---

## Problem

`footer.html` reads "...since **2016**." The committed, currently-live `locale-ui.js` — the client script that swaps English text for translated text inside the header/footer on every non-English page — still carried a dictionary key for the old text, "...since **1980**." Because the matcher does an exact-string lookup, the stale key silently failed to match rather than showing the false date, but the practical effect was the same class of failure either way: **this sentence rendered as raw, untranslated English in the footer of every page, in all 10 locales.**

## Root cause

`scripts/build_locale_ui.py` (the generator) was never re-run after the "1980 → 2016" correction was made to `header.html`/`footer.html`. More broadly, the generator had no mechanism to *notice* that it had gone stale: it only ever computed dictionaries from current source strings, so a forgotten re-run leaves the committed `locale-ui.js` silently frozen at whatever it was at last generation, with no signal that it's drifted.

Two compounding issues made this hard to catch and risky to fix mechanically:

1. **No separation between "read the cache" and "fetch a new translation."** `build_locale_ui.py` imported `translate_values()`, which calls the unofficial `translate.googleapis.com` endpoint for *any* string not yet cached, with up to 12 retries and ~45s backoff per attempt (worst case ≈18 minutes per string). This put a slow, unofficial, rate-limit-prone external service directly in the path of what CI treats as a "deterministic" build step.
2. **No stale/missing-key detection anywhere.** Nothing compared the shipped `locale-ui.js` against current source, so drift was invisible until a human happened to read the footer in a non-English locale.

## Fix

### 1. Populated the missing cache entries (additive only)

Compared current `header.html`/`footer.html` source strings against `data/localized-copy-cache.json` and found **10 unique English strings** (92 language×string combinations across the 10 locales) with no cached translation — these were new/changed UI copy that had never been through an authoring pass. Hand-translated all 10 into every locale that needed them and added them to the cache. **Nothing existing in the cache was modified or removed** — this was purely additive (verified: every line removed in the diff is a pre-existing entry gaining a trailing comma from JSON re-serialization after insertion, not a content change).

For the "since 2016" sentence specifically, I reused the sentence structure of the already-reviewed "since 1980" translations in every language and swapped only the year — same wording, corrected fact, in all 10 languages.

### 2. Separated "normal build" from "translation authoring" (`scripts/translate_fallback_pages.py`)

Added `require_cached_translations()` — a pure, network-free function that looks up every value in the governed cache and raises `TranslationCoverageError` (naming every missing string) if coverage is incomplete. The existing `translate_values()` (network-capable, used by this module's own fallback-page-translation and residue-cleanup entry points) is untouched and still available as the explicit, optional authoring path when a genuinely new string needs a first translation.

### 3. Made the generator offline and fail-loud (`scripts/build_locale_ui.py`)

Rewritten to import only `require_cached_translations` — it no longer imports `requests` or anything that can reach a network socket, structurally rather than by convention. Exposed `compute_dictionaries()` and `render_script()` as pure, reusable functions (shared with the new audit script, so "what would regeneration produce" can never drift from what `main()` actually writes). On any missing cache entry it now prints `[FAIL]` to stderr and exits 1 instead of silently calling out to Google Translate.

### 4. Added stale/missing/drift detection (`scripts/audit_locale_ui.py`, new)

A new read-only, network-free audit, wired into `.github/workflows/site_quality.yml` right after the generator chain. It reports, per language and source string:
- `missing_translation` — current source string has no cache entry (would block a fresh build).
- `stale_shipped_key` — the committed `locale-ui.js` has a key that no longer matches any current source string (exactly the "1980" bug class).
- `raw_english_in_shipped_output` — the cache *has* a real translation for a current string, but the committed `locale-ui.js` doesn't reflect it.
- `invalid_json_payload` — the embedded dictionary isn't valid JSON.
- A determinism check that regenerates the dictionary in memory and byte-compares it against the committed file.

## Determinism

| Test | Result |
|---|---|
| Two consecutive runs of `build_locale_ui.py` | **Identical** — same MD5 (`793f3d11...`) both times |
| Regenerate in-memory vs. committed file (via `audit_locale_ui.py`) | **PASS** — byte-identical |
| Runs with all socket connections monkey-patched to raise on use | **PASS** — completed successfully, proving zero network access is attempted, not just that none happened to occur |
| Static check for any `requests` import/usage in `build_locale_ui.py` | **None found** |
| Runtime | ~1 second (previously: hung past 4 minutes and counting, before being stopped, when the cache was incomplete) |

## Validation

| Check | Result |
|---|---|
| Stale-key detection catches the original bug | **Confirmed** — temporarily restored the pre-fix `locale-ui.js` and re-ran the new audit: it correctly flagged 6-7 stale keys per locale (including a *second*, previously-unnoticed dead "Established 1980" key) and 3 `raw_english_in_shipped_output` findings per locale, then correctly reported **0 findings** once the real fix was restored |
| Missing-key fail-loud behavior | **Confirmed** — a scratch test with a deliberately incomplete cache raised `TranslationCoverageError` naming the exact language and string, rather than hanging or silently succeeding |
| Footer renders correctly in all 10 locales + English | **Confirmed in a real browser** (Playwright, against a local HTTP server so the header/footer's own `fetch()`-based loading behaves as in production) — every locale shows "2016" in a properly translated sentence; none show "1980"; none leak raw English for this string. Spot-checked full sentence text for ar/fr/th. |
| Existing audit suite | **All 8 scripts PASS, 0 findings each** (audit_website, audit_commercial_content, audit_claims_and_products, validate_blog_navigation, audit_localizations, audit_performance, full_site_audit, audit_coverage_gaps) |
| New `audit_locale_ui.py` | **PASS, 0 findings** |
| Cloudflare asset build | **PASS** — 2,089 files (same count as the Phase 1 baseline), `locale-ui.js` in the bundle is byte-identical (same MD5) to the source copy, no scripts/reports/internal files leaked. Build artifact deleted after inspection; **nothing was deployed**. |
| Obsolete "1980" string, repo-wide search | Found in 9 files total. Classified: 2 are this project's own audit-report documentation of the bug (legitimate); 1 (`reports/visual-audit.json`) is a stale, non-gating historical snapshot from an unrelated standalone script, predating the fix; 5 (`data/quote-market-rates.json`, 4× `reports/lighthouse-*.json`) are coincidental numeric matches (a freight rate, pixel coordinates, a timing value) unrelated to the company-history string; 1 (`data/localized-copy-cache.json`) is the old translation retained as additive-only translation memory, never selected into `locale-ui.js`'s output. **Zero occurrences remain in any production-facing file.** |

## Files changed

| File | Change |
|---|---|
| `data/localized-copy-cache.json` | Additive only — added 92 missing (language × string) translation entries across 10 unique English strings. No existing entry modified or removed. |
| `scripts/translate_fallback_pages.py` | Added `TranslationCoverageError` and `require_cached_translations()` (offline lookup). Nothing else changed. |
| `scripts/build_locale_ui.py` | Rewritten: no longer imports anything network-capable; fails loudly (exit 1, clear stderr message) on incomplete cache coverage; exposes `compute_dictionaries()`/`render_script()` as reusable pure functions. |
| `scripts/audit_locale_ui.py` | **New.** Read-only, network-free validation: missing/stale/out-of-sync detection for the header/footer locale dictionary. |
| `locale-ui.js` | Regenerated from the now-complete cache. Contains the correct "2016" translations in all 10 locales; contains zero stale keys relative to current source. |
| `.github/workflows/site_quality.yml` | Added one step running `scripts/audit_locale_ui.py`, immediately after the existing deterministic-generator chain. |
| `reports/locale-ui-audit.json` | Generated output of the new audit (0 findings, current state). |

## Files deliberately NOT changed

- **`data/localized-copy-cache.json`'s existing entries**, including the now-orphaned "since 1980" key — left in place as harmless translation memory rather than pruned, since the cache is shared by other translation workflows (`translate_fallback_pages.py`'s fallback-page and residue-cleanup entry points) that cover a much larger set of pages; removing entries from a shared cache on the basis of one consumer's (header/footer's) current needs risked deleting data another workflow still legitimately depends on. The generator already excludes it from output by construction (it only ever selects entries matching *current* source values), so it poses no production risk.
- **`translate_values()`** (the network-capable function) — left fully intact for its legitimate, still-needed role as the explicit authoring path for genuinely new strings.
- Everything outside the localization generation system: product data, HS codes, MOQ, packaging, compliance/certification claims, company facts, legal text, commercial terms, page design, layout, colours, typography, navigation, URLs, and all editorial/business content in the 10 locales were not touched, per this phase's change-control rule.
- The Phase 1 finding about `audit_output.txt` being a stale root-level file, the two stray root-level scripts (`tmp-packing-test.cjs`, `fix_all_product_pages.py`), the 14 scripts without module docstrings, missing `package.json`/lockfile for `wrangler`, and the `.gitignore` gap around `.dev.vars` — all still open, intentionally left for a later phase.
- **Not deployed.** This phase built and inspected the Cloudflare asset bundle locally and deleted it afterward; `wrangler deploy` was never run.
