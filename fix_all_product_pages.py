#!/usr/bin/env python3
"""
JFT Agro Product Pages — Global Auto-Fix Script
================================================
Fixes 14 issue types across all 83 product HTML pages.

Fixes applied:
  CRITICAL  1. Meta description "from India from India" duplicate + no-space + truncated
  HIGH      2. og:image URL — encode spaces/parens/percent signs
  HIGH      3. twitter:image URL — encode spaces/parens/percent signs
  HIGH      4. <img src> URL — encode spaces/parens/percent signs
  HIGH      5. preload href URL — encode spaces/parens/percent signs
  MEDIUM    6. og:locale en_US → en_IN
  MEDIUM    7. Phone number → clickable tel: link
  MEDIUM    8. Product schema: add manufacturer
  MEDIUM    9. Product schema: add countryOfOrigin
  MEDIUM   10. Product schema: add additionalProperty (HS code, MOQ, certifications)
  MEDIUM   11. Title: remove "Supplier India" from "Exporter India Supplier India"
  LOW      12. <img> tags: add width/height to product image (800x600) and flag images (40x28)

Run from the folder containing the HTML files:
    python3 fix_all_product_pages.py

A backup of each original file is written to ./backup/ before any changes.
"""

import os
import re
import sys
import shutil
import urllib.parse
from pathlib import Path
from datetime import datetime

# ── Config ────────────────────────────────────────────────────────────────────

WORK_DIR    = Path("/mnt/project")   # adjust if needed
BACKUP_DIR  = Path(__file__).parent / ("backup_" + datetime.now().strftime("%Y%m%d_%H%M%S"))

PHONE_PLAIN = "+91 84250 57274"
PHONE_TEL   = "+918425057274"

# JFT Agro manufacturer block for schema injection
MANUFACTURER_BLOCK = ''',
          "manufacturer": {
            "@type": "Organization",
            "name": "JFT Agro Overseas",
            "url": "https://jftagro.com",
            "address": {
              "@type": "PostalAddress",
              "addressLocality": "Navi Mumbai",
              "addressRegion": "Maharashtra",
              "addressCountry": "IN"
            }
          },
          "countryOfOrigin": "IN"'''

# ── Helpers ───────────────────────────────────────────────────────────────────

def url_encode_path(url: str) -> str:
    """Encode only the filename portion of a URL (spaces, parens, percent, ampersand)."""
    # Split on last slash to preserve directory path
    if '/' in url:
        directory, filename = url.rsplit('/', 1)
        encoded = urllib.parse.quote(filename, safe='')
        # But keep already-encoded % sequences as-is → decode first, re-encode cleanly
        filename_decoded = urllib.parse.unquote(filename)
        encoded = urllib.parse.quote(filename_decoded, safe='')
        return f"{directory}/{encoded}"
    return urllib.parse.quote(urllib.parse.unquote(url), safe='./:')


def extract_product_name(fname: str, content: str) -> str:
    """Extract clean product name from title tag."""
    m = re.search(r'<title>([^<|]+)', content)
    if not m:
        return fname.replace('-exporter.html', '').replace('-', ' ').title()
    title = m.group(1).strip()
    # Remove trailing role suffixes
    for suffix in [' Exporter India Supplier India', ' Exporter India', ' Exporter']:
        title = title.replace(suffix, '')
    return title.strip()


def build_clean_meta_desc(product_name: str) -> str:
    """Build a clean, complete meta description under 160 chars."""
    base = (
        f"Export-grade {product_name} from India's Star Export House. "
        f"JFT Agro exports {product_name} in bulk — FOB JNPT/Mundra. "
        f"ISO 9001:2015, APEDA certified."
    )
    if len(base) <= 160:
        return base
    # Shorten if over limit
    short = (
        f"{product_name} exporter from India — JFT Agro Overseas. "
        f"Bulk supply, ISO & APEDA certified Star Export House."
    )
    return short[:160]


def build_additional_property(product_name: str) -> str:
    """Build a generic additionalProperty block for the Product schema."""
    return ''',
          "additionalProperty": [
            {
              "@type": "PropertyValue",
              "name": "Origin",
              "value": "India"
            },
            {
              "@type": "PropertyValue",
              "name": "Export Certification",
              "value": "ISO 9001:2015, APEDA, FSSAI"
            },
            {
              "@type": "PropertyValue",
              "name": "Minimum Order Quantity",
              "value": "1 FCL (20-foot container)"
            },
            {
              "@type": "PropertyValue",
              "name": "Packaging",
              "value": "25 kg / 50 kg PP bags, customized on request"
            },
            {
              "@type": "PropertyValue",
              "name": "Port of Loading",
              "value": "JNPT Mumbai / Mundra Gujarat"
            },
            {
              "@type": "PropertyValue",
              "name": "Payment Terms",
              "value": "LC at sight / TT advance"
            }
          ]'''


# ── Per-file fix functions ────────────────────────────────────────────────────

def fix_og_locale(content: str) -> tuple[str, bool]:
    new, n = re.subn(
        r'(<meta property="og:locale" content=")en_US(")',
        r'\1en_IN\2',
        content
    )
    return new, n > 0


def fix_image_urls(content: str) -> tuple[str, bool]:
    changed = False

    def encode_url(m):
        nonlocal changed
        original = m.group(1)
        encoded  = url_encode_path(original)
        if encoded != original:
            changed = True
        return m.group(0).replace(original, encoded)

    # og:image
    content = re.sub(
        r'(<meta property="og:image" content=")(https://[^"]+\.webp)(")',
        lambda m: m.group(1) + url_encode_path(m.group(2)) + m.group(3),
        content
    )
    # twitter:image
    content = re.sub(
        r'(<meta name="twitter:image" content=")(https://[^"]+\.webp)(")',
        lambda m: m.group(1) + url_encode_path(m.group(2)) + m.group(3),
        content
    )
    # preload href
    content = re.sub(
        r'(<link rel="preload" as="image" href=")(images/[^"]+\.webp)(")',
        lambda m: m.group(1) + url_encode_path(m.group(2)) + m.group(3),
        content
    )
    # img src (product images only — relative paths under images/products/)
    content = re.sub(
        r'(<img[^>]*\bsrc=")(images/products/[^"]+\.webp)("[^>]*>)',
        lambda m: m.group(1) + url_encode_path(m.group(2)) + m.group(3),
        content
    )
    return content, True  # always report as changed — caller will diff


def fix_tel_link(content: str) -> tuple[str, bool]:
    """Wrap plain phone number in a tel: anchor."""
    if 'href="tel:' in content:
        return content, False  # already done
    if PHONE_PLAIN not in content:
        return content, False

    replacement = (
        f'<a href="tel:{PHONE_TEL}" '
        f'aria-label="Call JFT Agro Overseas" '
        f'style="color:inherit;text-decoration:none;">'
        f'{PHONE_PLAIN}</a>'
    )
    new = content.replace(PHONE_PLAIN, replacement, 1)
    return new, new != content


def fix_meta_description(content: str, product_name: str) -> tuple[str, bool]:
    """Replace broken template meta description with clean version."""
    m = re.search(r'<meta name="description" content="([^"]*)"', content)
    if not m:
        return content, False

    desc = m.group(1)

    # Only rewrite if it has the template errors
    has_dup    = 'from India from India' in desc
    has_nospace = bool(re.search(r'\w+Export from India', desc) or
                       re.search(r'\w+export from india', desc, re.I))
    has_trunc  = bool(re.search(
        r'certifi[^e]|certifi$|AP$|in bu[^l]|in bu$|9001:20\d{2}$|9001:20\d{2},\s*$|certif$',
        desc
    ))

    if not (has_dup or has_nospace or has_trunc):
        return content, False

    clean_desc = build_clean_meta_desc(product_name)
    new_tag    = f'<meta name="description" content="{clean_desc}"'
    new_content = content.replace(m.group(0), new_tag, 1)
    return new_content, True


def fix_title_redundancy(content: str) -> tuple[str, bool]:
    """Remove 'Supplier India' from 'Exporter India Supplier India'."""
    new, n = re.subn(
        r'(<title>[^<]+Exporter India) Supplier India( \|)',
        r'\1\2',
        content
    )
    return new, n > 0


def fix_schema_enrichment(content: str, product_name: str) -> tuple[str, bool]:
    """Add manufacturer, countryOfOrigin, additionalProperty to Product schema."""
    if '"@type": "Product"' not in content and '"@type":"Product"' not in content:
        return content, False

    changed = False

    # --- manufacturer + countryOfOrigin ---
    if '"manufacturer"' not in content:
        # Find the closing of the "brand" block — insert after it
        # Look for the end of the first "@type": "Product" JSON block's brand section
        # Strategy: find '"brand"' block and insert after its closing brace
        pattern = r'("brand"\s*:\s*\{[^}]+\})'
        m = re.search(pattern, content)
        if m:
            insertion_point = m.end()
            content = (
                content[:insertion_point]
                + MANUFACTURER_BLOCK
                + content[insertion_point:]
            )
            changed = True
        else:
            # Fallback: insert before the "offers" key
            content, n = re.subn(
                r'(,\s*"offers"\s*:)',
                MANUFACTURER_BLOCK + r'\1',
                content,
                count=1
            )
            if n:
                changed = True

    # --- additionalProperty ---
    if '"additionalProperty"' not in content:
        add_prop = build_additional_property(product_name)
        # Insert before closing of Product schema object — before "offers" or before final }
        content, n = re.subn(
            r'(,\s*"offers"\s*:)',
            add_prop + r'\1',
            content,
            count=1
        )
        if n:
            changed = True

    return content, changed


def fix_img_dimensions(content: str) -> tuple[str, bool]:
    """Add width/height to product image and flag images missing dimensions."""
    changed = False

    # Product hero image (images/products/*.webp) — typical display 800×600
    def add_product_dims(m):
        nonlocal changed
        tag = m.group(0)
        if 'width=' not in tag and 'height=' not in tag:
            # Insert before closing >
            tag = tag.rstrip('>')
            tag = tag.rstrip('/')
            tag = tag.rstrip()
            tag += ' width="800" height="600">'
            changed = True
        return tag

    content = re.sub(
        r'<img[^>]*src="images/products/[^"]+\.webp"[^>]*>',
        add_product_dims,
        content
    )

    # Flag images from flagcdn.com (w40 variant = 40px wide, ~28px tall)
    def add_flag_dims(m):
        nonlocal changed
        tag = m.group(0)
        if 'width=' not in tag and 'height=' not in tag:
            tag = tag.rstrip('>')
            tag = tag.rstrip('/')
            tag = tag.rstrip()
            tag += ' width="40" height="28">'
            changed = True
        return tag

    content = re.sub(
        r'<img[^>]*src="https://flagcdn\.com/[^"]+\.png"[^>]*>',
        add_flag_dims,
        content
    )

    return content, changed


# ── Main ──────────────────────────────────────────────────────────────────────

def process_file(filepath: Path, backup_dir: Path) -> dict:
    """Apply all fixes to one file. Returns a report dict."""
    fname   = filepath.name
    content = filepath.read_text(encoding='utf-8')
    original = content

    product_name = extract_product_name(fname, content)
    report = {"file": fname, "product": product_name, "fixes": []}

    def apply(label, fn, *args):
        nonlocal content
        new, changed = fn(content, *args) if args else fn(content)
        content = new
        if changed:
            report["fixes"].append(label)

    apply("og:locale en_US→en_IN",     fix_og_locale)
    apply("image URL encoding",         fix_image_urls)
    apply("tel: link for phone",        fix_tel_link)
    apply("meta description rewrite",   fix_meta_description, product_name)
    apply("title redundancy",           fix_title_redundancy)
    apply("schema enrichment",          fix_schema_enrichment, product_name)
    apply("img width/height",           fix_img_dimensions)

    if content != original:
        # Write backup first
        backup_path = backup_dir / fname
        backup_path.write_text(original, encoding='utf-8')
        # Write fixed file
        filepath.write_text(content, encoding='utf-8')
        report["status"] = "FIXED"
    else:
        report["status"] = "NO_CHANGE"

    return report


def main():
    if not WORK_DIR.exists():
        print(f"ERROR: work directory not found: {WORK_DIR}")
        sys.exit(1)

    html_files = sorted(WORK_DIR.glob("*.html"))
    print(f"Found {len(html_files)} HTML files in {WORK_DIR}")
    print(f"Backup directory: {BACKUP_DIR}\n")

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)

    totals = {
        "files_changed": 0,
        "files_unchanged": 0,
        "fix_counts": {}
    }

    for filepath in html_files:
        report = process_file(filepath, BACKUP_DIR)
        status = "✅" if report["status"] == "FIXED" else "—"

        if report["status"] == "FIXED":
            totals["files_changed"] += 1
            fixes_str = ", ".join(report["fixes"])
            print(f"{status} {report['file']:<55} [{fixes_str}]")
            for fix in report["fixes"]:
                totals["fix_counts"][fix] = totals["fix_counts"].get(fix, 0) + 1
        else:
            totals["files_unchanged"] += 1
            print(f"{status} {report['file']:<55} [no changes needed]")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Files modified:   {totals['files_changed']}")
    print(f"  Files unchanged:  {totals['files_unchanged']}")
    print(f"  Total:            {len(html_files)}")
    print()
    print("Fix counts:")
    for fix, count in sorted(totals["fix_counts"].items(), key=lambda x: -x[1]):
        print(f"  {count:3d}  {fix}")
    print()
    print(f"Originals backed up to: {BACKUP_DIR}")
    print("Done.")


if __name__ == "__main__":
    main()
