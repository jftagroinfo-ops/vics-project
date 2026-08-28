# Phase 19 — Production Security Closure & Final Release Certification

Date: 2026-08-28
Status: Verification complete. **Zero website source files modified.** Final certification issued below.

## 1. Purpose

Close out the two UNKNOWN items left open by Phase 18, broaden production verification beyond the homepage, re-run the complete regression suite, perform a final live crawl, and issue a hard release-certification decision — not another open-ended audit.

## 2. Phase-18 UNKNOWN #1 — RESOLVED

**Question**: is `TURNSTILE_SECRET` configured in the live environment?

**Method**: `npx wrangler secret list` against the authenticated Cloudflare account — this lists secret *names* only, never values, and is a safe, read-only, legitimate verification method.

**Result**: only one secret is configured for the Worker: `WEB3FORMS_ACCESS_KEY`. **`TURNSTILE_SECRET` is not set.**

**Consequence, traced precisely from `worker.js`**: `verifyTurnstile()`'s guard (`if (!env.TURNSTILE_SECRET) return true;`) means Turnstile verification is currently a **no-op** — `/api/lead` accepts submissions with no CAPTCHA/challenge check at all. This is now a **confirmed fact, not a hypothesis**, and is escalated from Phase 18's UNKNOWN into a real, evidenced finding (§6).

## 3. Phase-18 UNKNOWN #2 — REMAINS UNKNOWN (genuinely, after a real attempt)

**Question**: does a Cloudflare dashboard-level rate-limiting rule protect `/api/lead`?

**Method attempted**: a direct, read-only call to the Cloudflare API (`GET /zones/{zone_id}/rate_limits` and `GET /zones/{zone_id}/rulesets`) using this session's existing, already-authenticated OAuth token (the same one `wrangler` uses).

**Result**: both calls returned `"Authentication error"` (Cloudflare error code 10000) — the token's scope list (`user:read, account:read, workers:*, zone:read, ssl_certs:write, ...`) does not include the firewall/rulesets/rate-limiting permission Cloudflare requires for this resource. The zone lookup itself succeeded (confirming the token and zone ID are valid), isolating the failure specifically to insufficient permission scope for this one resource type.

**Conclusion**: this remains **UNKNOWN**, but it is now an *evidenced* UNKNOWN (a genuine access-scope limitation, confirmed by a real failed API call) rather than an unattempted one. Resolving it would require either broader API token permissions or direct Cloudflare dashboard access, neither of which this session has or should request per Phase 18/19's own "do not ask for credentials" rule.

## 4. Broadened Production Header Verification

Fetched full response headers from 6 additional representative URLs beyond the homepage (a category page, a product page, an article, the quote calculator, the Arabic homepage, and a Thai contact page). **All 6 returned identical CSP and security-header values**, byte-for-byte matching the homepage and `worker.js`'s `SECURITY_HEADERS` — confirming uniform application across page types and all tested locales, not just the homepage. **Status: PASS.**

## 5. Cache Behavior Verification (production)

| Resource type | `CF-Cache-Status` | `Cache-Control` | Assessment |
|---|---|---|---|
| HTML (homepage) | `HIT` | `public, max-age=0, must-revalidate` | Edge-cached but always revalidated by browsers — correct |
| CSS | `HIT` | `public, max-age=0, must-revalidate` | Same pattern |
| Image | `HIT` | `public, max-age=604800, stale-while-revalidate=86400` | Long browser cache, appropriate for static public images |
| `/api/lead` | **not present** (not cached at edge) | `no-store` | Correct — confirms no PII-containing response can ever be publicly cached |

**Status: PASS.**

## 6. TLS/SSL — Disclosed Tooling Limitation

Attempted to verify negotiated TLS version and certificate details via `curl -v`. This environment's curl uses Windows' native **schannel** backend rather than OpenSSL, which does not print negotiated-protocol or certificate-subject details the way OpenSSL-backed curl does. Forcing `--tlsv1.0 --tls-max 1.0` returned `200`, but this cannot be trusted as proof the server accepts legacy TLS 1.0 — schannel's handling of these flags is not verified reliable in this environment, and a false "success" reading is a plausible tooling artifact rather than a confirmed server behavior. `ssl_verify_result: 0` (certificate validation passed) is the one TLS-related fact this session can state with confidence. **TLS version enforcement is a Cloudflare zone-level setting, not observable with confidence via this session's tooling — recommend confirming directly via the Cloudflare dashboard's SSL/TLS minimum-version setting, or an external tool such as SSL Labs, outside this session's capability. Classification: UNKNOWN (tooling-limited), not converted to PASS.**

## 7. `security.txt` / `robots.txt` / `sitemap.xml` Exposure

- `https://jftagro.com/.well-known/security.txt`: **exists, HTTP 200**, well-formed (`Contact`, `Canonical`, `Preferred-Languages`, `Policy`, `Expires: 2027-08-10`) — a genuinely good practice already in place, not a finding.
- `robots.txt`: re-confirmed (already checked in Phase 16/17) — correctly excludes `/scripts/`, `/reports/`, and internal tooling filenames.
- `sitemap.xml`: **1,453 URLs**, exactly matching the Phase 17 release and the local repository.

**Status: PASS.**

## 8. `/api/lead` — Final Safe Re-Verification

No new probes were run this phase beyond Phase 18's 7-test suite (already thorough and conclusive) — re-running identical safe tests would add no new evidence. The one substantive addition this phase is §2's Turnstile-secret confirmation, which changes the *classification* of the endpoint's abuse-resistance (see §6 risk register) without requiring any new HTTP testing.

## 9. Complete Regression Suite — Re-Run Fresh This Phase

| Script | Result |
|---|---|
| `audit_website.py` | 0 findings (1,753 pages — see note below) |
| `audit_localizations.py` | 0 findings |
| `full_site_audit.py` | 0 findings, 1,453 indexable pages |
| `check_links.py` | 0 broken links / 1,766 files |
| `audit_performance.py` | 0 findings |
| `audit_coverage_gaps.py` | 0 findings (see note below) |
| `audit_commercial_content.py` | 0 findings |
| `audit_claims_and_products.py` | 0 findings |
| `validate_blog_navigation.py` | pass |
| `audit_locale_ui.py` | 0 findings, determinism PASS |

**A genuine regression was found and root-caused (not a website defect)**: the first run of `audit_website.py` reported 3,506 pages (exactly double 1,753) and `audit_coverage_gaps.py` reported 52 `orphan_indexable_page` false positives. Root cause: a `.cloudflare-dist` directory — the actual deployed bundle from Phase 17, deliberately kept on disk after deployment rather than deleted — was still present, and these two audit scripts have no exclusion rule for build-output directories (the same class of issue first identified and fixed in Phase 11). Confirmed with certainty: **all 52 flagged paths began with `.cloudflare-dist/`**. Fixed by deleting the artifact (fully reproducible from source at any time; not source content; already gitignored) and re-running both scripts fresh — both now report 0 findings and the correct 1,753-page count. **This was an audit-hygiene oversight from Phase 17/18 (the deployed bundle should have been deleted after its verification purpose was served, per those phases' own "delete build artifacts after inspection" instruction), not a code or production defect.**

## 10. Final Crawl

Re-fetched `sitemap.xml` from production (1,453 URLs, exact match). Randomly sampled 20 URLs spanning English, Arabic, French, Thai, Indonesian, and Spanish, across product/category/article/regional/utility page types — **all 20 returned `200`.**

## 11. Production vs. Exact Phase-17 Release — Broadened Parity Check

Extended Phase 18's 2-file spot check to 7 additional critical files: `header.html`, `footer.html`, `locale-ui.js`, `contact.html`, `sample-request.js`, `jft-design-system.css`, `sitemap.xml` — **all 7 byte-for-byte identical** between production and the local repository. Combined with Phase 18's earlier confirmation on `jft-conversion.js` and `trade-regions.css`, **9 critical files have now been directly verified identical**, with no evidence of any drift, partial deployment, or stale-cache mixture.

## 12. Remaining-Risk Register

| ID | Item | Severity | Status | Disposition |
|---|---|---|---|---|
| P19-R1 | `TURNSTILE_SECRET` not configured — `/api/lead` has no active CAPTCHA/challenge verification | **LOW-MEDIUM** | Confirmed (not fixed) | Business decision: enabling Turnstile requires frontend integration + a new secret, explicitly requiring separate authorization per Phase 18 Part 38. Existing layered defenses (honeypot, Origin check, size/field limits) remain in place and functioning. |
| P19-R2 | Whether a Cloudflare dashboard rate-limit rule exists for `/api/lead` | UNKNOWN | Genuinely unresolved | Requires dashboard access or broader API token scope this session should not request |
| P19-R3 | TLS minimum version / cipher configuration | UNKNOWN (tooling-limited) | Genuinely unresolved | Requires Cloudflare dashboard access or an external tool (e.g. SSL Labs) this session cannot invoke |
| P18-INFO-1 | Permissions-Policy does not explicitly restrict `accelerometer`/`gyroscope`/`autoplay`/`fullscreen` | INFORMATIONAL | Documented, not actionable | No evidence of exploitability; carried forward unchanged from Phase 18 |
| P19-R4 | `.cloudflare-dist` build-artifact hygiene: two audit scripts have no exclusion rule for build-output directories | LOW (tooling, not site) | Root-caused, worked around (deleted the artifact) | A future phase could add a directory-exclusion rule to `audit_website.py`/`audit_coverage_gaps.py` if this keeps recurring; not done this phase (out of narrow scope, no website-facing impact) |

**No CRITICAL or HIGH severity item exists in this register.** The single most significant item (P19-R1) is a confirmed, real gap in one layer of a multi-layered defense — not a missing defense altogether, and not a defect in the code that was written (the Turnstile integration code is correct and functions exactly as designed when the secret is present; it is simply not currently provisioned).

## 13. Fix Decision Gate

No item in the risk register satisfies the fix-decision-gate's requirement of "no business-policy decision required" (P19-R1) or "root cause proven + fix within this session's access" (P19-R2, P19-R3). **Zero website source files were modified this phase.** The one operational action taken (deleting the stale `.cloudflare-dist` artifact) was not a website-source change — it was cleanup of a disposable, gitignored, fully-reproducible build output, matching the exact precedent already established across Phases 10-18.

## 14. FINAL RELEASE CERTIFICATION

### Decision: **READY WITH DISCLOSED LOW-RISK ITEMS**

**Why not an unconditional "READY FOR PRODUCTION":** one real, confirmed gap exists (P19-R1 — no active CAPTCHA/challenge on the public lead-generation endpoint) that a reasonable business owner should knowingly accept or address, not have silently glossed over. Two further items (P19-R2 rate-limiting, P19-R3 TLS configuration) remain genuinely unverifiable with this session's access and should be confirmed directly in the Cloudflare dashboard at the business's convenience, not treated as assumed-safe.

**Why not "NOT READY":** across Phases 17, 18, and 19, production has been independently verified — not merely assumed — to: serve all 1,453 sitemap URLs correctly (20/20 random sample returned 200 this phase); apply the complete, correct security-header set uniformly across every page type and locale tested; validate, sanitize, and safely reject malformed `/api/lead` submissions with zero PII leakage and zero stack-trace disclosure; expose zero sensitive files or source maps across 14 tested paths; safely normalize every path-traversal edge case tested; and match the exact, hash-verified Phase 17 release across 9 critical files with no drift. The complete 10-script regression suite passes clean. No CRITICAL or HIGH severity finding was identified in either security phase.

**What "disclosed low-risk items" means in practice**: the site is safe to continue operating as-is. The disclosed items are refinements a careful operator would want to know about and decide on deliberately (enabling Turnstile is a product/UX decision as much as a security one; confirming rate-limiting and TLS settings are dashboard checks, not code changes) — none of them represent an active, exploited, or trivially exploitable vulnerability in what was tested.
