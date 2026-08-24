#!/usr/bin/env python3
"""Check locale completeness, metadata, text residue, and source parity."""

from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re

from bs4 import BeautifulSoup, Comment


ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "reports" / "localization-audit.json"
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
# Evidence-led English resources remain English until a qualified native
# reviewer approves each localized legal and commercial meaning.
IGNORED = {
    "inner-page-hero-snippet.html",
    "seo-universal-head-snippet.html",
    "buyer-security.html",
    "export-documentation.html",
    "editorial-policy.html",
    "india-agricultural-export-market-data-sources.html",
}
# Avoid international trade loanwords such as "export", "product", and "market".
# The terms below are strong indicators that an English sentence survived.
ENGLISH_SENTENCE = re.compile(r"\b(?:the|with|from|this|that|your|buyer|buyers|request|shipping|supplied|choose|learn|read more)\b", re.I)


def visible_strings(path: Path) -> list[str]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    return [
        " ".join(str(node).split())
        for node in soup.find_all(string=True)
        if not isinstance(node, Comment) and node.parent and node.parent.name not in {"script", "style", "noscript", "code", "pre", "svg"}
        and " ".join(str(node).split())
    ]


def main() -> int:
    findings: dict[str, list[str]] = {}
    summary: dict[str, dict] = {}
    source_names = {
        path.name for path in ROOT.glob("*.html")
        if path.name not in IGNORED and "<html" in path.read_text(encoding="utf-8", errors="replace").lower()
    }
    for language in LOCALES:
        folder = ROOT / language
        names = {path.name for path in folder.glob("*.html") if path.name not in IGNORED and "<html" in path.read_text(encoding="utf-8", errors="replace").lower()}
        missing = sorted(source_names - names)
        fallback = []
        wrong_lang = []
        residue = []
        for name in sorted(names):
            path = folder / name
            text = path.read_text(encoding="utf-8", errors="replace")
            soup = BeautifulSoup(text, "html.parser")
            html = soup.html
            if soup.find("meta", attrs={"name": "jft-localization", "content": "english-fallback"}):
                fallback.append(name)
            if not html or html.get("lang") != language or (language == "ar" and html.get("dir") != "rtl"):
                wrong_lang.append(name)
            strings = visible_strings(path)
            English_matches = [value for value in strings if len(value.split()) >= 5 and ENGLISH_SENTENCE.search(value)]
            # Product/trade nouns remain in English by convention; flag only pages with substantial sentence residue.
            if len(English_matches) >= 4:
                residue.append(f"{name}: {len(English_matches)}")
        if fallback:
            findings[f"{language}_fallback_pages"] = fallback
        if wrong_lang:
            findings[f"{language}_language_metadata"] = wrong_lang
        if residue:
            findings[f"{language}_english_residue"] = residue
        if missing:
            findings[f"{language}_missing_pages"] = missing
        summary[language] = {"renderable_pages": len(names), "missing_pages": len(missing), "fallback_pages": len(fallback), "high_residue_pages": len(residue)}
    payload = {"summary": summary, "finding_counts": {key: len(value) for key, value in findings.items()}, "findings": findings}
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"summary": summary, "finding_counts": payload["finding_counts"]}, ensure_ascii=False, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
