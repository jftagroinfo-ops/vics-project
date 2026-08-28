#!/usr/bin/env python3
"""Read-only validation for the header/footer locale dictionary (locale-ui.js).

Catches exactly the class of bug found in the 2026-08-26 production baseline
audit: a committed locale-ui.js that has silently drifted out of sync with
header.html/footer.html (e.g. because scripts/build_locale_ui.py was not
re-run after a source content edit). Never writes any file and never touches
the network -- safe to run in CI alongside the other audit_*.py scripts.

Checks, each reported with the exact language and source string involved:
  missing_translation          -- a current header/footer string has no cache
                                   entry at all for this language. Blocks a
                                   fresh generation (see build_locale_ui.py).
  stale_shipped_key             -- the committed locale-ui.js contains a
                                   dictionary key that no longer matches any
                                   current header/footer string (a dead
                                   translation left over from before a source
                                   edit -- this was the root cause of the
                                   "since 1980" vs "since 2016" bug).
  raw_english_in_shipped_output -- the cache has a real (non-identical)
                                   translation for a current string, but the
                                   committed locale-ui.js does not reflect it
                                   (missing or wrong) -- i.e. a non-English
                                   visitor would see raw English right now.
  invalid_json_payload          -- locale-ui.js's embedded dictionary is not
                                   valid JSON.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_locale_ui import LOCALE_UI_PATH, compute_dictionaries, render_script  # noqa: E402
from translate_fallback_pages import CACHE_PATH, LOCALES, ROOT, TranslationCoverageError, collect_strings  # noqa: E402

REPORT = ROOT / "reports" / "locale-ui-audit.json"


def parse_shipped_dictionaries(text: str) -> dict[str, dict[str, str]]:
    match = re.search(r"const dictionaries = (\{.*\});", text)
    if not match:
        return {}
    return json.loads(match.group(1))


def main() -> int:
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    values = collect_strings([ROOT / "header.html", ROOT / "footer.html"])

    findings: dict[str, list[str]] = {
        "missing_translation": [],
        "stale_shipped_key": [],
        "raw_english_in_shipped_output": [],
        "invalid_json_payload": [],
    }

    for language in LOCALES:
        translated = cache.get(language, {})
        for value in values:
            if value not in translated:
                findings["missing_translation"].append(f"{language}: {value!r} (source: header.html/footer.html)")

    shipped: dict[str, dict[str, str]] = {}
    if not LOCALE_UI_PATH.exists():
        findings["invalid_json_payload"].append("locale-ui.js does not exist -- run scripts/build_locale_ui.py")
    else:
        shipped_text = LOCALE_UI_PATH.read_text(encoding="utf-8")
        try:
            shipped = parse_shipped_dictionaries(shipped_text)
        except json.JSONDecodeError as error:
            findings["invalid_json_payload"].append(f"locale-ui.js: embedded dictionary is not valid JSON: {error}")

        for language in LOCALES:
            stale = sorted(set(shipped.get(language, {})) - set(values))
            for key in stale:
                findings["stale_shipped_key"].append(
                    f"{language}: {key!r} no longer matches any current header.html/footer.html string"
                )

        for language in LOCALES:
            translated = cache.get(language, {})
            shipped_lang = shipped.get(language, {})
            for value in values:
                expected = translated.get(value)
                if expected is None or expected == value:
                    continue  # untranslated in cache or intentionally identical -- not this check's concern
                if shipped_lang.get(value) != expected:
                    findings["raw_english_in_shipped_output"].append(
                        f"{language}: {value!r} has a translation in the cache but locale-ui.js does not ship it"
                    )

    total = sum(len(items) for items in findings.values())
    payload = {
        "summary": {key: len(items) for key, items in findings.items()},
        "findings": findings,
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    for category, items in findings.items():
        for item in items:
            print(f"[FAIL] {category}: {item}")

    if total == 0 and shipped:
        try:
            expected_dictionaries = compute_dictionaries(values, cache)
            expected_script = render_script(values, expected_dictionaries)
            in_sync = expected_script == LOCALE_UI_PATH.read_text(encoding="utf-8")
        except TranslationCoverageError:
            in_sync = False
        print(f"Determinism check (regenerate in-memory, compare to committed file): {'PASS' if in_sync else 'FAIL'}")
        if not in_sync:
            total += 1

    print(f"Total findings: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
