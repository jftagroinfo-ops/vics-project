#!/usr/bin/env python3
"""Build the four reviewed-priority localized commercial landing pages."""

from __future__ import annotations

import html
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
LANGUAGES = {
    "ar": {
        "dir": "rtl", "name": "العربية", "title": "مصدّر المنتجات الزراعية الهندية",
        "description": "أرز بسمتي وتوابل وبقول وحبوب هندية للتصدير مع مواصفات واضحة ووثائق شحن وخيارات فحص مستقلة.",
        "nav_products": "المنتجات", "nav_process": "آلية التصدير", "nav_docs": "الوثائق", "nav_contact": "طلب عرض سعر",
        "eyebrow": "بيت تصدير معتمد · ISO 9001:2015", "headline": "منتجات زراعية هندية", "headline_em": "تصل إليكم بثقة موثّقة",
        "subhead": "توريد مباشر للأرز والتوابل والبقول والحبوب والبذور الزيتية إلى أكثر من 25 دولة، مع مواصفات الدفعة وخيارات الفحص المستقل وشروط شحن واضحة.",
        "browse": "استعرض المنتجات", "quote": "اطلب عرض سعر", "proof": "جودة يمكن للمشتري التحقق منها",
        "proof_text": "نقدّم المواصفات قبل الطلب، ونؤكد وثائق كل شحنة في الفاتورة الأولية. يمكن ترتيب فحص SGS أو Intertek أو Bureau Veritas عند الطلب وعلى نفقة الطرف المتفق عليه.",
        "products_title": "فئات التوريد الرئيسية", "process_title": "من المصدر إلى الحاوية", "docs_title": "ملف مستندات واضح قبل الشحن",
        "products": ["أرز بسمتي وغير بسمتي", "الكركم والفلفل الأحمر والكمون", "البقول والحمص", "القمح والذرة والدقيق", "السمسم والبذور الزيتية", "السكر والأعلاف الزراعية"],
        "steps": [("01", "تحديد المواصفات", "نؤكد الصنف والدرجة والتعبئة والكمية وميناء الوصول."), ("02", "العينة والعرض", "عينات مؤهلة وشروط شحن مؤكدة قبل الإرسال، ثم فاتورة أولية واضحة."), ("03", "الفحص والتعبئة", "اختبار الدفعة والتعبئة الغذائية وإتاحة فحص طرف ثالث عند الطلب."), ("04", "الشحن والمتابعة", "مستندات التصدير ورقم الحاوية ومتابعة مراحل الشحن.")],
        "docs": ["فاتورة تجارية وقائمة تعبئة", "بوليصة شحن وشهادة منشأ", "شهادة صحة نباتية عند انطباقها", "شهادة تبخير أو تحليل حسب المنتج", "تقارير فحص مستقلة عند الاتفاق"],
        "note": "تختلف المستندات والشهادات حسب المنتج وبلد الاستيراد. اطلب نسخاً سارية ومختومة قبل التعاقد.",
        "form_title": "أرسل متطلبات الاستيراد", "name_label": "الاسم", "email_label": "البريد الإلكتروني", "product_label": "المنتج المطلوب", "port_label": "ميناء الوصول", "send": "إرسال الطلب", "success": "تم استلام الطلب. سيتواصل معك فريق التصدير.",
    },
    "fr": {
        "dir": "ltr", "name": "Français", "title": "Exportateur indien de produits agricoles",
        "description": "Riz basmati, épices, légumineuses et céréales indiennes avec spécifications, documents d'expédition et inspection indépendante en option.",
        "nav_products": "Produits", "nav_process": "Processus", "nav_docs": "Documents", "nav_contact": "Demander un devis",
        "eyebrow": "Maison d'exportation reconnue · ISO 9001:2015", "headline": "L'agriculture indienne", "headline_em": "exportée avec des preuves",
        "subhead": "Approvisionnement direct en riz, épices, légumineuses, céréales et oléagineux pour des acheteurs dans plus de 25 pays, avec spécifications de lot, inspection tierce en option et conditions d'expédition claires.",
        "browse": "Voir les produits", "quote": "Demander un devis", "proof": "Une qualité que l'acheteur peut vérifier",
        "proof_text": "Nous confirmons les spécifications avant commande et les documents de chaque expédition sur la facture pro forma. Une inspection SGS, Intertek ou Bureau Veritas peut être organisée selon les conditions convenues.",
        "products_title": "Principales familles de produits", "process_title": "De l'origine au conteneur", "docs_title": "Un dossier documentaire clair avant expédition",
        "products": ["Riz basmati et non basmati", "Curcuma, piment rouge et cumin", "Légumineuses et pois chiches", "Blé, maïs et farines", "Sésame et oléagineux", "Sucre et ingrédients pour aliments animaux"],
        "steps": [("01", "Cadrage du besoin", "Variété, grade, emballage, volume et port de destination sont confirmés."), ("02", "Échantillon et offre", "Échantillons qualifiés, frais de messagerie confirmés et pro forma détaillée."), ("03", "Contrôle et emballage", "Contrôle du lot, emballage alimentaire et inspection tierce sur demande."), ("04", "Expédition et suivi", "Documents d'exportation, numéro du conteneur et suivi des étapes d'acheminement.")],
        "docs": ["Facture commerciale et liste de colisage", "Connaissement et certificat d'origine", "Certificat phytosanitaire si applicable", "Certificat de fumigation ou d'analyse selon le produit", "Rapport d'inspection indépendant si convenu"],
        "note": "Les documents et certifications varient selon le produit et le pays importateur. Demandez les copies valides et tamponnées avant de conclure.",
        "form_title": "Envoyez votre besoin d'importation", "name_label": "Nom", "email_label": "E-mail professionnel", "product_label": "Produit recherché", "port_label": "Port de destination", "send": "Envoyer la demande", "success": "Demande reçue. Notre équipe export vous contactera.",
    },
    "es": {
        "dir": "ltr", "name": "Español", "title": "Exportador de productos agrícolas de India",
        "description": "Arroz basmati, especias, legumbres y cereales de India con especificaciones, documentación de embarque e inspección independiente opcional.",
        "nav_products": "Productos", "nav_process": "Proceso", "nav_docs": "Documentos", "nav_contact": "Solicitar cotización",
        "eyebrow": "Casa exportadora reconocida · ISO 9001:2015", "headline": "Agricultura de India", "headline_em": "exportada con respaldo",
        "subhead": "Suministro directo de arroz, especias, legumbres, cereales y oleaginosas para compradores de más de 25 países, con especificaciones por lote, inspección externa opcional y condiciones de embarque claras.",
        "browse": "Ver productos", "quote": "Solicitar cotización", "proof": "Calidad que el comprador puede comprobar",
        "proof_text": "Confirmamos las especificaciones antes del pedido y los documentos de cada envío en la factura proforma. Se puede coordinar inspección de SGS, Intertek o Bureau Veritas según las condiciones acordadas.",
        "products_title": "Principales categorías de suministro", "process_title": "Del origen al contenedor", "docs_title": "Documentación clara antes del embarque",
        "products": ["Arroz basmati y no basmati", "Cúrcuma, chile rojo y comino", "Legumbres y garbanzos", "Trigo, maíz y harinas", "Sésamo y oleaginosas", "Azúcar e ingredientes para alimento animal"],
        "steps": [("01", "Definición del requisito", "Confirmamos variedad, grado, empaque, volumen y puerto de destino."), ("02", "Muestra y oferta", "Muestras calificadas, costo de mensajería confirmado y proforma detallada."), ("03", "Control y empaque", "Control del lote, empaque apto para alimentos e inspección externa opcional."), ("04", "Embarque y seguimiento", "Documentos de exportación, número de contenedor y seguimiento del trayecto.")],
        "docs": ["Factura comercial y lista de empaque", "Conocimiento de embarque y certificado de origen", "Certificado fitosanitario cuando corresponda", "Certificado de fumigación o análisis según el producto", "Informe de inspección independiente si se acuerda"],
        "note": "Los documentos y certificados varían según el producto y el país importador. Solicite copias vigentes y selladas antes de contratar.",
        "form_title": "Envíe su requisito de importación", "name_label": "Nombre", "email_label": "Correo empresarial", "product_label": "Producto requerido", "port_label": "Puerto de destino", "send": "Enviar solicitud", "success": "Solicitud recibida. Nuestro equipo de exportación se pondrá en contacto.",
    },
    "ru": {
        "dir": "ltr", "name": "Русский", "title": "Экспортёр сельскохозяйственной продукции из Индии",
        "description": "Индийский рис басмати, специи, бобовые и зерновые со спецификациями, отгрузочными документами и возможностью независимой инспекции.",
        "nav_products": "Продукция", "nav_process": "Процесс", "nav_docs": "Документы", "nav_contact": "Запросить расчёт",
        "eyebrow": "Признанный экспортный дом · ISO 9001:2015", "headline": "Сельхозпродукция Индии", "headline_em": "с подтверждённым качеством",
        "subhead": "Прямые поставки риса, специй, бобовых, зерновых и масличных культур покупателям более чем в 25 странах: спецификации партии, независимая инспекция по запросу и прозрачные условия отгрузки.",
        "browse": "Каталог продукции", "quote": "Запросить расчёт", "proof": "Качество, которое может проверить покупатель",
        "proof_text": "До заказа мы согласовываем спецификацию, а в проформе фиксируем комплект документов. Инспекция SGS, Intertek или Bureau Veritas организуется по запросу на согласованных условиях.",
        "products_title": "Основные категории поставок", "process_title": "От источника до контейнера", "docs_title": "Понятный комплект документов до отгрузки",
        "products": ["Рис басмати и другие сорта", "Куркума, красный перец и кумин", "Бобовые и нут", "Пшеница, кукуруза и мука", "Кунжут и масличные культуры", "Сахар и компоненты кормов"],
        "steps": [("01", "Согласование требований", "Подтверждаем сорт, класс, упаковку, объём и порт назначения."), ("02", "Образец и предложение", "Образцы для квалифицированных покупателей, согласование курьера и подробная проформа."), ("03", "Контроль и упаковка", "Проверка партии, пищевая упаковка и независимая инспекция по запросу."), ("04", "Отгрузка и отслеживание", "Экспортные документы, номер контейнера и контроль этапов перевозки.")],
        "docs": ["Коммерческий инвойс и упаковочный лист", "Коносамент и сертификат происхождения", "Фитосанитарный сертификат, если требуется", "Сертификат фумигации или анализа по продукту", "Отчёт независимой инспекции по согласованию"],
        "note": "Документы и сертификаты зависят от продукта и страны импорта. До заключения сделки запросите актуальные заверенные копии.",
        "form_title": "Отправьте требования к поставке", "name_label": "Имя", "email_label": "Рабочий e-mail", "product_label": "Требуемый продукт", "port_label": "Порт назначения", "send": "Отправить запрос", "success": "Запрос получен. Экспортный отдел свяжется с вами.",
    },
}


def build(lang: str, t: dict[str, object]) -> str:
    products = "".join(f'<li><i class="fa-solid fa-circle-check"></i>{html.escape(item)}</li>' for item in t["products"])
    steps = "".join(f'<article><b>{n}</b><h3>{html.escape(title)}</h3><p>{html.escape(body)}</p></article>' for n, title, body in t["steps"])
    docs = "".join(f'<li>{html.escape(item)}</li>' for item in t["docs"])
    alternates = "\n".join([
        '  <link rel="alternate" hreflang="en" href="https://jftagro.com/">',
        *[f'  <link rel="alternate" hreflang="{code}" href="https://jftagro.com/{code}/">' for code in LANGUAGES],
        '  <link rel="alternate" hreflang="x-default" href="https://jftagro.com/">',
    ])
    return f'''<!DOCTYPE html>
<html lang="{lang}" dir="{t['dir']}">
<head>
  <meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1">
  <title>{html.escape(t['title'])} | JFT Agro Overseas</title>
  <meta name="description" content="{html.escape(t['description'], quote=True)}">
  <meta name="robots" content="index,follow,max-image-preview:large">
  <link rel="canonical" href="https://jftagro.com/{lang}/">
  <meta property="og:type" content="website"><meta property="og:title" content="{html.escape(t['title'], quote=True)} | JFT Agro Overseas">
  <meta property="og:description" content="{html.escape(t['description'], quote=True)}"><meta property="og:url" content="https://jftagro.com/{lang}/">
  <meta property="og:image" content="https://jftagro.com/images/homepage/export-trust-hero-v2.webp">
{alternates}
  <link rel="stylesheet" href="../jft-design-system.css"><link rel="stylesheet" href="../jft-responsive.css">
  <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
  <script src="/jft-conversion.js" defer></script>
  <style>
    :root{{--green:#3d7030;--navy:#102b25;--gold:#eebf45;--cream:#f8f7f2;--line:#dfe6e1}}*{{box-sizing:border-box}}body{{margin:0;color:#22352f;background:#fff;font-family:Arial,sans-serif;line-height:1.65}}a{{color:inherit;text-decoration:none}}.wrap{{width:min(1180px,calc(100% - 40px));margin:auto}}header{{height:78px;display:flex;align-items:center;background:#fff;border-bottom:1px solid var(--line)}}nav{{display:flex;align-items:center;justify-content:space-between;gap:24px}}.logo{{font-weight:900;color:var(--navy);font-size:1.2rem}}.logo span{{color:var(--green)}}.links{{display:flex;align-items:center;gap:24px;font-weight:700;font-size:.9rem}}.nav-cta,.primary{{background:var(--gold);color:var(--navy);padding:12px 20px;border-radius:5px;font-weight:800}}.hero{{min-height:690px;color:#fff;display:flex;align-items:center;background:linear-gradient(90deg,rgba(10,29,25,.94) 0%,rgba(10,29,25,.8) 38%,rgba(10,29,25,.18) 70%),url('../images/homepage/export-trust-hero-v2.webp') center/cover}}[dir=rtl] .hero{{background:linear-gradient(270deg,rgba(10,29,25,.94) 0%,rgba(10,29,25,.8) 38%,rgba(10,29,25,.18) 70%),url('../images/homepage/export-trust-hero-v2.webp') center/cover}}.hero-copy{{max-width:650px}}.eyebrow{{color:var(--gold);font-weight:800;text-transform:uppercase;font-size:.78rem}}h1{{font-family:Georgia,serif;font-size:clamp(2.6rem,6vw,5.2rem);line-height:1.05;margin:20px 0}}h1 em{{display:block;color:var(--gold);font-weight:400}}.hero p{{font-size:1.12rem;color:#e1e9e5;max-width:610px}}.actions{{display:flex;gap:12px;flex-wrap:wrap;margin-top:28px}}.secondary{{border:1px solid rgba(255,255,255,.7);padding:11px 19px;border-radius:5px;font-weight:800}}section{{padding:82px 0}}h2{{font-family:Georgia,serif;color:var(--navy);font-size:clamp(2rem,4vw,3.2rem);margin:0 0 22px}}.proof{{background:var(--navy);color:#fff;padding:34px 0}}.proof .wrap{{display:grid;grid-template-columns:1fr 2fr;gap:28px;align-items:center}}.proof h2{{color:var(--gold);font-size:1.55rem;margin:0}}.proof p{{margin:0;color:#dce7e2}}.products{{background:var(--cream)}}.product-list{{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;padding:0;list-style:none}}.product-list li{{background:#fff;border:1px solid var(--line);padding:21px;display:flex;gap:12px;font-weight:700}}.product-list i{{color:var(--green)}}.steps{{display:grid;grid-template-columns:repeat(4,1fr);gap:24px}}.steps article{{border-top:3px solid var(--gold);padding-top:20px}}.steps b{{color:var(--green);font-size:1.35rem}}.steps h3{{color:var(--navy)}}.docs{{background:#eef3ef}}.docs-grid{{display:grid;grid-template-columns:1.2fr .8fr;gap:50px}}.docs ul{{padding-inline-start:22px}}.note{{background:#fff;border-inline-start:4px solid var(--gold);padding:18px}}.lead{{background:var(--navy);color:#fff}}.lead h2{{color:#fff}}form{{display:grid;grid-template-columns:repeat(2,1fr);gap:14px;max-width:820px}}label{{font-weight:700;font-size:.85rem}}input{{display:block;width:100%;margin-top:6px;padding:14px;border:1px solid #adc0b7;border-radius:4px;font:inherit}}button{{border:0;cursor:pointer;font:inherit}}.form-status{{grid-column:1/-1;min-height:24px;color:var(--gold)}}footer{{padding:30px 0;background:#091e19;color:#cbd9d3}}@media(max-width:760px){{.links a:not(.nav-cta){{display:none}}.hero{{min-height:640px;background-position:62% center}}[dir=rtl] .hero{{background-position:62% center}}.product-list,.steps,.docs-grid,form,.proof .wrap{{grid-template-columns:1fr}}section{{padding:58px 0}}}}
  </style>
</head>
<body>
<header><nav class="wrap"><a class="logo" href="../index.html">JFT <span>AGRO</span></a><div class="links"><a href="#products">{t['nav_products']}</a><a href="#process">{t['nav_process']}</a><a href="#documents">{t['nav_docs']}</a><a class="nav-cta" href="#contact">{t['nav_contact']}</a></div></nav></header>
<main>
  <section class="hero"><div class="wrap"><div class="hero-copy"><div class="eyebrow">{t['eyebrow']}</div><h1>{t['headline']}<em>{t['headline_em']}</em></h1><p>{t['subhead']}</p><div class="actions"><a class="primary" href="../products.html">{t['browse']}</a><a class="secondary" href="#contact">{t['quote']}</a></div></div></div></section>
  <aside class="proof"><div class="wrap"><h2>{t['proof']}</h2><p>{t['proof_text']}</p></div></aside>
  <section class="products" id="products"><div class="wrap"><h2>{t['products_title']}</h2><ul class="product-list">{products}</ul></div></section>
  <section id="process"><div class="wrap"><h2>{t['process_title']}</h2><div class="steps">{steps}</div></div></section>
  <section class="docs" id="documents"><div class="wrap docs-grid"><div><h2>{t['docs_title']}</h2><ul>{docs}</ul></div><p class="note">{t['note']}</p></div></section>
  <section class="lead" id="contact"><div class="wrap"><h2>{t['form_title']}</h2><form id="localizedLead"><label>{t['name_label']}<input name="full_name" autocomplete="name" required></label><label>{t['email_label']}<input name="email" type="email" autocomplete="email" required></label><label>{t['product_label']}<input name="product" required></label><label>{t['port_label']}<input name="port" required></label><button class="primary" type="submit">{t['send']}</button><div class="form-status" role="status" aria-live="polite"></div></form></div></section>
</main>
<footer><div class="wrap">JFT Agro Overseas · Navi Mumbai, India · <a href="mailto:jftagro.info@gmail.com">jftagro.info@gmail.com</a> · <a href="tel:+918425057274">+91 84250 57274</a> · <a href="tel:+918652362771">+91 86523 62771</a></div></footer>
<script>document.getElementById('localizedLead').addEventListener('submit',async function(e){{e.preventDefault();const b=this.querySelector('button');const s=this.querySelector('.form-status');b.disabled=true;try{{const data=Object.fromEntries(new FormData(this));data.lead_type='localized_quote';data.language='{lang}';data.subject='New {lang.upper()} Export Inquiry';await JFTConversion.submitLead(data);s.textContent={t['success']!r};this.reset();}}catch(_){{s.textContent='jftagro.info@gmail.com · WhatsApp +91 84250 57274';}}finally{{b.disabled=false;}}}});</script>
</body></html>
'''


def main() -> None:
    for language, translations in LANGUAGES.items():
        path = ROOT / language / "index.html"
        path.write_text(build(language, translations), encoding="utf-8")
        print(f"Built {path.relative_to(ROOT).as_posix()}")


if __name__ == "__main__":
    main()
