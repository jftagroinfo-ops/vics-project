#!/usr/bin/env python3
"""Convert mislabeled JPEGs and conservatively optimize oversized WebP assets."""

from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
MIN_BYTES = 450_000


def main() -> int:
    optimized = 0
    saved = 0
    for path in sorted((ROOT / "images").rglob("*.webp")):
        original_size = path.stat().st_size
        with Image.open(path) as source:
            actual_format = source.format
            if original_size < MIN_BYTES and actual_format == "WEBP":
                continue
            image = source.convert("RGBA" if "A" in source.getbands() else "RGB")
            width, height = image.size
        temporary = path.with_suffix(".audit-opt.webp")
        image.save(temporary, "WEBP", quality=82, method=6)
        new_size = temporary.stat().st_size
        if new_size < original_size * 0.9:
            temporary.replace(path)
            optimized += 1
            saved += original_size - new_size
            print(f"{path.relative_to(ROOT)}: {actual_format} {width}x{height}, {original_size} -> {new_size}")
        else:
            temporary.unlink()
    print(f"Optimized {optimized} assets; saved {saved / 1024 / 1024:.2f} MB.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
