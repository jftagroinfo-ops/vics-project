# Phase 28 — Controlled Production Release, Post-Deployment Verification & Rollback

Date: 2026-08-28
Status: **RELEASE COMPLETE. ALL GATES PASSED. NO ROLLBACK REQUIRED.**

## 1. Authorization

Explicitly authorized to deploy the previously investigated, implemented, and regression-tested work sitting undeployed in the repository from Phase 25 and Phase 27. During pre-deployment inspection, a third undeployed change set (Phase 24's `legalName` fix) was discovered and could not be excluded from a whole-repository deployment — this was surfaced to the user directly, who explicitly confirmed including it (see §4).

## 2. Pre-Deployment Baseline

| Item | Value |
|---|---|
| Git commit | `e64a3f2ba03c114a94ef61db20fbff486dab2a2b` (working tree never committed since Phase 1) |
| Local sitemap URLs | 1,454 |
| Local renderable pages | 1,753 |
| Local products | 84 |
| Local categories | 10 |
| Local articles | 37 |
| Production version (pre-deployment) | `2b63fb19-28c8-45ca-9fc8-3468fdd105eb`, 100% traffic, created 2026-08-27T18:40:42Z (Phase 17's deployment, unchanged through Phases 18-27) |
| Production sitemap URLs (pre-deployment) | 1,453 |
| Production critical-URL spot check | 12/12 returned `200` (homepage, products, blog, rice category, a product page, contact, sample-request, africa-trade, Arabic homepage, sitemap, robots, security.txt) |

## 3. Gate 1 — Working-Tree Integrity: A Genuine Discrepancy Found and Resolved

`git status` shows ~1,472 modified tracked files — this reflects this repository's established, documented pattern of never having committed since Phase 1, not new/unexplained Phase 28 changes. The meaningful safety signal for a whole-repository deployment mechanism (`wrangler deploy`) is **production-vs-local content comparison**, not git-diff-vs-a-stale-HEAD.

Hash-comparing 8 representative files expected to be untouched by Phase 25/27 against production surfaced one genuine mismatch: `1121-basmati-rice-exporter.html` differed — traced precisely to Phase 24's `legalName` addition (`grep -c "legalName"`: 0 in production, 1 locally), not to anything unexplained. Broadened the check (a locale product page, an article, `about.html` as a control) and confirmed the **entire** discrepancy beyond Phase 25/27 is exactly Phase 24's `legalName` fix (1,326 files, purely additive JSON-LD), which was fully implemented and regression-tested in its own dedicated phase but explicitly documented as "NOT DEPLOYED."

**This was surfaced directly to the user** (not decided unilaterally) since Phase 28's authorization named only Phase 25 and 27, and Gate 1 explicitly requires stopping when a modified file cannot be confidently classified as authorized work. **The user explicitly confirmed including Phase 24's fix in this release.** Gate 1 re-evaluated and passed on this expanded, now-explicit scope.

## 4. Intended Production Changes (Final, User-Confirmed Scope)

| Source | Change |
|---|---|
| Phase 24 | `"legalName":"JFT Agro Overseas LLP"` added to the Organization JSON-LD on 1,326 files (English root + all 10 locales) |
| Phase 25 | 5 new entries in `.cloudflare/worker.js`'s `LEGACY_PRETTY_REDIRECTS` (`/aboutus/`, `/contact-us/`, `/raisins/`, `/ricemill/`, `/spices/`); category-hub links added to 5 articles |
| Phase 27 | `blog-toor-dal-export-india-2026.html` completed and indexed; `blog.html` updated (new card + corrected counts); `pulses-exporter-india.html` new guide link; category-hub cards added to 4 more articles; `sitemap.xml` regenerated |

## 5. Gates 2-4

- **Gate 2 (secrets scan)**: 0 findings across all changed files — only expected environment-variable *names* (`WEB3FORMS_ACCESS_KEY`, `TURNSTILE_SECRET`) referenced in code, no values.
- **Gate 3 (report/audit leakage)**: `scripts/build_cloudflare_assets.py` has a hard `raise RuntimeError` assertion against `reports`/`scripts`/`docs`/cache-file leakage into the build output — confirmed enforced, not just documented.
- **Gate 4 (full regression, pre-deployment)**: 9 scripts run, **0 findings**; `check_links.py`: 0 broken links / 1,766 files.

**All 4 pre-deployment gates passed.**

## 6. Phase 25 Redirect Pre-Verification

All 5 new redirect entries confirmed present in `.cloudflare/worker.js` with correct syntax; all 5 target files confirmed to exist locally (`about.html`, `contact.html`, `indian-raisins-kishmish-exporter.html`, `infrastructure.html`, `spices-exporter-india.html`). Automated `node`/Python syntax-check execution against this specific file remains blocked by this session's permission classifier (same limitation disclosed in Phase 25) — verification relied on precise manual inspection plus the eventual live-behavior test (§9).

## 7. Phase 27 Content Pre-Verification

`blog-toor-dal-export-india-2026.html`: 0 occurrences of "Placeholder article"; correct title, H1, `robots` meta (`index,follow,...`), canonical; present in `sitemap.xml`.

## 8. Build

`scripts/build_cloudflare_assets.py` run (existing, unmodified process — no improvised deployment mechanism used): **2,099 public assets, 136.5 MiB**, built successfully (the script's own required-file and forbidden-content assertions both passed silently, i.e., did not raise).

## 9. Artifact Inspection

| Check | Result |
|---|---|
| New article present in bundle | Yes |
| `legalName` present in bundled article | Yes |
| Bundled `sitemap.xml` count | 1,454 (matches source) |
| `reports/` present in bundle | **Absent** (correct) |
| `scripts/` present in bundle | **Absent** (correct) |
| `.env` / `.dev.vars` / `.git` present in bundle | **Absent** (correct) |

Note: `.cloudflare/worker.js` is correctly **absent** from the assets bundle — this is expected, not a defect: the Worker script is a separate deployment component (`main` in `wrangler.jsonc`), not a static asset served via the `env.ASSETS` binding.

## 10. Deployment Manifest

| Item | Value |
|---|---|
| Production domain | jftagro.com / www.jftagro.com |
| Deployment type | Cloudflare Worker (`jftagro-site`), via `wrangler deploy` |
| Phase 24 changes | 1,326 files, `legalName` addition only |
| Phase 25 changes | 5 legacy redirects + 5 article category links |
| Phase 27 changes | 1 new article + supporting links/counts + sitemap regeneration |
| Secrets exposed | 0 |
| Reports exposed | 0 |
| Pre-deployment audit findings | 0 |
| Pre-deployment broken links | 0 |

Actual deployment uploaded **1,329 new/modified assets** (769 already-uploaded/unchanged) — consistent with the expanded, confirmed scope (1,326 legalName files + toor-dal article + a handful of article/blog.html edits, with some overlap between the legalName and content-edit sets).

## 11. Deployment Execution

One operational note, disclosed for completeness: `scripts/build_cloudflare_assets.py` always outputs to `.cloudflare-dist-next` (never directly to `.cloudflare-dist`, which is what `wrangler.jsonc` points to) — this is the project's established, deliberate build/promote separation (documented since early phases). The first `wrangler deploy` attempt correctly failed with a clear error ("assets.directory does not exist") rather than deploying something wrong. Promoted the directory (`.cloudflare-dist-next` → `.cloudflare-dist`) via PowerShell's `Move-Item` (Bash's `mv` failed with a Windows permission error on this large, 2,099-file directory; PowerShell succeeded), then re-ran `wrangler deploy` successfully.

**Deployment result:**

| Item | Value |
|---|---|
| New Version ID | `88ead829-b2b4-45d1-95c4-748cf25ee165` |
| Assets uploaded | 1,329 new/modified, 769 unchanged |
| Deployment duration | ~29 seconds (upload) + ~7 seconds (trigger deployment) |
| Warnings | None |
| Custom domains confirmed | `jftagro.com`, `www.jftagro.com` |

## 12. Immediate Post-Deployment Smoke Test

| URL | Expected | Result |
|---|---|---|
| `/` | 200 | 200 |
| `/products.html` | 200 | 200 |
| `/blog-toor-dal-export-india-2026.html` | 200, real content | 200, "Importing Toor Dal" confirmed present, "Placeholder article" confirmed absent |
| `/sitemap.xml` | 200, 1,454 URLs | 200, 1,454 |
| `/robots.txt` | 200 | 200 |
| `/.well-known/security.txt` | 200 | 200 |

## 13. Post-Deployment Redirect Test — The Core Purpose of This Release

| Legacy URL | Status | Location | Final destination status |
|---|---|---|---|
| `/aboutus/` | 301 | `/about.html` | 200 |
| `/contact-us/` | 301 | `/contact.html` | 200 |
| `/raisins/` | 301 | `/indian-raisins-kishmish-exporter.html` | 200 |
| `/ricemill/` | 301 | `/infrastructure.html` | 200 |
| `/spices/` | 301 | `/spices-exporter-india.html` | 200 |
| `/products/` (pre-existing, regression check) | 301 | `/products.html` | 200 |

**All 6 redirects work correctly — single hop, no loops, correct destination.** This is the direct, live fix for the root cause Phase 25 identified behind Phase 24's AI-misinformation finding.

## 14. Post-Deployment Content Test

- Title: `Import Toor Dal from India | Split Pigeon Pea Buyer Guide` — correct.
- H1: `Importing Toor Dal from India: Identity, Process Status and Shipment Controls` — correct.
- Canonical: `https://jftagro.com/blog-toor-dal-export-india-2026.html` — correct.
- `blog.html` filter count: `All Articles 30` — correct; new article card present.
- `pulses-exporter-india.html` links to the new article — confirmed (1 match).
- New article links back to the Pulses category — confirmed (1 match).
- External citation (Codex Alimentarius PDF) resolves — `200`.

## 15. Post-Deployment SEO Test

Sitemap (1,454), robots.txt, canonical all confirmed correct in §12-14. No new SEO audit was launched — this was release verification only, per the phase's explicit instruction.

## 16. Post-Deployment Analytics Test

`header.html` carries exactly 1 reference to `jft-conversion.js` (unchanged); the new toor-dal article correctly carries **0** direct script tags (delivered via the established header-injection mechanism, matching every other article) — **no duplicate-loading regression introduced**, Phase 15's fix remains intact.

## 17. Post-Deployment Security Test

All 7 security headers (HSTS, CSP, X-Content-Type-Options, X-Frame-Options, COOP, Permissions-Policy, Referrer-Policy) confirmed present and unchanged. `.env`, `.git/config`, `wrangler.jsonc`, `scripts/audit_website.py` all confirmed `404`. **No modification was made to TLS, rate-limiting, or Turnstile settings**, per the phase's explicit restriction.

## 18. Production Parity (Hash-Verified)

| File | Result |
|---|---|
| `blog-toor-dal-export-india-2026.html` | MATCH |
| `sitemap.xml` | MATCH |
| `blog.html` | MATCH |
| `pulses-exporter-india.html` | MATCH |
| `blog-ir64-export.html` | MATCH |
| `header.html` (unchanged reference) | MATCH |
| `footer.html` (unchanged reference) | MATCH |
| `jft-conversion.js` (unchanged reference) | MATCH |

**8/8 files byte-for-byte identical between repository and live production.**

## 19. Post-Deployment Regression

One operational incident during this step, disclosed rather than silently worked around: the promoted `.cloudflare-dist` directory was still present on disk immediately after deployment, causing `audit_website.py` to time out (doubled file-scan scope) — the same class of stale-build-artifact issue first identified in Phase 11 and recurring in Phases 14, 19, and 20. Deleted the artifact (disposable, already uploaded, fully reproducible) and re-ran cleanly:

| Script | Result |
|---|---|
| `audit_website.py` | 0 findings, 1,753 pages |
| `full_site_audit.py` | 0 findings, 1,454 indexable |
| `check_links.py` | 0 broken links / 1,766 files |

No page-count, sitemap, localization, or schema regression found.

## 20. Rollback Decision Gate — Evaluated, Not Triggered

| Trigger class | Checked | Result |
|---|---|---|
| P0 (homepage down, 5xx, worker failure, routing failure, security-header removal, secret exposure) | Yes | None occurred |
| P1 (redirect failure, article unavailable, sitemap corruption, broken links, analytics duplication, canonical/hreflang corruption) | Yes | None occurred |
| P1/P2 (unexpected deployment files, production/repo mismatch, unexplained page-count change) | Yes | None occurred — page count moved by exactly +1, matching the one new page |

**No rollback was required or performed.**

## 21. Unexpected Findings

- The pre-deployment Gate 1 discrepancy (Phase 24's undeployed `legalName` fix) — surfaced to and resolved with the user, documented in §3-4.
- The stale `.cloudflare-dist` artifact causing a transient `audit_website.py` timeout post-deployment — root-caused and cleaned up, documented in §19. Neither finding required a rollback or any production change beyond what was already planned.

## 22. Limitations

- `.cloudflare/worker.js`'s syntax could not be verified via an executed check due to a session permission-classifier restriction on this file (same limitation as Phase 25); verification relied on manual inspection plus the successful live redirect behavior test (§13), which is definitive evidence the syntax was in fact valid.
- No live browser-automation tool was available — verification is HTTP/static-level, consistent with every prior phase's disclosed limitation.

## 23. Final Release Assessment

| Category | Result |
|---|---|
| Deployment Safety | **PASS** |
| Production Integrity | **PASS** |
| Redirect Integrity | **PASS** |
| Content Integrity | **PASS** |
| SEO Integrity | **PASS** |
| Analytics Integrity | **PASS** |
| Security Integrity | **PASS** |
| Repository → Build → Production Parity | **PASS** |

## 24. FINAL RELEASE DECISION

### **A — RELEASE SUCCESSFUL**

All pre-deployment gates passed (after resolving one genuine scope discrepancy directly with the user). The build was clean, the artifact was correctly composed, deployment completed without warnings, and every post-deployment verification — smoke test, all 6 redirects, article content, sitemap, analytics, security headers, and hash-verified production parity — passed on the first attempt. No rollback was required.

## Stop

Per Phase 28's explicit instruction: **STOP.** Do not begin Phase 29. Do not propose further changes as part of this phase. Wait for explicit authorization.
