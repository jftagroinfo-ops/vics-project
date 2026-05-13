import os
import re

BASE_DIR = r'c:\Users\HP\Downloads\JFT_WEBSITE\vics-project'

def polish_website():
    print("--- Finalizing Polish & Quality Assurance ---")
    
    # 1. Fix the "images/../images/" ugly path loop
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                new_content = content.replace('images/../images/', 'images/')
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  - Cleaned up path loop in {os.path.relpath(path, BASE_DIR)}")

    # 2. Add SEO Meta to critical missing pages
    missing_meta_pages = ['404.html', 'privacy.html', 'terms.html', 'legal.html']
    for p in missing_meta_pages:
        full_p = os.path.join(BASE_DIR, p)
        if os.path.exists(full_p):
            with open(full_p, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            
            if '<meta name="description"' not in content:
                desc = '<meta name="description" content="JFT Agro Overseas - Legal Information, Privacy Policy, and Terms of Trade for global agricultural exports.">'
                content = content.replace('</title>', f'</title>\n{desc}')
            
            if 'rel="canonical"' not in content:
                canon = f'<link rel="canonical" href="https://jftagro.com/{p}">'
                content = content.replace('</title>', f'</title>\n{canon}')
                
            with open(full_p, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  - Injected SEO meta into {p}")

    # 3. Fix known broken blog links
    # blog-spice-trends.html -> blog-spice-trends-2026.html
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith('.html'):
                path = os.path.join(root, file)
                with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                new_content = content.replace('blog-spice-trends.html', 'blog-spice-trends-2026.html')
                if new_content != content:
                    with open(path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"  - Fixed blog link in {os.path.relpath(path, BASE_DIR)}")

    print("--- Polish Complete ---")

if __name__ == "__main__":
    polish_website()
