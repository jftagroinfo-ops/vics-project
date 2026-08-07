import os, re

html_files = [f for f in os.listdir('.') if f.endswith('.html')]
all_files = set(os.listdir('.'))
for root, dirs, files in os.walk('images'):
    for file in files:
        all_files.add(os.path.join(root, file).replace('\\', '/'))
for root, dirs, files in os.walk('assets'):
    for file in files:
        all_files.add(os.path.join(root, file).replace('\\', '/'))

referenced_files = set()

for f in html_files:
    with open(f, 'r', encoding='utf-8') as file:
        content = file.read()
        hrefs = re.findall(r'href=[\'\"]([^\'\"]+)[\'\"]', content)
        srcs = re.findall(r'src=[\'\"]([^\'\"]+)[\'\"]', content)
        for link in set(hrefs + srcs):
            link_clean = link.split('?')[0].split('#')[0]
            if link_clean.startswith('/'): 
                link_clean = link_clean[1:]
            referenced_files.add(link_clean)
            # also unquoted for spaces
            referenced_files.add(link_clean.replace('%20', ' '))

# Check what is unused
unused_files = []
for f in all_files:
    if f in ['index.html', '404.html']: continue # entry points
    if f.endswith('.html') and f not in referenced_files:
        unused_files.append(f)
    elif f.startswith('images/') and f not in referenced_files:
        unused_files.append(f)

print(f'Total unused HTML/Image files: {len(unused_files)}')
for u in unused_files[:30]:
    print(f'- {u}')
