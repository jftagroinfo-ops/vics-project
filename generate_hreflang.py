import os
import sys
import shutil
import re
from deep_translator import GoogleTranslator

# Fix encoding for non-ASCII output
sys.stdout.reconfigure(encoding='utf-8')

# Use relative pathing for portability (works on Local and GitHub Actions)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Automatically discover all pages to translate
ALL_FILES = [f for f in os.listdir(BASE_DIR) if f.endswith('.html')]
PAGES = [f for f in ALL_FILES if f not in ['footer.html', 'header.html', '404.html']]
# Prioritize core pages
CORE_PAGES = ['index.html', 'products.html', 'about.html', 'contact.html', 'quality-control.html', 'blog.html', 'faq.html']
PAGES = CORE_PAGES + [p for p in PAGES if p not in CORE_PAGES]

LANGS = {
    'ar': 'Arabic', 
    'fr': 'French', 
    'ru': 'Russian', 
    'es': 'Spanish', 
    'pt': 'Portuguese',
    'vi': 'Vietnamese',
    'ms': 'Malay',
    'id': 'Indonesian',
    'si': 'Sinhala',
    'th': 'Thai'
}

def extract_tag(html, tag):
    match = re.search(f'<{tag}[^>]*>(.*?)</{tag}>', html, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""

def extract_meta_content(html, name):
    match = re.search(f'<meta\\s+name=[\'"]{name}[\'"]\\s+content=[\'"](.*?)[\'"]\\s*/?>', html, re.IGNORECASE | re.DOTALL)
    return match.group(1).strip() if match else ""

# Generate the hreflang block dynamically
def get_hreflang_tags(page):
    tags = f'\n    <link rel="alternate" hreflang="en" href="https://jftagro.com/{page}" />'
    for l_code in LANGS:
        tags += f'\n    <link rel="alternate" hreflang="{l_code}" href="https://jftagro.com/{l_code}/{page}" />'
    tags += f'\n    <link rel="alternate" hreflang="x-default" href="https://jftagro.com/{page}" />\n'
    return tags

print(f"Starting Global Multilingual Generation for {len(PAGES)} pages...")

for lang_code, lang_name in LANGS.items():
    lang_dir = os.path.join(BASE_DIR, lang_code)
    os.makedirs(lang_dir, exist_ok=True)
    
    translator = GoogleTranslator(source='en', target=lang_code)
    
    for page in PAGES:
        src_path = os.path.join(BASE_DIR, page)
        if not os.path.exists(src_path):
            continue
            
        with open(src_path, 'r', encoding='utf-8') as f:
            html = f.read()
            
        # Clean existing hreflang tags if any
        html = re.sub(r'\s*<link rel="alternate" hreflang=.*?>', '', html)
            
        # Extract metadata
        title = extract_tag(html, 'title')
        desc = extract_meta_content(html, 'description')
        
        # Translate
        try:
            new_title = translator.translate(title) if title else ""
            new_desc = translator.translate(desc) if desc else ""
        except Exception as e:
            print(f"Translation error ({lang_code} - {page}): {e}")
            new_title = title
            new_desc = desc
            
        # Replace in HTML
        if title and new_title:
            html = html.replace(f'<title>{title}</title>', f'<title>{new_title}</title>')
        if desc and new_desc:
            html = html.replace(f'content="{desc}"', f'content="{new_desc}"')
            
        # Update HTML lang tag
        html = html.replace('<html lang="en">', f'<html lang="{lang_code}">')
        
        # Add hreflang links
        hreflang_block = get_hreflang_tags(page)
        html = html.replace('</head>', f'{hreflang_block}</head>')
        
        # Fix relative paths for assets
        html = html.replace('href="css/', 'href="../css/')
        html = html.replace('src="js/', 'src="../js/')
        html = html.replace('href="images/', 'href="../images/')
        html = html.replace('src="images/', 'src="../images/')
        html = html.replace("loadComponent('header-placeholder', 'header.html')", "loadComponent('header-placeholder', '../header.html')")
        html = html.replace("loadComponent('footer-placeholder', 'footer.html')", "loadComponent('footer-placeholder', '../footer.html')")
        
        # Write to lang directory
        dest_path = os.path.join(lang_dir, page)
        with open(dest_path, 'w', encoding='utf-8') as f:
            f.write(html)
            
        print(f"Generated {lang_code}/{page}")

# Update original English pages with full hreflang block
for page in PAGES:
    src_path = os.path.join(BASE_DIR, page)
    if not os.path.exists(src_path):
        continue
    with open(src_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Clean existing hreflang tags
    html = re.sub(r'\s*<link rel="alternate" hreflang=.*?>', '', html)
    
    hreflang_block = get_hreflang_tags(page)
    html = html.replace('</head>', f'{hreflang_block}</head>')
    
    with open(src_path, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"Updated hreflang for English {page}")

print("\n[SUCCESS] Global Multilingual Engine complete. JFT Agro now speaks 11 languages natively!")
