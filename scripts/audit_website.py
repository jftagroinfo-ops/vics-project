import os
import re
from urllib.parse import unquote
from bs4 import BeautifulSoup

# Configuration
BASE_DIR = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
IGNORE_DIRS = ['.git', '.github', 'images', 'assets', 'tools']
SKIP_FILES = {
    'footer.html',
    'header.html',
    'inner-page-hero-snippet.html',
    'seo-universal-head-snippet.html',
    'yandex_3fbd4b91e2017518.html'
}


def is_renderable_html(content):
    lower = content.lower()
    return '<html' in lower or '<!doctype' in lower

def audit_website():
    print("--- Starting Professional Website Audit ---")
    
    all_files = []
    for root, dirs, files in os.walk(BASE_DIR):
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
        for file in files:
            if file.endswith('.html'):
                all_files.append(os.path.join(root, file))
    
    print(f"Total HTML files found: {len(all_files)}")
    
    errors = {
        "broken_links": [],
        "missing_images": [],
        "seo_missing_desc": [],
        "seo_missing_title": [],
        "seo_missing_canonical": [],
        "missing_header_footer": [],
        "broken_js_css": []
    }

    # Build a set of all valid files for link checking
    valid_files = set()
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            rel_path = os.path.relpath(os.path.join(root, file), BASE_DIR).replace('\\', '/')
            valid_files.add(rel_path)

    for file_path in all_files:
        rel_file_path = os.path.relpath(file_path, BASE_DIR).replace('\\', '/')
        if os.path.basename(rel_file_path) in SKIP_FILES:
            continue

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            if not is_renderable_html(content):
                continue
            soup = BeautifulSoup(content, 'html.parser')
            
            # 1. SEO Checks
            title = soup.find('title')
            if not title or not title.text.strip():
                errors["seo_missing_title"].append(rel_file_path)
            
            desc = soup.find('meta', attrs={"name": "description"})
            if not desc or not desc.get('content'):
                errors["seo_missing_desc"].append(rel_file_path)

            canonical = soup.find('link', attrs={"rel": "canonical"})
            if not canonical:
                errors["seo_missing_canonical"].append(rel_file_path)

            # 2. Header/Footer injection checks
            # Usually injected via <div id="header-placeholder"> or similar
            if 'header-placeholder' not in content and 'fetch("header.html")' not in content:
                 # Check if it's a small helper file
                 if len(content) > 2000: 
                    errors["missing_header_footer"].append(f"{rel_file_path} (Header)")

            # 3. Image Checks
            imgs = soup.find_all('img')
            for img in imgs:
                src = img.get('src')
                if src and not src.startswith('http') and not src.startswith('data:'):
                    clean_src = src.split('?')[0].split('#')[0]
                    clean_src_decoded = unquote(clean_src)
                    if '/' in rel_file_path:
                        img_rel = os.path.normpath(os.path.join(os.path.dirname(rel_file_path), clean_src_decoded)).replace('\\', '/')
                    else:
                        img_rel = clean_src_decoded

                    if img_rel not in valid_files and clean_src_decoded not in valid_files and clean_src not in valid_files:
                        errors["missing_images"].append(f"{rel_file_path} -> {src}")

            # 4. Internal Link Checks
            links = soup.find_all('a')
            for link in links:
                href = link.get('href')
                if href and not href.startswith('http') and not href.startswith('#') and not href.lower().startswith('mailto:') and not href.lower().startswith('tel:') and not href.lower().startswith('javascript:'):
                    clean_href = href.split('?')[0].split('#')[0]
                    if not clean_href:
                        continue
                    clean_href_decoded = unquote(clean_href)
                    if '/' in rel_file_path:
                        link_rel = os.path.normpath(os.path.join(os.path.dirname(rel_file_path), clean_href_decoded)).replace('\\', '/')
                    else:
                        link_rel = clean_href_decoded
                    
                    candidate_paths = {link_rel, clean_href_decoded, clean_href, f'{clean_href_decoded}index.html', f'{clean_href}index.html'}
                    if not candidate_paths & valid_files:
                        errors["broken_links"].append(f"{rel_file_path} -> {href}")

    # Print Results
    print("\n--- Audit Results ---")
    for key, val in errors.items():
        if val:
            print(f"\n[!] {key.upper()} ({len(val)} items):")
            # Limit to first 10 for brevity
            for item in val[:10]:
                print(f"  - {item}")
            if len(val) > 10:
                print(f"  ... and {len(val)-10} more.")
        else:
            print(f"\n[OK] {key.upper()}")

if __name__ == "__main__":
    audit_website()
