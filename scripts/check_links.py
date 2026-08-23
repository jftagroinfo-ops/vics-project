import os, re, html, time
from collections import defaultdict
import urllib.parse
from pathlib import Path

root_path = Path('.').resolve()
excluded_dirs = {
    '.git',
    '.cloudflare-dist',
    '.cloudflare-dist-predeploy',
    '.wrangler',
    '.wrangler-dry-run',
    'node_modules',
    'reports',
}
helper_files = {
    'product-page-template.html',
    'inner-page-hero-snippet.html',
    'seo-universal-head-snippet.html',
}
broken_links_map = defaultdict(list)
existing_paths = set()
html_files = []
filesystem_excluded_dirs = {'.git', '.cloudflare', '.cloudflare-dist', '.cloudflare-dist-predeploy', '.github', '.vscode', '.wrangler', '.wrangler-dry-run', '__pycache__', 'docs', 'node_modules', 'reports', 'scripts'}
started = time.monotonic()
for directory, dirnames, filenames in os.walk(root_path):
    dirnames[:] = [
        name for name in dirnames
        if name not in filesystem_excluded_dirs
        and not name.startswith('.cloudflare-dist')
        and not name.startswith('.wrangler')
    ]
    existing_paths.add(os.path.normcase(os.path.abspath(directory)))
    relative_parts = Path(directory).relative_to(root_path).parts
    for filename in filenames:
        path = Path(directory) / filename
        existing_paths.add(os.path.normcase(os.path.abspath(path)))
        if filename.endswith('.html') and not excluded_dirs.intersection(relative_parts) and filename not in helper_files:
            html_files.append(path)

print(f'Indexed {len(existing_paths)} local paths and {len(html_files)} HTML files in {time.monotonic() - started:.1f}s', flush=True)

for index, f in enumerate(html_files, 1):
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
            target_key = os.path.normcase(os.path.abspath(target))
            exists = target_key in existing_paths
            if not exists:
                broken_links_map[link_clean].append(f.relative_to(root_path).as_posix())
    if index % 250 == 0:
        print(f'Checked {index}/{len(html_files)} HTML files', flush=True)

print(f'Total HTML files: {len(html_files)}')
print(f'Total Unique Broken Links: {len(broken_links_map)}')
for missing, referencers in sorted(broken_links_map.items(), key=lambda x: len(x[1]), reverse=True):
    print(f'- {missing} (referenced in {len(referencers)} files)')
