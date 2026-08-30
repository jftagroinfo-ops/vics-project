#!/usr/bin/env python3
"""
Phase 39 — Before-state inventory & rollback helper.

Part of a controlled performance/correctness fix that inlines header.html into
all non-homepage pages (mirroring the homepage architecture) to eliminate the
delayed client-side fetch('header.html') and the broken locale /<locale>/header.html
410 dependency.

This script ONLY reads + records state and (via --rollback) restores it.
It never performs the inlining itself. The inliner is scripts/phase39_inline_header.py.

Rollback model:
  Every affected HTML page is tracked by git (git ls-files '*.html' == 1788).
  So the safest rollback is: `git checkout -- <changed files>` or `git stash`.
  This script records exactly which files were changed (written to
  reports/phase39/changed_files.txt by the inliner) and can restore them.

Usage:
  python scripts/phase39_inventory_rollback.py --inventory
  python scripts/phase39_inventory_rollback.py --rollback
  python scripts/phase39_inventory_rollback.py --status
"""
import os
import sys
import json
import subprocess
import datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORTS = os.path.join(ROOT, "reports", "phase39")
CHANGED_FILE = os.path.join(REPORTS, "changed_files.txt")


def git(*args):
    return subprocess.run(
        ["git"] + list(args), cwd=ROOT, capture_output=True, text=True
    )


def iter_html():
    """Yield absolute paths of all source HTML pages (exclude build/dist dirs)."""
    skip = (".cloudflare-dist", ".cloudflare-dist-next", "reports", ".git", ".well-known")
    for dirpath, dirnames, filenames in os.walk(ROOT):
        if any(part in skip for part in dirpath.split(os.sep)):
            continue
        for fn in filenames:
            if fn.lower().endswith(".html"):
                yield os.path.join(dirpath, fn)


def count_markers():
    total = 0
    loader = 0          # has the fetch('header.html') loader
    inlined = 0         # already has JFT_INLINE_HEADER_START
    gated = 0           # preloader gated on jft:header-ready
    for p in iter_html():
        total += 1
        with open(p, "r", encoding="utf-8", errors="replace") as f:
            txt = f.read()
        if "data-jft-early-header-loader" in txt:
            loader += 1
        if "JFT_INLINE_HEADER_START" in txt:
            inlined += 1
        if "plMinDelayDone = false, plHeaderReady = false" in txt:
            gated += 1
    return total, loader, inlined, gated


def do_inventory():
    os.makedirs(REPORTS, exist_ok=True)
    total, loader, inlined, gated = count_markers()
    header_lines = 0
    hp = os.path.join(ROOT, "header.html")
    if os.path.exists(hp):
        with open(hp, "r", encoding="utf-8", errors="replace") as f:
            header_lines = sum(1 for _ in f)

    tracked = git("ls-files", "*.html").stdout.strip().splitlines()
    untracked = git("ls-files", "--others", "--exclude-standard", "*.html").stdout.strip().splitlines()

    inv = {
        "timestamp": datetime.datetime.now().isoformat(timespec="seconds"),
        "root": ROOT,
        "html_total_found": total,
        "html_git_tracked": len(tracked),
        "html_git_untracked": len(untracked),
        "pages_with_loader": loader,
        "pages_already_inlined": inlined,
        "pages_preloader_gated": gated,
        "header_html_lines": header_lines,
        "header_html_size_bytes": os.path.getsize(hp) if os.path.exists(hp) else 0,
    }
    out = os.path.join(REPORTS, "before_inventory.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(inv, f, indent=2)

    # Human-readable log line
    logline = (
        f"{inv['timestamp']} BEFORE total={total} tracked={inv['html_git_tracked']} "
        f"untracked={inv['html_git_untracked']} loader={loader} inlined={inlined} "
        f"gated={gated} header_lines={header_lines}\n"
    )
    with open(os.path.join(REPORTS, "audit.log"), "a", encoding="utf-8") as f:
        f.write(logline)

    print(json.dumps(inv, indent=2))
    print("\nRollback is available via git (tracked files) or this script --rollback.")
    print("Inventory written to", out)


def do_rollback():
    os.makedirs(REPORTS, exist_ok=True)
    if os.path.exists(CHANGED_FILE):
        with open(CHANGED_FILE, "r", encoding="utf-8") as f:
            changed = [l.strip() for l in f if l.strip()]
        print(f"Restoring {len(changed)} files recorded in changed_files.txt ...")
        res = git("checkout", "--", *changed)
        print(res.stdout or "", res.stderr or "")
        print(f"Restored {len(changed)} files via git checkout.")
    else:
        # Fallback: revert ALL tracked html to HEAD
        print("No changed_files.txt found; reverting ALL tracked html to HEAD.")
        res = git("checkout", "--", "*.html")
        print(res.stdout or "", res.stderr or "")
    with open(os.path.join(REPORTS, "audit.log"), "a", encoding="utf-8") as f:
        f.write(f"{datetime.datetime.now().isoformat(timespec='seconds')} ROLLBACK executed\n")


def do_status():
    if not os.path.exists(CHANGED_FILE):
        print("No changed_files.txt — nothing recorded as changed by the inliner.")
        return
    with open(CHANGED_FILE, "r", encoding="utf-8") as f:
        changed = [l.strip() for l in f if l.strip()]
    print(f"{len(changed)} files changed by Phase 39 inliner:")
    for c in changed[:50]:
        print("  ", os.path.relpath(c, ROOT))
    if len(changed) > 50:
        print(f"  ... and {len(changed) - 50} more")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cmd = sys.argv[1]
    if cmd == "--inventory":
        do_inventory()
    elif cmd == "--rollback":
        do_rollback()
    elif cmd == "--status":
        do_status()
    else:
        print("Unknown command:", cmd)
        print(__doc__)
        sys.exit(1)
