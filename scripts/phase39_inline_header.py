#!/usr/bin/env python3
"""
Phase 39 — Inline header.html into all non-homepage pages.

Goal (controlled scope, authorized):
  * Eliminate the delayed client-side fetch('header.html') on the 940
    non-homepage pages by inlining the existing header.html directly into each
    page, mirroring the homepage architecture (JFT_INLINE_HEADER_START/END).
  * Preserve all existing header markup, navigation, translations (locale-ui.js),
    links and behaviour. Do NOT redesign or rewrite content.
  * Do NOT touch .cloudflare/worker.js: the locale header.html 410 stays as a
    protection against exposing the internal include, since after inlining NO
    production page requests /<locale>/header.html.
  * Do NOT add preload/cache headers (unnecessary once the header is inlined).
  * Do NOT change canonical / hreflang / JSON-LD / sitemap / robots.

Idempotent + safe:
  * Skips any file already containing JFT_INLINE_HEADER_START or without the
    loader marker (so re-running is a no-op for inlined pages).
  * Records every changed file to reports/phase39/changed_files.txt (for rollback).
  * Rollback: python scripts/phase39_inventory_rollback.py --rollback
    (all source HTML is git-tracked, so `git checkout -- <files>` also works).

Preloader correctness:
  * 83 pages gate their preloader on the `jft:header-ready` event (which the
    fetch loader used to dispatch). The inline block therefore fires
    `document.dispatchEvent(new CustomEvent('jft:header-ready'))` once, so those
    pages hide the preloader immediately instead of waiting the 3s failsafe.

Usage:
  python scripts/phase39_inline_header.py --apply
  python scripts/phase39_inline_header.py --dry-run
"""
import os
import re
import sys
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports", "phase39")
CHANGED_FILE = os.path.join(REPORTS, "changed_files.txt")

SKIP_DIRS = (".cloudflare-dist", ".cloudflare-dist-next", "reports", ".git", ".well-known")

# Placeholder + inline-init script marker (single line).
LOADER_TAG = '<script data-jft-early-header-loader>'

# Empty placeholder line:  <div id="header-placeholder"></div>  (possibly with attrs).
# Line-ending agnostic (\r?\n) so CRLF source files keep CRLF.
PLACEHOLDER_RE = re.compile(r'<div id="header-placeholder"[^>]*>\s*</div>\s*\r?\n')

# The loader <script data-jft-early-header-loader> ... </script> (multi-line).
LOADER_BLOCK_RE = re.compile(
    r'<script data-jft-early-header-loader>.*?</script>\s*\r?\n', re.DOTALL
)

# Body-level redundant skip-link (any #main-content skip-link that appears BEFORE the
# header include). The include already provides one (with English text), so we drop the
# page body's to avoid a duplicate (accessibility regression). Localized pages use
# translated link text (e.g. Arabic), and attribute order varies, so match ANY <a>
# with class="skip-link" + href="#main-content" regardless of inner text. EOL-agnostic.
BODY_SKIPLINK_RE = re.compile(
    r'<a\s+(?:[^>]*\s)?class="skip-link"[^>]*?href="#main-content"[^>]*>.*?</a>\s*\r?\n'
    r'|<a\s+(?:[^>]*\s)?href="#main-content"[^>]*?class="skip-link"[^>]*>.*?</a>\s*\r?\n'
)

START_MARKER = "<!-- JFT_INLINE_HEADER_START -->"
END_MARKER = "<!-- JFT_INLINE_HEADER_END -->"

HEADER_EVENT_SNIPPET = "document.dispatchEvent(new CustomEvent('jft:header-ready'));"


def load_header():
    with open(os.path.join(ROOT, "header.html"), "r", encoding="utf-8") as f:
        return f.read()



def detect_eol(text):
    """Return '\\r\\n' if the file uses CRLF, else '\\n'."""
    if "\r\n" in text:
        return "\r\n"
    return "\n"


def build_inlined_block(header_html, eol):
    """Wrap header.html between markers; fire the header-ready event inline.

    We set the placeholder to state=ready (matches homepage) and dispatch
    jft:header-ready so the 83 gated preloader pages do not wait on a fetch.
    The scripts inside header.html run normally (no innerHTML recreation), which
    is strictly more reliable than the old fetch+script-clone path.

    `eol` matches the hosting page so we never flip line endings (keeps git diff
    clean and avoids touching unrelated lines).
    """
    event_line = (
        "<script>if(!window.__jftHeaderReadyFired){"
        "window.__jftHeaderReadyFired=true;"
        + HEADER_EVENT_SNIPPET
        + "}</script>"
    )
    # header.html is LF; convert its line endings to the page's eol.
    body = header_html.replace("\r\n", "\n").rstrip("\n")
    if eol != "\n":
        body = body.replace("\n", eol)
    return (
        START_MARKER
        + eol
        + body
        + eol
        + END_MARKER
        + eol
        + event_line
        + eol
    )


def iter_candidate_html():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if any(part in SKIP_DIRS for part in dirpath.split(os.sep)):
            continue
        for fn in filenames:
            if fn.lower().endswith(".html"):
                yield os.path.join(dirpath, fn)


def transform(text, header_html):
    """Return (new_text, changed_bool)."""
    # Already inlined -> skip.
    if START_MARKER in text:
        return text, False
    if LOADER_TAG not in text:
        return text, False
    if not PLACEHOLDER_RE.search(text):
        return text, False

    eol = detect_eol(text)
    inlined_block = build_inlined_block(header_html, eol)
    new = text

    # 1) Remove redundant body-level skip-link ONLY if it precedes the header
    #    include. The include already provides one; a duplicate is an a11y bug.
    #    We operate on the body region (before the placeholder) to keep the
    #    include's own skip-link intact, and use the page's eol for matching.
    ph_idx = new.find('<div id="header-placeholder"')
    body_region = new[:ph_idx] if ph_idx != -1 else new
    for m in BODY_SKIPLINK_RE.finditer(body_region):
        new = new.replace(m.group(0), "", 1)

    # 2) Replace the placeholder div with the inlined block (eol-aware).
    new = PLACEHOLDER_RE.sub(
        '<div id="header-placeholder" data-jft-header-state="ready">'
        + eol
        + inlined_block
        + "</div>"
        + eol,
        new,
        1,
    )

    # 3) Remove the now-obsolete fetch() loader script block.
    new = LOADER_BLOCK_RE.sub("", new, 1)

    # Sanity: loader must be gone, block must be present.
    if LOADER_TAG in new:
        # Should not happen; leave unchanged to be safe.
        return text, False
    if START_MARKER not in new:
        return text, False
    return new, True


def main():
    mode = sys.argv[1] if len(sys.argv) > 1 else "--dry-run"
    apply = mode == "--apply"
    os.makedirs(REPORTS, exist_ok=True)

    header_html = load_header()

    changed = []
    scanned = 0
    already = 0
    for path in iter_candidate_html():
        scanned += 1
        with open(path, "r", encoding="utf-8", errors="replace", newline="") as f:
            text = f.read()
        new_text, did = transform(text, header_html)
        if did:
            changed.append(path)
            if apply:
                # Preserve original line endings exactly (newline="" keeps CRLF).
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new_text)
        elif START_MARKER in text:
            already += 1

    with open(CHANGED_FILE, "w", encoding="utf-8") as f:
        for p in changed:
            f.write(p + "\n")

    with open(os.path.join(REPORTS, "audit.log"), "a", encoding="utf-8") as f:
        f.write(
            f"{datetime.datetime.now().isoformat(timespec='seconds')} INLINE "
            f"{'APPLY' if apply else 'DRYRUN'} scanned={scanned} changed={len(changed)} "
            f"already_inlined={already}\n"
        )

    print(f"mode={'APPLY' if apply else 'DRY-RUN'}")
    print(f"scanned={scanned} changed={len(changed)} already_inlined={already}")
    print(f"changed list -> {CHANGED_FILE}")
    if not apply:
        print("DRY-RUN: no files written. Re-run with --apply to write.")


if __name__ == "__main__":
    main()
