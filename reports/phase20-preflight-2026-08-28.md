# Phase 20 — Preflight

Date: 2026-08-28
Status: Baseline established. No website files modified during preflight.

## Starting State

- Current commit: `e64a3f2b` (unchanged since Phase 1 — nothing has ever been committed during this entire 20-phase engagement; all work remains in the working tree, deployed to production only via the Phase 17 `wrangler deploy`, independent of git history).
- `git status --short`: 1,172 paths (consistent with the cumulative uncommitted work of Phases 1-19; no unexpected file present).
- Current production URL: `https://jftagro.com/` — confirmed live, `HTTP 200`.
- Current production sitemap count: **1,453 URLs** (fetched live, matches the local repository exactly).
- Current local HTML page count: 1,753 renderable pages (per `full_site_audit.py`), 1,453 indexable.
- Current audit status (re-run fresh this phase, not assumed): all 10 scripts (`audit_website.py`, `audit_localizations.py`, `full_site_audit.py`, `check_links.py`, `audit_performance.py`, `audit_coverage_gaps.py`, `audit_commercial_content.py`, `audit_claims_and_products.py`, `validate_blog_navigation.py`, `audit_locale_ui.py`) — **0 findings, 0 broken links.**
- No stale `.cloudflare-dist`/`.cloudflare-dist-next` build artifact was present this time (the Phase 19 incident's root cause), confirmed absent before trusting the audit results.

## Phase-19 Risk Register (carried forward, unchanged, re-confirmed this phase)

| ID | Item | Severity | Status |
|---|---|---|---|
| P19-R1 | `TURNSTILE_SECRET` not configured — `/api/lead` has no active challenge verification | LOW-MEDIUM | Confirmed, business decision required |
| P19-R2 | Cloudflare dashboard rate-limit status for `/api/lead` | UNKNOWN | Genuinely unresolved (access-scope limited) |
| P19-R3 | TLS minimum version/cipher configuration | UNKNOWN (tooling-limited) | Genuinely unresolved |
| P18-INFO-1 | Permissions-Policy scope (`accelerometer`/`gyroscope`/`autoplay`/`fullscreen` not explicitly restricted) | INFORMATIONAL | Not actionable |
| P19-R4 | Audit scripts lack build-output directory exclusion | LOW (tooling only) | Worked around each time it recurs |
| — | WhatsApp prefilled message stays in English on non-English pages | BUSINESS JUDGMENT | Re-confirmed still present this phase (unchanged, not a regression — documented since Phase 14) |

None of these are P0/P1. No new item was found during preflight.

## Phase 20 Baseline

This is the exact state Phase 20's investigation began from. Any change made this phase will be measured against this baseline.
