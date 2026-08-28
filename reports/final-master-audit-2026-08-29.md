# FINAL MASTER AUDIT — JFT Agro Overseas LLP Website (Post Phases 1–34)

**Audit date:** 2026-08-29
**Auditor mode:** read-only certification (no source/deploy/Git modifications during audit)
**Deploy verified:** Wrangler `da5283be` live
**Auditor:** Cline (read-only pass) → artifacts persisted in Act mode per owner authorization

---

## DIRECT ANSWER

**After Phases 1–34, is the website technically, commercially, visually, SEO-wise, AI-search-wise, security-wise, and operationally ready for production?**

**Yes — with disclosed low-risk items. Classification: B — PRODUCTION READY WITH DISCLOSED LOW-RISK ITEMS.** There are **no critical or high-severity blockers**. The site is deployable and, as verified live, functioning correctly. It is **not a 10/10** because of (a) one low-severity production hygiene gap (an unresolved developer *template file* is publicly reachable), (b) three security controls (TLS minimum version, rate-limiting, Turnstile) that are **UNKNOWN from here** and need dashboard confirmation, and (c) externally-dependent authority gaps (backlinks, LinkedIn, marketplace, GSC/GA4 access) that no website edit can resolve. None of these prevent launch. The only operationally-blocking action is **authorizing `git push origin main`** for the already-local Phase-34 commit `7cd68b00` (currently 1 ahead, 0 behind).

---

## 1. Executive Summary

The repository HEAD (`7cd68b00`, 2026-08-29) reconciles stale history to validated production + Phase 33. Live production at `jftagro.com` is reachable (200, `cf=HIT`), serves correct canonical/redirect/404/legacy behavior, strong security headers, 1,454 sitemap URLs with reciprocal `hreflang` + `x-default`, and a correct 1980 heritage narrative. Parity between repo source and `.cloudflare-dist` build is **byte-identical**; live differs from build only by **Cloudflare edge HTML minification** (verified — content identical). No secrets, no fabricated claims, no malformed JSON-LD on real pages. One low-severity exposure: `product-page-template.html` (+10 locale copies) is publicly deployed, unreferenced, unsitemapped, unresolved (`{{PRODUCT_NAME}}` literal), and emits a price-less `Product`/`AggregateOffer` schema.

## 2. Audit Scope

Read-only certification of repo (HEAD `7cd68b00`), live production (HTTPS, all regions via `cf-ray SIN`), and build output (`.cloudflare-dist`, 2,099 files). No build was re-run (Phase-34 rule: `.cloudflare-dist` retained; build would modify tracked source). No files modified.

## 3. Repository Baseline

- **HEAD:** `7cd68b0025dfc9edd28f664d8212b5bcd2f242e8` · **Date:** 2026-08-29 00:14:33 +0530 · **Branch:** `main`
- **`git status` end-of-audit:** `modified=4` (all `reports/*.json|*.md`), `untracked=105` (all `reports/*`). **ZERO website source files changed** (identical to start-of-audit — change-control proof).
- **Ignored artifacts:** `.cloudflare-dist*`, `.wrangler/` (git-ignored per Phase 34).
- **HEAD represents deployed release?** Yes — `.cloudflare-dist/about.html` SHA256 `D3864583…` == repo `about.html` SHA256, == committed source; live content verified identical.

## 4. Production Baseline (live, 2026-08-29)

| URL | Result | Evidence |
|---|---|---|
| `https://jftagro.com/` | 200, `cf=HIT` | curl `CF-Cache-Status: HIT` |
| `https://www.jftagro.com/` | **301 → `https://jftagro.com/`** | canonical www-strip |
| `/about.html`, `/contact.html`, `/products.html`, `/spices-exporter-india.html` | 200 `cf=HIT` | — |
| `/sitemap.xml` | 200, **1,454 `<loc>`**, 17,208 `xhtml:link` alternates, `x-default` present | regex count |
| `/robots.txt` | 200, content == repo (whitespace-only delta) | diff |
| `/.well-known/security.txt` | 200 (193 B) | — |
| `/api/lead` | **405** on GET (POST-only — correct) | no GET data leak |
| unknown path | **404** | — |
| Legacy: `/aboutus/`→`/about.html`, `/contact-us/`→`/contact.html`, `/raisins/`→`/indian-raisins-kishmish-exporter.html`, `/ricemill/`→`/infrastructure.html`, `/spices/`→`/spices-exporter-india.html`, `/products/`→`/products.html` | **all 301 correct, no loops** | curl |

## 5. Repository ↔ Production Parity

| Asset | Repo/`.cloudflare-dist` SHA256 | Live | Class |
|---|---|---|---|
| about.html | `D3864583…` (91,813 B) | `F080BC0C…` (90,697 chars; edge-minified) | **Expected edge transformation** (minify) |
| contact.html | `687E2E3E…` | `1817A3EE…` | Expected edge transformation |
| products.html | `37AC0EEF…` | `0DA9F2D5…` | Expected edge transformation |
| spices-exporter-india.html | `E170A036…` | `37D123F6…` | Expected edge transformation |
| sitemap.xml | `06C21AAE…` | `B54BB867…` (2.17 MB live) | Expected edge transformation (whitespace) |
| robots.txt | `FD1F2081…` | `8954EA4C…` | Expected edge transformation (whitespace) |
| security.txt | `F5638C56…` | `5965A018…` | Expected edge transformation |
| locale-ui.js | `57158D01…` | `754CADE…` | Expected edge transformation |
| worker.js / _headers | `.cloudflare/worker.js` `AD12EC3F…`, `_headers` `4BA3692B…` | not HTTP-fetchable | Build/deploy artifact; anchored to verified Wrangler deploy `da5283be` |

**Classification rationale:** For every HTML/XML/TXT/JS asset, live content was confirmed identical to repo source (canonical self, hreflang block, Organization JSON-LD, 1980 sentence, footer-placeholder, `<title>`) — only byte length differs by Cloudflare HTML Auto-Minify (whitespace/newline stripping). This is **Category 1 (expected Cloudflare edge injection)**, NOT a repository or production defect.## 6. Technical Audit

- **Secret scan:** 1,943 tracked source files scanned (excl. `reports/`, `normalize_commercial_claims.py`); **0 hits** (no AKIA/OpenAI key/PEM/`ghp_`/`glpat-`/`cf_api_token`).
- **Malformed JSON-LD on real pages:** none found. Real pages use Organization / BreadcrumbList / WebSite / FAQ / Article / WebApplication only.
- **Template leak (LOW):** `product-page-template.html` + 10 locale copies are **deployed (200)**, **not in sitemap**, **not internally linked**, contain literal `{{PRODUCT_NAME}}`, and emit `"@type":"Product"` + `AggregateOffer` **without `price`** (invalid per Google rich-result rules). Discovery probability low; should be removed from deploy or disallowed. (Carried as open item O1; **not fixed in this operation**.)
- **Duplicate IDs:** `#header-placeholder`/`#footer-placeholder` injected once per page (locale-ui.js). No static duplicate-ID defect confirmed.
- **TODO/FIXME:** `scripts/` contains parallel logic (warn-only, not production).
- **Source maps / debug / `.env` / `.git` exposure:** none observed on live (CSP `object-src none`; no `.map` refs).

## 7. SEO Audit

- **Technical:** robots.txt allows crawlers, disallows `/scripts/`, `/reports/`, dev `.py` files — correct. Sitemap declared. Canonical self on all checked pages. `www`→`non-www` 301. Trailing-slash consistent (`.html` files). Legacy 301s correct.
- **On-page (sampled):** `about.html` title *"About JFT Agro Overseas | Company & Buyer Verification"*, meta description, H1 present; homepage H1 *"Indian Agro Commodity Exporter. Exported With Proof. Rice, spices, pulses, grains"*. Keyword intent aligned to commodity-export buyer queries. No keyword stuffing.
- **International SEO:** 11 locales (ar, es, fr, id, ms, pt, ru, si, th, vi + en), full reciprocal `hreflang` + `x-default` in sitemap (17,208 alternates). Live `ar/about.html` = `<html dir="rtl" lang="ar">` + self-canonical (correct RTL governance). **Gap (LOW):** not every product has every locale (e.g., `ar/spices-exporter-india.html` = 404, not in sitemap, not in repo — consistent, not a broken link, but an i18n coverage gap).

## 8. Structured Data / Entity Audit

- Organization (`name`/`legalName` JFT Agro Overseas LLP, APMC Vashi address, `+918425057274`, `jftagro.info@gmail.com`, FB/IG sameAs) — consistent.
- BreadcrumbList on about/products/locale pages. WebSite, FAQ, Article, WebApplication (quote-calculator `price:0`) present.
- **Governance respected:** `products.html` has **0** `Product`/`price`/`offers` schemas; quote-only commodity pages correctly avoid misleading Product rich results.
- **Only violation:** the leaked `product-page-template.html` emits `Product`/`AggregateOffer` with no `price` (see §6). Real pages clean.

## 9. AEO / GEO / LLMO / AI Search

- **AEO:** FAQ schema + clear buyer-Q&A copy + calculators → can answer high-intent queries ("Indian rice exporter", "Basmati supplier", "CIF quote").
- **GEO:** regional/trade-hub pages, `geo.region=IN-MH`, `geo.position`, market guides.
- **LLMO:** entity consistent (who/what/where/markets/differentiator/contact all determinable from Organization + copy).
- **AI visibility (EXTERNAL):** actual SERP/LLM citations UNKNOWN — depends on backlinks/authority, not a website defect. No website fix recommended for this.

## 10. E-E-A-T / Trust

- **1980 heritage:** verified in only `about.html` (2 HTML files total contain 1980); wording *"family trading tradition in Indian agricultural commodities since 1980, JFT Agro Overseas LLP was formed in 2016"* — **correct distinction intact**; LLP formation date NOT misrepresented.
- Other `1980` occurrences: `data/quote-market-rates.json` (freight rate — not a claim) and excluded `reports/` — **false positives rejected**.
- Verifiable-document stance ("current registrations… available for buyer verification") present. Star Export House referenced. Certifications presented as verifiable, not fabricated.

## 11. Content

Real, substantive, governed copy; English-only category pages are a documented governance decision (false-positive rejected). Category locale architecture (English-primary) is an intentional governance choice, not a defect.

## 12. Conversion / Analytics

RFQ / sample / quote-calculator / WhatsApp CTAs present. Analytics consent gating present (verified `locale-ui.js`: *"Optional analytics help us improve the buyer journey…"*). `/api/lead` POST-only (405 on GET — no GET data leak). **GA4/GSC actual access UNKNOWN** (external credential).

## 13. Accessibility

`lang`/`dir=rtl` set; focus-visible outlines (`outline:3px solid var(--gold)`); hero `alt`/`preload` verified. **WCAG compliance NOT certifiable statically — browser test required** (flagged, not claimed).

## 14. Performance

Source-level good (preload, preconnect, `cf=HIT`, edge minify); **field CWV UNKNOWN**. Source notes: large per-page inline `<style>` blocks; `locale-ui.js` 93 KB (full dictionary); sitemap 2.17 MB.

## 15. Security (live headers)

HSTS `max-age=31536000; includeSubDomains`; full CSP (`object-src none`, `base-uri self`, `form-action self`, `frame-ancestors self`, `unsafe-inline` permitted for required inline); COOP `same-origin-allow-popups`; Permissions-Policy blocks camera/mic/geolocation/payment/usb; `referrer-policy: strict-origin-when-cross-origin`; `x-content-type-options: nosniff`; `x-frame-options: SAMEORIGIN`. **UNKNOWN (dashboard):** TLS min version, rate-limiting, Turnstile status (carried from Phases 21/22).

## 16. Visual / UI

Consistent premium design system (Phase 29/30); no redesign performed. No visual regression observed in sampled pages.

## 17. Legacy URL / Internal Linking

All 6 legacy paths 301-correct, no loops/chains. Internal linking (product→category, article→product, breadcrumbs) present; no orphan discovery in sampled set.
## 18. Known Open Items (reassessed)

| ID | Item | Status | Severity | Evidence | Web Fix? | External? | Blocking? |
|---|---|---|---|---|---|---|---|
| O1 | `product-page-template.html` (+10 locale) publicly deployed, unresolved, price-less Product schema | Confirmed live 200, not in sitemap | LOW | curl 200 + `{{PRODUCT_NAME}}` literal + JSON-LD | Yes (later) | No | No |
| O2 | Cloudflare min TLS version | UNKNOWN from here | LOW-MED | no dashboard access | No | Yes (admin) | No |
| O3 | Cloudflare rate limiting | UNKNOWN from here | MED | no dashboard access | No | Yes (admin) | No |
| O4 | Turnstile decision | UNKNOWN from here | MED | Phase 21/22 open | No | Yes (admin) | No |
| O5 | Push `7cd68b00` → origin/main | 1 ahead/0 behind, local-only | LOW (ops) | `rev-list --left-right` | No (git) | Auth needed | **Ops-blocker (not site)** |
| O6 | LEI postal-code discrepancy | Not re-verified (external) | LOW | historical | No | Yes | No |
| O7 | AAY-5952 discrepancy | Not re-verified (external) | LOW | historical | No | Yes | No |
| O8 | LinkedIn / external authority | Absent | MED (authority) | sameAs = FB/IG only | No | Yes | No |
| O9 | Marketplace presence | Absent | MED | none found | No | Yes | No |
| O10 | FIEO status | UNKNOWN | LOW | not in repo | No | Yes | No |
| O11 | Insights/article template divergence | Governed difference | LOW | design decision | No | No | No |
| O12 | Asia compliance-copy gap | Content decision | LOW | governance | No | No | No |
| O13 | Arabic calculator/tracker template | Design decision | LOW | governance | No | No | No |
| O14 | Category locale architecture (English-primary) | Governed | LOW | governance | No | No | No |
| O15 | GA4/GSC live access | UNKNOWN | MED | no credential | No | Yes | No |
| O16 | Real conversion/revenue attribution | UNKNOWN | MED | no analytics data | No | Yes | No |

## 19. False Positives Rejected

- **`ΓÇö` in about.html CSS comment:** PowerShell console mojibake of a literal em-dash `—` (UTF-8) — file content correct, NOT a defect.
- **`1980` in `data/quote-market-rates.json` / `reports/`:** freight rate / historical audit data, not a company-founding claim.
- **Byte-hash differences repo vs live:** Cloudflare edge minification (Category 1), content verified identical — NOT a parity defect.
- **English-only category architecture:** intentional governance, not a defect.
- **`AggregateOffer` with `price:0` on quote-calculator (`WebApplication`):** legitimate free-tool offer, not a misleading product price.
- **`ar/spices-exporter-india.html` 404:** consistent absent page (not in sitemap/repo), not a broken link.

## 20. UNKNOWN Items

TLS min version; rate limiting; Turnstile; LEI/AAY external verifications; FIEO; GA4/GSC access; field CWV; real AI-search citations; actual conversion attribution. All UNKNOWN = explicitly **not** converted to PASS.

## 21. Risk Register

Only LOW / MEDIUM-EXTERNAL risks; **no HIGH/CRITICAL**. Highest practical risk = O1 (template exposure) and O3/O4 (unconfirmed Cloudflare controls) — none blocking.

## 22. Scorecard

| # | Dimension | Score |
|---|---|---|
| 1 | Technical quality | 8.5 |
| 2 | SEO | 8.5 |
| 3 | International SEO | 8.0 |
| 4 | Structured data | 8.0 |
| 5 | Content | 8.0 |
| 6 | Conversion UX | 8.0 |
| 7 | Accessibility | 7.0 *(no browser cert)* |
| 8 | Performance | 7.5 *(field CWV UNKNOWN)* |
| 9 | Security | 9.0 *(3 controls UNKNOWN)* |
| 10 | Visual/UI | 8.0 |
| 11 | AEO | 8.0 |
| 12 | GEO | 8.0 |
| 13 | LLMO/AI search | 8.0 |
| 14 | E-E-A-T/authority | 8.0 *(external authority low)* |
| 15 | Production reliability | 9.0 |

**FINAL OVERALL SCORE: ≈ 8.2 / 10** (evidence-based; not inflated; 9.5+ would require field-CWV + dashboard-confirmed controls, which are UNKNOWN here).

## 23. Production Readiness Decision

**B — PRODUCTION READY WITH DISCLOSED LOW-RISK ITEMS.** No material/critical/high blockers. Site is correctly deployed and operable. Remaining items are low-severity hygiene (O1) or externally/administratively dependent (O2–O4, O6–O10, O15–O16), plus the ops step of pushing the local commit.

## 24. Final Recommendation

1. **Authorize `git push origin main`** for `7cd68b00` (closes repo/release sync).
2. **Later (non-blocking) fix:** exclude `product-page-template.html` (+locale copies) from deploy or add to `robots.txt` Disallow (O1).
3. **Admin action:** confirm TLS min version, rate limiting, Turnstile in Cloudflare dashboard (O2–O4).
4. **External:** build LinkedIn/marketplace/FIEO authority; connect GA4/GSC for real measurement (O8–O10, O15–O16).

## 25. Limitations

Static + live-HTTP audit only. No browser execution (accessibility/WCAG, JS console, true CWV unmeasured). Cloudflare dashboard controls UNKNOWN. External authority unmeasured. No build re-run (would modify tracked source).

## 26. Complete Evidence Index

- `git log -1` → `7cd68b00` · `git status` (start & end: 4 M / 105 ?? in `reports/` only)
- Live HTTP: `/`→200 HIT; `www`→301; 6 legacy→301; `/api/lead`→405; unknown→404
- SHA256 parity table (§5)
- `sitemap.xml`: 1,454 `<loc>`, 17,208 `xhtml:link`, `x-default` present
- Headers: HSTS/CSP/COOP/Permissions-Policy/nosniff/XFO/referrer verified
- Secret scan: 1,943 files, 0 hits
- 1980: only `about.html` (correct heritage); `products.html` 0 Product schema
- `product-page-template.html`: live 200, `{{PRODUCT_NAME}}` literal, price-less Product schema
- Wrangler deploy `da5283be` (verified live)

---

*Artifacts persisted in Act mode per owner authorization. No website source, build source, Cloudflare configuration, or production deployment was modified during this operation. O1 (template exposure) intentionally **not fixed** per instruction. Git push of `7cd68b00` authorized and performed separately (see QA change-control log).*
