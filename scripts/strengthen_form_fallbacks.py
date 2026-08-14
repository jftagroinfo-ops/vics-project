#!/usr/bin/env python3
"""Keep direct buyer contact paths available when the form provider is unavailable."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
MAIL = "mailto:jftagro.info@gmail.com?subject=Website%20enquiry%20submission%20fallback"
WHATSAPP = "https://wa.me/918425057274"

REPLACEMENTS = {
    '<span>Submission failed. WhatsApp us: <strong>+91 84250 57274</strong></span>':
        f'<span>Automatic submission is unavailable. <a href="{MAIL}">Email us</a> or <a href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">WhatsApp +91 84250 57274</a>.</span>',
    '<span>Submission failed. Please retry or WhatsApp <strong>+91 84250 57274</strong>.</span>':
        f'<span>Automatic submission is unavailable. <a href="{MAIL}">Email us</a> or <a href="{WHATSAPP}" target="_blank" rel="noopener noreferrer">WhatsApp +91 84250 57274</a>.</span>',
    "status.innerHTML = 'Could not send automatically. Please use <a href=\"https://wa.me/918425057274\" target=\"_blank\" rel=\"noopener noreferrer\">WhatsApp +91 84250 57274</a>.';":
        f"status.innerHTML = 'Could not send automatically. <a href=\"{MAIL}\">Email jftagro.info@gmail.com</a> or <a href=\"{WHATSAPP}\" target=\"_blank\" rel=\"noopener noreferrer\">WhatsApp +91 84250 57274</a>.';",
    "formError.innerHTML='We could not record this request. Please retry, or <a href=\"https://wa.me/918425057274\" target=\"_blank\" rel=\"noopener\">contact the sample desk on WhatsApp</a>.';":
        f"formError.innerHTML='We could not record this request. <a href=\"{MAIL}\">Email the sample desk</a> or <a href=\"{WHATSAPP}\" target=\"_blank\" rel=\"noopener noreferrer\">contact us on WhatsApp</a>.';",
    "status.textContent = 'We could not subscribe you right now. Please try again.';":
        f"status.innerHTML = 'Automatic subscription is unavailable. <a href=\"mailto:jftagro.info@gmail.com?subject=Trade%20newsletter%20subscription\">Email your subscription request</a>.';",
    "s.textContent='jftagro.info@gmail.com · WhatsApp +91 84250 57274';":
        f"s.innerHTML='<a href=\"{MAIL}\">jftagro.info@gmail.com</a> · <a href=\"{WHATSAPP}\" target=\"_blank\" rel=\"noopener noreferrer\">WhatsApp +91 84250 57274</a>';",
}


def main() -> int:
    changed = 0
    replacements = 0
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in {".html", ".js"}:
            continue
        if ".git" in path.parts or "reports" in path.parts:
            continue
        original = path.read_text(encoding="utf-8", errors="strict")
        updated = original
        for old, new in REPLACEMENTS.items():
            count = updated.count(old)
            if count:
                updated = updated.replace(old, new)
                replacements += count
        if updated != original:
            path.write_text(updated, encoding="utf-8", newline="")
            changed += 1
    print(f"Added {replacements} direct-contact fallbacks in {changed} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
