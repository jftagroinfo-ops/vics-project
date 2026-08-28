# Phase 23 — Cloudflare Security Remediation & Final Production Re-Certification

Date: 2026-08-28
Status: Investigation and remediation attempt complete. **Zero website source files modified. Zero Cloudflare configuration modified (both remediation attempts confirmed blocked by permission scope, not silently skipped).**

## Part 1 — Baseline

| Item | Value |
|---|---|
| Git commit | `e64a3f2ba03c114a94ef61db20fbff486dab2a2b` (unchanged since Phase 1) |
| Git status at start | 1,181 paths |
| Stale build artifact present at start | No |
| Production | `https://jftagro.com/` — `HTTP 200` |
| Production sitemap URL count | 1,453 |
| Active Worker deployment | Version `2b63fb19-28c8-45ca-9fc8-3468fdd105eb`, created 2026-08-27T18:40:42Z, 100% traffic — unchanged since Phase 17, confirmed via `wrangler deployments status` |
| Current TLS behavior (pre-remediation) | TLS 1.0, 1.1, 1.2, 1.3 all accepted (per Phase 21/22, reconfirmed independently this phase) |
| Current `/api/lead` behavior | Unchanged from Phase 21/22 — POST-only, Origin allow-list, honeypot, 32KB/80-field caps, `no-store`, no PII echo |
| Current rate-limiting state | UNKNOWN per Phase 21/22 |
| Cloudflare permissions available | Same OAuth token as Phases 17-22, refreshed via `wrangler whoami` this phase; scopes unchanged (`zone:read`, `ssl_certs:write`, `workers:*`, and ~20 others — none covering Zone Settings or Firewall/Rulesets) |

## Part 2 — TLS (Objective A)

### A1 — Current configuration investigated

```
GET /zones/{zone_id}/settings/min_tls_version
→ {"success":false,"errors":[{"code":9109,"message":"Unauthorized to access requested resource"}]}
```

**Current Minimum TLS Version: could not be read via API this session** (confirmed by direct API call, not assumed). Behavioral evidence (handshake testing, below) is used as the authoritative substitute per the phase's own instruction that "the handshake behavior is the final authority."

**Configuration authority:** Cloudflare Zone → SSL/TLS → Edge Certificates → Minimum TLS Version. `.cloudflare/worker.js` was re-confirmed to have no code path affecting TLS negotiation — the handshake completes before any Worker code executes.

**Evidence:** direct OpenSSL negotiation (§A4) plus the API's own error response above.

### A2 — Target

TLS 1.2 minimum (TLS 1.0 and 1.1 disabled; TLS 1.2 and 1.3 remain enabled). No change to this target from Phase 21/22.

### A3 — Remediation attempted (not just re-read)

This phase went further than Phase 21/22 by attempting the actual write, not only reads, to obtain definitive evidence:

```
PATCH /zones/{zone_id}/settings/min_tls_version  body: {"value":"1.2"}
→ {"success":false,"errors":[{"code":9109,"message":"Unauthorized to access requested resource"}]}
```

Identical error to the read attempt. A sanity check (`GET /zones/{zone_id}`, plain zone metadata) succeeded with the same token in the same test run, proving the token is valid and current — the failure is specific to the **Zone Settings** permission group, which this token was never granted. **No privilege escalation, new token creation, or workaround was attempted, per Rule 4.**

**Exact permission required:** API Token/OAuth scope **Zone → Zone Settings → Edit**.
**Exact administrator action required:** Cloudflare dashboard → jftagro.com → SSL/TLS → Edge Certificates → set "Minimum TLS Version" to "TLS 1.2".

### A4 — Independent TLS verification (post-attempt, using OpenSSL — the handshake is the final authority)

| Protocol | Command | Result |
|---|---|---|
| TLS 1.3 | `openssl s_client -connect jftagro.com:443 -servername jftagro.com -tls1_3` | `Protocol: TLSv1.3` — succeeds |
| TLS 1.2 | `... -tls1_2` | `Protocol: TLSv1.2`, `ECDHE-ECDSA-CHACHA20-POLY1305` — succeeds |
| TLS 1.1 | `... -tls1_1 -cipher 'DEFAULT@SECLEVEL=0'` | `Protocol: TLSv1.1`, `ECDHE-RSA-AES128-SHA` — **still succeeds** |
| TLS 1.0 | `... -tls1 -cipher 'DEFAULT@SECLEVEL=0'` | `Protocol: TLSv1`, `ECDHE-RSA-AES128-SHA` — **still succeeds** |

Tested against both `https://jftagro.com/` (homepage) and `https://jftagro.com/api/lead` (forced TLS 1.1 connection, `GET /api/lead` returned `405` over the legacy-protocol connection, confirming the API endpoint is reachable over TLS 1.1 exactly like every other route).

**Result: unchanged from Phase 21/22, exactly as expected since the remediation attempt was confirmed blocked.** No fabricated success is claimed — the handshake evidence is definitive and matches the API's own rejection of the change.

## Part 3 — Rate Limiting (Objective B)

### B1 — Current state investigated, four distinct API surfaces tested

| Endpoint | Method | Result |
|---|---|---|
| `/zones/{id}/rate_limits` (legacy) | GET | `code 10000, "Authentication error"` |
| `/zones/{id}/rulesets/phases/http_ratelimit/entrypoint` (modern) | GET | `code 10000, "Authentication error"` |
| `/zones/{id}/rulesets` (modern, all) | GET | `code 10000, "Authentication error"` |
| `/zones/{id}/firewall/rules` (legacy WAF) | GET | `code 10000, "Authentication error"` |

**Existing rule: cannot be determined — read access blocked on every API surface tested.** No rule's scope, threshold, period, or action can be inspected from this session.

### B2 — Duplicate-rule avoidance

Not applicable — no existing rule could be read to check for duplication against, and (per B5) no new rule was created, so there is no possibility of a conflicting/duplicate rule having been introduced this phase.

### B3 — Existing application-level protections (re-confirmed unchanged, live-tested this phase)

Re-verified directly against production: `POST` with missing contact field → `400` generic message; honeypot field populated → `400 "Automated submission rejected"`; unsupported method (`GET`) → `405`; `Cache-Control: no-store` present on every response. All unchanged from Phase 21/22.

**Additional safe behavioral signal gathered this phase**: 5 rapid, honeypot-triggering (non-lead-creating) POST requests were sent in quick succession from this session's single test connection — all 5 returned an identical `400` with no `429`, no CAPTCHA/challenge interstitial, and no increasing latency. This is weak but genuine evidence that no aggressive, low-threshold (≤5 requests) rate-limit or bot-challenge is currently active for this exact request pattern — it does **not** prove no rate limit exists at a higher threshold, and is reported as exactly that limited a signal, not overstated.

### B4 — Is rate limiting actually required? (honest analysis, unchanged conclusion from Phase 22, now with one more data point)

Origin-header validation remains client-forgeable by non-browser scripts (not a cryptographic control); the honeypot stops only unsophisticated bots; no frequency-based throttling is confirmed to exist anywhere visible to this session. No positive evidence of actual abuse exists or is accessible to this session. This is a real, meaningful defense-in-depth gap, not a demonstrated active attack.

### B5 — Remediation attempted (write test, not only reads)

```
POST /zones/{id}/rate_limits   body: {"threshold":10,"period":60,"match":{"request":{"url":"jftagro.com/api/lead","methods":["POST"]}},"action":{"mode":"challenge","timeout":3600}}
→ {"success":false,"errors":[{"code":10000,"message":"Authentication error"}]}
```

Identical failure to the read attempts, confirming write access is equally blocked, not merely unread. **No rule was created. No production state was changed by this attempt** — the API rejected the request outright before any rule could be persisted.

### B6 — Documented, not pretended successful

| Item | Detail |
|---|---|
| State | UNKNOWN whether any Cloudflare dashboard-level rule already protects `/api/lead`; confirmed that no NEW rule was created this session |
| Reason | All 4 tested API surfaces (legacy rate-limits, modern rulesets, modern rulesets rate-limit phase, legacy firewall rules) fail identically with a permission-scope error on both read and write |
| Required permission | **Zone → Firewall Services → Edit** (or **Zone WAF → Edit**, depending on legacy vs. modern rule type) |
| Recommended rule scope | `http.request.uri.path eq "/api/lead" AND http.request.method eq "POST"` only |
| Recommended threshold | 10 requests per IP per 10 minutes, 1-hour temporary block (unchanged recommendation from Phase 22 — no new evidence this phase changes the appropriate threshold) |
| Verification method | After dashboard configuration, from a single test connection issue a small number of safe, honeypot-triggering POSTs and confirm the configured Nth request returns `429` |

## Part 4 — Security Regression (Objective D)

| Check | Result |
|---|---|
| Security headers (HSTS, CSP, COOP, Permissions-Policy, Referrer-Policy, X-Content-Type-Options, X-Frame-Options) | All 7 present, byte-identical to Phase 18-22's documented values |
| CSP | Unchanged string, no new origins, no relaxation |
| CORS | `/api/lead` OPTIONS still returns no `Access-Control-*` headers — unchanged |
| `/api/lead` validation | POST-only, honeypot, size/field caps, generic errors, no PII — all re-confirmed live this phase |
| Sensitive files | `/.env`, `/.git/config`, `/wrangler.jsonc`, `/reports/QA-CHANGE-CONTROL.md` — all `404` |
| Routing | Known page → `200`; unknown path → `404`; `www` → apex `301` — all unchanged |
| Cache | `/api/lead` → `Cache-Control: no-store`, reconfirmed |

**Zero drift detected anywhere.**

## Part 5 — Repository Integrity (Objective E/G)

- `git status --short`: **1,181 paths before, 1,181 paths after** the entire phase (a transient temporary file, `p23_audits.txt`, was created in the repository root during the audit run and deleted before this final count — confirmed via the matching before/after totals).
- **Changed source files: 0.**
- **Changed Cloudflare configuration: 0** (both attempted changes were rejected by the API before any state was persisted).
- Generated artifacts: `.cloudflare-dist-next` was rebuilt once via the existing, unmodified `scripts/build_cloudflare_assets.py` for the parity check below, then deleted immediately after — confirmed absent at the end of the phase.
- Build result: 2,099 public assets, 135.7 MiB — consistent with every prior phase's build output.

## Part 6 — Production Verification (Objective E, hash-based)

Computed SHA-256 hashes for 8 critical files across Repository, the freshly-rebuilt-then-deleted bundle, and live production:

| File | Result |
|---|---|
| `header.html` | ALL MATCH |
| `footer.html` | ALL MATCH |
| `jft-conversion.js` | ALL MATCH |
| `contact.html` | ALL MATCH |
| `locale-ui.js` | ALL MATCH |
| `sitemap.xml` | ALL MATCH |
| `rice-exporter-india.html` | ALL MATCH |
| `1121-basmati-rice-exporter.html` | ALL MATCH |

**All 8 files byte-identical across Repository → Bundle → Production. Zero mismatches.**

## Part 7 — Regression Suite (Objective F) — Full Current Script Inventory, Not Assumed Unchanged

The repository was checked fresh for its current audit/validation script inventory rather than assuming the 10-script set used in Phases 17-22 is still complete. **16 read-only audit/validation scripts were identified and run** (6 more than the previously-used set: `check_unused.py`, `validate_buyer_brief_cards.py`, `validate_editorial_governance.py`, `validate_localization_governance.py`, `validate_nested_component_pages.py`, `validate_seo_alignment.py`). Each was inspected for file-write operations before running (0 found in any) to confirm they are genuinely read-only.

| Script | Result | Exit code |
|---|---|---|
| `audit_website.py` | 0 findings, 1,753 pages | 0 |
| `audit_localizations.py` | 0 findings (locale counts are informational metadata) | 0 |
| `full_site_audit.py` | 0 findings, 1,453 indexable | 0 |
| `audit_performance.py` | 0 findings | 0 |
| `audit_coverage_gaps.py` | 0 findings (`finding_counts: {}`; locale counts are informational metadata) | 0 |
| `audit_commercial_content.py` | 0 findings, 84 product pages audited | 0 |
| `audit_claims_and_products.py` | 0 findings | 0 |
| `validate_blog_navigation.py` | Passed — 259 blog cards, 66 legacy redirects, 0 stale schema images | 0 |
| `audit_locale_ui.py` | 0 findings, determinism PASS | 0 |
| `check_links.py` | 0 broken links / 1,766 files | 0 |
| `check_unused.py` | **71 unused HTML/image files listed** — see note below | 0 |
| `validate_buyer_brief_cards.py` | Passed for 15 product pages | 0 |
| `validate_editorial_governance.py` | Passed — 4 editorial records, 0 approved / 4 gated (descriptive of pipeline state, not an error — see note below) | 0 |
| `validate_localization_governance.py` | Passed — 10 locale governance records, 0 approved / 10 gated (same as above) | 0 |
| `validate_nested_component_pages.py` | Passed for 2 pages | 0 |
| `validate_seo_alignment.py` | **FAILED — see note below** | **1** |

**15 of 16 scripts pass cleanly. `validate_seo_alignment.py` fails (exit code 1).**

### Note on `check_unused.py` (71 unused files, exit 0 — not a live-site defect)

The list includes files that are *expected* to be unreferenced by design: `blog-eu-mrl-basmati.html` and `blog-spice-trends-2026.html` are two of the deliberately-retired articles in `worker.js`'s `LEGACY_ARTICLE_REDIRECTS` map (visitors are 301-redirected before ever reaching these static files, so their being "unused" is the correct, intended state), and `product-page-template.html` is a generator template, not a live page. The remaining ~68 entries are `.webp`/`.jpg` image assets sitting in the repository without being referenced by any current HTML — this is repository housekeeping (unused disk space), not a production defect: an unreferenced image is never served to a visitor and has zero effect on production behavior, SEO, security, or conversion. **Classification: informational, repository hygiene only, explicitly out of Phase 23's Cloudflare-only scope.**

### Note on the two governance scripts (exit 0 — genuine passes, not failures)

Reading `scripts/validate_editorial_governance.py`'s source confirms its actual failure condition: it only returns a non-zero exit if an article makes an unsupported visible "reviewed by [named person]" claim without a matching `approved` record. The printed line `"Validated 4 editorial records; 0 approved, 4 gated"` is purely descriptive of the current editorial pipeline state (no article has yet completed a human review sign-off) — since the script returned exit `0`, this confirms the 4 gated articles correctly do **not** display any unsupported reviewer claim. `validate_localization_governance.py` follows the identical pattern for locale-content review claims. **Both are genuine PASSES; "gated" describes an editorial-workflow stage, not a defect.**

### Finding: `validate_seo_alignment.py` FAILS (exit code 1) — real, but explicitly OUT OF SCOPE for Phase 23

Full output: `Validated 926 FAQPage blocks and 83 cluster pages`, followed by ~34 lines of `Missing cluster link: <page> -> <target>`, the large majority reading `Missing cluster link: <product-page>.html -> sample-request.html` (30 product pages across pulses, oilseeds, flour, and several spice categories), plus 4 lines specific to `certificates.html` (missing links to a blog article, `buyer-security.html`, `export-documentation.html`, and a "documentation-center" link).

**This is a genuine, currently-failing validation** — not a false positive, not a stale-artifact issue (no `.cloudflare-dist` was present during the run), and not something introduced by any action taken in this phase (zero website files were modified in Phases 17-23; this script was simply never run as part of the regression set those phases used). **This finding is explicitly NOT addressed in Phase 23**, per the Critical Fix Decision Gate's own condition 10 ("Is it within this phase's explicit scope?") — internal content linking between product pages and the sample-request conversion flow is an SEO/content/conversion matter, not Cloudflare configuration, TLS, or rate limiting, and Phase 23's rules explicitly forbid HTML/content changes outside proven Cloudflare-driven necessity. **Recommended for a dedicated future phase** (out of scope to start here) that can properly investigate root cause (why these ~30 pages lack the link the site's own content-cluster validator expects), assess actual conversion impact, and apply the smallest safe fix under that phase's own change-control gate.

## Part 8 — Risk Register

| ID | Finding | Status | Evidence |
|---|---|---|---|
| P23-R1 (=P22-R1=P21-R1) | TLS 1.0/1.1 accepted alongside 1.2/1.3 | **MEDIUM, UNRESOLVED** | Direct OpenSSL handshake test, both before and after a genuine (blocked) remediation attempt |
| P23-R2 (=P22-R2=P19-R2) | Rate-limiting status for `/api/lead` | **UNKNOWN, UNRESOLVED** | 4 distinct API surfaces tested (read + write), all blocked identically |
| P23-R3 (=P22-R3=P19-R1) | `TURNSTILE_SECRET` not configured | **LOW-MEDIUM, OUT OF SCOPE (by design, per Rule 5)** | Unchanged from Phase 22; deliberately preserved per this phase's explicit instruction |
| P23-R4 (new, incidental) | `validate_seo_alignment.py` fails — ~30 product pages + `certificates.html` missing expected internal cluster links (mostly to `sample-request.html`) | **MEDIUM (content/conversion), OUT OF SCOPE for Phase 23** | `python scripts/validate_seo_alignment.py`, exit code 1, full output captured |
| P23-INFO-1 (new, incidental) | 71 unused HTML/image files in repository | **INFORMATIONAL** | `check_unused.py`, exit 0; several entries are expected-unused-by-design (retired articles, template file) |
| P18-INFO-1 | Permissions-Policy scope incomplete | **INFORMATIONAL** | Unchanged |
| P20-R1 | Category pages (Phase 10) not localized | **LOW, OUT OF SCOPE** | Unchanged, reconfirmed correct in Phase 22 |

**No CRITICAL or HIGH severity item exists. Zero items were converted from UNKNOWN to a false PASS, and zero were downgraded without evidence.**

## Stop

Per Phase 23's explicit instruction: **STOP. Do not begin Phase 24.**
