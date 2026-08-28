# JFT Agro Overseas — Production Baseline & Change-Control Audit

**Phase:** 1 — Production Baseline (audit only)
**Date:** 2026-08-26
**Rule in effect during this phase:** no website source file was modified, redesigned, refactored, or fixed. Findings are documented, not corrected.

Companion machine-readable file: `reports/production-baseline-2026-08-26.json`
Change-control record: `reports/QA-CHANGE-CONTROL.md`

---

## A. Repository baseline

| Field | Value |
|---|---|
| Branch | `main` |
| Commit | `e64a3f2ba03c114a94ef61db20fbff486dab2a2b` (`e64a3f2b`) |
| Matches expected baseline commit | **Yes** — confirmed by exact match, no need to stop |
| Working tree | Clean, except one **untracked, uncommitted** local directory `.claude/` (Claude Code's own tool-permission settings — not a website file, not part of the repo history) |
| Node | v24.15.0 |
| npm | 11.12.1 |
| Python | 3.11.9 |
| pip | 24.0 |
| wrangler | 4.126.0, resolved live via `npx` — **not pinned** (no `package.json`/lockfile in the repo) |

## B. File counts (whole repository)

| Type | Count |
|---|---|
| HTML | 1,789 |
| CSS | 16 |
| JS | 12 |
| JSON | 29 |
| XML | 2 |
| Python scripts | 81 (80 in `scripts/`, 1 at repo root) |
| Markdown docs | 65 |
| CSV | 23 |
| PDF | 4 |
| Images | 382 (228 `.webp`, 102 `.jpg`, 51 `.png`, 1 `.ico`) |
| Fonts | 9 (`.woff2`) |

## C. Page counts (classification reused from `scripts/audit_coverage_gaps.py`'s own logic)

| Kind | Count |
|---|---|
| Indexable | 1,438 |
| Utility / noindex | 293 |
| Shared helper/template | 46 |
| Legacy redirect | 7 |
| Locale fallback (intentional English) | 5 |
| Temporary (`tmp-`/`audit-` prefixed) | 0 |
| **Total HTML files** | **1,789** |

## D. Locale counts

| Locale | Indexable | Utility/noindex | Locale fallback | Helper |
|---|---|---|---|---|
| en (root) | 142 | 3 | 1 | 6 (+7 legacy redirects) |
| ar | 129 | 29 | 1 | 4 |
| es | 129 | 29 | 1 | 4 |
| fr | 129 | 29 | 1 | 4 |
| id | 130 | 29 | 0 | 4 |
| ms | 130 | 29 | 0 | 4 |
| pt | 130 | 29 | 0 | 4 |
| ru | 129 | 29 | 1 | 4 |
| si | 130 | 29 | 0 | 4 |
| th | 130 | 29 | 0 | 4 |
| vi | 130 | 29 | 0 | 4 |

## E. Product inventory

- **Total products:** 84
- **By category:** rice 20, spices 17, herbs 15, feed 15, oilseeds 5, flour 5, pulses 4, wheat 1, sugar 1, raisins 1
- **Duplicate product URLs/slugs:** none found
- **Products missing a URL/slug:** 0
- **Products missing a required field** (`c`, `t`, `u`, `h`, `i`, `s`): none found

Product data integrity is clean.

## F. Existing audit results

All 8 read-only scripts that make up the CI "Site Quality Gate" were re-run exactly as-is (not modified) against the current commit:

| Script | Purpose | Result | Findings |
|---|---|---|---|
| `audit_website.py` | Structural audit of every renderable page | **PASS** | 0 |
| `audit_commercial_content.py` | Commercial contract surface of every product page | **PASS** | 0 |
| `audit_claims_and_products.py` | Unsupported-claims and master-data consistency gate | **PASS** | 0 |
| `validate_blog_navigation.py` | Blog cards, images, legacy redirects | **PASS** | 0 |
| `audit_localizations.py` | Locale completeness, residue, source parity | **PASS** | 0 |
| `audit_performance.py` | Static performance budgets | **PASS** | 0 |
| `full_site_audit.py` | SEO/accessibility/integrity scan | **PASS** | 0 |
| `audit_coverage_gaps.py` | Inventory, link graph, schema, encoding | **PASS** | 0 |

**The CI workflow (`site_quality.yml`) also runs an 11-script "deterministic generator" step before these audits**, then asserts `git diff --exit-code` (i.e. re-running the generators against committed source must produce zero difference). This step is **not** a pure audit — it writes files. I attempted to reproduce it read-only-safely and could not complete it; see Section G for why, and Section H for a concrete, independently-verified finding that strongly indicates this check would currently fail.

## G. Existing warnings / issues found (not fixed)

### G.1 — Generator-chain reproducibility could not be verified end-to-end

The first script in the chain, `build_locale_ui.py`, depends on `translate_fallback_pages.py`'s `translate_values()`, which calls the **unofficial** `https://translate.googleapis.com/translate_a/single` endpoint for any source string not already cached in `data/localized-copy-cache.json`, with **up to 12 retry attempts** and up to ~45s backoff between attempts (worst case ≈18 minutes for a single uncached string).

I checked the cache directly (read-only, no network calls) and found **92 header/footer string×locale combinations currently uncached**. A live attempt to run this script hung past 4 minutes with no output before I stopped it, specifically to avoid an unbounded delay and keep this phase read-only-safe. `git status` immediately after confirmed **zero files were modified** by the attempt.

### G.2 — Independent proof the generated output is already stale (see Section H below for detail)

Without running the generator, I compared the **already-committed** `locale-ui.js` dictionary against the **current** `header.html`/`footer.html` source text directly. They disagree. This is strong, direct evidence that if the CI generator step ran to completion today, it would very likely produce a diff and **fail** the `git diff --exit-code` assertion — independent of the network-timeout risk in G.1.

## H. CRITICAL — stale localization artifact with a dead factual-correction key

`footer.html` currently reads:

> "...Bridging Indian farms to global ports with excellence in quality, logistics, and transparency **since 2016**."

The already-committed, currently-live `locale-ui.js` — the client-side script that swaps English text for translated text in the header/footer on every non-English page — still carries a dictionary entry keyed on the **old** text:

> "...transparency **since 1980**." (translated into all 10 languages)

Because `locale-ui.js`'s matcher does an exact-string dictionary lookup, the stale key **does not match** the corrected source text, so it silently fails rather than displaying the false "1980" figure. The practical effect: **this sentence renders in raw, untranslated English inside the footer of every page, in every one of the 10 locales**, because the translation dictionary was never regenerated after the "1980 → 2016" correction was made to the English source.

I quantified the full scope of this drift (comparing current source strings against the shipped dictionary, read-only, no generator run):

| Locale | Stale keys (reference text no longer in source) | Current source strings with no shipped translation |
|---|---|---|
| ar | 7 | 12 |
| es | 6 | 14 |
| fr | 6 | 17 |
| id | 6 | 14 |
| ms | 6 | 18 |
| pt | 6 | 14 |
| ru | 6 | 12 |
| si | 6 | 15 |
| th | 7 | 11 |
| vi | 6 | 14 |

This was established purely by direct text comparison — no network calls, no file writes. **Not corrected, per this phase's rules.**

## I. Suspicious / stale files (documented, not removed)

| File | Git status | Last touched | Issue |
|---|---|---|---|
| `audit_output.txt` | tracked | 2026-08-09 | Stale snapshot claiming "1612 renderable HTML pages" — current count is 1743. Dead artifact duplicating what `reports/*.json` already tracks live. |
| `tmp-packing-test.cjs` | tracked | 2026-08-12 | Ad-hoc Playwright test script for `packing-calculator.html`, temp-named, committed at repo root. Not referenced anywhere; not part of the deploy bundle (wrong extension), but unnecessary repo clutter. |
| `fix_all_product_pages.py` | tracked | 2026-06-14 | Only `.py` file at repo root instead of `scripts/`. ~2.5 months stale. Not part of the deploy bundle. |

**14 of the 80 scripts in `scripts/` have no module docstring** (purpose not documented in-file): `check_links.py`, `check_unused.py`, `fetch_agro_news.py`, `final_polish.py`, `find_missing_blogs.py`, `fix_blog_social_images.py`, `fix_image_typos.py`, `integrate_blog_editorial_images.py`, `jft_ai_engine.py`, `propagate_products_fix.py`, `replace_jute_blog_references.py`, `thorough_fix.py`, `update_editorial_labels.py`, `validate_buyer_brief_cards.py`. Most read as one-off historical fix scripts by name.

**Duplicate filenames** found across the repo (e.g. `index.html` in 14 locations, `README.md` ×3, thumbnail-vs-full-size logo pairs) were all reviewed individually and are **expected by design** (per-locale mirrors, thumbnail variants, per-folder READMEs) — none indicate accidental duplication or drift.

## J. Build reproducibility (Step 7)

| Question | Answer |
|---|---|
| Does `scripts/build_cloudflare_assets.py` complete? | **Yes** — produced 2,089 files (134.3 MiB) without error, on the first attempt, with no network dependency. |
| Does it produce the expected public bundle? | Yes — its own internal `required`/`forbidden` assertions passed (it raises `RuntimeError` itself if they don't), and I independently confirmed the same. |
| Does the build alter source files? | No — it only writes to `.cloudflare-dist-next/` (gitignored output directory). |
| Are generated files deterministic? | **Partially unverified** — `build_cloudflare_assets.py` itself is deterministic and network-free; the separate 11-script "generator chain" in CI could not be verified end-to-end (see G.1), and independent evidence (Section H) suggests it is currently **not** in sync with source. |
| Unexpected files generated? | No. |
| Are internal scripts/reports excluded from the public bundle? | **Yes, confirmed** — see Section K. |
| Does the output match the expected architecture? | Yes. |

The local test build was deleted immediately after inspection; nothing was deployed.

## K. Deployment safety (Step 8)

Built a disposable local copy of the exact bundle `wrangler deploy` would publish, inspected it, then deleted it. **Nothing was deployed to Cloudflare during this phase.**

| Check | Result |
|---|---|
| Python scripts in bundle | 0 |
| `scripts/` directory present | No |
| `reports/` directory present | No |
| `docs/` directory present | No |
| `.git` present | No |
| `.env` / `.vars` / secret / credential files | 0 found |
| `data/localized-copy-cache.json` (translation cache) | Not present in bundle |
| `data/localization-review.json` | Not present in bundle |
| Hardcoded secrets in `.cloudflare/worker.js` | None found |
| Benign markdown accidentally included | 3 files — `assets/brochures/generated/README.md`, `images/editorial/SOURCES.md`, `images/PHOTO_CREDITS.md` (image-sourcing/credit notes only, not sensitive) |

**Verdict: no exposure risk found.** `build_cloudflare_assets.py`'s own allow-list approach (copying only specific directories and file types, plus explicit `forbidden` name checks) is working as intended.

## L. Secrets/config safety note

No real `.dev.vars` file currently exists locally or in git — there is no active secret exposure. However, `.gitignore` only excludes `.wrangler/` and the `.cloudflare-dist*` build directories; it does **not** explicitly list `.dev.vars`. This means there is currently no repository-level safety net if a developer later creates `.dev.vars` from `.dev.vars.example` and runs a broad `git add`. No incident has occurred — this is a preventive gap, not an active leak.

## M. Current git state (starting commit, preserved)

```
commit e64a3f2ba03c114a94ef61db20fbff486dab2a2b
branch main (up to date with origin/main)
```

This commit is the frozen baseline for all subsequent optimization phases. See `reports/QA-CHANGE-CONTROL.md`.

---

## Summary table

| Category | Count |
|---|---|
| CRITICAL findings | 1 |
| HIGH findings | 3 |
| MEDIUM findings | 2 |
| LOW findings | 2 |
| INFORMATIONAL notes | 4 |

(Full severity breakdown is in the final chat response, not duplicated here to avoid drift between the two.)
