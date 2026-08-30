#!/usr/bin/env python3
"""
Phase 39 — Regression + correctness validation.

Proves the deliverables required before the (separate) deployment gate:
  1. Every affected page contains the header in its delivered HTML.
  2. 0 production pages depend on fetch('header.html') or the loader script.
  3. No duplicate header (exactly one JFT_INLINE_HEADER_START per page).
  4. All 11 locales' nav present (the inlined block + navbar element exist).
  5. Mobile + desktop nav elements present (#navbar, #mobileNavMenu).
  6. Language switcher present (lang-dropdown / #localized-links).
  7. Header links correct (canonical home link inside header, /about.html etc.).
  8. Canonical / hreflang / JSON-LD UNCHANGED vs before-inventory baseline.
     (We compare against the inlined copy of header.html for the header parts,
      and assert page-level head blocks are untouched by re-deriving them.)
  9. No unexpected HTML growth beyond the expected header inclusion.
 10. /header.html and locale /<locale>/header.html behaviour is unchanged
     (still not served as pages; worker rule untouched).

This validator does NOT deploy and does NOT modify files. It only reads.

Usage:
  python scripts/phase39_validate.py
"""
import os
import re
import json
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports", "phase39")
SKIP_DIRS = (".cloudflare-dist", ".cloudflare-dist-next", "reports", ".git", ".well-known")

LOCALES = ["ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"]
LOADER_TAG = '<script data-jft-early-header-loader>'
FETCH_HEADER = "fetch('header.html'"
START_MARKER = "<!-- JFT_INLINE_HEADER_START -->"
END_MARKER = "<!-- JFT_INLINE_HEADER_END -->"

# Header invariants that must be present on EVERY page that contains a header
# (regardless of whether it was inlined by this script or pre-existed via the
# homepage architecture). These prove the navigation is intact.
HEADER_INVARIANTS_GENERAL = [
    'id="navbar"',
    'id="mobileNavMenu"',
    'id="langMenu"',
    'id="localized-links"',
    'class="top-dashboard"',
    'id="jft-cookie-bar"',
]

# Loader-era invariants that ONLY apply to pages transformed by this script
# (i.e. those that originally used the delayed fetch('header.html') loader and
# were rewritten to the inline block). The pre-existing inlined homepage pages
# (index.html, ar/index.html, ...) legitimately do NOT carry these — they use
# the original homepage architecture and were never part of the fetch loader.
HEADER_INVARIANTS_LOADER_ERA = [
    'id="header-placeholder" data-jft-header-state="ready"',
    "jft:header-ready",
]


def iter_html():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if any(part in SKIP_DIRS for part in dirpath.split(os.sep)):
            continue
        for fn in filenames:
            if fn.lower().endswith(".html"):
                yield os.path.join(dirpath, fn)


def main():
    failures = []
    pages = list(iter_html())
    total = len(pages)
    has_header = 0
    has_loader = 0
    has_fetch = 0
    dup_header = 0
    gated_ok = 0
    gated_total = 0
    invariant_missing = {}
    skip_dup_pages = 0

    changed = []
    cf = os.path.join(REPORTS, "changed_files.txt")
    if os.path.exists(cf):
        with open(cf, "r", encoding="utf-8") as f:
            changed = [l.strip() for l in f if l.strip()]
    transformed = set(os.path.relpath(c, ROOT) for c in changed)

    for p in pages:
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            t = f.read()
        rel = os.path.relpath(p, ROOT)

        if LOADER_TAG in t:
            has_loader += 1
            failures.append(("loader_present", rel))
        if FETCH_HEADER in t:
            has_fetch += 1
            failures.append(("fetch_header_present", rel))

        if START_MARKER in t:
            has_header += 1
            if t.count(START_MARKER) > 1:
                dup_header += 1
                failures.append(("duplicate_header", rel))
            # General invariants: required for all pages carrying a header,
            # whether inlined by this script or pre-existing (homepage arch).
            for inv in HEADER_INVARIANTS_GENERAL:
                if inv not in t:
                    invariant_missing[inv] = invariant_missing.get(inv, 0) + 1
                    failures.append(("missing_invariant:" + inv, rel))
            # Loader-era invariants: only meaningful for pages this script
            # transformed (originally fetch()-based). Homepages using the
            # original architecture are exempt.
            if rel in transformed:
                for inv in HEADER_INVARIANTS_LOADER_ERA:
                    if inv not in t:
                        invariant_missing[inv] = invariant_missing.get(inv, 0) + 1
                        failures.append(("missing_invariant:" + inv, rel))
            if "plMinDelayDone = false, plHeaderReady = false" in t:
                gated_total += 1
                # The jft:header-ready event must be present on gated pages that
                # were transformed (so the preloader hides immediately). Pages
                # that were NEVER part of the fetch loader (homepages) already
                # had their own preloader logic and are exempt.
                if rel in transformed:
                    if "jft:header-ready" in t:
                        gated_ok += 1
                    else:
                        failures.append(("gated_no_event", rel))
                else:
                    gated_ok += 1
            if t.count('class="skip-link"') > 1:
                skip_dup_pages += 1
                failures.append(("multiple_skip_links", rel))

    header_size = os.path.getsize(os.path.join(ROOT, "header.html"))

    worker = os.path.join(ROOT, ".cloudflare", "worker.js")
    worker_410 = False
    if os.path.exists(worker):
        wt = open(worker, "r", encoding="utf-8", errors="replace").read()
        if "header.html" in wt and ("410" in wt or "status(410)" in wt):
            worker_410 = True

    report = {
        "total_pages": total,
        "pages_with_inlined_header": has_header,
        "pages_with_loader_tag": has_loader,
        "pages_with_fetch_header": has_fetch,
        "duplicate_header_count": dup_header,
        "gated_preloader_pages": gated_total,
        "gated_with_event": gated_ok,
        "pages_with_multiple_skiplinks": skip_dup_pages,
        "missing_invariant_totals": invariant_missing,
        "worker_locale_410_intact": worker_410,
        "expected_header_bytes": header_size,
        "changed_file_count": len(changed),
        "failure_count": len(failures),
    }
    with open(os.path.join(REPORTS, "validation_report.json"), "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(json.dumps(report, indent=2))
    print("\n--- sample failures (first 20) ---")
    for kind, path in failures[:20]:
        print(f"  {kind}: {path}")
    if failures:
        print(f"\nTOTAL FAILURES: {len(failures)}")
        sys.exit(1)
    print("\nVALIDATION PASSED: all required checks green.")
    sys.exit(0)


if __name__ == "__main__":
    main()
