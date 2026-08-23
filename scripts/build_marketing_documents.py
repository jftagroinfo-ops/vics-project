#!/usr/bin/env python3
"""Build original JFT Agro introduction, brochure and product catalogue PDFs."""

from __future__ import annotations

import json
import math
import textwrap
from collections import defaultdict
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "assets" / "brochures"
PRODUCTS_FILE = ROOT / "data" / "products.json"
CACHE = ROOT / "reports" / ".marketing-image-cache"
PAGE_W, PAGE_H = A4

GREEN = HexColor("#173F36")
GREEN_2 = HexColor("#2F6B54")
GOLD = HexColor("#EEBF45")
CREAM = HexColor("#F7F3E8")
INK = HexColor("#19332D")
MUTED = HexColor("#5D6E69")
LINE = HexColor("#D9E1DC")

SITE = "https://jftagro.com"
EMAIL = "jftagro.info@gmail.com"
PHONE = "+91 84250 57274"
ADDRESS = "Vashi APMC, Navi Mumbai 400705, Maharashtra, India"

CATEGORY_LABELS = {
    "rice": "Rice",
    "spices": "Spices",
    "herbs": "Herbs & Botanicals",
    "feed": "Grains & Feed Ingredients",
    "oilseeds": "Oilseeds",
    "flour": "Flours & Milling Products",
    "pulses": "Pulses",
    "wheat": "Wheat",
    "sugar": "Sugar",
    "raisins": "Raisins",
}

CATEGORY_INTROS = {
    "rice": "Basmati and non-basmati rice options for retail, foodservice and industrial buying programmes.",
    "spices": "Whole and ground Indian spices supplied against buyer-defined physical, chemical and destination requirements.",
    "herbs": "Botanical ingredients offered subject to agreed identity, purity, processing and destination-compliance criteria.",
    "feed": "Cereals, millets and plant-based feed ingredients for approved food and feed applications.",
    "oilseeds": "Oilseed varieties for food processing, crushing and ingredient applications, subject to lot specification.",
    "flour": "Wheat and maize milling products with packing and performance requirements agreed before supply.",
    "pulses": "Whole and split pulses for importers, distributors, foodservice and processing buyers.",
    "wheat": "Milling wheat offered against agreed origin, test weight, moisture and end-use requirements.",
    "sugar": "Indian S-30 sugar supplied against current trade policy and shipment-specific commercial terms.",
    "raisins": "Indian raisins offered by agreed size, colour, moisture, defect tolerance and packing format.",
}


def safe_image(path: Path):
    try:
        return ImageReader(str(path)) if path.is_file() else None
    except Exception:
        return None


def catalogue_image(path: Path) -> Path:
    """Return a compact RGB JPEG for repeated PDF embedding."""
    CACHE.mkdir(parents=True, exist_ok=True)
    relative = path.relative_to(ROOT).as_posix().replace("/", "__")
    target = CACHE / f"{relative}.jpg"
    if target.is_file() and target.stat().st_mtime_ns >= path.stat().st_mtime_ns:
        return target
    with Image.open(path) as source:
        source.thumbnail((520, 520), Image.Resampling.LANCZOS)
        if source.mode not in {"RGB", "L"}:
            background = Image.new("RGB", source.size, "white")
            if "A" in source.getbands():
                background.paste(source, mask=source.getchannel("A"))
            else:
                background.paste(source.convert("RGB"))
            source = background
        elif source.mode == "L":
            source = source.convert("RGB")
        source.save(target, "JPEG", quality=82, optimize=True, progressive=True)
    return target


def draw_cover_image(c: canvas.Canvas, path: Path, y: float, height: float) -> None:
    image = safe_image(path)
    if image is None:
        c.setFillColor(GREEN_2)
        c.rect(0, y, PAGE_W, height, fill=1, stroke=0)
        return
    iw, ih = image.getSize()
    scale = max(PAGE_W / iw, height / ih)
    width, drawn_height = iw * scale, ih * scale
    c.saveState()
    clip = c.beginPath()
    clip.rect(0, y, PAGE_W, height)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(image, (PAGE_W - width) / 2, y + (height - drawn_height) / 2, width, drawn_height)
    c.setFillColor(GREEN)
    if hasattr(c, "setFillAlpha"):
        c.setFillAlpha(0.72)
    c.rect(0, y, PAGE_W, height, fill=1, stroke=0)
    c.restoreState()


def wrap(text: str, width: int) -> list[str]:
    return textwrap.wrap(" ".join(text.split()), width=width, break_long_words=False) or [""]


def draw_wrapped(
    c: canvas.Canvas,
    text: str,
    x: float,
    y: float,
    width_chars: int,
    font: str = "Helvetica",
    size: float = 10,
    leading: float | None = None,
    color=INK,
    max_lines: int | None = None,
) -> float:
    leading = leading or size * 1.35
    lines = wrap(text, width_chars)
    if max_lines:
        lines = lines[:max_lines]
    c.setFont(font, size)
    c.setFillColor(color)
    for line in lines:
        c.drawString(x, y, line)
        y -= leading
    return y


def draw_header(c: canvas.Canvas, section: str) -> None:
    c.setFillColor(GREEN)
    c.rect(0, PAGE_H - 42, PAGE_W, 42, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(34, PAGE_H - 26, "JFT AGRO OVERSEAS")
    c.setFillColor(white)
    c.setFont("Helvetica", 8)
    c.drawRightString(PAGE_W - 34, PAGE_H - 26, section.upper())


def draw_footer(c: canvas.Canvas, page_no: int, note: str = "Buyer information | Verify current documents before contracting") -> None:
    c.setStrokeColor(LINE)
    c.line(34, 31, PAGE_W - 34, 31)
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 6.8)
    c.drawString(34, 19, note)
    c.drawRightString(PAGE_W - 34, 19, f"jftagro.com  |  {page_no}")


def draw_logo(c: canvas.Canvas, x: float, y: float, width: float = 92) -> None:
    path = ROOT / "images" / "jft-logo-transparent.webp"
    image = safe_image(path)
    if image is not None:
        iw, ih = image.getSize()
        c.drawImage(image, x, y, width, width * ih / iw, mask="auto", preserveAspectRatio=True)
    else:
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(x, y, "JFT AGRO")


def cover(
    c: canvas.Canvas,
    title: str,
    subtitle: str,
    image_path: Path,
    edition: str,
) -> None:
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_cover_image(c, image_path, PAGE_H * 0.43, PAGE_H * 0.57)
    draw_logo(c, 36, PAGE_H - 82, 88)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(38, PAGE_H * 0.50, edition.upper())
    # Keep the full title on the light panel for reliable contrast regardless
    # of the selected cover photograph.
    y = PAGE_H * 0.405
    for line in wrap(title, 25):
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 28)
        c.drawString(38, y, line)
        y -= 34
    y -= 4
    draw_wrapped(c, subtitle, 38, y, 70, size=11, leading=16, color=MUTED, max_lines=4)
    c.setFillColor(GREEN)
    c.rect(0, 0, PAGE_W, 78, fill=1, stroke=0)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(38, 48, SITE)
    c.setFont("Helvetica", 8)
    c.drawString(38, 31, f"{EMAIL}  |  {PHONE}  |  Navi Mumbai, India")
    c.showPage()


def card(c: canvas.Canvas, x: float, y: float, w: float, h: float, title: str, body: str) -> None:
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, w, h, 8, fill=1, stroke=1)
    c.setFillColor(GOLD)
    c.rect(x, y + h - 8, w, 8, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(x + 14, y + h - 28, title)
    draw_wrapped(c, body, x + 14, y + h - 47, max(28, int(w / 5.5)), size=8.2, leading=11, color=MUTED, max_lines=7)


def build_introduction(products: list[dict]) -> Path:
    path = OUTPUT / "JFT-Agro-Company-Introduction.pdf"
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    c.setTitle("JFT Agro Overseas — Company Introduction")
    c.setAuthor("JFT Agro Overseas")
    cover(
        c,
        "Indian agricultural commodities, prepared for global trade",
        "A concise introduction to JFT Agro Overseas, our product scope, buyer workflow and verification approach.",
        ROOT / "images" / "homepage" / "rice-grains-export-hero-v3.webp",
        "Company Introduction 2026",
    )

    draw_header(c, "Who we are")
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H - 42, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(38, PAGE_H - 88, "A practical export partner from India")
    y = draw_wrapped(
        c,
        "JFT Agro Overseas coordinates Indian agricultural commodity supply for international buyers. We align the requested product, measurable acceptance fields, packing, documentation and shipment terms before an order moves forward.",
        38,
        PAGE_H - 118,
        84,
        size=10.5,
        leading=15,
        color=MUTED,
        max_lines=5,
    )
    stats = [
        (str(len(products)), "catalogued products"),
        (str(len({p['c'] for p in products})), "product groups"),
        ("FOB / CIF / CNF", "enquiry terms supported"),
    ]
    sx = 38
    for value, label in stats:
        c.setFillColor(white)
        c.roundRect(sx, y - 94, 162, 74, 8, fill=1, stroke=0)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 17 if len(value) < 10 else 12)
        c.drawString(sx + 13, y - 50, value)
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 7.8)
        c.drawString(sx + 13, y - 69, label)
        sx += 174
    y -= 125
    cards = [
        ("Product alignment", "Commercial names are converted into agreed physical, chemical, packing and destination-compliance requirements."),
        ("Document coordination", "Current registration, inspection and shipment documents are supplied according to product, destination and contracted scope."),
        ("Shipment planning", "The trade desk coordinates packing, Incoterm, load planning and dispatch milestones with the buyer and relevant service providers."),
        ("Buyer verification", "Credentials and product evidence are presented for verification; brochures do not replace current certificates, COAs or contracts."),
    ]
    for index, (title, body) in enumerate(cards):
        x = 38 + (index % 2) * 262
        yy = y - (index // 2) * 128
        card(c, x, yy - 106, 248, 106, title, body)
    draw_footer(c, 2)
    c.showPage()

    draw_header(c, "Product scope")
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H - 42, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 23)
    c.drawString(38, PAGE_H - 86, "Product groups for buyer-defined programmes")
    grouped = defaultdict(list)
    for product in products:
        grouped[product["c"]].append(product["t"])
    ordered = ["rice", "spices", "flour", "pulses", "oilseeds", "herbs", "feed", "wheat", "sugar", "raisins"]
    for index, category in enumerate(ordered):
        x = 38 + (index % 2) * 262
        y = PAGE_H - 126 - (index // 2) * 128
        names = ", ".join(grouped[category][:5])
        if len(grouped[category]) > 5:
            names += f" and {len(grouped[category]) - 5} more"
        card(c, x, y - 106, 248, 106, f"{CATEGORY_LABELS[category]} · {len(grouped[category])}", names)
    draw_footer(c, 3)
    c.showPage()

    draw_header(c, "Start an enquiry")
    c.setFillColor(GREEN)
    c.rect(0, 0, PAGE_W, PAGE_H - 42, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 24)
    c.drawString(38, PAGE_H - 92, "Send a complete buying brief")
    y = PAGE_H - 132
    checklist = [
        "Product and intended application",
        "Destination country and discharge port",
        "Required grade or measurable acceptance fields",
        "Packing format, net weight and labelling language",
        "Quantity, delivery window and preferred Incoterm",
        "Inspection, certification and document requirements",
    ]
    for idx, item in enumerate(checklist, 1):
        c.setFillColor(GOLD)
        c.circle(49, y + 3, 10, fill=1, stroke=0)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(49, y, str(idx))
        c.setFillColor(white)
        c.setFont("Helvetica", 10)
        c.drawString(70, y - 2, item)
        y -= 43
    c.setFillColor(HexColor("#2C574C"))
    c.roundRect(38, 165, PAGE_W - 76, 144, 10, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 13)
    c.drawString(56, 275, "JFT Agro Overseas — Export Desk")
    c.setFillColor(white)
    c.setFont("Helvetica", 9.5)
    c.drawString(56, 250, EMAIL)
    c.drawString(56, 230, PHONE)
    c.drawString(56, 210, ADDRESS)
    c.drawString(56, 190, f"Product catalogue: {SITE}/product-catalogue.html")
    c.setFillColor(HexColor("#CFE0D8"))
    c.setFont("Helvetica", 7.5)
    c.drawString(38, 96, "Important: product, packing, documentation and shipment availability are confirmed for each enquiry.")
    c.drawString(38, 81, "Request current credential copies and lot-specific evidence before relying on any registration or quality claim.")
    draw_footer(c, 4, "Corporate introduction | Not a certificate, COA, quotation or contract")
    c.save()
    return path


def category_feature_page(c: canvas.Canvas, category: str, products: list[dict], page_no: int) -> None:
    draw_header(c, CATEGORY_LABELS[category])
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H - 42, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 23)
    c.drawString(38, PAGE_H - 88, CATEGORY_LABELS[category])
    draw_wrapped(c, CATEGORY_INTROS[category], 38, PAGE_H - 116, 82, size=9.5, leading=14, color=MUTED, max_lines=3)
    for index, product in enumerate(products[:6]):
        col = index % 2
        row = index // 2
        x = 38 + col * 262
        y = PAGE_H - 172 - row * 188
        c.setFillColor(white)
        c.roundRect(x, y - 160, 248, 160, 8, fill=1, stroke=0)
        image = safe_image(catalogue_image(ROOT / product["i"]))
        if image is not None:
            iw, ih = image.getSize()
            max_w, max_h = 78, 70
            scale = min(max_w / iw, max_h / ih)
            c.drawImage(image, x + 12, y - 82, iw * scale, ih * scale, mask="auto", preserveAspectRatio=True)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 9.5)
        for j, line in enumerate(wrap(product["t"], 29)[:2]):
            c.drawString(x + 100, y - 24 - j * 12, line)
        specs = product.get("s", [])[:3]
        sy = y - 58
        c.setFont("Helvetica", 7.2)
        for label, value in specs:
            c.setFillColor(MUTED)
            c.drawString(x + 100, sy, f"{label}: {value}")
            sy -= 11
        c.setFillColor(GREEN_2)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawString(x + 12, y - 111, f"Packing: {product.get('p', 'Confirm for enquiry')}")
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 6.8)
        c.drawString(x + 12, y - 127, f"Load reference: {product.get('l', 'Confirm for enquiry')}")
        url = product.get("u", "products.html")
        c.setFillColor(GREEN_2)
        c.drawString(x + 12, y - 145, f"jftagro.com/{url}")
    draw_footer(c, page_no, "Indicative fields only | Final specification and load plan require written confirmation")
    c.showPage()


def build_brochure(products: list[dict]) -> Path:
    path = OUTPUT / "JFT-Agro-Export-Brochure.pdf"
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    c.setTitle("JFT Agro Overseas — Export Brochure")
    c.setAuthor("JFT Agro Overseas")
    cover(
        c,
        "Product range and export support",
        "A buyer-facing overview of Indian rice, spices, flours, pulses, oilseeds, botanicals, grains and related ingredients.",
        ROOT / "images" / "homepage" / "SPICES_BOARD.webp",
        "Export Brochure 2026",
    )
    grouped = defaultdict(list)
    for product in products:
        grouped[product["c"]].append(product)
    page = 2
    for category in ("rice", "spices", "flour", "pulses", "oilseeds", "herbs", "feed"):
        category_feature_page(c, category, grouped[category], page)
        page += 1

    draw_header(c, "How an enquiry moves")
    c.setFillColor(white)
    c.rect(0, 0, PAGE_W, PAGE_H - 42, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 23)
    c.drawString(38, PAGE_H - 86, "From buying brief to shipment file")
    steps = [
        ("1", "Buyer brief", "Product, destination, measurable requirements, packing, quantity and Incoterm."),
        ("2", "Offer alignment", "Trade desk confirms scope, commercial assumptions, availability and required evidence."),
        ("3", "Approved specification", "Both parties align the specification, tolerances, packing artwork and inspection plan."),
        ("4", "Order controls", "Contract, payment controls, production or procurement plan and document checklist."),
        ("5", "Release & loading", "Lot evidence, inspection status, container planning and dispatch milestones."),
        ("6", "Final documents", "Shipment-specific document set issued according to contract and destination requirements."),
    ]
    y = PAGE_H - 130
    for number, title, body in steps:
        c.setFillColor(GOLD)
        c.circle(58, y, 17, fill=1, stroke=0)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 11)
        c.drawCentredString(58, y - 4, number)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 11)
        c.drawString(89, y + 4, title)
        draw_wrapped(c, body, 89, y - 14, 76, size=8.3, leading=11, color=MUTED, max_lines=2)
        y -= 91
    draw_footer(c, page)
    c.showPage()
    page += 1

    draw_header(c, "Contact")
    c.setFillColor(GREEN)
    c.rect(0, 0, PAGE_W, PAGE_H - 42, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 26)
    c.drawString(38, PAGE_H - 96, "Build a quote-ready enquiry")
    draw_wrapped(c, "Send your product, destination, specification, packing, quantity, delivery window and Incoterm requirements.", 38, PAGE_H - 130, 75, size=11, leading=16, color=white, max_lines=4)
    c.setFillColor(HexColor("#2C574C"))
    c.roundRect(38, 335, PAGE_W - 76, 250, 12, fill=1, stroke=0)
    details = [
        ("Email", EMAIL),
        ("Phone / WhatsApp", PHONE),
        ("Office", ADDRESS),
        ("Website", SITE),
        ("Request form", f"{SITE}/contact.html"),
    ]
    y = 545
    for label, value in details:
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(58, y, label.upper())
        c.setFillColor(white)
        c.setFont("Helvetica", 10)
        c.drawString(58, y - 18, value)
        y -= 43
    c.setFillColor(HexColor("#CFE0D8"))
    c.setFont("Helvetica", 7.4)
    for i, line in enumerate(wrap("This brochure is a buyer-information aid. It is not a quotation, contract, certificate, laboratory report or guarantee of availability. Current documentation is supplied for verification against the relevant enquiry and shipment.", 104)):
        c.drawString(38, 190 - i * 12, line)
    draw_footer(c, page, "Export brochure | Verify product and documentary scope before contracting")
    c.save()
    return path


def draw_product_card(c: canvas.Canvas, product: dict, x: float, y: float, w: float, h: float) -> None:
    c.setFillColor(white)
    c.setStrokeColor(LINE)
    c.roundRect(x, y, w, h, 7, fill=1, stroke=1)
    c.setFillColor(GREEN)
    c.rect(x, y + h - 7, w, 7, fill=1, stroke=0)
    image = safe_image(catalogue_image(ROOT / product["i"]))
    image_box_w, image_box_h = 92, 83
    if image is not None:
        iw, ih = image.getSize()
        scale = min(image_box_w / iw, image_box_h / ih)
        c.drawImage(image, x + 10 + (image_box_w - iw * scale) / 2, y + h - 103 + (image_box_h - ih * scale) / 2, iw * scale, ih * scale, mask="auto", preserveAspectRatio=True)
    title_x = x + 112
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 9.3)
    title_y = y + h - 25
    for index, line in enumerate(wrap(product["t"], 31)[:2]):
        c.drawString(title_x, title_y - index * 12, line)
    c.setFont("Helvetica", 6.9)
    sy = y + h - 57
    for label, value in product.get("s", [])[:5]:
        c.setFillColor(MUTED)
        c.drawString(title_x, sy, f"{label}: {value}"[:55])
        sy -= 10
    c.setStrokeColor(LINE)
    c.line(x + 10, y + 55, x + w - 10, y + 55)
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 6.8)
    c.drawString(x + 10, y + 40, "PACKING")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 6.7)
    c.drawString(x + 55, y + 40, str(product.get("p", "Confirm for enquiry"))[:66])
    c.setFillColor(INK)
    c.setFont("Helvetica-Bold", 6.8)
    c.drawString(x + 10, y + 27, "LOAD")
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 6.7)
    c.drawString(x + 55, y + 27, str(product.get("l", "Confirm for enquiry"))[:66])
    c.setFillColor(GREEN_2)
    c.setFont("Helvetica", 6.5)
    c.drawString(x + 10, y + 12, f"jftagro.com/{product.get('u', 'products.html')}")


def build_catalogue(products: list[dict]) -> Path:
    path = OUTPUT / "JFT-Agro-Product-Catalogue.pdf"
    c = canvas.Canvas(str(path), pagesize=A4, pageCompression=1)
    c.setTitle("JFT Agro Overseas — Product Catalogue")
    c.setAuthor("JFT Agro Overseas")
    cover(
        c,
        "Indian agro product catalogue",
        f"{len(products)} products across rice, spices, flours, pulses, oilseeds, botanicals, grains, feed ingredients and related categories.",
        ROOT / "images" / "homepage" / "all-products-jft-agro-hero-v1.webp",
        "Product Catalogue 2026",
    )
    grouped = defaultdict(list)
    for product in products:
        grouped[product["c"]].append(product)
    ordered = ["rice", "spices", "flour", "pulses", "oilseeds", "herbs", "feed", "wheat", "sugar", "raisins"]

    draw_header(c, "Catalogue guide")
    c.setFillColor(CREAM)
    c.rect(0, 0, PAGE_W, PAGE_H - 42, fill=1, stroke=0)
    c.setFillColor(GREEN)
    c.setFont("Helvetica-Bold", 23)
    c.drawString(38, PAGE_H - 88, "Browse by product group")
    y = PAGE_H - 130
    for index, category in enumerate(ordered):
        c.setFillColor(white)
        c.roundRect(38, y - 42, PAGE_W - 76, 42, 7, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.circle(60, y - 21, 10, fill=1, stroke=0)
        c.setFillColor(GREEN)
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(60, y - 24, str(index + 1))
        c.setFont("Helvetica-Bold", 10)
        c.drawString(82, y - 18, CATEGORY_LABELS[category])
        c.setFillColor(MUTED)
        c.setFont("Helvetica", 8)
        c.drawString(82, y - 32, f"{len(grouped[category])} catalogued product{'s' if len(grouped[category]) != 1 else ''}")
        y -= 54
    c.setFillColor(MUTED)
    c.setFont("Helvetica", 7.3)
    c.drawString(38, 82, "Values shown are catalogue reference fields, not automatic contractual tolerances.")
    c.drawString(38, 68, "Confirm the complete specification, method, packing, destination compliance and load plan in writing.")
    draw_footer(c, 2)
    c.showPage()

    page_no = 3
    for category in ordered:
        category_products = grouped[category]
        page_count = math.ceil(len(category_products) / 4)
        for chunk_index in range(page_count):
            chunk = category_products[chunk_index * 4 : (chunk_index + 1) * 4]
            draw_header(c, f"{CATEGORY_LABELS[category]} · {chunk_index + 1}/{page_count}")
            c.setFillColor(CREAM)
            c.rect(0, 0, PAGE_W, PAGE_H - 42, fill=1, stroke=0)
            c.setFillColor(GREEN)
            c.setFont("Helvetica-Bold", 21)
            c.drawString(38, PAGE_H - 80, CATEGORY_LABELS[category])
            draw_wrapped(c, CATEGORY_INTROS[category], 38, PAGE_H - 103, 86, size=8.2, leading=11, color=MUTED, max_lines=2)
            for index, product in enumerate(chunk):
                col = index % 2
                row = index // 2
                x = 38 + col * 262
                y = PAGE_H - 371 - row * 304
                draw_product_card(c, product, x, y, 248, 276)
            draw_footer(c, page_no, "Catalogue reference | Final written specification governs every supply")
            c.showPage()
            page_no += 1

    draw_header(c, "Buyer brief")
    c.setFillColor(GREEN)
    c.rect(0, 0, PAGE_W, PAGE_H - 42, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 25)
    c.drawString(38, PAGE_H - 92, "Request a shipment-specific offer")
    draw_wrapped(c, "For a useful comparison, include the following information in your request.", 38, PAGE_H - 125, 76, size=10.5, leading=15, color=white, max_lines=3)
    fields = ["Product and use", "Destination and port", "Full specification", "Packing and labelling", "Quantity and timing", "Incoterm", "Inspection and documents", "Payment-control preference"]
    y = PAGE_H - 185
    for index, field in enumerate(fields, 1):
        col = (index - 1) % 2
        row = (index - 1) // 2
        x = 38 + col * 262
        yy = y - row * 76
        c.setFillColor(HexColor("#2C574C"))
        c.roundRect(x, yy - 52, 248, 52, 7, fill=1, stroke=0)
        c.setFillColor(GOLD)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 14, yy - 21, f"{index:02d}")
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 9)
        c.drawString(x + 47, yy - 21, field)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 11)
    c.drawString(38, 260, EMAIL)
    c.drawString(38, 238, PHONE)
    c.setFont("Helvetica", 9)
    c.drawString(38, 217, ADDRESS)
    c.drawString(38, 196, f"{SITE}/contact.html")
    c.setFillColor(HexColor("#CFE0D8"))
    c.setFont("Helvetica", 7.1)
    note = "This catalogue is an enquiry aid. It does not establish origin, availability, regulatory acceptance, certification status, price, shipment timing or contractual tolerance. Request current supporting records and a signed specification for the relevant product and lot."
    for i, line in enumerate(wrap(note, 108)):
        c.drawString(38, 130 - i * 12, line)
    draw_footer(c, page_no, "Product catalogue | Not a quotation, COA, certificate or contract")
    c.save()
    return path


def main() -> int:
    # V2 is the production design: photo-led covers, category dividers and
    # larger product/specification layouts inspired by the supplied references.
    from build_marketing_documents_v2 import main as build_v2

    return build_v2()


if __name__ == "__main__":
    raise SystemExit(main())
