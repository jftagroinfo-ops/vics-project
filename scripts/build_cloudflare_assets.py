#!/usr/bin/env python3
"""Build the static asset directory consumed by the Cloudflare Worker."""

from __future__ import annotations

import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / ".cloudflare-dist-next"

PUBLIC_DIRECTORIES = (
    ".well-known",
    "ar",
    "assets",
    "es",
    "fr",
    "id",
    "images",
    "logistics",
    "ms",
    "products",
    "pt",
    "ru",
    "si",
    "th",
    "vi",
)

ROOT_SUFFIXES = {".html", ".css", ".js"}
ROOT_FILES = {
    ".nojekyll",
    "BingSiteAuth.xml",
    "d5ab72c3785258477f77b42bfe4201cb.txt",
    "favicon.ico",
    "manifest.json",
    "news.json",
    "robots.txt",
    "sitemap.xml",
}
RUNTIME_DATA = {
    "packing-reference-data.json",
    "port-transit-reference-data.json",
    "products.json",
    "quote-market-rates.json",
}

# Phase 35: exclude accidental public-template artifacts from the built asset set.
EXCLUDED_ROOT_FILES = {
    "product-page-template.html",
}


def copy_file(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main() -> None:
    if OUTPUT.exists():
        resolved = OUTPUT.resolve()
        if resolved.parent != ROOT.resolve() or resolved.name != ".cloudflare-dist-next":
            raise RuntimeError(f"Refusing to replace unexpected path: {resolved}")
        shutil.rmtree(resolved)
    OUTPUT.mkdir()

    for source in ROOT.iterdir():
        if source.is_file() and (source.suffix.lower() in ROOT_SUFFIXES or source.name in ROOT_FILES):
            if source.name in EXCLUDED_ROOT_FILES:
                continue
            copy_file(source, OUTPUT / source.name)

    for directory in PUBLIC_DIRECTORIES:
        source = ROOT / directory
        if not source.is_dir():
            raise FileNotFoundError(source)
        shutil.copytree(source, OUTPUT / directory)

    for filename in RUNTIME_DATA:
        copy_file(ROOT / "data" / filename, OUTPUT / "data" / filename)

    copy_file(ROOT / ".cloudflare" / "_headers", OUTPUT / "_headers")

    required = (
        "index.html",
        "robots.txt",
        "sitemap.xml",
        "editorial-policy.html",
        "india-agricultural-export-market-data-sources.html",
        "logistics/mundra-rice-exports/index.html",
        "logistics/nhava-sheva-agro-exports/index.html",
        "assets/data/india-agricultural-export-market-data-sources-2026.csv",
        "data/products.json",
        "_headers",
    )
    missing = [name for name in required if not (OUTPUT / name).is_file()]
    if missing:
        raise RuntimeError(f"Asset build is missing required files: {missing}")

    forbidden = ("reports", "scripts", "docs", "localized-copy-cache.json", "localization-review.json")
    leaked = [name for name in forbidden if (OUTPUT / name).exists()]
    if leaked:
        raise RuntimeError(f"Internal files leaked into asset build: {leaked}")

    files = [path for path in OUTPUT.rglob("*") if path.is_file()]
    total_bytes = sum(path.stat().st_size for path in files)
    print(f"Built {len(files)} public assets ({total_bytes / 1024 / 1024:.1f} MiB) at {OUTPUT}")


if __name__ == "__main__":
    main()
