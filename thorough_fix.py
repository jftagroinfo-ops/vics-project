import os
import re

BASE_DIR = r'c:\Users\HP\Downloads\JFT_WEBSITE\vics-project'
SUBDIRS = ['ar', 'fr', 'vi', 'ms', 'id', 'th', 'si', 'ru', 'es', 'pt']

def thorough_fix():
    print("--- Starting Thorough Forensic Fix ---")
    
    # 1. Fix INFRASTRUCTURE typo globally
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                new_content = content.replace('images/INFRASTRUCTURE/INFRASTRUCTURE/', 'images/INFRASTRUCTURE/')
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  - Typo fixed in {os.path.relpath(path, BASE_DIR)}")

    # 2. Fix all subdirectories
    for sub in SUBDIRS:
        sub_path = os.path.join(BASE_DIR, sub)
        if not os.path.exists(sub_path): continue
        
        for file in os.listdir(sub_path):
            if file.endswith('.html'):
                path = os.path.join(sub_path, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # A. Fix component loading
                content = content.replace("'header.html'", "'../header.html'")
                content = content.replace("'footer.html'", "'../footer.html'")
                
                # B. Fix common relative assets that missed the ../
                # Check for images/, products/, css/, js/ at the start of src/href/url
                # We use regex to find src="images/..." and replace with src="../images/..."
                
                def fix_rel(match):
                    attr = match.group(1)
                    val = match.group(2)
                    if val.startswith('http') or val.startswith('#') or val.startswith('../') or val.startswith('/') or val.startswith('mailto:') or val.startswith('tel:'):
                        return match.group(0)
                    return f'{attr}="../{val}"'

                # Fix src="..." and href="..."
                content = re.sub(r'(src|href)="([^"]+)"', fix_rel, content)
                # Fix url('...') in styles
                content = re.sub(r"url\('([^']+)'\)", lambda m: f"url('../{m.group(1)}')" if not (m.group(1).startswith('http') or m.group(1).startswith('../') or m.group(1).startswith('/')) else m.group(0), content)

                with open(path, 'w', encoding='utf-8') as f:
                    f.write(content)
                print(f"  - Repaired all paths in {sub}/{file}")

    print("--- Thorough Fix Complete ---")

if __name__ == "__main__":
    thorough_fix()
