# Phase 21 — Production Security Hardening & Edge Protection Audit

Date: 2026-08-28
Status: Investigation complete. **Zero website source files modified.** This is the pre-implementation investigation report required by §23 — since the Fix Decision Gate (§22) was not satisfied by any candidate finding, no implementation report was needed.

## 1. Purpose

Phase 21 is a strict, narrowly-scoped security-hardening phase: `/api/lead` protection, Cloudflare edge protection, and TLS/security verification only. It builds directly on Phase 18 (initial security audit) and Phase 19 (closure of two UNKNOWNs, one of which — Cloudflare API rate-limit/rulesets access — remained genuinely unresolved). This phase re-verifies every claim against current production and repository state rather than assuming prior reports remain accurate, and attempts to close the TLS UNKNOWN using tooling not available in prior phases.

## 2. Baseline (frozen before any testing)

| Item | Value |
|---|---|
| Git commit | `e64a3f2ba03c114a94ef61db20fbff486dab2a2b` (unchanged since Phase 1) |
| Git status (working tree) | 1,177 paths (consistent with cumulative uncommitted Phases 1-20 work) |
| Stale build artifact present | No (`.cloudflare-dist` / `.cloudflare-dist-next` both absent) |
| Production homepage | `https://jftagro.com/` — `HTTP 200` |
| Production sitemap URL count | 1,453 (matches repository exactly) |
| `.cloudflare/worker.js` | Read in full; byte-for-byte unchanged from the version documented in Phase 18/19 (`SECURITY_HEADERS`, `handleLead`, `verifyTurnstile`, redirect maps all identical) |
| `wrangler.jsonc` | Read in full; unchanged — `main: ./.cloudflare/worker.js`, `assets.directory: ./.cloudflare-dist`, no KV/Durable Object/rate-limiting bindings configured |
| Configured secrets (`wrangler secret list`) | Only `WEB3FORMS_ACCESS_KEY` — `TURNSTILE_SECRET` still not set (re-confirmed) |

This is the exact state all findings below are measured against.

## 3. `/api/lead` — Deep Security Verification (highest priority)

All tests below are safe, non-destructive, synthetic requests that either fail validation before reaching Web3Forms or use a HEAD/method probe. **No real lead was created; no real PII was submitted.**

| Test | Expected | Observed | Result |
|---|---|---|---|
| `GET /api/lead` | 405 | `405 Method Not Allowed` | PASS |
| `PUT /api/lead` | 405 | `405` | PASS |
| `PATCH /api/lead` | 405 | `405` | PASS |
| `DELETE /api/lead` | 405 | `405` | PASS |
| `HEAD /api/lead` | 405 | `405` (see note below) | PASS |
| `OPTIONS /api/lead` with CORS preflight headers | 405, no CORS preflight support | `405`, zero `Access-Control-*` headers returned | PASS — confirms Origin-header validation, not CORS, is the actual authorization boundary (by design, re-confirmed) |
| `TRACE /api/lead` (and site-wide) | rejected | `405` | PASS |
| Empty POST body, correct Origin, no Content-Type | 400, generic message | `{"success":false,"message":"Invalid form payload"}` / `400` | PASS — no stack trace, no internal detail |
| No `Origin` header | 403 | `{"success":false,"message":"Invalid submission origin"}` / `403` | PASS |
| Wrong `Origin` (`https://evil.example.com`) | 403 | `403`, identical message | PASS |
| Malformed `Origin` (no scheme) | 403 | `403` | PASS |
| `Origin: null` | 403 | `403` | PASS |
| `Origin: https://www.jftagro.com` (should be allowed by code) | passes origin check, continues to next validation | `400 "Automated submission rejected"` (honeypot-adjacent test payload) — confirms `www` origin is correctly accepted, request proceeded past the origin gate | PASS |
| Honeypot field (`website`) populated | 400, rejected as automated | `{"success":false,"message":"Automated submission rejected"}` / `400` | PASS |
| Malformed JSON body | 400, generic message | `{"success":false,"message":"Invalid form payload"}` / `400` | PASS |
| Payload with 90 fields (limit is 80) | 400 | `400 "Invalid form payload"` | PASS — field-count cap enforced |
| Body >32KB (actual ~40KB body, not just a spoofed header) | 413 | `{"success":false,"message":"Submission is too large"}` / `413` | PASS |
| `Content-Type: text/plain` with form-style body | 400 (unparseable by `request.formData()`) | `400 "Invalid form payload"` | PASS |
| Missing `email`/`phone`/`whatsapp` entirely | 400 | `{"success":false,"message":"Email or phone is required"}` / `400` | PASS |

**No PII was echoed back in any response.** No stack traces, no internal error detail, no upstream Web3Forms credentials exposed in any tested path. Cache-Control on every `/api/lead` response observed: `no-store` — confirmed no edge-caching risk for a PII-bearing endpoint.

**Note on `HEAD`:** an initial test using default curl/keep-alive settings appeared to hang indefinitely. Root-caused: this is a client-side artifact of this Windows session's `schannel` curl backend mis-handling connection reuse after a HEAD response with a JSON `Content-Type` but no body — confirmed by retesting with `Connection: close`, which returned `405` in under 1 second with all expected headers present. This is the same class of tooling limitation already disclosed in Phase 19 (§17, schannel TLS-detail limitation) — **not a server-side defect**, and is documented here rather than silently worked around, per the phase's investigation-first rule.

## 4. Turnstile — Re-Verified, Not Assumed

- `wrangler secret list` (fresh call, this phase): only `WEB3FORMS_ACCESS_KEY` configured. **`TURNSTILE_SECRET` remains absent.**
- Frontend check: `grep -n "turnstile"` across `contact.html` and `sample-request.js` returns **zero matches** — no Turnstile widget script, no site-key reference, no hidden `cf-turnstile-response` field anywhere in the current frontend. Turnstile is not partially wired up; it is completely absent on both sides.
- `verifyTurnstile()` in `worker.js` (line 158): `if (!env.TURNSTILE_SECRET) return true;` — confirmed unconditional no-op, unchanged from Phase 19.
- **Per this phase's explicit instruction not to add Turnstile reflexively**: implementing it end-to-end requires first creating a Turnstile widget in the Cloudflare dashboard to obtain a site key and secret — an action this session has no API pathway to perform (Turnstile widget creation is a dashboard-only or a separate Turnstile-specific API requiring its own token scope, distinct from anything available here). Even if a secret existed, wiring the frontend widget into `contact.html` (11 language copies) and `sample-request.js` is itself a multi-file, user-facing UX change requiring its own review — not a "smallest safe fix" candidate for this phase. **Disposition: confirmed absent, not implemented this phase, unchanged from Phase 19's classification (LOW-MEDIUM, business decision required).**

## 5. Rate Limiting — Re-Attempted, Still Genuinely UNKNOWN

- Refreshed the session's Cloudflare OAuth token via `wrangler whoami` (the previous token had expired) to rule out "expired token" as the cause of Phase 19's failure.
- Re-attempted `GET /zones/{zone_id}/rate_limits` and `GET /zones/{zone_id}/rulesets` with the freshly-refreshed token.
- **Result: identical failure** — `{"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}` for both.
- Sanity check: `GET /zones/{zone_id}` (plain zone read) with the same token **succeeded**, proving the token itself is valid and the failure is specifically a missing permission scope for the firewall/rate-limiting resource group, not an expired or malformed token.
- **Conclusion: genuinely re-confirmed UNKNOWN**, with fresher and more conclusive evidence than Phase 19 (which could not rule out token expiry as a contributing factor). This is not a new gap — it is the same gap, now backed by cleaner evidence.

## 6. TLS/SSL — RESOLVED (upgraded from Phase 19's UNKNOWN)

Phase 19 could not determine TLS details because this session's `curl` used Windows' `schannel` backend. This phase found a genuine OpenSSL 3.5.5 binary available via Git Bash (`mingw64`), enabling real, authoritative TLS testing for the first time.

| Test | Result |
|---|---|
| Default negotiation | `TLSv1.3`, cipher `TLS_AES_256_GCM_SHA384` |
| Forced `-tls1_3` | Succeeds — `TLSv1.3` |
| Forced `-tls1_2` | Succeeds — `TLSv1.2`, `ECDHE-ECDSA-CHACHA20-POLY1305` |
| Forced `-tls1_1` (with `-cipher DEFAULT@SECLEVEL=0` to bypass OpenSSL 3.x's own default restriction on offering legacy protocols) | **Succeeds** — full handshake completed, `Protocol: TLSv1.1`, `Cipher: ECDHE-RSA-AES128-SHA` |
| Forced `-tls1` (TLS 1.0) | **Succeeds** — full handshake completed, `Protocol: TLSv1`, `Cipher: ECDHE-RSA-AES128-SHA` |
| Control test: `tls-v1-0.badssl.com` (a host known to only support TLS 1.0) with the identical `SECLEVEL=0` flag | Succeeds, confirming this OpenSSL configuration **can** genuinely negotiate legacy TLS versions when a server offers them — ruling out "client-side restriction" as an explanation for jftagro.com's TLS 1.0/1.1 acceptance |

**Finding, MEDIUM severity, confirmed (not a guess, not an artifact):** production `jftagro.com` currently accepts TLS 1.0 and TLS 1.1 in addition to TLS 1.2/1.3. TLS 1.0/1.1 were formally deprecated by the IETF in 2021 (RFC 8996) and have been disabled by default in all major browsers since ~2020, so no legitimate modern browser visitor is exposed — the practical risk is limited to unusual/legacy clients (old bots, old corporate proxies) that could still negotiate a weaker protocol, and to compliance posture (PCI-DSS has required TLS 1.2+ since 2018) rather than a demonstrated active exploit against Cloudflare's TLS 1.0/1.1 implementation specifically.

**Remediation path**: this is a Cloudflare **zone-level** setting (`SSL/TLS → Edge Certificates → Minimum TLS Version`), not a `worker.js` code change. Attempted to read/set it via the Cloudflare API (`GET /zones/{zone_id}/settings/min_tls_version` and `/settings/tls_1_3`) using the same freshly-refreshed OAuth token — **both calls failed** with `{"success":false,"errors":[{"code":9109,"message":"Unauthorized to access requested resource"}]}`, a distinct error code from the rate-limiting failure, confirming this specific permission (Zone Settings) is also outside the current token's granted scope. **This finding cannot be remediated from within this session** — it requires either direct Cloudflare dashboard access or an API token with the Zone Settings Edit permission, neither of which this session has or should request.

**Classification: CONFIRMED, MEDIUM severity, remediation requires Cloudflare dashboard access outside this session's scope.** Not implemented this phase; not converted to a false PASS or silently dropped.

## 7. Security Headers — Broadened Verification

Tested across: homepage, a category page (via `quote-calculator.html`), a 404 page, and the `ar/` locale homepage (via its 301→200 redirect chain).

- **404 pages carry the full `SECURITY_HEADERS` set** — confirmed via `withSecurityHeaders()` wrapping every `env.ASSETS.fetch()` response regardless of status code. This is a positive finding: even error pages are protected, not just 200 responses.
- **301 redirect responses (e.g., `/index.html` normalization, `www`→apex) carry minimal headers** (no CSP, no HSTS in the redirect response itself) — this is expected and not a finding: a 301 with an empty body and a `Location` header has no content to protect, and the eventual 200 response (which the browser follows to) carries the full header set, confirmed by testing the resolved URL directly.
- All previously-documented headers (`Strict-Transport-Security`, `Content-Security-Policy`, `X-Content-Type-Options`, `Referrer-Policy`, `Permissions-Policy`, `Cross-Origin-Opener-Policy`, `X-Frame-Options`) remain present and byte-identical to `worker.js`'s `SECURITY_HEADERS` object across every page type tested. **Zero drift from Phase 18/19.**

## 8. CSP Deep Audit

Mapped every external origin permitted in the live CSP against actual site usage (`grep -rl` across all HTML/JS source):

| Origin | Files referencing it | Assessed use |
|---|---|---|
| `static.cloudflareinsights.com` | 1,033 | Cloudflare Web Analytics/RUM beacon |
| `cdnjs.cloudflare.com` | 1,033 | Font Awesome / shared library CDN |
| `cdn.jsdelivr.net` | 990 | Shared JS library CDN |
| `translate.google.com` / `translate.googleapis.com` | 990 each | Google Translate widget |
| `www.googletagmanager.com` | 1,035 | GA4 (`G-MWZ2ZWZP4G`) |
| `fonts.googleapis.com` / `fonts.gstatic.com` | 1,435 / 1,044 | Web fonts |
| `www.google-analytics.com` / `region1.google-analytics.com` | 1,033 each | GA4 data collection |
| `www.google.com` / `maps.google.com` | 1,033 / 1,001 | reCAPTCHA-adjacent Google services / embedded maps |
| `api.frankfurter.app`, `api.exchangerate-api.com`, `open.er-api.com`, `ok.surf` | 1,023-1,034 | Currency-conversion widgets (multiple fallback providers) |

**Every single allowed origin is actively referenced across hundreds to 1,400+ pages — zero stale or unused CSP allowances found.** No directive was removed or narrowed. Per this phase's explicit instruction, **no attempt was made to eliminate `'unsafe-inline'`** — the static-HTML architecture's inline `<script>`/`<style>` usage (confirmed extensively in Phase 18) is a legitimate structural dependency, not an oversight, and removing it without a nonce/hash migration plan would break the site.

## 9. CORS Behavior

`OPTIONS /api/lead` with a full preflight header set (`Origin`, `Access-Control-Request-Method`, `Access-Control-Request-Headers`) returns `405` with **zero `Access-Control-*` response headers**. This means:

- Browsers cannot successfully complete a cross-origin `fetch()`/XHR to `/api/lead` that would require a CORS preflight (e.g., `Content-Type: application/json`) — the preflight itself fails.
- A simple cross-origin form POST (which doesn't trigger a preflight) could still reach the Worker, but the Worker's own `Origin` header check (§3) rejects any origin other than `https://jftagro.com`/`https://www.jftagro.com` before any data is forwarded to Web3Forms.
- **Confirmed, consistent with Phase 18/19's documented conclusion: Origin-header validation, not CORS, is the deliberate security boundary here.** CORS is correctly understood as a browser-only mitigation, not an authentication mechanism — no change made, per this phase's explicit instruction not to "fix" a non-browser bypass by tightening CORS alone.

## 10. Static File / Sensitive-Path Exposure

Tested directly against production (not inferred from source):

| Path | Result |
|---|---|
| `/.env`, `/.dev.vars`, `/.git/config`, `/.gitignore` | 404 |
| `/scripts/audit_website.py` | 404 |
| `/reports/QA-CHANGE-CONTROL.md`, `/reports/phase19-*.json` | 404 |
| `/wrangler.jsonc`, `/.cloudflare/worker.js` | 404 |
| `/data/localized-copy-cache.json` | 404 |
| `/package.json`, `/node_modules/`, `/.wrangler/` | 404 |

**Zero sensitive files exposed.** All 13 tested paths return 404, consistent with Phase 18/19's findings — no regression.

## 11. Worker Routing / Path Normalization

| Test | Result |
|---|---|
| `/..%2f..%2f..%2fetc%2fpasswd` | 400 (rejected at Cloudflare edge before reaching Worker logic) |
| `/....//....//etc/passwd`, `/%2e%2e/%2e%2e/wrangler.jsonc` | 404 |
| `//api/lead` (double slash) | 404 (not normalized to `/api/lead` — safe fail-closed, not a bypass) |
| `/api/lead/../lead` | 405 (correctly normalizes to `/api/lead`, then correctly rejects GET) — confirms path normalization does not create a routing bypass |
| `/api/lead%20`, `/API/LEAD` | 404 (case-sensitive, exact-match only — no case-insensitive or trailing-space bypass) |
| `/index.html%00.jpg` (null-byte injection attempt) | 400 |
| `/1121-basmati-rice-exporter.html/` (trailing slash on a file) | 404 |
| `Host: evil.com` header with correct SNI | **403 Forbidden at the Cloudflare edge**, before reaching the Worker — confirms Cloudflare's own host-validation rejects Host-header mismatches |
| `TRACE` method (site-wide) | 405 |
| `POST /index.html` (unexpected method on a static asset) | 301 (harmless — static assets are read-only; no mutation is possible regardless of method) |
| `www.jftagro.com` → apex redirect | 301, `Location: https://jftagro.com/` |
| `http://` → `https://` redirect | 301 |

**No path traversal, no open redirect, no origin confusion, no host-header bypass found.** All routing behavior matches `worker.js`'s documented logic exactly.

## 12. Cache Behavior

- `/api/lead`: `Cache-Control: no-store` confirmed on the error-path response tested this phase (consistent with Phase 19's finding that this applies to all `/api/lead` responses, success or failure) — no PII-cacheability risk.
- Static HTML/CSS/images: not re-tested in full this phase (Phase 19 already confirmed `HIT`/`must-revalidate` and long-cache-with-revalidation patterns, both correct); no code affecting caching was touched, so no drift is possible.

## 13. Web3Forms Upstream Handling

Re-traced (not re-tested against the live upstream, to avoid creating real submissions): `handleLead()` forwards a sanitized, allow-listed field set to `https://api.web3forms.com/submit` via server-side `fetch()`, attaching `env.WEB3FORMS_ACCESS_KEY` (never exposed to the client), and returns only a boolean `success` flag plus a generic message to the browser — never the upstream's raw response body, never the access key, never internal error detail. Unchanged from Phase 18's trace; no new testing needed since no code changed.

## 14. security.txt / DNS / Host Security

- `https://jftagro.com/.well-known/security.txt`: confirmed live, well-formed, unchanged (`Contact: mailto:jftagro.info@gmail.com`, `Policy: /privacy.html`, `Expires: 2027-08-10`).
- `www` → apex and HTTP → HTTPS redirects both correctly return `301`.
- Host-header mismatch correctly rejected at the Cloudflare edge (§11) — no DNS changes made or needed; this is audit-only per the phase's explicit instruction.

## 15. Third-Party Dependency Risk

Covered fully by §8's CSP-origin usage mapping — every external dependency (GA4, Google Fonts, Font Awesome/jsDelivr, Google Translate, Google Maps, Cloudflare Insights, three currency-API fallback providers) is actively used across the majority of the site's pages. No dependency was found to be safely removable, and none was removed.

## 16. Findings Summary by Classification

| Finding | Classification |
|---|---|
| TLS 1.0/1.1 accepted alongside 1.2/1.3 | **TRUE SECURITY ISSUE (MEDIUM)** — confirmed, cannot be fixed within this session (zone-level, requires dashboard/API-scope access this session lacks) |
| `TURNSTILE_SECRET` not configured, no frontend widget | **CONFIGURATION GAP (LOW-MEDIUM)** — confirmed unchanged from Phase 19, requires new dashboard-created resource, not implementable this session |
| Cloudflare rate-limit/ruleset status for `/api/lead` | **UNKNOWN** — genuinely re-attempted with a freshly-verified-valid token, still access-scope-limited |
| `/api/lead` method/CORS/Origin/payload/honeypot handling | **PASS** — every tested vector behaves exactly as designed, zero bypass found |
| Security headers (all page types, including 404) | **PASS** — zero drift from Phase 18/19 |
| CSP directive/origin set | **PASS** — every allowed origin actively used, no stale entries, no unjustified rewrite attempted |
| Static file / sensitive-path exposure | **PASS** — 13/13 tested paths return 404 |
| Worker routing / path normalization / Host-header handling | **PASS** — no traversal, no bypass, no open redirect |
| Cache behavior for `/api/lead` | **PASS** — `no-store` confirmed |
| `HEAD /api/lead` apparent hang | **FALSE POSITIVE / TOOLING ARTIFACT** — root-caused to this session's Windows `schannel` curl backend, not a server defect; confirmed via `Connection: close` retest |
| Permissions-Policy scope (accelerometer/gyroscope/autoplay/fullscreen) | **INFORMATIONAL** — carried forward unchanged from Phase 18, no new evidence of exploitability |

## 17. Fix Decision Gate — Applied to Every Candidate

| Candidate | Gate result |
|---|---|
| TLS 1.0/1.1 acceptance | Fails gate condition "fix within session's access" — remediation is a Cloudflare zone setting, and both dashboard access and the required API permission scope are unavailable this session. **DO NOT FIX. Document.** |
| Turnstile absence | Fails gate condition "fix is compatible with current architecture achievable now" — requires a new dashboard-created Turnstile widget (site key + secret) that cannot be obtained via any access this session has, plus a multi-file frontend change beyond a minimal patch. **DO NOT FIX. Document.** |
| Rate limiting (Worker-level mitigation as a substitute) | Fails gate condition "root cause proven" — rate-limiting status is UNKNOWN, not confirmed absent; adding a new Worker-level throttle would require new infrastructure (KV/Durable Object — none currently bound in `wrangler.jsonc`) with no confirmed abuse problem to justify it, and real risk of false-positives against legitimate shared-IP/corporate/mobile buyers. **DO NOT FIX. Document.** |

**No candidate finding satisfied all 10 gate conditions. Zero website source files were modified this phase.**

## 18. Regression / Change Diff Discipline

- `git status --short` before and after this phase's entire investigation: **1,177 paths, unchanged** — confirms zero files were created, modified, or deleted.
- No `.cloudflare-dist`/`.cloudflare-dist-next` artifact was created or left behind.
- Per §32's instruction, there is no diff to justify file-by-file since no website file changed.

## 19. Remaining Risk Register (final for this phase)

| ID | Item | Severity | Status |
|---|---|---|---|
| P21-R1 | TLS 1.0/1.1 accepted alongside 1.2/1.3 | **MEDIUM** | Confirmed with direct evidence this phase (upgraded from Phase 19's UNKNOWN); remediation requires Cloudflare dashboard/API-scope access outside this session |
| P19-R1 | `TURNSTILE_SECRET` not configured, no frontend widget | LOW-MEDIUM | Re-confirmed unchanged; business decision + dashboard resource creation required |
| P19-R2 | Cloudflare rate-limit/ruleset status for `/api/lead` | UNKNOWN | Re-attempted with a verified-fresh token this phase; genuinely still inaccessible |
| P18-INFO-1 | Permissions-Policy scope (accelerometer/gyroscope/autoplay/fullscreen not explicitly restricted) | INFORMATIONAL | Unchanged, not actionable |
| P19-R4 | Audit scripts lack build-artifact directory exclusion | LOW (tooling only) | Did not recur this phase (no artifact present) |
| P20-R1 | Category pages (Phase 10) not localized | LOW (scope/completeness, not security) | Unchanged, out of this phase's security-only scope |

**No CRITICAL or HIGH severity item found or exists in the register.**

## 20. Recommendation

The site's code-layer security posture (Worker routing, `/api/lead` validation, security headers, CSP) is thorough and shows zero exploitable defects across two full dedicated security phases (18, 21) plus Phase 19's closure work. The three items that remain (TLS minimum version, Turnstile, rate-limiting confirmation) are **all zone/dashboard-level items outside this session's access**, not code defects — they should be addressed directly in the Cloudflare dashboard at the business's convenience:

1. **Set minimum TLS version to 1.2** (`SSL/TLS → Edge Certificates → Minimum TLS Version`) — a single dashboard toggle, no code change required, no legitimate visitor impact (modern browsers already default to 1.2/1.3).
2. **Confirm or create a rate-limiting rule for `/api/lead`** in the dashboard's WAF/Rate Limiting section.
3. **Decide whether to enable Turnstile** — if yes, create a Turnstile widget in the dashboard first (obtaining a site key + secret), then a small, separately-scoped follow-up phase can wire the frontend widget and `TURNSTILE_SECRET` into the existing (already-correct) `verifyTurnstile()` code path.

## 21. Stop

Per Phase 21's explicit instruction: **STOP. Do not begin Phase 22.**
