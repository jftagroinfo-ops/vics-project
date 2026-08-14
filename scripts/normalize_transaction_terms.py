#!/usr/bin/env python3
"""Normalize samples, payment wording and illustrative document templates."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAFE_PAYMENT = "Payment terms are stated only in the signed Proforma Invoice or Sales Contract after buyer, banking and transaction review. Website examples are illustrative and are not payment instructions."
SAFE_HOME_FAQ = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"How is the minimum order quantity confirmed?","acceptedAnswer":{"@type":"Answer","text":"MOQ and container payload are product-specific planning values. The written quotation confirms packing, payload, route and legal weight limits."}},{"@type":"Question","name":"How are payment terms agreed?","acceptedAnswer":{"@type":"Answer","text":"Payment terms are stated only in the signed Proforma Invoice or sales contract after buyer, banking and transaction review. Website examples are not binding instructions."}},{"@type":"Question","name":"Can a trade buyer request samples?","acceptedAnswer":{"@type":"Answer","text":"Qualified trade buyers may request a standard 250–500g evaluation sample per selected product. Final size, availability, courier cost and dispatch timing are confirmed before shipment."}},{"@type":"Question","name":"When is a Proforma Invoice issued?","acceptedAnswer":{"@type":"Answer","text":"Complete enquiries are reviewed during published business hours. Quotation timing depends on product specification, availability, packing, destination and freight confirmation."}}]}</script>'''


def replace_outer_line(line: str) -> str:
    if "30%" not in line or "70%" not in line:
        return line
    newline = "\n" if line.endswith("\n") else ""
    core = line[:-1] if newline else line
    match = re.match(r'^(\s*<(?P<tag>p|li|td|div)\b[^>]*>).*?(</(?P=tag)>\s*)$', core, flags=re.I)
    if match:
        return f"{match.group(1)}{SAFE_PAYMENT}{match.group(3)}{newline}"
    if "<strong>JFT Agro" in core or "standard terms" in core.lower():
        indent = re.match(r'^\s*', core).group(0)
        return f"{indent}<strong>Payment terms:</strong> {SAFE_PAYMENT}{newline}"
    return line.replace("30%", "[ILLUSTRATIVE ADVANCE %]").replace("70%", "[ILLUSTRATIVE BALANCE %]")


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        # Repair placeholders from early versions of this migration. Percentage
        # values inside CSS are presentation values, not payment terms.
        updated = text.replace("[ILLUSTRATIVE ADVANCE %]", "30%").replace("[ILLUSTRATIVE BALANCE %]", "70%")
        if path.name == "index.html":
            updated = re.sub(r'<script type="application/ld\+json">\s*\{[^<]*"@type":"FAQPage"[^<]*"What is the minimum order quantity for JFT Agro Overseas\?"[^<]*\}\s*</script>', SAFE_HOME_FAQ, updated, count=1, flags=re.S)
        updated = updated.replace("30% Advance + 70% against Scan BL. Established clients may use Irrevocable LC at sight.", SAFE_PAYMENT)
        updated = updated.replace("Standard terms are 30% advance + 70% against Scan Bill of Lading. Established buyers may use 100% Irrevocable LC at sight from top-tier banks.", SAFE_PAYMENT)
        updated = re.sub(r'<div class="faq-a"><p>We work on .*?</p></div>', f'<div class="faq-a"><p>{SAFE_PAYMENT}</p></div>', updated, flags=re.S)
        updated = re.sub(r'<div class="faq-answer">(?=[^<]*(?:30%|30\s*%)).*?</div>', f'<div class="faq-answer">{SAFE_PAYMENT}</div>', updated, flags=re.S)
        updated = re.sub(r'<div class="reg-item"><h4>Payment Terms[^<]*</h4><p>.*?</p></div>', f'<div class="reg-item"><h4>Payment terms</h4><p>{SAFE_PAYMENT}</p></div>', updated, flags=re.S)
        updated = ''.join(replace_outer_line(line) for line in updated.splitlines(keepends=True))
        updated = re.sub(r'100%\s+Irrevocable', 'Irrevocable', updated, flags=re.I)

        if path.name == "blog-how-to-export-india-to-africa.html" and "ILLUSTRATIVE TEMPLATE NOTICE" not in updated:
            notice = ('<div class="tip-box"><strong>ILLUSTRATIVE TEMPLATE NOTICE:</strong> Every company identifier, address, bank, account, SWIFT/BIC, amount, percentage and shipment reference in the templates below is fictional or a placeholder. Do not use it for a shipment or payment. Replace every field and independently verify payment instructions through a known company contact.</div>\n')
            updated = updated.replace('<div class="doc-widget">', notice + '<div class="doc-widget">', 1)

        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="")
            changed += 1
    print(f"Updated {changed} HTML documents")


if __name__ == "__main__":
    main()
