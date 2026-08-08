#!/usr/bin/env python3
"""Generate the downloadable JFT Agro corporate introduction PDF."""

from __future__ import annotations

import shutil
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import (
    Image,
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parent.parent
OUTPUT = ROOT / "output" / "pdf" / "JFT_Agro_Introduction.pdf"
ASSET = ROOT / "assets" / "JFT_Agro_Introduction.pdf"
NAVY = colors.HexColor("#1A3C34")
GREEN = colors.HexColor("#3D7030")
GOLD = colors.HexColor("#EEBF45")
CREAM = colors.HexColor("#F8F6EF")
MUTED = colors.HexColor("#56645F")


def page_frame(canvas, doc) -> None:
    width, height = A4
    canvas.saveState()
    canvas.setFillColor(NAVY)
    canvas.rect(0, height - 14 * mm, width, 14 * mm, fill=1, stroke=0)
    canvas.setFillColor(GOLD)
    canvas.rect(0, height - 15.5 * mm, width, 1.5 * mm, fill=1, stroke=0)
    canvas.setFont("Helvetica-Bold", 8)
    canvas.setFillColor(colors.white)
    canvas.drawString(18 * mm, height - 9 * mm, "JFT AGRO OVERSEAS")
    canvas.setFillColor(NAVY)
    canvas.setFont("Helvetica", 7.5)
    canvas.drawString(18 * mm, 10 * mm, "jftagro.com  |  exports@jftagro.com  |  +91 84250 57274")
    canvas.drawRightString(width - 18 * mm, 10 * mm, f"Page {doc.page}")
    canvas.restoreState()


def bullet(text: str, style: ParagraphStyle) -> Paragraph:
    return Paragraph(f"<font color='#EEBF45'>●</font>&nbsp;&nbsp;{text}", style)


def build() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title = ParagraphStyle(
        "Title",
        parent=styles["Title"],
        fontName="Helvetica-Bold",
        fontSize=27,
        leading=31,
        textColor=NAVY,
        alignment=TA_CENTER,
        spaceAfter=8,
    )
    subtitle = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        fontName="Helvetica",
        fontSize=12,
        leading=18,
        textColor=MUTED,
        alignment=TA_CENTER,
    )
    heading = ParagraphStyle(
        "Heading",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=16,
        leading=20,
        textColor=NAVY,
        spaceBefore=6,
        spaceAfter=6,
    )
    body = ParagraphStyle(
        "Body",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=9.5,
        leading=15,
        textColor=MUTED,
        spaceAfter=4,
    )
    small = ParagraphStyle("Small", parent=body, fontSize=8, leading=12)
    card_head = ParagraphStyle(
        "CardHead", parent=body, fontName="Helvetica-Bold", fontSize=10.5, textColor=NAVY, spaceBefore=2, spaceAfter=3
    )

    doc = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        rightMargin=18 * mm,
        leftMargin=18 * mm,
        topMargin=25 * mm,
        bottomMargin=19 * mm,
        title="JFT Agro Overseas — Corporate Introduction",
        author="JFT Agro Overseas LLP",
        subject="Corporate introduction and export enquiry guide",
    )
    story = []
    logo = ROOT / "images" / "jft logo.png"
    story.extend(
        [
            Spacer(1, 8 * mm),
            Image(str(logo), width=65 * mm, height=30 * mm),
            Spacer(1, 6 * mm),
            Paragraph("Indian agricultural commodities.<br/>Prepared for global trade.", title),
            Paragraph("Corporate introduction and export enquiry guide", subtitle),
            Spacer(1, 12 * mm),
        ]
    )
    overview = Table(
        [
            [Paragraph("PRODUCTS", card_head), Paragraph("EXPORT SUPPORT", card_head), Paragraph("TRADE DESK", card_head)],
            [
                Paragraph("Rice, spices, grains, flours, pulses, oilseeds and feed ingredients", small),
                Paragraph("Specifications, packing options, inspection documents and shipment coordination", small),
                Paragraph("FOB, CIF and CNF enquiries handled from Navi Mumbai, India", small),
            ],
        ],
        colWidths=[55 * mm, 55 * mm, 55 * mm],
    )
    overview.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), CREAM),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D7DDD8")),
                ("INNERGRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D7DDD8")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 8),
                ("RIGHTPADDING", (0, 0), (-1, -1), 8),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
            ]
        )
    )
    story.extend(
        [
            overview,
            Spacer(1, 10 * mm),
            Paragraph("A practical export partner", heading),
            Paragraph(
                "JFT Agro Overseas connects international buyers with export-ready agricultural commodities sourced from India. "
                "Our trade desk aligns product grade, packing, documentation and dispatch requirements before an order moves forward, "
                "helping importers compare offers on clear commercial terms.",
                body,
            ),
            Paragraph(
                "This profile is an introduction, not a certificate pack. Current registrations, inspection documents and stamped copies "
                "are supplied for verification against the product, destination and shipment concerned.",
                body,
            ),
            PageBreak(),
            Paragraph("Export portfolio", heading),
        ]
    )

    portfolio = [
        ("Rice", "Basmati and non-basmati varieties, including raw, steam, sella, parboiled and broken grades."),
        ("Spices", "Whole and ground spices such as turmeric, cumin, chilli, coriander, fennel, fenugreek and ginger."),
        ("Grains & flours", "Wheat, maize, millet, sorghum, rice flour, wheat flour and other buyer-specified grades."),
        ("Pulses & oilseeds", "Selected dals, peas, beans, sesame, groundnut and other crop-season-dependent products."),
        ("Feed ingredients", "Commodity feed inputs offered against specification, inspection and destination requirements."),
    ]
    for name, description in portfolio:
        story.append(KeepTogether([Paragraph(name, card_head), Paragraph(description, body)]))
    story.extend(
        [
            Spacer(1, 4 * mm),
            Paragraph("What to include in an enquiry", heading),
            bullet("Product name, grade and any required specification or tolerance", body),
            bullet("Required quantity and preferred pack size / bag material", body),
            bullet("Destination port and requested Incoterm (for example FOB, CIF or CNF)", body),
            bullet("Target shipment window and any destination-specific documents", body),
            bullet("Inspection, private-label or sample requirements", body),
            Spacer(1, 4 * mm),
            Paragraph("Typical export workflow", heading),
        ]
    )
    steps = [
        ["01", "Enquiry review", "Confirm product, grade, volume, packing and destination."],
        ["02", "Commercial offer", "Share specifications, validity, lead time and applicable trade terms."],
        ["03", "Quality & documents", "Align inspection, certificates and lab / shipment documentation."],
        ["04", "Packing & dispatch", "Coordinate production, packing, container loading and shipping documents."],
    ]
    table = Table(steps, colWidths=[13 * mm, 42 * mm, 110 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (0, -1), GOLD),
                ("TEXTCOLOR", (0, 0), (0, -1), NAVY),
                ("FONTNAME", (0, 0), (0, -1), "Helvetica-Bold"),
                ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
                ("TEXTCOLOR", (1, 0), (1, -1), NAVY),
                ("TEXTCOLOR", (2, 0), (2, -1), MUTED),
                ("FONTSIZE", (0, 0), (-1, -1), 8.5),
                ("LEADING", (0, 0), (-1, -1), 12),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("ROWBACKGROUNDS", (1, 0), (-1, -1), [CREAM, colors.white]),
                ("BOX", (0, 0), (-1, -1), 0.6, colors.HexColor("#D7DDD8")),
                ("INNERGRID", (0, 0), (-1, -1), 0.35, colors.HexColor("#D7DDD8")),
                ("TOPPADDING", (0, 0), (-1, -1), 8),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
                ("LEFTPADDING", (0, 0), (-1, -1), 7),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7),
            ]
        )
    )
    story.extend(
        [
            table,
            Spacer(1, 9 * mm),
            Paragraph("Start a trade conversation", heading),
            Paragraph(
                "Email <b>exports@jftagro.com</b> or WhatsApp <b>+91 84250 57274</b><br/>"
                "JFT Agro Overseas LLP, APMC Market, Phase II, Sector 19, Vashi, Navi Mumbai 400705, India<br/>"
                "Website: <b>https://jftagro.com</b>",
                body,
            ),
            Spacer(1, 3 * mm),
            Paragraph(
                "Document note: Product availability, crop, price, certifications and shipping terms are subject to written confirmation. "
                "Request current certificate copies from the trade desk before relying on a registration or approval for import clearance.",
                small,
            ),
        ]
    )
    doc.build(story, onFirstPage=page_frame, onLaterPages=page_frame)
    ASSET.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(OUTPUT, ASSET)
    print(f"Generated {OUTPUT} and copied it to {ASSET}")


if __name__ == "__main__":
    build()
