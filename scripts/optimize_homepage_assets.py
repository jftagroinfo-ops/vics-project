#!/usr/bin/env python3
"""Create deterministic, display-sized homepage image derivatives."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "images" / "homepage"
THUMBS = SOURCE / "thumbs"
BADGES = ("FSSAI", "STAR HOUSE", "APEDA", "SPICES_BOARD", "MSME", "AEO", "IEC", "DGFT", "COFFEE_BOARD")


def save_scaled(source: Path, destination: Path, size: tuple[int, int], quality: int = 82) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        converted = image.convert("RGBA")
        converted.thumbnail(size, Image.Resampling.LANCZOS)
        background = Image.new("RGBA", converted.size, "white")
        background.alpha_composite(converted)
        background.convert("RGB").save(destination, "WEBP", quality=quality, method=6)


def save_badge(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        converted = image.convert("RGBA")
        converted.thumbnail((220, 115), Image.Resampling.LANCZOS)
        canvas = Image.new("RGB", (240, 135), "white")
        canvas.paste(converted, ((240 - converted.width) // 2, (135 - converted.height) // 2), converted)
        canvas.save(destination, "WEBP", quality=82, method=6)


def main() -> None:
    for name in BADGES:
        save_badge(SOURCE / f"{name}.webp", THUMBS / f"{name}.webp")
    save_scaled(ROOT / "images" / "Farm.webp", SOURCE / "farm-home.webp", (900, 900), quality=84)
    save_scaled(ROOT / "images" / "jft logo.png", ROOT / "images" / "jft-logo-display.webp", (400, 200), quality=88)
    with Image.open(SOURCE / "export-trust-hero-v2.webp") as hero:
        ImageOps.fit(hero.convert("RGB"), (1200, 630), Image.Resampling.LANCZOS).save(
            SOURCE / "export-trust-og.webp", "WEBP", quality=86, method=6
        )
    print(f"Generated {len(BADGES) + 3} optimized homepage assets.")


if __name__ == "__main__":
    main()
