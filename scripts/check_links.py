import os, re, html
from collections import defaultdict
import urllib.parse
from pathlib import Path

root_path = Path('.').resolve()
html_files = [p for p in root_path.rglob('*.html') if '.git' not in p.parts and p.name not in {'product-page-template.html', 'inner-page-hero-snippet.html'}]

broken_links_map = defaultdict(list)

for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        hrefs = re.findall(r'href=[\'\"]([^\'\"]+)[\'\"]', content)
        srcs = re.findall(r'src=[\'\"]([^\'\"]+)[\'\"]', content)
        for link in set(hrefs + srcs):
            link = html.unescape(link).strip()
            if not link or '${' in link or '{{' in link or link.startswith(('http', '#', 'mailto:', 'tel:', 'data:', 'javascript:')):
                continue
            link_clean = link.split('?')[0].split('#')[0]
            if not link_clean: 
                continue
            
            link_clean = urllib.parse.unquote(link_clean)
            target = root_path / link_clean.lstrip('/') if link_clean.startswith('/') else f.parent / link_clean
            if not target.resolve().exists():
                broken_links_map[link_clean].append(f.relative_to(root_path).as_posix())

print(f'Total HTML files: {len(html_files)}')
print(f'Total Unique Broken Links: {len(broken_links_map)}')
for missing, referencers in sorted(broken_links_map.items(), key=lambda x: len(x[1]), reverse=True):
    print(f'- {missing} (referenced in {len(referencers)} files)')
