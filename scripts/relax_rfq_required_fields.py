# -*- coding: utf-8 -*-
"""Phase 13 finding: contact.html's RFQ form requires 10 fields before a
buyer can submit, including Port of Discharge and Target Shipment Month -
two details a genuine first-time enquiry often cannot supply yet (the buyer
may not have picked a discharge port, or a firm shipment month, before they
even have a quote to plan around). External B2B RFQ best-practice guidance
is consistent on this: name, email, product and quantity are the fields a
usable first quote needs; everything else should be optional so it does not
block submission.

This script makes exactly two fields optional (Port of Discharge everywhere
it exists; Target Shipment Month, which only exists in the English page)
without deleting either field or losing any information from buyers who do
fill them in. It changes structure only (the `required` attribute and the
visual `*` marker) - no translated label or placeholder text is touched."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOCALES = ["ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi"]

PORT_REQ_MARKER = re.compile(r'(for="port">[^<]*)<span class="req">\*</span>')
PORT_REQUIRED_ATTR = re.compile(r'(name="port"[^>]*?)\s+required(?:="")?')

SHIPMENT_REQ_MARKER = re.compile(r'(for="shipment_month">[^<]*)<span class="req">\*</span>')
SHIPMENT_REQUIRED_ATTR = re.compile(r'(name="shipment_month"[^>]*?)\s+required\b')


def patch(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    changed = []

    new_text, n = PORT_REQ_MARKER.subn(r'\1<span class="opt">(optional)</span>', text)
    if n:
        text = new_text
        changed.append(f"port label marker x{n}")

    new_text, n = PORT_REQUIRED_ATTR.subn(r'\1', text)
    if n:
        text = new_text
        changed.append(f"port required attr x{n}")

    new_text, n = SHIPMENT_REQ_MARKER.subn(r'\1<span class="opt">(optional)</span>', text)
    if n:
        text = new_text
        changed.append(f"shipment_month label marker x{n}")

    new_text, n = SHIPMENT_REQUIRED_ATTR.subn(r'\1', text)
    if n:
        text = new_text
        changed.append(f"shipment_month required attr x{n}")

    if changed:
        path.write_text(text, encoding="utf-8", newline="\n")
    return changed


def main() -> None:
    files = [ROOT / "contact.html"] + [ROOT / loc / "contact.html" for loc in LOCALES]
    for path in files:
        if not path.exists():
            print(f"{path}: MISSING")
            continue
        result = patch(path)
        print(f"{path.relative_to(ROOT)}: {', '.join(result) if result else 'no change'}")


if __name__ == "__main__":
    main()
