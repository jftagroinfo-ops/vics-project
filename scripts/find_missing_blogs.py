#!/usr/bin/env python3
import os
import re
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

pattern = re.compile(r'href\s*=\s*["\']([^"\']*blog-[^"\']*?\.html)["\']', re.IGNORECASE)
refs = defaultdict(list)
referenced_files = set()

for dirpath, dirnames, filenames in os.walk(ROOT):
    # skip virtualenvs, .git, node_modules
    if any(part in ('.git', 'node_modules', '__pycache__') for part in dirpath.split(os.sep)):
        continue
    for fname in filenames:
        if not fname.lower().endswith(('.html', '.htm')):
            continue
        fpath = os.path.join(dirpath, fname)
        try:
            with open(fpath, 'r', encoding='utf-8', errors='ignore') as fh:
                for idx, line in enumerate(fh, start=1):
                    for m in pattern.finditer(line):
                        raw = m.group(1)
                        base = os.path.basename(raw)
                        referenced_files.add(base)
                        refs[base].append((os.path.relpath(fpath, ROOT), idx, line.strip()))
        except Exception as e:
            print(f"Warning: couldn't read {fpath}: {e}")

existing_files = set()
for dirpath, dirnames, filenames in os.walk(ROOT):
    if any(part in ('.git', 'node_modules', '__pycache__') for part in dirpath.split(os.sep)):
        continue
    for fname in filenames:
        if fname.lower().endswith(('.html', '.htm')):
            existing_files.add(fname)

missing = sorted(referenced_files - existing_files)

print(f"Scanned: {len(referenced_files)} unique blog references found.")
print(f"Existing blog files discovered: {len(existing_files)}")
print(f"Missing targets: {len(missing)}\n")

if missing:
    print('Missing blog files and their source contexts:\n')
    for m in missing:
        print('---', m)
        for src, ln, text in refs.get(m, []):
            print(f"  {src}#L{ln}: {text}")
        print()
else:
    print('No missing blog targets found.')

# Optionally write a brief report
report_path = os.path.join(ROOT, 'scripts', 'missing_blogs_report.txt')
with open(report_path, 'w', encoding='utf-8') as rep:
    rep.write(f"Scanned: {len(referenced_files)} unique blog references\n")
    rep.write(f"Existing blog files discovered: {len(existing_files)}\n")
    rep.write(f"Missing targets: {len(missing)}\n\n")
    if missing:
        rep.write('Missing blog files and their source contexts:\n\n')
        for m in missing:
            rep.write('--- ' + m + '\n')
            for src, ln, text in refs.get(m, []):
                rep.write(f"  {src}#L{ln}: {text}\n")
            rep.write('\n')
print(f"Wrote report to {report_path}")
