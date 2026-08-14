#!/usr/bin/env python3
"""Start shared-header loading at the top of each page instead of DOMContentLoaded."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MARKER = "data-jft-early-header-loader"
PLACEHOLDER = re.compile(r'(<div\s+id=["\']header-placeholder["\'][^>]*></div>)', re.I)
LATE_CALL = re.compile(
    r"\s*loadComp\(\s*([\"'])header-placeholder\1\s*,\s*([\"'])(?P<src>[^\"']*header\.html)\2\s*\)\s*;",
    re.I,
)


def loader(source: str) -> str:
    return f"""<script {MARKER}>
  (function () {{
    var target = document.getElementById('header-placeholder');
    if (!target || target.dataset.jftHeaderState === 'loading' || target.dataset.jftHeaderState === 'ready') return;
    function injectHeader() {{
      target.dataset.jftHeaderState = 'loading';
      target.setAttribute('aria-busy', 'true');
      return fetch('{source}', {{ credentials: 'same-origin' }}).then(function (response) {{
        if (!response.ok) throw new Error('{source} not found');
        return response.text();
      }}).then(function (html) {{
        target.innerHTML = html;
        target.querySelectorAll('script').forEach(function (oldScript) {{
          var newScript = document.createElement('script');
          Array.from(oldScript.attributes).forEach(function (attribute) {{
            newScript.setAttribute(attribute.name, attribute.value);
          }});
          newScript.textContent = oldScript.textContent;
          oldScript.parentNode.replaceChild(newScript, oldScript);
        }});
        target.dataset.jftHeaderState = 'ready';
        target.removeAttribute('aria-busy');
        document.dispatchEvent(new CustomEvent('jft:header-ready'));
      }});
    }}
    injectHeader().catch(function (error) {{
      target.dataset.jftHeaderState = 'error';
      target.removeAttribute('aria-busy');
      console.warn(error);
    }});
  }}());
</script>"""


def main() -> int:
    changed = 0
    for path in ROOT.rglob("*.html"):
        if ".git" in path.parts or "reports" in path.parts:
            continue
        text = path.read_text(encoding="utf-8", errors="strict")
        if MARKER in text:
            continue
        match = LATE_CALL.search(text)
        placeholder = PLACEHOLDER.search(text)
        if not match or not placeholder:
            continue
        source = match.group("src")
        updated = LATE_CALL.sub("", text)
        updated = PLACEHOLDER.sub(rf"\1\n{loader(source)}", updated, count=1)
        path.write_text(updated, encoding="utf-8", newline="")
        changed += 1
    print(f"Moved shared-header loading earlier in {changed} pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
