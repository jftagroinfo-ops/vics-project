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
CACHE_PATH = ROOT / "data" / "localized-copy-cache.json"
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")

# Closed-vocabulary shared UI components: on the English root pages, each of
# these selectors carries a single dominant text/attribute value across
# every occurrence (verified empirically, not assumed). Because the value is
# effectively fixed, any locale-page occurrence that isn't the governed cache
# translation of that value is a strong, low-false-positive signal that the
# component's English source text changed after this page's copy was
# translated and nothing re-synced the shipped HTML (the defect class that
# let "Order on WhatsApp" ship untranslated 830 times -- see Phase 6 report).
CLOSED_VOCABULARY_COMPONENTS = (
    {"selector": "a.btn-wa-product", "attr": None, "dominance_threshold": 0.9, "file_glob": "*-exporter.html"},
    # wa-fab's aria-label is deliberately page-specific on articles/guides (e.g. "Ask about
    # coriander on WhatsApp"), so the closed-vocabulary assumption only holds within the
    # product-detail template family, not site-wide.
    {"selector": "a.wa-fab", "attr": "aria-label", "dominance_threshold": 0.9, "file_glob": "*-exporter.html"},
)
# Evidence-led English resources remain English until a qualified native
# reviewer approves each localized legal and commercial meaning.
IGNORED = {
    "inner-page-hero-snippet.html",
    "seo-universal-head-snippet.html",
    "buyer-security.html",
    "export-documentation.html",
    "editorial-policy.html",
    "india-agricultural-export-market-data-sources.html",
    # Phase 10 commodity-category pages: deliberately English-only this phase
    # (see reports/phase10-commodity-architecture-2026-08-27.md, Part F --
    # locale versions require native-quality translation of substantial new
    # narrative content and are explicitly deferred, not silently missing).
    "rice-exporter-india.html",
    "spices-exporter-india.html",
    "herbs-seeds-exporter-india.html",
    "animal-feed-exporter-india.html",
    "oilseeds-exporter-india.html",
    "flour-exporter-india.html",
    "wheat-exporter-india.html",
    "sugar-exporter-india.html",
    "raisins-exporter-india.html",
    "pulses-exporter-india.html",
}
# Avoid international trade loanwords such as "export", "product", and "market".
# The terms below are strong indicators that an English sentence survived.
ENGLISH_SENTENCE = re.compile(r"\b(?:the|with|from|this|that|your|buyer|buyers|request|shipping|supplied|choose|learn|read more)\b", re.I)
# A source string that reads as ordinary English prose (a common function word, or a
# multi-word phrase) but whose cached "translation" is byte-identical to the English is a
# strong signal the string was never actually translated. Brand names, HS/grade codes,
# port names, prices and dates are also frequently -- and correctly -- identical, so this
# is reported as an informational metric for human review (Part R), never a hard failure.
CACHE_IDENTITY_FUNC_WORDS = re.compile(r"\b(?:the|and|with|from|this|that|your|our|for|are|is|of|to|in|on|a|an)\b", re.I)


def check_cache_self_identical(cache: dict) -> dict[str, list[str]]:
    suspicious: dict[str, list[str]] = {}
    for language, entries in cache.items():
        flagged = []
        for source, translation in entries.items():
            if source != translation:
                continue
            words = source.split()
            if len(words) >= 2 and (CACHE_IDENTITY_FUNC_WORDS.search(source) or len(words) >= 4):
                flagged.append(source)
        if flagged:
            suspicious[language] = sorted(flagged)
    return suspicious


def visible_strings(path: Path) -> list[str]:
    soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
    return [
        " ".join(str(node).split())
        for node in soup.find_all(string=True)
        if not isinstance(node, Comment) and node.parent and node.parent.name not in {"script", "style", "noscript", "code", "pre", "svg"}
        and " ".join(str(node).split())
    ]


def component_value(el, attr: str | None) -> str | None:
    value = el.get(attr) if attr else el.get_text(strip=True)
    return value if value else None


def find_dominant_english_values(component: dict) -> dict[str, float]:
    """For a closed-vocabulary component, return {value: share} across the
    English root pages, restricted to values clearing the dominance threshold."""
    counts: Counter[str] = Counter()
    for path in ROOT.glob(component.get("file_glob", "*.html")):
        if path.name in IGNORED:
            continue
        soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
        for el in soup.select(component["selector"]):
            value = component_value(el, component["attr"])
            if value:
                counts[value] += 1
    total = sum(counts.values())
    if not total:
        return {}
    return {
        value: count / total
        for value, count in counts.items()
        if count / total >= component["dominance_threshold"]
    }


def check_component_drift(cache: dict) -> tuple[dict[str, list[str]], dict[str, list[str]]]:
    """Detect locale-page component text that doesn't match the governed
    cache translation of the current dominant English value for that
    component. Catches source-string renames that orphaned already-shipped
    locale HTML (see CLOSED_VOCABULARY_COMPONENTS)."""
    drift: dict[str, list[str]] = {}
    cache_gaps: dict[str, list[str]] = {}
    dominants = {component["selector"]: find_dominant_english_values(component) for component in CLOSED_VOCABULARY_COMPONENTS}
    for component in CLOSED_VOCABULARY_COMPONENTS:
        for english_value in dominants[component["selector"]]:
            for language in LOCALES:
                if english_value not in cache.get(language, {}):
                    cache_gaps.setdefault(component["selector"], []).append(
                        f"{language}: no governed translation for {english_value!r}"
                    )
    for language in LOCALES:
        folder = ROOT / language
        for component in CLOSED_VOCABULARY_COMPONENTS:
            dominant = dominants[component["selector"]]
            if not dominant:
                continue
            # Require the governed cache translation where one exists. Only fall back to
            # accepting the raw English value when this language has no cache entry at all
            # for it -- that gap is already surfaced separately via component_cache_gaps,
            # so it must not also be silently treated as an acceptable locale value here
            # (that silence is exactly what let the WhatsApp CTA drift go undetected).
            expected = {
                cache.get(language, {}).get(v, v) for v in dominant
            }
            for path in sorted(folder.glob(component.get("file_glob", "*.html"))):
                if path.name in IGNORED:
                    continue
                soup = BeautifulSoup(path.read_text(encoding="utf-8", errors="replace"), "html.parser")
                for el in soup.select(component["selector"]):
                    value = component_value(el, component["attr"])
                    if value and value not in expected:
                        drift.setdefault(f"{language}_{component['selector']}", []).append(f"{path.name}: {value!r}")
    return drift, cache_gaps


def check_product_faq_drift() -> dict[str, list[str]]:
    """Detect drift between the governed product-FAQ source (Phase 7:
    data/product-faq-templates.json + data/products.json, rendered by
    scripts/build_product_faq_locale.py) and what a locale page actually
    ships. Regenerates the expected FAQ markup in-memory and byte-compares it
    against the committed page -- the same determinism-check pattern as
    audit_locale_ui.py (Phase 2) -- so it catches missing translation,
    English leakage, and stale content the moment a locale page falls out of
    sync with the governed source, regardless of the specific string
    involved. This is deliberately a regeneration diff, not a string-content
    heuristic, so it cannot be fooled by paraphrasing and does not need
    updating if the template wording changes."""
    import sys

    scripts_dir = str(Path(__file__).resolve().parent)
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)
    import build_product_faq_locale as faq_gen  # noqa: PLC0415

    drift: dict[str, list[str]] = {}
    for product in faq_gen.PRODUCTS:
        for language in LOCALES:
            path = ROOT / language / product["u"]
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            try:
                expected_items = faq_gen.product_faq_items_localized(product, language)
            except faq_gen.MissingTranslation as exc:
                drift.setdefault(f"{language}_missing_faq_translation", []).append(f"{product['u']}: {exc}")
                continue
            soup = BeautifulSoup(text, "html.parser")
            section = soup.select_one(".prod-faq-section")
            if section is None:
                continue  # not every page uses the governed 5-question template (e.g. bespoke regulatory FAQs)
            items = section.select(".faq-item")
            if len(items) != 5:
                continue
            actual_items = "\n".join(str(item) for item in items)
            if actual_items != expected_items:
                drift.setdefault(f"{language}_product_faq_drift", []).append(product["u"])
    return drift


# Phase 8: the product-FAQ accordion's click handler (an inline <script> block
# after </section>, not the FAQ text itself) had its open/closed branches
# inverted on every locale page -- a functional JS bug, not a translation
# defect, but caught here because it is exactly the same "locale page must
# match the correct English-root pattern" shape as check_component_drift.
# The correct pattern (proven by the English root pages and by the real-
# browser regression test in scripts/browser_faq_accordion_test.py):
FAQ_ACCORDION_CORRECT_SCRIPT = (
    "document.querySelectorAll('.faq-q').forEach(function(q){q.addEventListener('click',"
    "function(){var a=this.nextElementSibling;"
    "if(a.classList.contains('open')){a.style.maxHeight=a.scrollHeight+'px';}"
    "else{a.style.maxHeight='0';}});});"
)
FAQ_ACCORDION_INVERTED_SCRIPT = (
    "document.querySelectorAll('.faq-q').forEach(function(q){q.addEventListener('click',"
    "function(){var a=this.nextElementSibling;"
    "if(a.classList.contains('open')){a.style.maxHeight='0';}"
    "else{a.style.maxHeight=a.scrollHeight+'px';}});});"
)


def check_faq_accordion_script() -> dict[str, list[str]]:
    findings: dict[str, list[str]] = {}
    for language in LOCALES:
        folder = ROOT / language
        for path in sorted(folder.glob("*-exporter.html")):
            text = path.read_text(encoding="utf-8", errors="replace")
            if FAQ_ACCORDION_CORRECT_SCRIPT in text:
                continue
            if FAQ_ACCORDION_INVERTED_SCRIPT in text:
                findings.setdefault(f"{language}_faq_accordion_inverted", []).append(path.name)
            elif ".prod-faq-section" in text and "faq-q'" in text:
                findings.setdefault(f"{language}_faq_accordion_unrecognized", []).append(path.name)
    return findings


def main() -> int:
    findings: dict[str, list[str]] = {}
    summary: dict[str, dict] = {}
    cache = json.loads(CACHE_PATH.read_text(encoding="utf-8")) if CACHE_PATH.exists() else {}
    component_drift, component_cache_gaps = check_component_drift(cache)
    findings.update(component_drift)
    findings.update(check_product_faq_drift())
    findings.update(check_faq_accordion_script())
    if component_cache_gaps:
        findings["shared_component_cache_gaps"] = [
            f"{selector}: {issue}" for selector, issues in component_cache_gaps.items() for issue in issues
        ]
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
    # Informational only (see check_cache_self_identical docstring): mixes real gaps with
    # correctly-preserved brand/code/proper-noun text, so it is reported for human review
    # (Part R) rather than gating CI the way `findings` does.
    cache_self_identical = check_cache_self_identical(cache)
    payload = {
        "summary": summary,
        "finding_counts": {key: len(value) for key, value in findings.items()},
        "findings": findings,
        "informational": {
            "cache_self_identical_translation_counts": {lang: len(items) for lang, items in cache_self_identical.items()},
            "cache_self_identical_translations": cache_self_identical,
        },
    }
    REPORT.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"summary": summary, "finding_counts": payload["finding_counts"], "informational_counts": payload["informational"]["cache_self_identical_translation_counts"]}, ensure_ascii=False, indent=2))
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
