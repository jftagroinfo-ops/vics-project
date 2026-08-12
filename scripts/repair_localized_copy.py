#!/usr/bin/env python3
"""Repair known machine-translation punctuation and response-time claims."""

from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent.parent
REPLACEMENTS = {
    "fr": {
        "l.'Inde": "l'Inde",
        "d.'Inde": "d'Inde",
        "d.'aneth": "d'aneth",
        "d.'expédition": "d'expédition",
        "d.'exportation": "d'exportation",
        "d.'épices": "d'épices",
        "d.'herbe": "d'herbe",
        "dans les 24 heures": "généralement sous un jour ouvrable",
        "dans les 24\u00a0heures": "généralement sous un jour ouvrable",
    },
    "es": {"en un plazo de 24 horas": "normalmente en un día hábil", "en 24 horas": "normalmente en un día hábil"},
    "id": {"dalam waktu 24 jam": "biasanya dalam satu hari kerja"},
    "ms": {"India.'s": "India's", "dalam masa 24 jam": "biasanya dalam satu hari bekerja"},
    "pt": {"em 24 horas": "normalmente em um dia útil"},
    "ru": {"в течение 24 часов": "обычно в течение одного рабочего дня"},
    "vi": {"trong vòng 24 giờ": "thường trong vòng một ngày làm việc"},
}


def main() -> int:
    changed = 0
    for locale, replacements in REPLACEMENTS.items():
        for path in (ROOT / locale).glob("*.html"):
            text = path.read_text(encoding="utf-8", errors="replace")
            updated = text
            for source, target in replacements.items():
                updated = re.sub(re.escape(source), target, updated, flags=re.I)
            if updated != text:
                path.write_text(updated, encoding="utf-8", newline="\n")
                changed += 1
    print(f"Repaired localized copy in {changed} pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
