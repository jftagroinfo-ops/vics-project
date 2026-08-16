from __future__ import annotations

import html
import re
from pathlib import Path
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
GENERATED = Path(r"C:\Users\HP\.codex\generated_images\019ffc43-839a-7522-8488-b2dadc9e289e")
OUT = ROOT / "images" / "editorial" / "blog"
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")

# slug: (generated filename, concise accessible subject)
IMAGES = {
    "blog-apeda-registration-indian-exporter-explained": ("exec-a3d41dca-4439-4fa8-8221-9c988a890b92.png", "APEDA export compliance review"),
    "blog-basmati-export-guide": ("exec-3e996840-acf9-40f1-8164-28ddd2f28f62.png", "Basmati rice grade comparison"),
    "blog-bill-of-lading-explained-importers": ("exec-9b52ea5c-ecce-47be-a232-d8d3de8c4d51.png", "bill of lading review at an export terminal"),
    "blog-cif-fob-explained": ("exec-1d7d6fd3-cabf-4c62-a968-e75fef3bc075.png", "CIF and FOB export workflow"),
    "blog-coriander-seeds-export-india-2026": ("exec-55376784-3535-4133-a998-e142b659174f.png", "coriander seed quality inspection"),
    "blog-cumin-jeera-price-outlook-2026": ("exec-cd1ea8e3-1065-448e-a923-8bde6ac8d2e5.png", "cumin quality and market analysis"),
    "blog-eu-mrl-basmati": ("exec-5b6468a6-7b5e-4b44-be94-16e97870b218.png", "basmati rice residue testing"),
    "blog-green-mung-beans-export-india-2026": ("exec-07031e68-a55b-437c-bd15-2f801802feff.png", "green mung bean grading"),
    "blog-groundnut-peanut-export-india-2026": ("exec-4b5d5fc7-e457-4f70-9344-50a15676fd5c.png", "groundnut export quality testing"),
    "blog-how-to-choose-indian-agro-exporter": ("exec-8a65741d-a8a9-40c7-8e29-26bdbc2c7c2b.png", "agro exporter due diligence"),
    "blog-how-to-export-india-to-africa": ("exec-a3cbec29-f499-4780-997c-3b3dc54582d9.png", "PP bag cargo prepared for Africa"),
    "blog-how-to-import-rice-nigeria-west-africa": ("exec-20a85cd8-e590-4598-a991-2c9f36f8f06f.png", "BOPP rice cargo inspection for West Africa"),
    "blog-how-to-read-proforma-invoice-india-export": ("exec-9def567f-76ed-494c-9071-f188e8a67243.png", "export proforma invoice review"),
    "blog-import-duty-indian-rice-by-country": ("exec-6c65c88c-beb0-45f2-bf5b-93dc66e4b49d.png", "rice tariff and import duty analysis"),
    "blog-import-indian-agro-kenya-east-africa": ("exec-5ab3cc32-774f-4dc3-9dd6-e5f43a445577.png", "East Africa agro cargo inspection"),
    "blog-import-indian-spices-uk-europe": ("exec-94229231-1203-41e3-baa3-c4cd027fe07f.png", "Indian spice compliance inspection"),
    "blog-indian-white-rice-export-policy-2026-latest-updates": ("exec-bff82302-138c-4f77-b7e2-2be99d9421b2.png", "white rice export policy analysis"),
    "blog-india-rice-export-sri-lanka-bangladesh": ("exec-e3a4eb17-323b-40c6-a4e9-a88b7f5b5770.png", "regional rice cargo at an Indian port"),
    "blog-india-uae-cepa": ("exec-ed888cfb-a3e2-4f95-9fd9-f18155eeef5e.png", "India UAE agro trade inspection"),
    "blog-india-vs-thailand-rice-comparison": ("exec-d893ed9d-27fb-46a5-abac-109f0f830a24.png", "India and Thailand rice grade comparison"),
    "blog-ir64-africa": ("exec-84c6af34-251c-475c-b5a2-83a1ef1fda77.png", "IR64 rice inspection for African markets"),
    "blog-ir64-export": ("exec-e8d752df-1ce8-46d6-bfcd-d9df964bdfdf.png", "IR64 rice export grading"),
    "blog-lc-vs-tt": ("exec-ef6fc9be-b5f7-49d6-9496-ff1a40e9d979.png", "trade finance document review"),
    "blog-letter-of-credit-food-imports-india": ("exec-ef6fc9be-b5f7-49d6-9496-ff1a40e9d979.png", "letter of credit review for food imports"),
    "blog-private-label-rice": ("exec-4d292846-e57a-4d8e-8c08-5c63ac44c884.png", "private-label BOPP rice packing line"),
    "blog-psyllium-husk-export-india-2026": ("exec-8cb45bea-013f-479e-9ac3-5710dfd60615.png", "psyllium husk laboratory testing"),
    "blog-red-chilli-teja-export-india-2026": ("exec-294cd00e-b240-4332-a72d-4c6d8846072d.png", "Teja red chilli quality inspection"),
    "blog-sesame-export-2026": ("exec-ff98af4f-f300-48ff-9617-b4aa3b72f6dc.png", "natural and hulled sesame comparison"),
    "blog-sgs-inspection-indian-agro-exports": ("exec-1d0a54f6-1405-4b86-9464-0dabd8bb0053.png", "independent pre-shipment cargo inspection"),
    "blog-spice-trends-2026": ("exec-21135868-411a-4e7b-8bce-44bd1abc27ab.png", "Indian spice market analysis"),
    "blog-toor-dal-export-india-2026": ("exec-6bcfb4cc-22ea-466d-b950-41f3886970e2.png", "toor dal export grading"),
    "blog-top-indian-agro-commodities-import-2026": ("exec-3057c9a5-d83e-402f-acf2-74749e16e87b.png", "Indian agro commodity trade samples"),
    "blog-turmeric-finger-export-india-2026": ("exec-ce87ac73-86d1-4e39-a9bc-09ec7c88d9b0.png", "turmeric finger quality inspection"),
    "blog-turmeric-market-outlook-2026": ("exec-e5aaee38-218b-449b-8193-69b4bf47b1ba.png", "turmeric market analysis"),
    "blog-basmati-rice-import-uae-esma-standards": ("exec-ea062c6e-3ae8-4807-801e-d6187f0003db.png", "basmati rice inspection for the UAE"),
    "blog-black-pepper-powder-export-india-2026": ("exec-12c2186c-a99b-4e62-8609-143b55f4731a.png", "black pepper export quality inspection"),
    "blog-fennel-seeds-export-india-2026": ("exec-5ec08d4e-b071-4790-9fd6-bd285d19c5d0.png", "fennel seed export grading"),
    "blog-fenugreek-seeds-export-india-2026": ("exec-33a04a58-9122-4150-8757-ae2e65ea893b.png", "fenugreek seed export grading"),
    "blog-fssai-apeda-agmark-certifications-explained": ("exec-6f6e3afb-735a-4296-a320-77ea9fba7592.png", "Indian food export compliance review"),
    "blog-indian-spice-export-middle-east-gulf": ("exec-f925f7ff-6415-40c9-a567-f558a02783f5.png", "Indian spice inspection for Gulf markets"),
    "blog-moringa-powder-export-india-2026": ("exec-bca71f0b-283a-4d90-bba2-b8e8fe3d7b79.png", "moringa powder export quality testing"),
    "blog-phytosanitary-certificate-india-exports": ("exec-775f9f25-eda4-4f47-92f9-5941b222020a.png", "phytosanitary export inspection"),
    "blog-sugar-s30-export-india-2026": ("exec-b63adb2c-017c-44f2-b74b-8fd10c86d593.png", "S30 sugar crystal quality inspection"),
    "blog-wheat-flour-atta-export-india-2026": ("exec-c0f083a8-bfce-42cd-a773-8afca4035c0e.png", "wheat flour export quality inspection"),
    "blog-yellow-maize-export-india-2026": ("exec-fe9dea1c-6b9f-4273-beec-0d5c6ed9bcc6.png", "yellow maize export quality inspection"),
}

BLOG_LANDING = ("exec-cfa7bd3e-2fa8-49eb-9001-afac531d349b.png", "JFT Agro trade insights")


def webp_name(slug: str) -> str:
    return f"{slug.removeprefix('blog-')}-v1.webp"


def convert_images() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    items = dict(IMAGES)
    items["blog-insights"] = BLOG_LANDING
    for slug, (source, _alt) in items.items():
        destination = OUT / webp_name(slug)
        with Image.open(GENERATED / source) as image:
            image = image.convert("RGB")
            image.thumbnail((1440, 960), Image.Resampling.LANCZOS)
            image.save(destination, "WEBP", quality=84, method=6)


def local_src(path: Path, slug: str) -> str:
    prefix = "../" if path.parent != ROOT else ""
    return f"{prefix}images/editorial/blog/{webp_name(slug)}"


def update_metadata(text: str, slug: str) -> str:
    absolute = f"https://jftagro.com/images/editorial/blog/{webp_name(slug)}"
    text = re.sub(r'(<meta property=["\']og:image["\'] content=["\'])[^"\']*(["\'])', rf'\g<1>{absolute}\2', text, count=1, flags=re.I)
    if re.search(r'<meta name=["\']twitter:image["\']', text, flags=re.I):
        text = re.sub(r'(<meta name=["\']twitter:image["\'] content=["\'])[^"\']*(["\'])', rf'\g<1>{absolute}\2', text, count=1, flags=re.I)
    else:
        text = re.sub(r'(<meta property=["\']og:image["\'][^>]*>)', rf'\1\n<meta name="twitter:image" content="{absolute}">', text, count=1, flags=re.I)
    text = re.sub(r'(["\']image["\']\s*:\s*["\'])[^"\']+(["\'])', rf'\g<1>{absolute}\2', text, count=1)
    return text


def update_article(path: Path, slug: str, subject: str) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    original = text
    src = local_src(path, slug)
    alt = f"JFT Agro editorial image showing {subject}"
    tag = f'<img src="{src}" alt="{html.escape(alt, quote=True)}" width="1440" height="960" loading="eager" fetchpriority="high">'
    text = update_metadata(text, slug)

    # Full-width SEO article headers already provide the image frame.
    seo_pattern = r'(<header\b[^>]*class=["\'][^"\']*seo-article-hero[^"\']*["\'][^>]*>\s*)<img\b[^>]*>'
    if re.search(seo_pattern, text, flags=re.I):
        text = re.sub(seo_pattern, rf'\1{tag}', text, count=1, flags=re.I)
    elif re.search(r'<img\b[^>]*class=["\'][^"\']*article-hero[^"\']*["\'][^>]*>', text, flags=re.I):
        article_tag = tag[:-1] + ' class="article-hero">'
        text = re.sub(r'<img\b[^>]*class=["\'][^"\']*article-hero[^"\']*["\'][^>]*>', article_tag, text, count=1, flags=re.I)
    else:
        figure = f'\n<figure class="jft-editorial-hero">{tag}<figcaption>JFT Agro Editorial • {html.escape(subject.title())}</figcaption></figure>'
        text, count = re.subn(r'(<h1\b[^>]*class=["\'][^"\']*article-title[^"\']*["\'][^>]*>.*?</h1>)', rf'\1{figure}', text, count=1, flags=re.I | re.S)
        if count == 0:
            text, count = re.subn(r'(<h1\b[^>]*>.*?</h1>)', rf'\1{figure}', text, count=1, flags=re.I | re.S)
        if count == 0:
            raise RuntimeError(f"No article H1/image insertion point in {path}")

    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
        return True
    return False


def update_blog_index(path: Path) -> bool:
    if not path.exists():
        return False
    text = path.read_text(encoding="utf-8")
    original = text
    landing_absolute = f"https://jftagro.com/images/editorial/blog/{webp_name('blog-insights')}"
    text = re.sub(r'(<meta property=["\']og:image["\'] content=["\'])[^"\']*(["\'])', rf'\g<1>{landing_absolute}\2', text, count=1, flags=re.I)
    if re.search(r'<meta name=["\']twitter:image["\']', text, flags=re.I):
        text = re.sub(r'(<meta name=["\']twitter:image["\'] content=["\'])[^"\']*(["\'])', rf'\g<1>{landing_absolute}\2', text, count=1, flags=re.I)
    else:
        text = re.sub(r'(<meta property=["\']og:image["\'][^>]*>)', rf'\1\n<meta name="twitter:image" content="{landing_absolute}">', text, count=1, flags=re.I)

    # Each blog card is an anchor; replace only its first image.
    for slug, (_source, subject) in IMAGES.items():
        href = re.escape(slug + ".html")
        pattern = rf'(<a\b[^>]*href=["\']{href}["\'][^>]*>.*?)(<img\b[^>]*>)(.*?</a>)'
        src = local_src(path, slug)
        img = f'<img src="{src}" alt="{html.escape(subject.title(), quote=True)}" loading="lazy" width="1440" height="960">'
        text = re.sub(pattern, rf'\1{img}\3', text, count=1, flags=re.I | re.S)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
        return True
    return False


def main() -> None:
    convert_images()
    changed = []
    for slug, (_source, subject) in IMAGES.items():
        for base in (ROOT, *(ROOT / locale for locale in LOCALES)):
            path = base / f"{slug}.html"
            if update_article(path, slug, subject):
                changed.append(path)
    for base in (ROOT, *(ROOT / locale for locale in LOCALES)):
        path = base / "blog.html"
        if update_blog_index(path):
            changed.append(path)
    print(f"Created {len(IMAGES) + 1} editorial WebP images")
    print(f"Updated {len(changed)} HTML files")


if __name__ == "__main__":
    main()
