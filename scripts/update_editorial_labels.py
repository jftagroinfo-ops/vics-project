from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [ROOT / "index.html"] + [ROOT / locale / "index.html" for locale in ("id", "ms", "pt", "si", "th", "vi")]

for path in FILES:
    text = path.read_text(encoding="utf-8")
    text = text.replace("Temporary illustrative image", "JFT Agro-Export Workflow")
    text = text.replace("JFT Agro • Representative export workflow", "JFT Agro-Export Workflow")
    text = text.replace("Illustrative rice sample inspection", "Representative rice sample inspection")
    text = text.replace("Illustrative export packing line filling and sealing plain food-grade sacks", "Representative export packing line filling and sealing food-grade PP sacks")
    text = text.replace("Illustrative warehouse container-loading workflow", "Representative warehouse container-loading workflow")
    path.write_text(text, encoding="utf-8", newline="")
