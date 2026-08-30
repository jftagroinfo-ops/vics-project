import os, re
target = os.path.join("ar", "10-parboiled-rice-ir-64-exporter.html")
t = open(target, encoding="utf-8", errors="replace", newline="").read()
for m in re.finditer(r'skip-link', t):
    i = m.start()
    print("--- at", i, "---")
    print(repr(t[i-60:i+200]))