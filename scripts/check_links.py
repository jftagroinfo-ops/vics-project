import os, re
from collections import defaultdict
import urllib.parse

html_files = [f for f in os.listdir('.') if f.endswith('.html')]
all_files = set(os.listdir('.'))
for root, dirs, files in os.walk('images'):
    for file in files:
        all_files.add(os.path.join(root, file).replace('\\', '/'))
for root, dirs, files in os.walk('assets'):
    for file in files:
        all_files.add(os.path.join(root, file).replace('\\', '/'))

broken_links_map = defaultdict(list)

for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        hrefs = re.findall(r'href=[\'\"]([^\'\"]+)[\'\"]', content)
        srcs = re.findall(r'src=[\'\"]([^\'\"]+)[\'\"]', content)
        for link in set(hrefs + srcs):
            if link.startswith(('http', '#', 'mailto:', 'tel:', 'data:')): 
                continue
            link_clean = link.split('?')[0].split('#')[0]
            if not link_clean: 
                continue
            
            link_clean = urllib.parse.unquote(link_clean)
            
            if link_clean.startswith('/'): 
                link_clean = link_clean[1:]
                
            if link_clean not in all_files and not os.path.exists(link_clean):
                broken_links_map[link_clean].append(f)

print(f'Total HTML files: {len(html_files)}')
print(f'Total Unique Broken Links: {len(broken_links_map)}')
for missing, referencers in sorted(broken_links_map.items(), key=lambda x: len(x[1]), reverse=True):
    print(f'- {missing} (referenced in {len(referencers)} files)')
