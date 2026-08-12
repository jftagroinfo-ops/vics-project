#!/usr/bin/env python3
"""Apply reviewed English title and description improvements without reserializing HTML."""

from pathlib import Path
import html
import re

ROOT = Path(__file__).resolve().parent.parent

TITLES = {
    "index.html": "Indian Rice & Spice Exporter | JFT Agro Star Export House",
    "products.html": "Indian Rice, Spices & Grains Catalogue | JFT Agro",
    "faq.html": "Agro Export FAQ: Orders, Payments & Shipping | JFT Agro",
    "blog-apeda-registration-indian-exporter-explained.html": "APEDA Registration for Indian Exporters | Buyer Guide",
    "blog-bill-of-lading-explained-importers.html": "Bill of Lading Guide for First-Time Importers | JFT Agro",
    "blog-cumin-jeera-price-outlook-2026.html": "Indian Cumin Price Outlook 2026 | Importer Guide",
    "blog-green-mung-beans-export-india-2026.html": "Green Mung Bean Export from India 2026 | Buyer Guide",
    "blog-groundnut-peanut-export-india-2026.html": "Groundnut Export from India 2026 | Buyer Guide",
    "blog-how-to-choose-indian-agro-exporter.html": "How to Choose an Indian Agro Exporter | Buyer Checklist",
    "blog-how-to-export-india-to-africa.html": "Exporting from India to Africa: Documents & Payment Guide",
    "blog-how-to-import-rice-nigeria-west-africa.html": "Import Rice from India to West Africa | Buyer Guide",
    "blog-how-to-read-proforma-invoice-india-export.html": "How to Read an Indian Export Proforma Invoice | JFT Agro",
    "blog-import-duty-indian-rice-by-country.html": "Indian Rice Import Duties by Country 2026 | Buyer Guide",
    "blog-import-indian-agro-kenya-east-africa.html": "Import Indian Agro Products to Kenya | Duties & Documents",
    "blog-india-rice-export-sri-lanka-bangladesh.html": "India Rice Exports to Sri Lanka & Bangladesh | 2026 Guide",
    "blog-india-vs-thailand-rice-comparison.html": "Indian vs Thai Rice: 2026 Importer Comparison | JFT Agro",
    "blog-ir64-export.html": "IR64 Parboiled Rice Export Grades & Markets | 2026 Guide",
    "blog-letter-of-credit-food-imports-india.html": "Letters of Credit for Food Imports from India | Buyer Guide",
    "blog-psyllium-husk-export-india-2026.html": "Psyllium Husk Export from India 2026 | Buyer Guide",
    "blog-red-chilli-teja-export-india-2026.html": "Indian Red Chilli Export 2026: Teja & Guntur Grades",
    "blog-sgs-inspection-indian-agro-exports.html": "Third-Party Inspection for Indian Agro Exports | Guide",
    "blog-top-indian-agro-commodities-import-2026.html": "Top Indian Agro Commodities to Import in 2026 | Guide",
    "blog-turmeric-finger-export-india-2026.html": "Indian Turmeric Finger Export 2026 | Grade Guide",
}

DESCRIPTIONS = {
    "blog-how-to-choose-indian-agro-exporter.html": "Evaluate Indian agro exporters with a practical buyer checklist covering registrations, specifications, inspection, payment terms and shipment controls.",
    "blog-how-to-export-india-to-africa.html": "Guide to exporting goods from India to Africa, including commercial documents, payment structures, shipment planning and importer due diligence.",
    "blog-how-to-import-rice-nigeria-west-africa.html": "Guide for West African rice importers covering Indian grades, documentation, destination procedures, payment terms and common sourcing mistakes.",
    "blog-import-duty-indian-rice-by-country.html": "Compare indicative Indian rice import-duty considerations by destination and learn what to confirm with a licensed customs adviser before contracting.",
    "blog-import-indian-spices-uk-europe.html": "Checklist for importing Indian spices into the UK and EU, covering classification, pesticide MRLs, contaminants, labels and supplier controls.",
    "blog-india-vs-thailand-rice-comparison.html": "Compare Indian and Thai rice by variety, specification, market use, availability and commercial considerations for international buyers in 2026.",
    "blog-top-indian-agro-commodities-import-2026.html": "Explore ten Indian agro commodities for import in 2026, with demand context, sourcing considerations, specifications and buyer due diligence.",
    "blog-turmeric-finger-export-india-2026.html": "Compare Indian turmeric finger origins, curcumin ranges, commercial specifications, testing considerations and sourcing controls for importers.",
    "shipment-tracker.html": "Validate an ISO 6346 container number and open the relevant carrier's official tracking portal using a container, Bill of Lading or booking reference.",
}


def main() -> int:
    changed = 0
    for name in sorted(set(TITLES) | set(DESCRIPTIONS)):
        path = ROOT / name
        text = path.read_text(encoding="utf-8")
        updated = text
        if name in TITLES:
            updated, count = re.subn(r"<title[^>]*>.*?</title>", f"<title>{html.escape(TITLES[name], quote=False)}</title>", updated, count=1, flags=re.I | re.S)
            if count != 1:
                raise RuntimeError(f"Expected one title in {name}")
        if name in DESCRIPTIONS:
            replacement = f'<meta name="description" content="{html.escape(DESCRIPTIONS[name], quote=True)}">'
            updated, count = re.subn(r"<meta\s+name=[\"']description[\"'][^>]*>", replacement, updated, count=1, flags=re.I | re.S)
            if count != 1:
                raise RuntimeError(f"Expected one description in {name}")
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="\n")
            changed += 1
    print(f"Optimized reviewed metadata on {changed} English pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
