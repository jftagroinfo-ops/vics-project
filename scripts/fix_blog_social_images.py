from pathlib import Path
import re

from integrate_blog_editorial_images import IMAGES, LOCALES, ROOT, webp_name


def ensure_meta(path: Path, slug: str) -> None:
    text = path.read_text(encoding="utf-8")
    absolute = f"https://jftagro.com/images/editorial/blog/{webp_name(slug)}"
    additions = []
    if not re.search(r'<meta\s+property=["\']og:image["\']', text, re.I):
        additions.append(f'<meta property="og:image" content="{absolute}">')
    if not re.search(r'<meta\s+name=["\']twitter:image["\']', text, re.I):
        additions.append(f'<meta name="twitter:image" content="{absolute}">')
    if additions:
        text = re.sub(r'</head>', "\n".join(additions) + "\n</head>", text, count=1, flags=re.I)
        path.write_text(text, encoding="utf-8", newline="")


for slug in IMAGES:
    for base in (ROOT, *(ROOT / locale for locale in LOCALES)):
        path = base / f"{slug}.html"
        if path.exists():
            ensure_meta(path, slug)
