from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CSS = ROOT / "jft-design-system.css"
GRID_MARKER = 'margin-top:34px'


def main() -> int:
    product_pages = sorted(ROOT.glob("*-exporter.html"))
    affected = [page for page in product_pages if GRID_MARKER in page.read_text(encoding="utf-8")]
    css = CSS.read_text(encoding="utf-8")
    required_rules = (
        '.jft-info-grid[style*="margin-top:34px"]',
        "grid-template-columns: repeat(auto-fit,minmax(220px,1fr))",
        "background: #fff",
        "color: var(--navy)",
        "color: #59645f",
        "font-size: clamp(1.8rem,3.2vw,2.65rem)",
    )
    missing = [rule for rule in required_rules if rule not in css]
    if len(affected) != 15:
        print(f"Expected 15 buyer-brief product pages; found {len(affected)}")
        return 1
    if missing:
        print("Missing buyer-brief CSS rules: " + ", ".join(missing))
        return 1
    print("Buyer-brief card validation passed for 15 product pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
