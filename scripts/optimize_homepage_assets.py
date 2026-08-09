#!/usr/bin/env python3
"""Create deterministic, display-sized homepage image derivatives."""

from __future__ import annotations

from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "images" / "homepage"
THUMBS = SOURCE / "thumbs"
BADGES = ("FSSAI", "STAR HOUSE", "APEDA", "SPICES_BOARD", "MSME", "AEO", "IEC", "DGFT", "COFFEE_BOARD")


def save_scaled(source: Path, destination: Path, size: tuple[int, int], quality: int = 82) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image.thumbnail(size, Image.Resampling.LANCZOS)
        image.convert("RGB").save(destination, "WEBP", quality=quality, method=6)


def main() -> None:
    for name in BADGES:
        save_scaled(SOURCE / f"{name}.webp", THUMBS / f"{name}.webp", (240, 135))
    save_scaled(ROOT / "images" / "Farm.webp", SOURCE / "farm-home.webp", (900, 900), quality=84)
    print(f"Generated {len(BADGES) + 1} optimized homepage assets.")


if __name__ == "__main__":
    main()
