from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPLACEMENTS = {
    "50 kg jute bags": "50 kg food-grade BOPP bags",
    "jute bags with an inner liner": "woven PP or BOPP bags with an approved food-grade inner liner",
    "jute-style presentation packs": "premium BOPP presentation packs",
    "50 kg Jute/PP bags": "50 kg BOPP/PP bags",
    "sacs jute de 50 kg": "sacs BOPP de 50 kg",
    "sacs de jute de 50 kg": "sacs BOPP de 50 kg",
    "Sacs Jute/PP de 50 kg": "Sacs BOPP/PP de 50 kg",
    "beg Jute/PP 50 kg": "beg BOPP/PP 50 kg",
    "50 kg Jute/PP බෑග්": "50 kg BOPP/PP බෑග්",
}

for path in ROOT.glob("**/blog*.html"):
    if ".cloudflare-dist" in path.parts:
        continue
    text = path.read_text(encoding="utf-8")
    for old, new in REPLACEMENTS.items():
        text = text.replace(old, new)
    path.write_text(text, encoding="utf-8", newline="")
