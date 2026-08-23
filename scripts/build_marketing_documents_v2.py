#!/usr/bin/env python3
"""Build the premium, editorial V3 JFT Agro marketing document suite."""

from __future__ import annotations

import json
import math
from collections import defaultdict
from pathlib import Path

from reportlab.lib.colors import HexColor, white
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

from build_marketing_documents import (
    ADDRESS,
    CACHE,
    CATEGORY_INTROS,
    CATEGORY_LABELS,
    CREAM,
    EMAIL,
    GOLD,
    GREEN,
    GREEN_2,
    INK,
    LINE,
    MUTED,
    OUTPUT,
    PAGE_H,
    PAGE_W,
    PHONE,
    PRODUCTS_FILE,
    ROOT,
    SITE,
    catalogue_image,
    safe_image,
    wrap,
)


ORANGE = HexColor("#E76528")
SAGE = HexColor("#A9C59B")
SUN = HexColor("#F5CA45")
PALE = HexColor("#FFF9E9")
RED = HexColor("#B54735")
BRONZE = HexColor("#B78845")
MIST = HexColor("#EEF3EF")
GENERATED = ROOT / "assets" / "brochures" / "generated"

GROUPS = [
    ("rice", "RICE", ["rice"], "Basmati and non-basmati programmes", ORANGE),
    ("spices", "SPICES", ["spices"], "Whole and ground Indian spices", RED),
    ("milling", "FLOURS & MILLING", ["flour", "wheat"], "Wheat and maize milling products", HexColor("#C98E34")),
    ("pulses", "PULSES & OILSEEDS", ["pulses", "oilseeds"], "Pulses, beans and oilseeds", GREEN_2),
    ("botanicals", "HERBS & BOTANICALS", ["herbs"], "Botanical ingredients and powders", HexColor("#557B43")),
    ("feed", "GRAINS & FEED", ["feed"], "Cereals, millets and feed ingredients", HexColor("#8A6C35")),
    ("speciality", "SPECIALITY PRODUCTS", ["sugar", "raisins"], "Sugar and Indian raisins", HexColor("#7A456E")),
]


def draw_crop(c: canvas.Canvas, path: Path, x: float, y: float, w: float, h: float, darken: float = 0) -> None:
    image_path = catalogue_image(path) if path.is_file() else path
    image = safe_image(image_path)
    if image is None:
        c.setFillColor(GREEN_2)
        c.rect(x, y, w, h, fill=1, stroke=0)
        return
    iw, ih = image.getSize()
    scale = max(w / iw, h / ih)
    dw, dh = iw * scale, ih * scale
    c.saveState()
    clip = c.beginPath()
    clip.rect(x, y, w, h)
    c.clipPath(clip, stroke=0, fill=0)
    c.drawImage(image, x + (w - dw) / 2, y + (h - dh) / 2, dw, dh, mask="auto")
    if darken:
        c.setFillColor(GREEN)
        if hasattr(c, "setFillAlpha"):
            c.setFillAlpha(darken)
        c.rect(x, y, w, h, fill=1, stroke=0)
    c.restoreState()


def draw_logo_light(c: canvas.Canvas, x: float, y: float, width: float = 100) -> None:
    image = safe_image(ROOT / "images" / "jft-logo-transparent.webp")
    if image:
        iw, ih = image.getSize()
        c.drawImage(image, x, y, width, width * ih / iw, mask="auto")


def footer(c: canvas.Canvas, page: int, dark: bool = False) -> None:
    color = HexColor("#D9E6E0") if dark else MUTED
    c.setFillColor(color)
    c.setFont("Helvetica", 6.7)
    c.drawString(30, 17, "JFT AGRO OVERSEAS  ·  INDIA TO GLOBAL MARKETS")
    c.drawRightString(PAGE_W - 30, 17, f"JFTAGRO.COM  ·  {page:02d}")


def top_rule(c: canvas.Canvas, label: str, color=GREEN) -> None:
    c.setFillColor(color)
    c.rect(0, PAGE_H - 38, PAGE_W, 38, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 8)
    c.drawString(30, PAGE_H - 24, "JFT AGRO OVERSEAS")
    c.setFillColor(white)
    c.drawRightString(PAGE_W - 30, PAGE_H - 24, label)


def cover_v2(c: canvas.Canvas, title: str, subtitle: str, image: Path, edition: str, accent=GOLD) -> None:
    draw_crop(c, image, 0, 0, PAGE_W, PAGE_H, darken=.08)
    c.setFillColor(GREEN)
    if hasattr(c, "setFillAlpha"): c.setFillAlpha(.93)
    c.rect(0, PAGE_H - 122, PAGE_W, 122, fill=1, stroke=0)
    c.rect(0, 0, PAGE_W, 58, fill=1, stroke=0)
    c.setFillAlpha(1)
    draw_logo_light(c, 34, PAGE_H - 94, 108)
    c.setFillColor(accent); c.roundRect(PAGE_W - 190, PAGE_H - 83, 155, 26, 13, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 7.2)
    c.drawCentredString(PAGE_W - 112.5, PAGE_H - 73, edition.upper())

    c.setFillColor(white)
    if hasattr(c, "setFillAlpha"): c.setFillAlpha(.96)
    c.roundRect(30, 282, 314, 300, 10, fill=1, stroke=0)
    c.setFillAlpha(1)
    c.setFillColor(accent); c.rect(30, 545, 314, 37, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 7.8)
    c.drawString(49, 559, "INDIAN ORIGIN  /  MEASURABLE SPECS  /  EXPORT SUPPORT")
    c.setFillColor(GREEN); c.setFont("Times-Bold", 32)
    y = 505
    for line in wrap(title, 18):
        c.drawString(49, y, line); y -= 37
    c.setStrokeColor(HexColor("#D9D1BE")); c.line(49, y - 3, 310, y - 3)
    c.setFillColor(MUTED); c.setFont("Helvetica", 9.5); y -= 31
    for line in wrap(subtitle, 43):
        c.drawString(49, y, line); y -= 14
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 7.2)
    c.drawString(49, 312, "BUYER-FOCUSED EDITION  |  2026")
    c.setFillColor(white); c.setFont("Helvetica", 7)
    c.drawString(34, 30, f"{SITE}  |  {EMAIL}  |  {PHONE}")
    c.showPage()


def photo_tile(c: canvas.Canvas, product: dict, x: float, y: float, w: float, h: float, color=GREEN) -> None:
    draw_crop(c, ROOT / product["i"], x, y, w, h, darken=.18)
    c.setFillColor(color)
    if hasattr(c, "setFillAlpha"):
        c.setFillAlpha(.86)
    c.rect(x, y, w, 42, fill=1, stroke=0)
    c.setFillAlpha(1)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9.3)
    for idx, line in enumerate(wrap(product["t"], max(18, int(w / 6.2)))[:2]):
        c.drawString(x + 11, y + 26 - idx * 11, line)


def feature_stat(c: canvas.Canvas, x: float, y: float, value: str, label: str, color=GREEN) -> None:
    c.setFillColor(color)
    c.roundRect(x, y, 156, 70, 6, fill=1, stroke=0)
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 17 if len(value) < 12 else 11)
    c.drawString(x + 14, y + 39, value)
    c.setFillColor(white)
    c.setFont("Helvetica", 7.5)
    c.drawString(x + 14, y + 20, label)


def build_introduction(products: list[dict]) -> Path:
    out = OUTPUT / "JFT-Agro-Company-Introduction.pdf"
    c = canvas.Canvas(str(out), pagesize=A4, pageCompression=1)
    c.setTitle("JFT Agro Overseas — Company Introduction")
    cover_v2(c, "INDIAN AGRO. GLOBAL TRADE.", "A refined introduction to JFT Agro Overseas, our product portfolio and buyer-controlled export workflow.", GENERATED / "jft-premium-commodity-cover-v1.png", "Company Profile 2026")

    # Editorial opening
    c.setFillColor(PALE); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_crop(c, GENERATED / "jft-indian-farm-origin-editorial-v1.png", PAGE_W * .54, 0, PAGE_W * .46, PAGE_H, darken=.08)
    c.setFillColor(ORANGE); c.rect(0, PAGE_H - 135, PAGE_W * .54, 135, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 27)
    c.drawString(34, PAGE_H - 70, "BUILT FOR")
    c.drawString(34, PAGE_H - 103, "BUYER CLARITY")
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 14)
    c.drawString(34, PAGE_H - 180, "A practical export partner from India")
    body = "JFT Agro Overseas coordinates Indian agricultural commodity supply for international buyers. We align the product, measurable acceptance fields, packing, documents and shipment terms before an order moves forward."
    y = PAGE_H - 210
    c.setFillColor(MUTED); c.setFont("Helvetica", 9.5)
    for line in wrap(body, 53): c.drawString(34, y, line); y -= 14
    y -= 20
    for value, label in [("84", "catalogued products"), ("10", "product groups"), ("FOB · CIF · CNF", "enquiry terms")]:
        feature_stat(c, 34, y - 70, value, label); y -= 86
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 8)
    c.drawString(34, 55, "NAVI MUMBAI · MAHARASHTRA · INDIA")
    footer(c, 2); c.showPage()

    # Product mosaic
    c.setFillColor(CREAM); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    top_rule(c, "PRODUCT UNIVERSE")
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 27)
    c.drawString(30, PAGE_H - 82, "ONE DESK. TEN PRODUCT GROUPS.")
    c.setFillColor(MUTED); c.setFont("Helvetica", 9)
    c.drawString(30, PAGE_H - 104, "From staple foods to spices, botanicals and feed ingredients.")
    featured = [products[0], products[20], products[37], products[42], products[47], products[52], products[67], products[-1]]
    positions = [(30, 500, 255, 190), (310, 500, 255, 190), (30, 285, 160, 190), (215, 285, 160, 190), (400, 285, 165, 190), (30, 70, 255, 190), (310, 70, 122, 190), (447, 70, 118, 190)]
    colors = [ORANGE, RED, GREEN_2, HexColor("#C98E34"), HexColor("#557B43"), HexColor("#8A6C35"), HexColor("#7A456E"), GREEN]
    for product, pos, color in zip(featured, positions, colors): photo_tile(c, product, *pos, color)
    footer(c, 3); c.showPage()

    # Buyer workflow
    c.setFillColor(GREEN); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_crop(c, ROOT / "images" / "homepage" / "operational-rice-milling-hd-v1.webp", 0, PAGE_H - 270, PAGE_W, 270, darken=.55)
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 9); c.drawString(30, PAGE_H - 66, "HOW AN ENQUIRY MOVES")
    c.setFillColor(white); c.setFont("Helvetica-Bold", 28); c.drawString(30, PAGE_H - 105, "FROM BUYING BRIEF TO SHIPMENT FILE")
    steps = [("01", "DEFINE", "Product, use, destination and measurable acceptance fields."), ("02", "ALIGN", "Packing, quantity, Incoterm, timing and documentary scope."), ("03", "APPROVE", "Written specification, commercial terms and payment controls."), ("04", "VERIFY", "Lot evidence, inspection status and release requirements."), ("05", "DISPATCH", "Container plan, loading milestones and final documents.")]
    y = 500
    for number, title, body in steps:
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 19); c.drawString(35, y, number)
        c.setFillColor(white); c.setFont("Helvetica-Bold", 13); c.drawString(92, y + 3, title)
        c.setFillColor(HexColor("#CFE0D8")); c.setFont("Helvetica", 8.5)
        c.drawString(170, y + 3, body)
        c.setStrokeColor(HexColor("#53766D")); c.line(35, y - 25, PAGE_W - 35, y - 25)
        y -= 82
    footer(c, 4, True); c.showPage()

    # Verification spread
    c.setFillColor(white); c.rect(0, 0, PAGE_W, PAGE_H, fill=1, stroke=0)
    draw_crop(c, GENERATED / "jft-quality-verification-editorial-v1.png", 0, 0, PAGE_W * .46, PAGE_H, darken=.18)
    c.setFillColor(ORANGE); c.rect(PAGE_W * .46, PAGE_H - 205, PAGE_W * .54, 205, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 27)
    c.drawString(PAGE_W * .50, PAGE_H - 72, "PROOF THAT")
    c.drawString(PAGE_W * .50, PAGE_H - 105, "MATCHES THE")
    c.drawString(PAGE_W * .50, PAGE_H - 138, "SHIPMENT")
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 12)
    c.drawString(PAGE_W * .50, PAGE_H - 245, "Verification before reliance")
    items = ["Current registration and certification copies", "Approved product specification and tolerances", "Lot-specific COA or inspection evidence where agreed", "Packing artwork and shipment document checklist", "Destination-specific requirements confirmed for the order"]
    y = PAGE_H - 285
    for item in items:
        c.setFillColor(GOLD); c.circle(PAGE_W * .51, y + 2, 5, fill=1, stroke=0)
        c.setFillColor(MUTED); c.setFont("Helvetica", 8.5)
        for idx, line in enumerate(wrap(item, 48)[:2]): c.drawString(PAGE_W * .54, y - idx * 11, line)
        y -= 52
    c.setFillColor(PALE); c.roundRect(PAGE_W * .50, 85, PAGE_W * .44, 120, 7, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 9); c.drawString(PAGE_W * .53, 175, "IMPORTANT")
    c.setFillColor(MUTED); c.setFont("Helvetica", 7.5)
    note = "A brochure is not a certificate, COA, quotation or contract. Request current records for the relevant product, destination and shipment."
    yy=154
    for line in wrap(note, 48): c.drawString(PAGE_W * .53, yy, line); yy -= 11
    footer(c, 5); c.showPage()

    # Contact
    draw_crop(c, GENERATED / "jft-export-operations-editorial-v1.png", 0, 0, PAGE_W, PAGE_H, darken=.58)
    c.setFillColor(GREEN); c.setFillAlpha(.94); c.roundRect(30, 70, PAGE_W - 60, PAGE_H - 140, 12, fill=1, stroke=0); c.setFillAlpha(1)
    draw_logo_light(c, 55, PAGE_H - 130, 110)
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold", 10); c.drawString(55, PAGE_H - 185, "START WITH A COMPLETE BUYING BRIEF")
    c.setFillColor(white); c.setFont("Helvetica-Bold", 29); c.drawString(55, PAGE_H - 230, "LET'S BUILD A")
    c.drawString(55, PAGE_H - 265, "QUOTE-READY ENQUIRY")
    checklist = ["Product and intended use", "Destination country and discharge port", "Specification and tolerance fields", "Packing, labelling and quantity", "Delivery window and Incoterm", "Inspection and document requirements"]
    y = PAGE_H - 320
    for idx, item in enumerate(checklist, 1):
        c.setFillColor(GOLD); c.circle(65, y + 2, 9, fill=1, stroke=0)
        c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 7); c.drawCentredString(65, y, str(idx))
        c.setFillColor(white); c.setFont("Helvetica", 9); c.drawString(88, y - 2, item); y -= 38
    c.setFillColor(GOLD); c.rect(55, 130, PAGE_W - 110, 72, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 11); c.drawString(72, 174, EMAIL)
    c.setFont("Helvetica", 9); c.drawString(72, 151, f"{PHONE}  ·  {ADDRESS}")
    footer(c, 6, True); c.save(); return out


def mini_product(c: canvas.Canvas, product: dict, x: float, y: float, w: float, h: float, accent=ORANGE) -> None:
    c.setFillColor(white); c.roundRect(x, y, w, h, 7, fill=1, stroke=0)
    draw_crop(c, ROOT / product["i"], x, y + 80, w, h - 80)
    c.setFillColor(accent); c.rect(x, y + 66, w, 14, fill=1, stroke=0)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold", 9)
    for idx, line in enumerate(wrap(product["t"], max(20, int(w / 6.4)))[:2]): c.drawString(x + 11, y + 51 - idx * 11, line)
    specs = product.get("s", [])[:2]
    c.setFillColor(MUTED); c.setFont("Helvetica", 6.8); sy = y + 24
    for label, value in specs: c.drawString(x + 11, sy, f"{label}: {value}"[:42]); sy -= 10


def build_brochure(products: list[dict]) -> Path:
    out = OUTPUT / "JFT-Agro-Export-Brochure.pdf"
    c = canvas.Canvas(str(out), pagesize=A4, pageCompression=1)
    c.setTitle("JFT Agro Overseas — Export Brochure")
    cover_v2(c, "PRODUCT RANGE. EXPORT SUPPORT.", "A premium buyer brochure for clear, specification-led Indian agricultural commodity enquiries.", GENERATED / "jft-export-operations-editorial-v1.png", "Export Portfolio 2026", ORANGE)
    grouped=defaultdict(list)
    for p in products: grouped[p["c"]].append(p)

    # Contents/photo index
    c.setFillColor(PALE); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0); top_rule(c,"PRODUCT INDEX",ORANGE)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",27); c.drawString(30,PAGE_H-83,"EXPLORE THE RANGE")
    c.setFillColor(MUTED); c.setFont("Helvetica",9); c.drawString(30,PAGE_H-105,"Selected products appear in this brochure. The complete catalogue covers all 84 products.")
    tiles=[grouped["rice"][0],grouped["spices"][0],grouped["flour"][0],grouped["pulses"][0],grouped["oilseeds"][0],grouped["herbs"][0],grouped["feed"][0],grouped["raisins"][0]]
    for i,p in enumerate(tiles):
        col=i%2; row=i//2; photo_tile(c,p,30+col*275,500-row*143,255,125,[ORANGE,RED,HexColor("#C98E34"),GREEN_2,HexColor("#557B43"),HexColor("#557B43"),HexColor("#8A6C35"),HexColor("#7A456E")][i])
    footer(c,2); c.showPage()

    page=3
    feature_sets=[("RICE",grouped["rice"][:8],ORANGE,"Basmati and non-basmati rice for retail, foodservice and processing programmes."),("SPICES",grouped["spices"][:8],RED,"Whole and ground spices aligned to buyer-defined physical and chemical fields."),("FLOURS & MILLING",grouped["flour"]+grouped["wheat"],HexColor("#C98E34"),"Wheat and maize milling products supplied against agreed end-use requirements."),("PULSES & OILSEEDS",grouped["pulses"]+grouped["oilseeds"][:4],GREEN_2,"Pulses, beans and oilseeds for distribution and processing buyers."),("HERBS & BOTANICALS",grouped["herbs"][:8],HexColor("#557B43"),"Botanical products offered subject to identity, purity and destination-compliance criteria."),("GRAINS & FEED",grouped["feed"][:8],HexColor("#8A6C35"),"Cereals, millets and feed ingredients for approved food and feed applications.")]
    for title,items,accent,desc in feature_sets:
        c.setFillColor(PALE); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0); top_rule(c,title,accent)
        c.setFillColor(accent); c.rect(0,PAGE_H-155,PAGE_W,117,fill=1,stroke=0)
        c.setFillColor(white); c.setFont("Helvetica-Bold",25); c.drawString(30,PAGE_H-91,title)
        c.setFont("Helvetica",9); c.drawString(30,PAGE_H-119,desc)
        for i,p in enumerate(items[:8]):
            col=i%2; row=i//2; mini_product(c,p,30+col*275,505-row*145,255,130,accent)
        footer(c,page); c.showPage(); page+=1

    # Packing and documents
    c.setFillColor(GREEN); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)
    draw_crop(c,GENERATED/"jft-export-operations-editorial-v1.png",0,PAGE_H-310,PAGE_W,310,darken=.55)
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold",9); c.drawString(30,PAGE_H-70,"COMMERCIAL ALIGNMENT")
    c.setFillColor(white); c.setFont("Helvetica-Bold",27); c.drawString(30,PAGE_H-110,"PACKING, LOAD & DOCUMENTS")
    cols=[("PACKING",["PP, non-woven, kraft or carton formats","Retail and bulk net weights","Buyer artwork and destination labelling","Final format confirmed before order"]),("LOAD PLANNING",["Container type and payload estimate","Product-density and packing assumptions","Port, route and cut-off coordination","Final load plan requires confirmation"]),("DOCUMENTS",["Commercial and transport documents","Origin and phytosanitary scope where applicable","Inspection or laboratory evidence as agreed","Current credential copies for verification"])]
    for i,(title,items) in enumerate(cols):
        x=30+i*185; c.setFillColor(HexColor("#2C574C")); c.roundRect(x,155,170,300,8,fill=1,stroke=0)
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold",12); c.drawString(x+15,420,title)
        y=383
        for item in items:
            c.setFillColor(white); c.circle(x+18,y+3,3,fill=1,stroke=0); c.setFont("Helvetica",7.7)
            for j,line in enumerate(wrap(item,28)[:2]): c.drawString(x+30,y-j*10,line)
            y-=58
    footer(c,page,True); c.showPage(); page+=1

    # Workflow
    c.setFillColor(PALE); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0); top_rule(c,"BUYER WORKFLOW",ORANGE)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",27); c.drawString(30,PAGE_H-84,"SIX CONTROL POINTS")
    c.setFillColor(MUTED); c.setFont("Helvetica",9); c.drawString(30,PAGE_H-106,"A clear enquiry reduces assumptions and makes offers easier to compare.")
    steps=[("01","BUYER BRIEF","Product, destination, specification and quantity."),("02","OFFER ALIGNMENT","Availability, packing, Incoterm and evidence scope."),("03","APPROVED SPEC","Written tolerances, artwork and inspection plan."),("04","ORDER CONTROLS","Contract, payment and document checklist."),("05","RELEASE & LOAD","Lot evidence, container plan and dispatch."),("06","FINAL FILE","Shipment-specific documents issued as agreed.")]
    for i,(n,t,b) in enumerate(steps):
        col=i%2; row=i//2; x=30+col*275; y=565-row*180
        c.setFillColor([ORANGE,RED,GREEN_2,HexColor("#C98E34"),HexColor("#557B43"),HexColor("#7A456E")][i]); c.roundRect(x,y,255,145,8,fill=1,stroke=0)
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold",20); c.drawString(x+16,y+102,n)
        c.setFillColor(white); c.setFont("Helvetica-Bold",11); c.drawString(x+16,y+76,t)
        c.setFont("Helvetica",8); yy=y+54
        for line in wrap(b,38): c.drawString(x+16,yy,line); yy-=11
    footer(c,page); c.showPage(); page+=1

    # Contact
    draw_crop(c,GENERATED/"jft-premium-commodity-cover-v1.png",0,0,PAGE_W,PAGE_H,darken=.62)
    c.setFillColor(ORANGE); c.rect(0,0,PAGE_W*.42,PAGE_H,fill=1,stroke=0)
    draw_logo_light(c,35,PAGE_H-105,100)
    c.setFillColor(white); c.setFont("Helvetica-Bold",28); c.drawString(35,PAGE_H-180,"READY TO")
    c.drawString(35,PAGE_H-215,"SOURCE")
    c.drawString(35,PAGE_H-250,"FROM INDIA?")
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",9); c.drawString(35,PAGE_H-300,"SEND A COMPLETE BUYING BRIEF")
    c.setFont("Helvetica",8); yy=PAGE_H-328
    for line in wrap("Product · destination · specification · packing · quantity · delivery window · Incoterm · documents",35): c.drawString(35,yy,line); yy-=12
    c.setFillColor(white); c.roundRect(PAGE_W*.47,110,PAGE_W*.47,PAGE_H-220,10,fill=1,stroke=0)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",14); c.drawString(PAGE_W*.51,PAGE_H-165,"JFT AGRO EXPORT DESK")
    details=[("EMAIL",EMAIL),("PHONE / WHATSAPP",PHONE),("OFFICE",ADDRESS),("WEBSITE",SITE),("REQUEST FORM",f"{SITE}/contact.html")]
    yy=PAGE_H-210
    for label,value in details:
        c.setFillColor(ORANGE); c.setFont("Helvetica-Bold",7); c.drawString(PAGE_W*.51,yy,label)
        c.setFillColor(MUTED); c.setFont("Helvetica",8.5)
        for line in wrap(value,42): c.drawString(PAGE_W*.51,yy-16,line); yy-=11
        yy-=35
    c.setFillColor(PALE); c.roundRect(PAGE_W*.51,150,PAGE_W*.38,100,6,fill=1,stroke=0)
    c.setFillColor(MUTED); c.setFont("Helvetica",6.8); yy=220
    note="Buyer-information brochure only. Current certificates, lot evidence, price, availability and shipment terms require enquiry-specific confirmation."
    for line in wrap(note,48): c.drawString(PAGE_W*.53,yy,line); yy-=10
    footer(c,page,True); c.save(); return out


def section_products(all_products: list[dict], categories: list[str]) -> list[dict]:
    return [p for p in all_products if p["c"] in categories]


def product_strip(c: canvas.Canvas, p: dict, x: float, y: float, w: float, h: float, accent) -> None:
    c.setFillColor(white); c.roundRect(x, y, w, h, 8, fill=1, stroke=0)
    draw_crop(c, ROOT / p["i"], x, y, 190, h)
    c.setFillColor(accent); c.rect(x + 190, y, 7, h, fill=1, stroke=0)
    tx = x + 218
    c.setFillColor(accent); c.setFont("Helvetica-Bold", 6.5)
    c.drawString(tx, y + h - 22, CATEGORY_LABELS[p["c"]].upper())
    c.setFillColor(GREEN); c.setFont("Times-Bold", 14)
    title_y = y + h - 45
    for i, line in enumerate(wrap(p["t"], 35)[:2]): c.drawString(tx, title_y - i * 15, line)

    specs = p.get("s", [])[:6]
    start_y = y + h - 82
    col_w = 150
    for idx, (label, value) in enumerate(specs):
        col, row = idx % 2, idx // 2
        sx, sy = tx + col * col_w, start_y - row * 35
        c.setFillColor(MIST); c.roundRect(sx, sy - 22, col_w - 10, 28, 4, fill=1, stroke=0)
        c.setFillColor(accent); c.setFont("Helvetica-Bold", 5.8); c.drawString(sx + 8, sy - 3, str(label).upper()[:21])
        c.setFillColor(INK); c.setFont("Helvetica", 7); c.drawString(sx + 8, sy - 15, str(value)[:27])

    c.setStrokeColor(LINE); c.line(tx, y + 45, x + w - 18, y + 45)
    c.setFillColor(INK); c.setFont("Helvetica-Bold", 6); c.drawString(tx, y + 30, "PACKING / OFFER BASIS")
    c.setFillColor(MUTED); c.setFont("Helvetica", 6.5)
    c.drawString(tx, y + 17, str(p.get("p", "Confirm for enquiry"))[:54])
    c.setFillColor(accent); c.roundRect(x + w - 120, y + 13, 102, 22, 11, fill=1, stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold", 5.8)
    c.drawCentredString(x + w - 69, y + 21, "VIEW LIVE PRODUCT PAGE")


def group_divider(c: canvas.Canvas, title: str, subtitle: str, items: list[dict], accent, page: int) -> None:
    hero=items[0]
    draw_crop(c,ROOT/hero["i"],0,0,PAGE_W,PAGE_H,darken=.38)
    c.setFillColor(accent); c.setFillAlpha(.92); c.rect(0,0,PAGE_W*.48,PAGE_H,fill=1,stroke=0); c.setFillAlpha(1)
    c.setFillColor(white); c.setFont("Helvetica-Bold",32); yy=PAGE_H-150
    for line in wrap(title,18): c.drawString(32,yy,line); yy-=38
    c.setFillColor(GOLD); c.rect(32,yy-5,85,7,fill=1,stroke=0); yy-=42
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",10); c.drawString(32,yy,subtitle.upper()); yy-=35
    c.setFont("Helvetica",8.5)
    names=" · ".join(p["t"] for p in items)
    for line in wrap(names,38): c.drawString(32,yy,line); yy-=13
    c.setFillColor(white); c.setFont("Helvetica-Bold",9); c.drawString(32,75,f"{len(items)} PRODUCTS IN THIS SECTION")
    footer(c,page,True); c.showPage()


def build_catalogue(products: list[dict]) -> Path:
    out=OUTPUT/"JFT-Agro-Product-Catalogue.pdf"
    c=canvas.Canvas(str(out),pagesize=A4,pageCompression=1)
    c.setTitle("JFT Agro Overseas — Product Catalogue")
    cover_v2(c,"84 PRODUCTS. ONE EXPORT DESK.","A comprehensive, specification-led catalogue of Indian agricultural commodities for global buyers.",GENERATED/"jft-premium-commodity-cover-v1.png","Master Catalogue 2026",ORANGE)
    page=2

    # Welcome spread
    c.setFillColor(PALE); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0)
    draw_crop(c,GENERATED/"jft-indian-farm-origin-editorial-v1.png",PAGE_W*.50,0,PAGE_W*.50,PAGE_H)
    c.setFillColor(ORANGE); c.rect(0,PAGE_H-150,PAGE_W*.50,150,fill=1,stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold",27); c.drawString(30,PAGE_H-75,"INDIA'S PRODUCT")
    c.drawString(30,PAGE_H-108,"DIVERSITY, ORGANISED")
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",13); c.drawString(30,PAGE_H-190,"Catalogue purpose")
    body="This catalogue helps buyers shortlist JFT Agro products and prepare a measurable enquiry. Each card connects to a live product page and presents selected reference fields from the maintained website dataset."
    yy=PAGE_H-220; c.setFillColor(MUTED); c.setFont("Helvetica",9)
    for line in wrap(body,47): c.drawString(30,yy,line); yy-=14
    feature_stat(c,30,390,"84","catalogued products",GREEN); feature_stat(c,30,300,"10","commercial categories",GREEN_2); feature_stat(c,30,210,"CURRENT","website-linked pages",HexColor("#557B43"))
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",8); c.drawString(30,90,"FINAL WRITTEN SPECIFICATION GOVERNS EVERY SUPPLY")
    footer(c,page); c.showPage(); page+=1

    # Index
    c.setFillColor(CREAM); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0); top_rule(c,"CONTENTS",ORANGE)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",28); c.drawString(30,PAGE_H-84,"PRODUCT CONTENTS")
    y=PAGE_H-135
    for idx,(_,title,cats,subtitle,accent) in enumerate(GROUPS,1):
        items=section_products(products,cats)
        c.setFillColor(accent); c.roundRect(30,y-72,PAGE_W-60,72,7,fill=1,stroke=0)
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold",18); c.drawString(47,y-31,f"{idx:02d}")
        c.setFillColor(white); c.setFont("Helvetica-Bold",12); c.drawString(92,y-27,title)
        c.setFont("Helvetica",7.8); c.drawString(92,y-46,subtitle)
        c.setFont("Helvetica-Bold",8); c.drawRightString(PAGE_W-48,y-36,f"{len(items)} PRODUCTS")
        y-=88
    c.setFillColor(MUTED); c.setFont("Helvetica",7); c.drawString(30,55,"Values are catalogue references. Confirm specification, method, packing, destination compliance and load plan in writing.")
    footer(c,page); c.showPage(); page+=1

    for _,title,cats,subtitle,accent in GROUPS:
        items=section_products(products,cats)
        group_divider(c,title,subtitle,items,accent,page); page+=1
        for chunk_start in range(0,len(items),3):
            chunk=items[chunk_start:chunk_start+3]
            c.setFillColor(PALE); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0); top_rule(c,title,accent)
            c.setFillColor(accent); c.setFont("Helvetica-Bold",20); c.drawString(30,PAGE_H-76,title)
            c.setFillColor(MUTED); c.setFont("Helvetica",8); c.drawRightString(PAGE_W-30,PAGE_H-76,f"PRODUCTS {chunk_start+1}–{chunk_start+len(chunk)} OF {len(items)}")
            ys=[535,305,75]
            for p,y in zip(chunk,ys): product_strip(c,p,30,y,PAGE_W-60,205,accent)
            footer(c,page); c.showPage(); page+=1

    # Quick-reference list
    c.setFillColor(CREAM); c.rect(0,0,PAGE_W,PAGE_H,fill=1,stroke=0); top_rule(c,"QUICK REFERENCE",ORANGE)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",25); c.drawString(30,PAGE_H-82,"ALL PRODUCTS AT A GLANCE")
    c.setFillColor(MUTED); c.setFont("Helvetica",8); c.drawString(30,PAGE_H-104,"Use the page URL in each product card for the current website record.")
    columns=[products[i::3] for i in range(3)]
    for col,items in enumerate(columns):
        x=30+col*185; y=PAGE_H-140
        for p in items:
            c.setFillColor(GREEN); c.setFont("Helvetica-Bold",6.8)
            for line in wrap(p["t"],28)[:2]: c.drawString(x,y,line); y-=9
            c.setFillColor(MUTED); c.setFont("Helvetica",5.8); c.drawString(x,y,CATEGORY_LABELS[p["c"]].upper()); y-=16
    footer(c,page); c.showPage(); page+=1

    # Final contact
    draw_crop(c,GENERATED/"jft-export-operations-editorial-v1.png",0,0,PAGE_W,PAGE_H,darken=.62)
    c.setFillColor(GREEN); c.setFillAlpha(.94); c.rect(0,0,PAGE_W*.58,PAGE_H,fill=1,stroke=0); c.setFillAlpha(1)
    draw_logo_light(c,35,PAGE_H-105,105)
    c.setFillColor(GOLD); c.setFont("Helvetica-Bold",9); c.drawString(35,PAGE_H-165,"REQUEST A SHIPMENT-SPECIFIC OFFER")
    c.setFillColor(white); c.setFont("Helvetica-Bold",29); c.drawString(35,PAGE_H-210,"YOUR BUYING")
    c.drawString(35,PAGE_H-245,"BRIEF STARTS")
    c.drawString(35,PAGE_H-280,"THE CONVERSATION")
    fields=["Product and intended use","Destination and port","Full specification","Packing and labelling","Quantity and timing","Incoterm","Inspection and documents","Payment-control preference"]
    y=PAGE_H-335
    for idx,field in enumerate(fields,1):
        c.setFillColor(GOLD); c.setFont("Helvetica-Bold",7); c.drawString(35,y,f"{idx:02d}")
        c.setFillColor(white); c.setFont("Helvetica",8.5); c.drawString(65,y,field); y-=31
    c.setFillColor(ORANGE); c.rect(35,105,PAGE_W*.45,82,fill=1,stroke=0)
    c.setFillColor(white); c.setFont("Helvetica-Bold",10); c.drawString(50,157,EMAIL)
    c.setFont("Helvetica",8); c.drawString(50,136,PHONE); c.drawString(50,119,SITE)
    c.setFillColor(white); c.roundRect(PAGE_W*.63,95,PAGE_W*.30,240,8,fill=1,stroke=0)
    c.setFillColor(GREEN); c.setFont("Helvetica-Bold",11); c.drawString(PAGE_W*.67,300,"IMPORTANT")
    c.setFillColor(MUTED); c.setFont("Helvetica",7.2); yy=275
    note="This catalogue is an enquiry aid. It does not establish origin, availability, regulatory acceptance, certification status, price, shipment timing or contractual tolerance. Request current supporting records and a signed specification for the relevant product and lot."
    for line in wrap(note,31): c.drawString(PAGE_W*.67,yy,line); yy-=11
    footer(c,page,True); c.save(); return out


def main() -> int:
    OUTPUT.mkdir(parents=True,exist_ok=True); CACHE.mkdir(parents=True,exist_ok=True)
    products=json.loads(PRODUCTS_FILE.read_text(encoding="utf-8"))
    files=[build_introduction(products),build_brochure(products),build_catalogue(products)]
    for path in files: print(f"Built V3 {path.relative_to(ROOT)} ({path.stat().st_size/1024/1024:.2f} MiB)")
    return 0


if __name__ == "__main__": raise SystemExit(main())
