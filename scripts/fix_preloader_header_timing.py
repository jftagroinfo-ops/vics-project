#!/usr/bin/env python3
"""Fix P29-1 for the 83 product pages that have both a preloader and the
async header-fetch mechanism: the preloader currently hides on a fixed,
guessed timeout (900ms touch / 1400ms non-touch) with no relationship to
whether the header has actually finished loading. On a slow connection the
header can still be fetching when the timeout fires, so the page content
appears before the header - the exact defect reported.

The header-loader already dispatches a `jft:header-ready` custom event the
instant injection completes (see the `data-jft-early-header-loader` script).
This fix makes the preloader hide only once BOTH the original minimum
delay has elapsed AND the header is actually ready - preserving the exact
original timing in the common case (header ready well within 900-1400ms),
and only changing behavior in the failure case the bug report describes.
The existing hard 3000ms fallback is left untouched as a safety net if the
header fetch fails entirely (jft:header-ready is only dispatched on
success, never in the .catch() error path).

Exact-match-guarded; touches only the 83 files with the precise known
pattern (not sugar-s30-supplier.html, which has no preloader). Idempotent.
"""

from __future__ import annotations

import glob
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

OLD = """    /* Preloader */
    var plDelay = ('ontouchstart' in window) ? 900 : 1400;
    setTimeout(function(){ var p=document.getElementById('preloader');if(p){p.style.opacity='0';setTimeout(function(){p.style.display='none';},500);} }, plDelay);
    setTimeout(function(){ var p=document.getElementById('preloader');if(p){p.style.opacity='0';p.style.display='none';} }, 3000);"""

NEW = """    /* Preloader */
    var plDelay = ('ontouchstart' in window) ? 900 : 1400;
    var plMinDelayDone = false, plHeaderReady = false;
    function plMaybeHide(){
      if(!plMinDelayDone || !plHeaderReady) return;
      var p=document.getElementById('preloader');if(p){p.style.opacity='0';setTimeout(function(){p.style.display='none';},500);}
    }
    setTimeout(function(){ plMinDelayDone = true; plMaybeHide(); }, plDelay);
    document.addEventListener('jft:header-ready', function(){ plHeaderReady = true; plMaybeHide(); });
    setTimeout(function(){ var p=document.getElementById('preloader');if(p){p.style.opacity='0';p.style.display='none';} }, 3000);"""


def find_product_files() -> list[Path]:
    candidates = sorted(set(glob.glob(str(ROOT / "*-exporter.html"))) | set(glob.glob(str(ROOT / "*-supplier.html"))))
    return [Path(p) for p in candidates if not Path(p).name.startswith("blog-")]


def main() -> None:
    fixed = 0
    skipped_already = 0
    skipped_no_pattern = 0
    for path in find_product_files():
        source = path.read_text(encoding="utf-8")
        if NEW in source:
            skipped_already += 1
            continue
        count = source.count(OLD)
        if count == 0:
            skipped_no_pattern += 1
            continue
        if count != 1:
            raise SystemExit(f"{path.name}: expected exactly 1 match, found {count}, aborting")
        path.write_text(source.replace(OLD, NEW, 1), encoding="utf-8")
        fixed += 1
    print(
        f"Fixed: {fixed}. Already fixed: {skipped_already}. "
        f"No preloader pattern (expected, e.g. sugar-s30-supplier.html): {skipped_no_pattern}."
    )


if __name__ == "__main__":
    main()
