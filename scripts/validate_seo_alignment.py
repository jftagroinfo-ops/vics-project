#!/usr/bin/env python3
"""Validate visible SEO content against structured data and cluster rules."""

from __future__ import annotations

import json
import re
from pathlib import Path

from lxml import html


ROOT = Path(__file__).resolve().parent.parent
IGNORED_DIRS = {".git", ".cloudflare", ".cloudflare-dist", ".wrangler", "reports", "__pycache__"}
CLUSTER_LINKS = {
    "editorial-policy.html": {
        "about.html",
        "blog.html",
        "india-agricultural-export-market-data-sources.html",
        "export-documentation.html",
    },
    "india-agricultural-export-market-data-sources.html": {
        "assets/data/india-agricultural-export-market-data-sources-2026.csv",
        "editorial-policy.html",
        "export-documentation.html",
    },
    "blog-certificate-of-analysis-food-imports.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-food-container-loading-inspection-checklist.html",
        "quality-control.html",
        "certificates.html",
        "export-documentation.html",
    },
    "blog-food-container-loading-inspection-checklist.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-certificate-of-analysis-food-imports.html",
        "infrastructure.html",
        "export-documentation.html",
    },
    "blog-how-to-choose-indian-agro-exporter.html": {
        "certificates.html",
        "buyer-security.html",
        "blog-letter-of-credit-food-imports-india.html",
        "blog-how-to-read-proforma-invoice-india-export.html",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-food-container-loading-inspection-checklist.html",
        "export-documentation.html",
    },
    "buyer-security.html": {
        "blog-how-to-choose-indian-agro-exporter.html",
        "blog-letter-of-credit-food-imports-india.html",
        "blog-how-to-read-proforma-invoice-india-export.html",
        "certificates.html",
        "export-documentation.html",
    },
    "certificates.html": {
        "blog-how-to-choose-indian-agro-exporter.html",
        "buyer-security.html",
        "export-documentation.html",
    },
    "quality-control.html": {
        "blog-certificate-of-analysis-food-imports.html",
        "blog-food-container-loading-inspection-checklist.html",
        "export-documentation.html",
    },
    "infrastructure.html": {
        "blog-certificate-of-analysis-food-imports.html",
        "blog-food-container-loading-inspection-checklist.html",
        "export-documentation.html",
    },
    "5-parboiled-rice-ir-64-exporter.html": {
        "blog-ir64-export.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "export-documentation.html",
        "logistics/mundra-rice-exports/",
    },
    "logistics/mundra-rice-exports/index.html": {
        "/1121-basmati-rice-exporter.html",
        "/5-parboiled-rice-ir-64-exporter.html",
        "/export-documentation.html",
        "/blog-food-container-loading-inspection-checklist.html",
        "/port-transit-calculator.html",
        "/logistics/nhava-sheva-agro-exports/",
        "/blog-how-to-write-agro-commodity-purchase-specification.html",
        "/contact.html",
    },
    "blog-how-to-write-agro-commodity-purchase-specification.html": {
        "assets/templates/agro-commodity-purchase-specification-template.txt",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-food-container-loading-inspection-checklist.html",
        "export-documentation.html",
        "buyer-security.html",
    },
    "logistics/nhava-sheva-agro-exports/index.html": {
        "/export-documentation.html",
        "/port-transit-calculator.html",
        "/blog-food-container-loading-inspection-checklist.html",
        "/logistics/mundra-rice-exports/",
        "/contact.html",
    },
    "port-transit-calculator.html": {
        "logistics/nhava-sheva-agro-exports/",
        "logistics/mundra-rice-exports/",
        "export-documentation.html",
        "quote-calculator.html",
    },
    "export-documentation.html": {
        "logistics/nhava-sheva-agro-exports/",
        "contact.html",
    },
    "blog-india-rice-export-sri-lanka-bangladesh.html": {
        "5-parboiled-rice-ir-64-exporter.html",
        "25-silky-sortex-white-exporter.html",
        "100-broken-rice-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "port-transit-calculator.html",
        "export-documentation.html",
        "blog-certificate-of-analysis-food-imports.html",
    },
    "blog-import-indian-agro-kenya-east-africa.html": {
        "chickpeas-kabuli-exporter.html",
        "green-mung-beans-exporter.html",
        "toor-dal-split-pigeon-pea-exporter.html",
        "yellow-peas-matar-exporter.html",
        "export-documentation.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-food-container-loading-inspection-checklist.html",
    },
    "asia-trade.html": {
        "1121-basmati-rice-exporter.html",
        "turmeric-finger-exporter.html",
        "sesame-seeds-naturalhulled-exporter.html",
        "dry-red-chilli-exporter.html",
        "cumin-seeds-jeera-exporter.html",
        "export-documentation.html",
        "blog-india-rice-export-sri-lanka-bangladesh.html",
        "blog-green-mung-beans-export-india-2026.html",
    },
    "moringa-powder-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-certificate-of-analysis-food-imports.html",
        "sample-request.html",
    },
    "senna-leaves-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-certificate-of-analysis-food-imports.html",
        "sample-request.html",
    },
    "henna-powder-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-certificate-of-analysis-food-imports.html",
        "sample-request.html",
    },
    "tamarind-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
        "export-documentation.html",
    },
    "africa-trade.html": {
        "5-parboiled-rice-ir-64-exporter.html",
        "100-broken-rice-exporter.html",
        "1121-white-sella-basmati-exporter.html",
        "sugar-s30-supplier.html",
        "yellow-maize-corn-exporter.html",
        "export-documentation.html",
        "blog-food-container-loading-inspection-checklist.html",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-how-to-import-rice-nigeria-west-africa.html",
        "blog-import-indian-agro-kenya-east-africa.html",
    },
    "yellow-peas-matar-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "psyllium-husk-exporter.html": {
        "blog-psyllium-husk-export-india-2026.html",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "blog-psyllium-husk-export-india-2026.html": {
        "psyllium-husk-exporter.html",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "indian-raisins-kishmish-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "sugar-s30-supplier.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-certificate-of-analysis-food-imports.html",
        "export-documentation.html",
    },
    "blog-ir64-export.html": {
        "5-parboiled-rice-ir-64-exporter.html",
        "10-parboiled-rice-ir-64-exporter.html",
        "100-broken-rice-exporter.html",
        "africa-trade.html",
        "export-documentation.html",
        "quality-control.html",
    },
    "blog-basmati-export-guide.html": {
        "1121-basmati-rice-exporter.html",
        "1121-raw-basmati-rice-exporter.html",
        "1121-steam-basmati-rice-exporter.html",
        "1121-white-sella-basmati-exporter.html",
        "1509-steam-basmati-rice-exporter.html",
        "1509-golden-sella-basmati-exporter.html",
        "1718-steam-basmati-rice-exporter.html",
        "1718-golden-sella-basmati-exporter.html",
        "1401-steam-basmati-rice-exporter.html",
        "1401-sella-basmati-rice-exporter.html",
    },
    "1121-basmati-rice-exporter.html": {
        "1121-raw-basmati-rice-exporter.html",
        "1121-steam-basmati-rice-exporter.html",
        "1121-white-sella-basmati-exporter.html",
        "blog-basmati-export-guide.html",
    },
    "1718-steam-basmati-rice-exporter.html": {
        "1718-golden-sella-basmati-exporter.html",
        "blog-basmati-export-guide.html",
    },
    "1718-golden-sella-basmati-exporter.html": {
        "1718-steam-basmati-rice-exporter.html",
        "blog-basmati-export-guide.html",
    },
    "1401-steam-basmati-rice-exporter.html": {
        "1401-sella-basmati-rice-exporter.html",
        "blog-basmati-export-guide.html",
    },
    "1401-sella-basmati-rice-exporter.html": {
        "1401-golden-sella-basmati-exporter.html",
        "blog-basmati-export-guide.html",
    },
    "uae-trade.html": {
        "1121-basmati-rice-exporter.html",
        "1509-steam-basmati-rice-exporter.html",
        "export-documentation.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-food-container-loading-inspection-checklist.html",
    },
    "europe-trade.html": {
        "blog-basmati-export-guide.html",
        "blog-import-indian-spices-uk-europe.html",
        "export-documentation.html",
        "quality-control.html",
        "blog-certificate-of-analysis-food-imports.html",
    },
    "100-broken-rice-exporter.html": {
        "blog-ir64-export.html",
    },
    "5-silky-sortex-white-exporter.html": {
        "25-silky-sortex-white-exporter.html",
    },
    "25-silky-sortex-white-exporter.html": {
        "5-silky-sortex-white-exporter.html",
    },
    "pr-11-rice-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-certificate-of-analysis-food-imports.html",
    },
    "samba-rice-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
    },
    "blog-india-vs-thailand-rice-comparison.html": {
        "blog-basmati-export-guide.html",
        "blog-ir64-export.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
    },
    "blog-import-duty-indian-rice-by-country.html": {
        "blog-how-to-import-rice-nigeria-west-africa.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
    },
    "blog-how-to-import-rice-nigeria-west-africa.html": {
        "blog-import-duty-indian-rice-by-country.html",
        "export-documentation.html",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-food-container-loading-inspection-checklist.html",
        "africa-trade.html",
        "5-parboiled-rice-ir-64-exporter.html",
        "25-silky-sortex-white-exporter.html",
        "100-broken-rice-exporter.html",
    },
    "wheat-flour-chakki-fresh-atta-exporter.html": {
        "maida-refined-wheat-flour-exporter.html",
        "semolina-sooji-rava-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
        "export-documentation.html",
    },
    "maida-refined-wheat-flour-exporter.html": {
        "wheat-flour-chakki-fresh-atta-exporter.html",
        "semolina-sooji-rava-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "semolina-sooji-rava-exporter.html": {
        "wheat-flour-chakki-fresh-atta-exporter.html",
        "maida-refined-wheat-flour-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "milling-wheat-exporter.html": {
        "wheat-flour-chakki-fresh-atta-exporter.html",
        "maida-refined-wheat-flour-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
    },
    "yellow-maize-corn-exporter.html": {
        "maize-grits-exporter.html",
        "corn-flour-maize-flour-exporter.html",
        "corn-starch-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
    },
    "maize-grits-exporter.html": {
        "yellow-maize-corn-exporter.html",
        "corn-flour-maize-flour-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
    },
    "corn-flour-maize-flour-exporter.html": {
        "corn-starch-exporter.html",
        "maize-grits-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "corn-starch-exporter.html": {
        "corn-flour-maize-flour-exporter.html",
        "yellow-maize-corn-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
    },
    "corn-gluten-meal-exporter.html": {
        "corn-starch-exporter.html",
        "corn-flour-maize-flour-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
    },
    "cumin-seeds-jeera-exporter.html": {
        "blog-cumin-jeera-price-outlook-2026.html",
        "coriander-seeds-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "blog-cumin-jeera-price-outlook-2026.html": {
        "cumin-seeds-jeera-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "coriander-seeds-exporter.html": {
        "blog-coriander-seeds-export-india-2026.html",
        "cumin-seeds-jeera-exporter.html",
        "sample-request.html",
    },
    "blog-coriander-seeds-export-india-2026.html": {
        "coriander-seeds-exporter.html",
        "blog-import-indian-spices-uk-europe.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "turmeric-finger-exporter.html": {
        "blog-turmeric-finger-export-india-2026.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "blog-turmeric-finger-export-india-2026.html": {
        "turmeric-finger-exporter.html",
        "blog-turmeric-market-outlook-2026.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "blog-turmeric-market-outlook-2026.html": {
        "turmeric-finger-exporter.html",
        "blog-turmeric-finger-export-india-2026.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
    },
    "dry-red-chilli-exporter.html": {
        "blog-red-chilli-teja-export-india-2026.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "blog-red-chilli-teja-export-india-2026.html": {
        "dry-red-chilli-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "fennel-seeds-sounff-exporter.html": {
        "fenugreek-seeds-methi-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "fenugreek-seeds-methi-exporter.html": {
        "blog-certificate-of-analysis-food-imports.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "green-cardamom-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "black-pepper-powder-exporter.html": {
        "blog-certificate-of-analysis-food-imports.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "dry-ginger-powder-exporter.html": {
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "black-cumin-seeds-nigella-exporter.html": {
        "cumin-seeds-jeera-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "ajwain-seeds-powder-exporter.html": {
        "blog-certificate-of-analysis-food-imports.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "sesame-seeds-naturalhulled-exporter.html": {
        "blog-sesame-export-2026.html",
        "groundnuts-peanuts-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "blog-sesame-export-2026.html": {
        "sesame-seeds-naturalhulled-exporter.html",
        "groundnuts-peanuts-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "groundnuts-peanuts-exporter.html": {
        "blog-groundnut-peanut-export-india-2026.html",
        "sesame-seeds-naturalhulled-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "blog-groundnut-peanut-export-india-2026.html": {
        "groundnuts-peanuts-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "blog-sgs-inspection-indian-agro-exports.html",
        "sample-request.html",
    },
    "sunflower-seeds-exporter.html": {
        "safflower-seeds-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "safflower-seeds-exporter.html": {
        "sunflower-seeds-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "soya-bean-exporter.html": {
        "soybean-meal-doc-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "soybean-meal-doc-exporter.html": {
        "soya-bean-exporter.html",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "deoiled-rice-bran-dorb-exporter.html": {
        "soybean-meal-doc-exporter.html",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "chickpeas-kabuli-exporter.html": {
        "green-mung-beans-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "green-mung-beans-exporter.html": {
        "blog-green-mung-beans-export-india-2026.html",
        "chickpeas-kabuli-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "blog-green-mung-beans-export-india-2026.html": {
        "green-mung-beans-exporter.html",
        "blog-certificate-of-analysis-food-imports.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
    "toor-dal-split-pigeon-pea-exporter.html": {
        "green-mung-beans-exporter.html",
        "blog-how-to-write-agro-commodity-purchase-specification.html",
        "sample-request.html",
    },
}


def compact(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def element_text(element) -> str:
    return compact(" ".join(element.itertext()))


def visible_faq(document) -> list[tuple[str, str]]:
    pairs = []
    class_match = "contains(concat(' ', normalize-space(@class), ' '), ' {} ')"
    for question in document.xpath(f"//*[{class_match.format('faq-q')}]"):
        answers = question.xpath(
            f"following-sibling::*[1][{class_match.format('faq-a')}]"
        )
        if answers:
            q_text = element_text(question)
            a_text = element_text(answers[0])
            if q_text and a_text:
                pairs.append((q_text, a_text))
    if pairs:
        return pairs
    for details in document.xpath("//details"):
        summaries = details.xpath("./summary[1] | .//summary[1]")
        if not summaries:
            continue
        summary = summaries[0]
        answers = details.xpath(f".//*[{class_match.format('faq-answer')}][1]")
        q_text = element_text(summary)
        if answers:
            a_text = element_text(answers[0])
        else:
            all_text = element_text(details)
            a_text = compact(all_text[len(q_text):]) if all_text.startswith(q_text) else all_text
        if q_text and a_text:
            pairs.append((q_text, a_text))
    return pairs


def schema_objects(document) -> list[dict]:
    objects = []
    for script in document.xpath(
        "//script[translate(@type, 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', "
        "'abcdefghijklmnopqrstuvwxyz')='application/ld+json']"
    ):
        data = json.loads(script.text or "")
        if isinstance(data, dict) and "@graph" in data:
            objects.extend(item for item in data["@graph"] if isinstance(item, dict))
        elif isinstance(data, dict):
            objects.append(data)
    return objects


def main() -> int:
    findings = []
    checked_faq = 0
    for path in sorted(ROOT.rglob("*.html")):
        relative = path.relative_to(ROOT)
        if any(
            part in IGNORED_DIRS
            or part.startswith(".cloudflare-dist")
            or part.startswith("backup_")
            for part in relative.parts
        ):
            continue
        source = path.read_text(encoding="utf-8")
        if "FAQPage" not in source:
            continue
        document = html.fromstring(source)
        visible = visible_faq(document)
        structured_objects = schema_objects(document)
        page_text = compact(
            " ".join(
                document.xpath(
                    "//text()[not(ancestor::script) and not(ancestor::style) "
                    "and not(ancestor::noscript)]"
                )
            )
        ).casefold()
        for obj in structured_objects:
            if obj.get("@type") != "FAQPage":
                continue
            checked_faq += 1
            structured = [
                (
                    compact(str(item.get("name", ""))),
                    compact(str(item.get("acceptedAnswer", {}).get("text", ""))),
                )
                for item in obj.get("mainEntity", [])
            ]
            if visible and structured != visible:
                findings.append(f"FAQ mismatch: {relative.as_posix()}")
            elif not visible and any(
                compact(str(item.get("name", ""))).casefold() not in page_text
                for item in obj.get("mainEntity", [])
            ):
                findings.append(f"FAQ content not visible: {relative.as_posix()}")

    for page_name, required in CLUSTER_LINKS.items():
        path = ROOT / page_name
        document = html.fromstring(path.read_text(encoding="utf-8"))
        links = {href.split("#", 1)[0] for href in document.xpath("//a/@href")}
        for target in sorted(required - links):
            findings.append(f"Missing cluster link: {page_name} -> {target}")
        if page_name != "export-documentation.html" and not {
            "export-documentation.html",
            "/export-documentation.html",
        }.intersection(links):
            findings.append(f"Missing documentation-center link: {page_name}")

    print(f"Validated {checked_faq} FAQPage blocks and {len(CLUSTER_LINKS)} cluster pages.")
    if findings:
        for finding in findings[:50]:
            print(f"- {finding}")
        if len(findings) > 50:
            print(f"- ... and {len(findings) - 50} more")
        return 1
    print("All visible FAQ/schema and cluster-link checks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
