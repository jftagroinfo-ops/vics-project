#!/usr/bin/env python3
"""Generate the localized product-FAQ block for every product page, in every locale.

Governed source chain (see reports/product-faq-localization-2026-08-27.md, Part D):

    data/products.json (product facts: spec, HS code, MOQ, packing, documents)
        + data/localized-copy-cache.json (governed vocabulary: product names, spec
          labels, document-type names -- reused verbatim, not re-translated here)
        + data/product-faq-templates.json (governed question/answer sentence
          templates per locale, with {placeholder} tokens for product variables)
    -> this script (deterministic, offline, no network)
    -> the <!-- PRODUCT FAQ SECTION --> ... <section class="prod-faq-section">
       block's 5 .faq-item children on every locale/<product>.html page

This mirrors, for locales, exactly what scripts/remediate_production_claims.py's
product_faq() already does for the English root pages -- same 5 questions, same
governed product variables, same "do not translate codes/numbers" rule -- so
locale pages reach parity with the current English FAQ instead of carrying the
retired pre-rewrite FAQ content (Phase 6 finding F2).

Only the 5 .faq-item elements are replaced. The section's own heading and
brand-tag (already correctly localized, unrelated to F2) are left untouched.
"""

from __future__ import annotations

import html
import json
from pathlib import Path

from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
CACHE = json.loads((ROOT / "data/localized-copy-cache.json").read_text(encoding="utf-8"))
TEMPLATES = json.loads((ROOT / "data/product-faq-templates.json").read_text(encoding="utf-8"))["keys"]
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")
KEY_ORDER = ("product_faq.spec", "product_faq.hs_moq_packing", "product_faq.container", "product_faq.documents", "product_faq.sample")


class MissingTranslation(Exception):
    pass


# Standardized technical/scientific abbreviations and scale names that stay
# identical in every locale by the site's own established convention (see
# Part F: "do not translate standardized commercial abbreviations" -- MOQ is
# that section's own example). Verified against data/products.json: these are
# exactly the spec labels used somewhere across the 84 products that have no
# governed cache translation, and all are abbreviations/standard names, not
# ordinary prose words that were simply missed.
PRESERVED_LABELS = {"MOQ", "ICUMSA", "FFA", "PH", "SO2", "Lead (Pb)", "COA", "Curcumin"}


def cached(locale: str, source: str) -> str:
    """Look up a governed vocabulary translation. Fails loudly if absent --
    never falls back to raw English silently -- except for the small set of
    standardized abbreviations in PRESERVED_LABELS, which are kept verbatim
    by design in every locale."""
    if source in PRESERVED_LABELS:
        return source
    value = CACHE.get(locale, {}).get(source)
    if value is None:
        raise MissingTranslation(f"{locale}: no governed translation for {source!r}")
    return value


def localized_name(locale: str, product: dict) -> str:
    return cached(locale, product["t"])


def localized_spec_text(locale: str, product: dict) -> str:
    specs = [pair for pair in product["s"] if pair[0] not in {"HS Code", "MOQ"}][:5]
    parts = []
    for label, value in specs:
        translated_label = cached(locale, label)
        parts.append(f"<strong>{html.escape(translated_label, quote=False)}</strong>: {html.escape(value, quote=False)}")
    return "؛ ".join(parts) if locale == "ar" else "; ".join(parts)


def localized_documents(locale: str, names: list[str]) -> str:
    translated = [cached(locale, name) for name in names]
    return "، ".join(translated) if locale == "ar" else ", ".join(translated)


def faq_item(question: str, answer: str) -> str:
    return (
        '<div class="faq-item" style="border-bottom:1px solid rgba(26,60,52,.08)">\n'
        '<div aria-expanded="false" class="faq-q" onclick="var answer=this.nextElementSibling;'
        "var open=answer.classList.toggle('open');this.setAttribute('aria-expanded',String(open));"
        "this.querySelector('.faq-chevron').classList.toggle('rotated',open)\" "
        "onkeydown=\"if(event.key==='Enter'||event.key===' '){event.preventDefault();this.click();}\" "
        'role="button" style="display:flex;justify-content:space-between;align-items:center;'
        "padding:20px 0;cursor:pointer;font-family:'Montserrat',sans-serif;font-weight:700;"
        'font-size:.95rem;color:#1a3c34" tabindex="0">\n'
        f"          {question}\n"
        '          <i class="fa-solid fa-chevron-down faq-chevron" style="color:#3d7030;'
        'font-size:.75rem;transition:transform .3s;flex-shrink:0"></i>\n'
        "</div>\n"
        '<div class="faq-a" style="max-height:0;overflow:hidden;transition:max-height .4s ease;'
        'font-size:.93rem;color:#666;line-height:1.8">\n'
        f'<div style="padding:0 0 20px">{answer}</div>\n'
        "</div>\n"
        "</div>"
    )


def product_faq_items_localized(product: dict, locale: str) -> str:
    name = html.escape(localized_name(locale, product), quote=False)
    trade = product["trade"]
    spec_text = localized_spec_text(locale, product)
    documents = localized_documents(locale, product["compliance"]["documents"])
    conditional = localized_documents(locale, product["compliance"]["conditional_documents"])
    substitutions = {
        "name": name,
        "spec_text": spec_text,
        "hs_code": html.escape(trade["hs_code"], quote=False),
        "moq": html.escape(trade["moq"], quote=False),
        "packaging": html.escape(trade["packaging"], quote=False),
        "container_20ft": html.escape(trade["container_20ft"], quote=False),
        "documents": documents,
        "conditional": conditional,
    }
    items = []
    for key in KEY_ORDER:
        entry = TEMPLATES[key]
        translation = entry["translations"][locale]
        question = translation["question"].format(**substitutions)
        answer = translation["answer"].format(**substitutions)
        items.append(faq_item(question, answer))
    return "\n".join(items)


def replace_faq_items(text: str, new_items: str) -> tuple[str, int]:
    """Replace the 5 .faq-item children of .prod-faq-section, leaving the
    section's own opening markup (brand-tag, heading) and everything outside
    the FAQ items byte-for-byte untouched.

    BeautifulSoup is used only to *locate* the exact first/last .faq-item
    substrings; the actual edit is a plain string replace on the original raw
    text, not a re-serialization of the parsed tree -- re-serializing risks
    silently reformatting unrelated parts of the file (the exact mistake this
    project hit and fixed in Phase 4 on two BeautifulSoup-misparsed files)."""
    soup = BeautifulSoup(text, "html.parser")
    section = soup.select_one(".prod-faq-section")
    if section is None:
        return text, 0
    items = section.select(".faq-item")
    if len(items) != 5:
        return text, 0
    first_raw = str(items[0])
    last_raw = str(items[-1])
    start = text.find(first_raw)
    if start == -1:
        return text, 0
    last_start = text.find(last_raw, start)
    if last_start == -1:
        return text, 0
    end = last_start + len(last_raw)
    if text[start:end].count('class="faq-item"') != 5:
        return text, 0
    new_text = text[:start] + new_items + text[end:]
    return new_text, 1


def main() -> int:
    changed = 0
    errors: list[str] = []
    for product in PRODUCTS:
        for locale in LOCALES:
            path = ROOT / locale / product["u"]
            if not path.exists():
                continue
            text = path.read_text(encoding="utf-8")
            try:
                new_items = product_faq_items_localized(product, locale)
            except MissingTranslation as exc:
                errors.append(f"{path.relative_to(ROOT)}: {exc}")
                continue
            updated, count = replace_faq_items(text, new_items)
            if count and updated != text:
                path.write_text(updated, encoding="utf-8", newline="\n")
                changed += 1
    if errors:
        print(f"FAILED: {len(errors)} missing translations, 0 files written for those.")
        for e in errors[:10]:
            print(" ", e)
        return 1
    print(f"Regenerated product FAQ blocks in {changed} locale pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
