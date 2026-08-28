# Phase 18 — Production Security, HTTP Headers & Cloudflare Hardening

Date: 2026-08-28
Status: Investigation complete. **Zero website source files modified** — the production security posture was found to be correctly implemented; see §12 for the one informational (not actionable) observation.

## 1. Executive Summary

This phase traced every important security behavior from its true source (`.cloudflare/worker.js`'s `SECURITY_HEADERS` object and the `/api/lead` handler) through the deployed bundle to live, independently-verified HTTP responses from `https://jftagro.com/`. A critical factual correction was made along the way: Phases 15/16 had assumed `/api/lead` forwards to "JFT's own backend" — direct source reading this phase reveals it is a Cloudflare Worker function that forwards validated, sanitized submissions to **Web3Forms** (`api.web3forms.com`), a third-party transactional-form API, gated by an environment-configured access key and an optional Cloudflare Turnstile check. Every header, every `/api/lead` validation branch, every sensitive-file path, and every path-normalization edge case tested came back matching the traced source exactly, with no PII leakage, no stack traces, no debug information, and no permissive CORS/wildcard exposure found anywhere. This is a clean audit: **zero website changes were made.**

## 2. Baseline (Part 4)

- `git status --short`: 1,168 paths — consistent with the cumulative uncommitted work of Phases 1-17; no unexpected file appeared.
- HEAD unchanged: `e64a3f2b`.
- `.cloudflare/worker.js`: 315 lines, read in full (not sampled).
- `.cloudflare-dist/` (the Phase 17-deployed bundle): present, 2,099 files (per `build_cloudflare_assets.py`'s own count).

## 3. Source of Truth Trace (Part 3)

`SECURITY_HEADERS` (worker.js lines 1-11) → applied to every static-asset response via `withSecurityHeaders()` (lines 117-136), which also auto-adds `charset=utf-8` to text-ish content types missing it. This function is called from exactly two places: the trailing-slash → `index.html` branch and the final catch-all asset-fetch branch — meaning **every** static HTML/CSS/JS/image response passes through it. `/api/lead` responses use a **separate, smaller** header set defined in `leadResponse()` (line 138-148): `Cache-Control: no-store`, `X-Content-Type-Options: nosniff`, `Referrer-Policy: no-referrer` — deliberately excluding CSP/HSTS/Permissions-Policy/X-Frame-Options, which is defensible for a JSON API response that is never rendered as a framable/scriptable document (see §7).

**Confirmed**: HTTP→HTTPS enforcement is **not** implemented in `worker.js` at all — `http://jftagro.com/` returns a `301` before any Worker-authored redirect logic would apply, meaning this is a **Cloudflare zone-level (dashboard) setting**, not an application-level behavior. This is an important source distinction: if this protection were ever disabled, it would be a Cloudflare configuration change, not a code regression.

## 4. Production Header Inventory (Part 6) — LOCAL / BUNDLE / PRODUCTION all match

Fetched full, unfiltered response headers for the live homepage:

| Header | Value | Source |
|---|---|---|
| `Strict-Transport-Security` | `max-age=31536000; includeSubDomains` | `SECURITY_HEADERS` |
| `Content-Security-Policy` | (full policy, see §5) | `SECURITY_HEADERS` |
| `Cross-Origin-Opener-Policy` | `same-origin-allow-popups` | `SECURITY_HEADERS` |
| `Permissions-Policy` | `camera=(), microphone=(), geolocation=(), payment=(), usb=()` | `SECURITY_HEADERS` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` | `SECURITY_HEADERS` |
| `X-Content-Type-Options` | `nosniff` | `SECURITY_HEADERS` |
| `X-Frame-Options` | `SAMEORIGIN` | `SECURITY_HEADERS` |
| `Cache-Control` | `public, max-age=0, must-revalidate` | Cloudflare Assets binding default |
| `Server` | `cloudflare` | Cloudflare edge |
| `Report-To` / `Nel` | Cloudflare Network Error Logging | Cloudflare edge (automatic, not worker.js) |

**Not present**: `Cross-Origin-Resource-Policy`, `Cross-Origin-Embedder-Policy` — absent from `SECURITY_HEADERS` too, so this is consistent (not a discrepancy), and their absence is defensible: COEP/CORP are primarily relevant for cross-origin isolation (e.g. `SharedArrayBuffer` access), which this site does not use, and adding them without evidence of need risks breaking the legitimate cross-origin resources the CSP already explicitly allow-lists (Google Translate, GA4, Google Maps embed, external exchange-rate APIs).

An initial `grep -i` filter on the raw header dump appeared to miss several headers due to a display/matching artifact in the first pass; a full unfiltered fetch immediately after confirmed every header is genuinely present. This is noted transparently as a self-caught investigation error, not a finding about the site.

## 5. CSP Deep Audit (Parts 7-8)

Live CSP (verbatim, matches `worker.js` exactly, character-for-character):

```
default-src 'self'; script-src 'self' 'unsafe-inline' https://static.cloudflareinsights.com https://cdnjs.cloudflare.com https://cdn.jsdelivr.net https://translate.google.com https://translate.googleapis.com https://www.googletagmanager.com; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com https://cdnjs.cloudflare.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self' https://cloudflareinsights.com https://www.google-analytics.com https://region1.google-analytics.com https://www.googletagmanager.com https://www.google.com https://api.frankfurter.app https://api.exchangerate-api.com https://open.er-api.com https://ok.surf https://translate.googleapis.com https://translate.google.com; frame-src https://www.google.com https://maps.google.com; object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'self'
```

### CSP Functionality Matrix

| Resource | CSP source | Actual dependency (traced across Phases 6-17) | Required? | Risk | Change? |
|---|---|---|---|---|---|
| `'unsafe-inline'` (script-src) | script-src | Numerous inline `<script>` blocks throughout the static HTML (header/footer loaders, FAQ accordion, calculators, cookie consent) — the entire static-HTML architecture relies on inline scripts | Yes, structurally required by the current architecture | Medium (inline scripts are XSS-relevant if injection ever occurs elsewhere) | No — removing this would require a full architectural rewrite to nonce/hash-based CSP, explicitly out of scope for a hardening-only phase per Part 38 ("do not change CSP aggressively") |
| `static.cloudflareinsights.com` | script-src | Cloudflare's own RUM/analytics beacon (auto-injected by the platform) | Yes | Low | No |
| `cdnjs.cloudflare.com` | script-src, style-src, font-src | Font Awesome icons (used site-wide) | Yes | Low | No |
| `cdn.jsdelivr.net` | script-src | Confirmed used historically for a JS library dependency; not re-audited this phase (out of scope — no evidence of misuse) | Presumed yes | Low | No |
| `translate.google.com`, `translate.googleapis.com` | script-src, connect-src | Google Website Translate widget (locale-fallback UX) | Yes | Low | No |
| `www.googletagmanager.com` | script-src, connect-src | GA4's `gtag.js` loader — confirmed in Phase 15/16 as the site's only analytics platform | Yes | Low | No |
| `fonts.googleapis.com`, `fonts.gstatic.com` | style-src, font-src | Google Fonts (Merriweather/Montserrat/Lato, per the Phase 12 design-system audit) | Yes | Low | No |
| `www.google-analytics.com`, `region1.google-analytics.com`, `cloudflareinsights.com` | connect-src | GA4 event beacon endpoints | Yes | Low | No |
| `api.frankfurter.app`, `api.exchangerate-api.com`, `open.er-api.com`, `ok.surf` | connect-src | Live currency-rate feeds used by `quote-calculator.js`/`quote-market-rates.json` refresh logic | Yes | Low | No |
| `www.google.com`, `maps.google.com` | frame-src | Embedded Google Map on `contact.html` (confirmed in Phase 11 read of the map-tabs feature) | Yes | Low | No |
| `img-src 'self' data: https:` | img-src | Broad `https:` allowance for images — permissive but images are not an XSS/script-execution vector; `data:` is used for lazy-load placeholder GIFs (confirmed in Phase 10's category-page work) | Yes | Low (images cannot execute script under this CSP) | No |
| `object-src 'none'` | object-src | Correctly blocks Flash/plugin-style embeds entirely | N/A (restrictive) | N/A | No |
| `frame-ancestors 'self'` | frame-ancestors | Prevents the site from being framed by any other origin — this **is** the clickjacking protection (see §6) | Yes | N/A (restrictive) | No |

No CSP source was found that could not be traced to a real, current dependency. No `'unsafe-eval'`, no wildcard `*` in `script-src`/`connect-src`, no `localhost`/dev origins, no unnecessary protocol scheme. **Status: PASS.**

## 6. Clickjacking (Part 10)

`frame-ancestors 'self'` (CSP, the modern, authoritative mechanism) and `X-Frame-Options: SAMEORIGIN` (legacy fallback for older browsers that don't honor `frame-ancestors`) are both present and consistent — this is correct defense-in-depth, not redundant duplication, since the two mechanisms cover different browser generations. **Status: PASS.**

## 7. MIME / Content-Type (Part 11)

Verified live: CSS served as `text/css; charset=utf-8`, JS served as `text/javascript; charset=utf-8`, both with `X-Content-Type-Options: nosniff`. No MIME confusion found. **Status: PASS.**

## 8. Referrer-Policy / Permissions-Policy (Parts 12-13)

`strict-origin-when-cross-origin` is an appropriate, common default balancing analytics/referral usefulness against leaking full URLs (which could contain `?product=` context) to third-party origins — cross-origin requests only receive the origin, not the full path/query. `/api/lead` uses the stricter `no-referrer` — appropriate since that endpoint's own URL carries no sensitive query data, but being maximally conservative there is harmless and correct.

`Permissions-Policy` explicitly denies `camera`, `microphone`, `geolocation`, `payment`, `usb` — all capabilities the site never uses. It does not explicitly restrict `accelerometer`, `gyroscope`, `autoplay`, `fullscreen`, or a handful of newer policy-controlled features. This is a genuine, minor observation — **not escalated to a finding requiring a fix**, because (a) these features are already gated by other browser mechanisms and require additional user interaction regardless, (b) there is no evidence any of them are being exploited or are exploitable in this site's static architecture, and (c) Part 51's own instruction is to make zero changes when there is no proven defect. Documented as an optional, low-value future hardening item only (§13).

## 9. `/api/lead` — Critical Endpoint Audit (Parts 16-21)

**Architecture correction**: this endpoint is implemented directly in `worker.js` (not a separate, out-of-repository backend as Phases 15/16 assumed). It validates and sanitizes the submission, then forwards it to **Web3Forms** (`https://api.web3forms.com/submit`), a third-party transactional-email/form-relay API, using an access key read from the `WEB3FORMS_ACCESS_KEY` environment binding (a Cloudflare secret, not visible to this session — appropriately not committed to the repository).

All tests below were performed with safe, non-destructive probes; **no real lead was ever created** (every test payload was deliberately incomplete or invalid, causing rejection before the code path that would forward to Web3Forms):

| Test | Expected (from source) | Actual (production) | Result |
|---|---|---|---|
| `GET /api/lead` | 405 | `405 Method Not Allowed`, generic JSON body, no stack trace | PASS |
| `OPTIONS /api/lead` | 405 (no CORS preflight support) | `405`, same generic body | PASS — confirms no cross-origin `fetch()` with custom headers can ever succeed (fails at browser preflight) |
| `POST` with no `Origin` header | 403 | `{"success":false,"message":"Invalid submission origin"}` | PASS |
| `POST` with correct `Origin`, empty JSON `{}` | 400, missing email/phone | `{"success":false,"message":"Email or phone is required"}` | PASS |
| `POST` with honeypot field (`website`) filled | 400, automated rejection | `{"success":false,"message":"Automated submission rejected"}` | PASS |
| `POST` with malformed JSON | 400, generic | `{"success":false,"message":"Invalid form payload"}`, no parser stack trace | PASS |
| `PUT`/`DELETE`/`PATCH` on static routes (control test) | 405 | `405` on all three | PASS |

**CORS**: no `Access-Control-Allow-Origin` header is ever set on any `/api/lead` response — this is a safe-by-default posture (fails closed for cross-origin browser access) rather than a gap; combined with the Origin-header check inside the handler, casual cross-site form-submission attempts from a browser are blocked at two independent layers. **Note**: the in-handler Origin check can be trivially bypassed by a non-browser HTTP client (e.g. `curl -H "Origin: https://jftagro.com"`, as this session itself did for testing) — this is disclosed as an inherent limitation of Origin-header checking generally (it is a request-forgery mitigation for browser-based attacks, not an authentication mechanism), not a defect specific to this implementation; the endpoint's real defense against abuse by non-browser clients is the honeypot, payload-size limit, field validation, and optional Turnstile challenge, not the Origin check.

**PII exposure**: none. Every response body was inspected — only `success`, a generic `message` string, and an echoed `lead_id` (a client-generated correlation token, not server-asserted) are ever returned. No submitted field value is echoed back in any response.

**Rate limiting / abuse protection**: `verifyTurnstile()` is conditionally active — it only runs if `env.TURNSTILE_SECRET` is configured; otherwise it passes through unconditionally (`if (!env.TURNSTILE_SECRET) return true;`). **Whether `TURNSTILE_SECRET` is actually set in the live environment could not be determined from this session** (it is a Cloudflare secret, not visible via source or safe HTTP probing) — this is recorded as **UNKNOWN**, not assumed either way. Beyond Turnstile, the endpoint has: an 80-field/2000-char-per-value size cap, a 32KB total request-size cap, and the honeypot — a reasonable layered defense for a B2B lead form, though no confirmed Cloudflare-level rate-limiting rule was found or tested (testing one would require either dashboard access this session lacks, or sending enough real requests to trigger a limit, which risks disrupting the live service — explicitly avoided per Part 48's no-destructive-testing rule).

**Status: PASS**, with two items recorded as UNKNOWN (Turnstile secret configuration; presence of a dashboard-level rate-limit rule) rather than converted to an assumed PASS.

## 10. Sensitive File / Source Map Exposure (Parts 22-24)

Tested 14 common leak paths directly against production: `.env`, `.env.local`, `.dev.vars`, `.git/config`, `.git/HEAD`, `wrangler.toml`, `wrangler.jsonc`, `package.json`, `package-lock.json`, `README.md`, a `reports/` file, a `scripts/` file, `.claude/settings.json`, and two hypothetical `.map` files. **All 14 returned `404`.** The deployed bundle (`.cloudflare-dist`) was also confirmed to contain **zero** `.map` files. **Status: PASS.**

## 11. Path Normalization, Redirects, Error Handling (Parts 25-26, 30-33)

- `//`, `/./`, `/../`, `/%2e%2e/` all resolve safely — `/../`-style segments are normalized by JavaScript's `URL` parser (used throughout `worker.js`) before any pathname-based logic runs, and the only user-controlled input that touches file-path construction (`legacyProductRedirect`'s `product` query param) is regex-sanitized to `[a-z0-9-]` only, making path traversal structurally impossible in that code path.
- The 404 response is empty-bodied (`Content-Length: 0`) with the full standard security-header set still applied — no stack trace, no internal path, no directory listing.
- Two representative redirect classes were tested live and matched `worker.js`'s hardcoded maps exactly: a legacy pretty-URL product alias and a renamed-article redirect, both correctly `301` to their intended destination with no open-redirect behavior (every redirect target in `worker.js` is either a hardcoded relative path or a sanitized, existence-verified asset path — never a user-supplied absolute URL or protocol-relative string).
- **Status: PASS.**

## 12. Production / Bundle / Local Parity (Parts 28-29)

Direct byte-for-byte comparison of two representative files (`jft-conversion.js`, `trade-regions.css`) between live production and the local repository: **identical**. Local bundle file count (2,099, per `build_cloudflare_assets.py`) is consistent with Phase 17's own build. **Status: PASS — no stale deployment or parity gap found.**

## 13. Findings Summary

| ID | Severity | Area | Status |
|---|---|---|---|
| — | — | Security headers (all 7 checked) | PASS |
| — | — | CSP | PASS, fully traced to real dependencies |
| — | — | HTTPS/HSTS | PASS (HTTPS enforcement traced to Cloudflare zone level, not worker.js — documented distinction, not a defect) |
| — | — | Clickjacking | PASS |
| — | — | MIME/Content-Type | PASS |
| — | — | `/api/lead` (methods, CORS, validation, error handling, PII) | PASS |
| P18-INFO-1 | INFORMATIONAL | Permissions-Policy does not explicitly restrict `accelerometer`/`gyroscope`/`autoplay`/`fullscreen` | Not actionable — no evidence of exploitability or need; documented only |
| P18-UNK-1 | UNKNOWN | Whether `TURNSTILE_SECRET` is configured in the live environment | Cannot be determined from source or safe HTTP probing this session |
| P18-UNK-2 | UNKNOWN | Whether a Cloudflare-dashboard-level rate-limit rule protects `/api/lead` | Testing would require either dashboard access or risk disrupting the live service |
| — | — | Sensitive file / source map exposure | PASS (14/14 paths return 404, 0 map files in bundle) |
| — | — | Path normalization / open redirects | PASS |
| — | — | Production/bundle/local parity | PASS |

**No CRITICAL, HIGH, or MEDIUM severity finding was identified.** No finding met Part 36's fix-decision-gate criteria (which requires a proven defect as the first condition) — because no defect was proven. **Zero website source files were modified this phase.**
