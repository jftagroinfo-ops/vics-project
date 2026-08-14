#!/usr/bin/env python3
"""Remove unsupported commercial claims and make root product FAQs data-led.

This script is intentionally deterministic. It uses data/products.json as the
commercial source of truth and limits broad edits to known product-page paths.
"""

from __future__ import annotations

import html
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PRODUCTS = json.loads((ROOT / "data/products.json").read_text(encoding="utf-8"))
LOCALES = ("ar", "es", "fr", "id", "ms", "pt", "ru", "si", "th", "vi")

COPY = {
    "en": {
        "carrier_h": "Booking-specific carrier planning",
        "carrier_p": "Carrier, routing and sailing options are confirmed for each booking. Equipment, space and sailing dates remain subject to carrier availability and the written contract.",
        "history_h": "Documented company history",
        "history_p": "JFT Agro Overseas LLP was registered in 2016. Any predecessor-business history is supplied for buyer verification before it is relied upon.",
        "capacity": "Processing scope and facility capacity are documented during buyer due diligence and confirmed for the contracted product.",
        "markets": "International market support",
    },
    "ar": {"carrier_h":"تخطيط الناقل حسب الحجز","carrier_p":"يتم تأكيد الناقل والمسار وخيارات الإبحار لكل حجز. وتظل المعدات والمساحة ومواعيد الإبحار خاضعة لتوافر الناقل والعقد المكتوب.","history_h":"تاريخ الشركة الموثق","history_p":"تم تسجيل JFT Agro Overseas LLP في عام 2016. وتُقدَّم أي معلومات عن نشاط سابق للتحقق منها قبل الاعتماد عليها.","capacity":"يتم توثيق نطاق المعالجة وطاقة المنشأة أثناء العناية الواجبة وتأكيدهما للمنتج المتعاقد عليه.","markets":"دعم الأسواق الدولية"},
    "es": {"carrier_h":"Planificación de transportista por reserva","carrier_p":"El transportista, la ruta y las opciones de salida se confirman para cada reserva. El equipo, el espacio y las fechas están sujetos a disponibilidad y al contrato escrito.","history_h":"Historia empresarial documentada","history_p":"JFT Agro Overseas LLP se registró en 2016. Cualquier historia de una empresa predecesora se facilita para verificación antes de utilizarla.","capacity":"El alcance de procesamiento y la capacidad de la instalación se documentan durante la diligencia debida y se confirman para el producto contratado.","markets":"Soporte para mercados internacionales"},
    "fr": {"carrier_h":"Planification du transporteur par réservation","carrier_p":"Le transporteur, l'itinéraire et les options de départ sont confirmés pour chaque réservation. L'équipement, l'espace et les dates restent soumis à disponibilité et au contrat écrit.","history_h":"Historique documenté de l'entreprise","history_p":"JFT Agro Overseas LLP a été immatriculée en 2016. Tout historique d'une entreprise antérieure est fourni pour vérification avant utilisation.","capacity":"Le périmètre de transformation et la capacité du site sont documentés lors de la vérification acheteur et confirmés pour le produit contractuel.","markets":"Accompagnement des marchés internationaux"},
    "id": {"carrier_h":"Perencanaan pengangkut per pemesanan","carrier_p":"Pengangkut, rute, dan opsi pelayaran dikonfirmasi untuk setiap pemesanan. Peralatan, ruang, dan tanggal pelayaran tunduk pada ketersediaan dan kontrak tertulis.","history_h":"Riwayat perusahaan terdokumentasi","history_p":"JFT Agro Overseas LLP terdaftar pada 2016. Riwayat usaha pendahulu diberikan untuk verifikasi sebelum digunakan.","capacity":"Ruang lingkup pemrosesan dan kapasitas fasilitas didokumentasikan selama uji tuntas pembeli dan dikonfirmasi untuk produk yang dikontrak.","markets":"Dukungan pasar internasional"},
    "ms": {"carrier_h":"Perancangan pengangkut mengikut tempahan","carrier_p":"Pengangkut, laluan dan pilihan pelayaran disahkan bagi setiap tempahan. Peralatan, ruang dan tarikh pelayaran tertakluk pada ketersediaan dan kontrak bertulis.","history_h":"Sejarah syarikat yang didokumenkan","history_p":"JFT Agro Overseas LLP didaftarkan pada 2016. Sejarah perniagaan terdahulu diberikan untuk pengesahan sebelum digunakan.","capacity":"Skop pemprosesan dan kapasiti kemudahan didokumenkan semasa usaha wajar pembeli dan disahkan untuk produk kontrak.","markets":"Sokongan pasaran antarabangsa"},
    "pt": {"carrier_h":"Planejamento de transportadora por reserva","carrier_p":"A transportadora, a rota e as opções de embarque são confirmadas para cada reserva. Equipamento, espaço e datas estão sujeitos à disponibilidade e ao contrato escrito.","history_h":"Histórico empresarial documentado","history_p":"A JFT Agro Overseas LLP foi registrada em 2016. Qualquer histórico de empresa antecessora é fornecido para verificação antes do uso.","capacity":"O escopo de processamento e a capacidade da instalação são documentados na diligência do comprador e confirmados para o produto contratado.","markets":"Suporte a mercados internacionais"},
    "ru": {"carrier_h":"Планирование перевозчика для бронирования","carrier_p":"Перевозчик, маршрут и варианты рейса подтверждаются для каждого бронирования. Оборудование, место и даты зависят от наличия и письменного договора.","history_h":"Документированная история компании","history_p":"JFT Agro Overseas LLP зарегистрирована в 2016 году. Сведения о предшествующем бизнесе предоставляются для проверки до их использования.","capacity":"Объём переработки и мощность объекта документируются при проверке покупателем и подтверждаются для контрактного товара.","markets":"Поддержка международных рынков"},
    "si": {"carrier_h":"වෙන්කිරීම අනුව ප්‍රවාහක සැලසුම","carrier_p":"සෑම වෙන්කිරීමකටම ප්‍රවාහකයා, මාර්ගය සහ යාත්‍රා විකල්ප තහවුරු කරයි. උපකරණ, ඉඩ සහ දින ලබාගත හැකි බව හා ලිඛිත ගිවිසුමට යටත් වේ.","history_h":"ලේඛනගත සමාගම් ඉතිහාසය","history_p":"JFT Agro Overseas LLP 2016 දී ලියාපදිංචි කරන ලදී. පෙර ව්‍යාපාර ඉතිහාසයක් භාවිතයට පෙර පරීක්ෂාව සඳහා සපයනු ලැබේ.","capacity":"සැකසුම් විෂය පථය සහ පහසුකම් ධාරිතාව ගැනුම්කරුගේ පරීක්ෂාවේදී ලේඛනගත කර ගිවිසුම්ගත නිෂ්පාදනය සඳහා තහවුරු කරයි.","markets":"ජාත්‍යන්තර වෙළඳපොළ සහාය"},
    "th": {"carrier_h":"การวางแผนผู้ขนส่งตามการจอง","carrier_p":"ผู้ขนส่ง เส้นทาง และเที่ยวเรือจะยืนยันเป็นรายงานจอง อุปกรณ์ พื้นที่ และวันเดินเรือขึ้นอยู่กับความพร้อมและสัญญาเป็นลายลักษณ์อักษร","history_h":"ประวัติบริษัทที่มีเอกสาร","history_p":"JFT Agro Overseas LLP จดทะเบียนในปี 2016 ประวัติธุรกิจก่อนหน้าจะจัดให้ตรวจสอบก่อนนำไปอ้างอิง","capacity":"ขอบเขตการแปรรูปและกำลังการผลิตของสถานที่จะมีเอกสารระหว่างการตรวจสอบผู้ซื้อและยืนยันสำหรับสินค้าตามสัญญา","markets":"การสนับสนุนตลาดต่างประเทศ"},
    "vi": {"carrier_h":"Lập kế hoạch hãng vận chuyển theo đặt chỗ","carrier_p":"Hãng vận chuyển, tuyến và lựa chọn chuyến tàu được xác nhận cho từng đặt chỗ. Thiết bị, chỗ và ngày tàu chạy phụ thuộc vào tình trạng sẵn có và hợp đồng bằng văn bản.","history_h":"Lịch sử công ty có tài liệu","history_p":"JFT Agro Overseas LLP được đăng ký năm 2016. Mọi lịch sử doanh nghiệp tiền nhiệm được cung cấp để xác minh trước khi sử dụng.","capacity":"Phạm vi chế biến và công suất cơ sở được lập hồ sơ trong quá trình thẩm định của người mua và xác nhận cho sản phẩm theo hợp đồng.","markets":"Hỗ trợ thị trường quốc tế"},
}


def faq_item(question: str, answer: str) -> str:
    return f'''      <div class="faq-item" style="border-bottom:1px solid rgba(26,60,52,.08)">
        <div class="faq-q" role="button" tabindex="0" aria-expanded="false" onclick="var answer=this.nextElementSibling;var open=answer.classList.toggle('open');this.setAttribute('aria-expanded',String(open));this.querySelector('.faq-chevron').classList.toggle('rotated',open)" onkeydown="if(event.key==='Enter'||event.key===' '){{event.preventDefault();this.click();}}" style="display:flex;justify-content:space-between;align-items:center;padding:20px 0;cursor:pointer;font-family:'Montserrat',sans-serif;font-weight:700;font-size:.95rem;color:#1a3c34">
          {question}<i class="fa-solid fa-chevron-down faq-chevron" style="color:#3d7030;font-size:.75rem;transition:transform .3s;flex-shrink:0"></i>
        </div><div class="faq-a" style="max-height:0;overflow:hidden;transition:max-height .4s ease;font-size:.93rem;color:#666;line-height:1.8"><div style="padding:0 0 20px">{answer}</div></div>
      </div>'''


def product_faq(product: dict) -> str:
    name = html.escape(product["t"])
    trade = product["trade"]
    specs = [pair for pair in product["s"] if pair[0] not in {"HS Code", "MOQ"}][:5]
    spec_text = "; ".join(f"<strong>{html.escape(k)}</strong>: {html.escape(v)}" for k, v in specs)
    documents = ", ".join(html.escape(x) for x in product["compliance"]["documents"])
    conditional = ", ".join(html.escape(x) for x in product["compliance"]["conditional_documents"])
    items = [
        (f"What specification is published for {name}?", f"The current reference specification lists {spec_text}. These are planning values; the signed specification, approved sample and agreed tolerances control the order."),
        (f"What are the HS code, MOQ and packing options for {name}?", f"Reference HS code: <strong>{html.escape(trade['hs_code'])}</strong>. MOQ: <strong>{html.escape(trade['moq'])}</strong>. Published packing: <strong>{html.escape(trade['packaging'])}</strong>. Classification, packing and legal weight limits must be confirmed for the destination and contract."),
        (f"How much {name} fits in a container?", f"The planning reference for a 20-foot container is <strong>{html.escape(trade['container_20ft'])}</strong>. Final payload depends on bag construction, palletisation, carrier limits, route and applicable law; the written loading plan controls."),
        (f"Which documents can be requested for {name}?", f"The base document set is {documents}. {conditional} are arranged only when applicable and written into the quotation or contract."),
        (f"Can I request a trade sample of {name}?", "Qualified trade buyers may request a standard 250–500g evaluation sample per selected product. Availability, final size, courier cost and dispatch timing are confirmed before shipment; larger samples require separate written approval."),
    ]
    body = "\n\n".join(faq_item(q, a) for q, a in items)
    return f'''<!-- PRODUCT FAQ SECTION -->
<section class="prod-faq-section" data-product-specific-faq="true" style="background:#fff;padding:60px 0;border-top:1px solid rgba(26,60,52,.07)">
  <div class="jft-wide-container"><div class="reveal" style="max-width:800px;margin:0 auto">
    <span class="brand-tag" style="margin-bottom:20px"><i class="fa-solid fa-circle-question"></i> Product-specific FAQ</span>
    <h2 style="font-size:clamp(1.6rem,3vw,2.2rem);font-weight:900;color:#1a3c34;margin-bottom:36px">{name}: <em style="color:#3d7030;font-style:italic">commercial questions</em></h2>
{body}
  </div></div>
</section>'''


def localize_product_page(path: Path, locale: str) -> bool:
    text = path.read_text(encoding="utf-8")
    original = text
    c = COPY[locale]

    # Product schema must not claim the seller manufactured the product.
    text = re.sub(r',?\s*"manufacturer"\s*:\s*\{\s*"@type"\s*:\s*"Organization"\s*,\s*"name"\s*:\s*"JFT Agro Overseas"\s*\}', "", text)
    # Contract-specific carrier planning replaces named-carrier guarantees.
    text = re.sub(r'<h3>[^<]*</h3>\s*<p>[^<]*(?:Maersk)[^<]*(?:MSC)[^<]*(?:CMA)[^<]*</p>', f'<h3>{c["carrier_h"]}</h3>\n        <p>{c["carrier_p"]}</p>', text, flags=re.I)
    # Entity history: the LLP date is the only date currently supported in repository governance.
    text = re.sub(r'<h3>[^<]*</h3>\s*<p>[^<]*1980[^<]*</p>', f'<h3>{c["history_h"]}</h3>\n        <p>{c["history_p"]}</p>', text, flags=re.I)
    text = re.sub(r'<span([^>]*)>[^<]*250\s*(?:MT|TM|طن|ตัน)[^<]*</span>', lambda m: f'<span{m.group(1)}>{c["capacity"]}</span>', text, flags=re.I)
    text = re.sub(r'(<span class="cta-trust-item"><i class="fa-solid fa-globe"></i>)\s*[^<]*25\+[^<]*(</span>)', rf'\1 {c["markets"]}\2', text, flags=re.I)
    # Fixed turnaround and free-sample language are not contractual promises.
    text = text.replace("Processing typically within one business day.", "Availability, courier cost and timing are confirmed before dispatch.")
    text = re.sub(r'<div style="padding:0 0 20px">.{0,1200}?250.{0,600}?500.{0,1200}?</div>', '<div style="padding:0 0 20px">Qualified trade buyers may request a standard <strong>250–500g evaluation sample</strong> per selected product. Final size, availability, courier cost and dispatch timing are confirmed before shipment. Larger samples require separate written approval.</div>', text, flags=re.I | re.S)
    # Root template wording; translated templates still receive the structural claim fixes above.
    text = re.sub(r'We are not brokers or traders\s*[—â€“-]+\s*JFT Agro is the <strong>manufacturer and primary exporter</strong>\. Direct factory pricing, zero middlemen, and total quality accountability from field to port\.', 'JFT Agro coordinates sourcing, processing, testing, packing and export documentation against the approved specification. Facility identity, processing scope and applicable evidence are available during buyer due diligence.', text, flags=re.I)
    text = re.sub(r'Get factory-direct pricing for', 'Request a contract-based quote for', text, flags=re.I)
    text = re.sub(r'Tell us your quantity, destination port, and packaging requirement\. We typically respond within one business day\.', 'Tell us your quantity, destination port and packaging requirement. Complete enquiries are reviewed during published business hours; quotation timing depends on product and freight confirmation.', text, flags=re.I)

    if text != original:
        path.write_text(text, encoding="utf-8", newline="")
        return True
    return False


def main() -> None:
    changed = 0
    about_only = "--about-only" in sys.argv
    if not about_only:
        for product in PRODUCTS:
            for locale in ("en",) + LOCALES:
                path = ROOT / product["u"] if locale == "en" else ROOT / locale / product["u"]
                if path.exists() and localize_product_page(path, locale):
                    changed += 1
            root_path = ROOT / product["u"]
            text = root_path.read_text(encoding="utf-8")
            replacement = product_faq(product)
            updated, count = re.subn(r'<!--[^>]*PRODUCT FAQ SECTION[^>]*-->.*?<section class="prod-faq-section".*?</section>', replacement, text, count=1, flags=re.I | re.S)
            if count and updated != text:
                root_path.write_text(updated, encoding="utf-8", newline="")
                changed += 1

    # Remove dangerous illustrative identifiers and payment coordinates everywhere,
    # then normalize legacy history/volume badges outside product templates.
    paths = [ROOT / "about.html", *(ROOT / locale / "about.html" for locale in LOCALES)] if about_only else ROOT.rglob("*.html")
    for path in paths:
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8")
        protected_sections: list[str] = []

        def protect_owner_directed(match: re.Match[str]) -> str:
            protected_sections.append(match.group(0))
            return f"<!-- OWNER_DIRECTED_SECTION_{len(protected_sections) - 1} -->"

        updated = re.sub(
            r'<section\b[^>]*data-claim-status="owner-directed"[^>]*>.*?</section>',
            protect_owner_directed,
            text,
            flags=re.I | re.S,
        )
        updated = updated.replace("AABFJ1234C", "[ILLUSTRATIVE IEC]")
        updated = updated.replace("MH/2025/00XXX", "[ILLUSTRATIVE RCMC]")
        updated = updated.replace("27[ILLUSTRATIVE IEC]1ZX", "[ILLUSTRATIVE GSTIN]")
        updated = updated.replace("YESBINBB", "[ILLUSTRATIVE SWIFT/BIC]")
        updated = re.sub(r'(<span>Bank(?: Name)?\s*:\s*</span><strong>)[^<]+(</strong>)', r'\1[ILLUSTRATIVE BANK]\2', updated, flags=re.I)
        locale = path.parts[len(ROOT.parts)] if len(path.parts) > len(ROOT.parts) + 1 and path.parts[len(ROOT.parts)] in LOCALES else "en"
        c = COPY[locale]
        updated = re.sub(r'<p([^>]*)>[^<]*1980[^<]*</p>', lambda m: f'<p{m.group(1)}>{c["history_p"]}</p>', updated, flags=re.I)
        updated = re.sub(r'<div class="author-bio">[^<]*1980[^<]*</div>', f'<div class="author-bio">{c["history_p"]}</div>', updated, flags=re.I)
        updated = re.sub(r'(<meta[^>]*content=")[^"]*1980[^"]*(")', rf'\1{c["history_p"]}\2', updated, flags=re.I)
        updated = re.sub(r'<title>[^<]*1980[^<]*</title>', '<title>About JFT Agro Overseas | Company &amp; Buyer Verification</title>', updated, flags=re.I)
        market_word = {"en":"multiple", "ar":"متعددة", "es":"varios", "fr":"plusieurs", "id":"berbagai", "ms":"pelbagai", "pt":"vários", "ru":"несколько", "si":"බහු", "th":"หลาย", "vi":"nhiều"}[locale]
        updated = updated.replace("25+", market_word)
        updated = re.sub(r'<h3>[^<]*1980[^<]*</h3>', f'<h3>{c["history_h"]}</h3>', updated, flags=re.I)
        updated = updated.replace('"foundingDate":"1980",', '')
        updated = re.sub(r'<p([^>]*)>[^<]*Maersk[^<]*MSC[^<]*CMA[^<]*</p>', lambda m: f'<p{m.group(1)}>{c["carrier_p"]}</p>', updated, flags=re.I)
        updated = re.sub(r'Factory[- ]direct', 'Contract-based', updated, flags=re.I)
        updated = re.sub(r'Free samples?', 'Trade samples on request', updated, flags=re.I)
        updated = re.sub(r'(?:We |Our team )?typically respond(?:s)? within one business day', 'Complete enquiries are reviewed during published business hours', updated, flags=re.I)
        updated = re.sub(r'(?:Response |Processing )?typically within one business day', 'Timing is confirmed after commercial review', updated, flags=re.I)
        updated = re.sub(r'(?:Average first-response time is )?under 4 business hours', 'Response timing depends on enquiry completeness and published business hours', updated, flags=re.I)
        updated = re.sub(r'(?:in|under|within) 24 hours', 'after commercial review', updated, flags=re.I)
        updated = re.sub(r'within 4 business hours', 'after commercial review', updated, flags=re.I)
        # Any remaining 1980 reference is a company-history badge or structured
        # field. Use the supported LLP registration year, not a predecessor claim.
        updated = updated.replace("1980", "2016")
        # Remove residual capacity/volume badges from translated landing pages.
        updated = re.sub(r'(<(?:p|span|div)[^>]*>)(?:(?!</(?:p|span|div)>).)*250\s*(?:MT|TM|طن(?:ًا)?\s*متري(?:ًا)?|ตัน)(?:(?!</(?:p|span|div)>).)*(</(?:p|span|div)>)', lambda m: f'{m.group(1)}{c["capacity"]}{m.group(2)}', updated, flags=re.I | re.S)
        updated = re.sub(r'(<div class="vc-stat">)500\+.*?(</div>)', rf'\1{c["markets"]}\2', updated, flags=re.I)
        if path.name == "about.html":
            updated = re.sub(r'<div class="stats-strip">.*?(?=<section class="story-section)', '', updated, count=1, flags=re.S)
            updated = re.sub(r'<div class="global-stats reveal">.*?(?=<div class="countries-box)', '', updated, count=1, flags=re.S)
            updated = re.sub(r'<section class="growth-section sp" id="milestones">.*?</section>', '', updated, count=1, flags=re.S)
            story_paragraphs = list(re.finditer(r'<p class="story-p">.*?</p>', updated, flags=re.S))
            if len(story_paragraphs) > 1:
                item = story_paragraphs[1]
                replacement = f'<p class="story-p">{c["capacity"]} The publicly listed processing unit is at Balap, Raigad; identity and applicable supporting records are available during buyer due diligence.</p>'
                updated = updated[:item.start()] + replacement + updated[item.end():]
            updated = re.sub(r'<div class="story-quote">.*?</div>', '<div class="story-quote">“Verify the entity, specification, sample, inspection scope and payment instructions before committing to a shipment.”</div>', updated, count=1, flags=re.S)
            updated = re.sub(r'<div class="sb-item"><i class="fa-solid fa-industry"></i>.*?</div>', '', updated, flags=re.S)
            updated = re.sub(r'<div class="usp-row"><div class="usp-ico"><i class="fa-solid fa-industry"></i></div><div><h4>.*?</h4><p>.*?</p></div></div>', '', updated, count=1, flags=re.S)
            updated = re.sub(r'<div class="ab-badge-glass">.*?</div>', '<div class="ab-badge-glass"><span class="bgnum">Docs</span><span class="bglbl">Verify Current Evidence</span></div>', updated, count=1, flags=re.S)
        for index, section in enumerate(protected_sections):
            updated = updated.replace(f"<!-- OWNER_DIRECTED_SECTION_{index} -->", section)
        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="")
            changed += 1
    print(f"Updated {changed} HTML documents")


if __name__ == "__main__":
    main()
