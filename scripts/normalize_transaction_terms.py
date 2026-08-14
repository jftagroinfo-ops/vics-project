#!/usr/bin/env python3
"""Normalize samples, payment wording and illustrative document templates."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SAFE_PAYMENT = "Payment terms are stated only in the signed Proforma Invoice or Sales Contract after buyer, banking and transaction review. Website examples are illustrative and are not payment instructions."
PAYMENT_I18N = {
    "ar":"تُحدد شروط الدفع فقط في الفاتورة الأولية أو عقد البيع الموقع بعد مراجعة المشتري والبنك والمعاملة. أمثلة الموقع توضيحية وليست تعليمات دفع.",
    "es":"Las condiciones de pago se indican únicamente en la factura proforma o el contrato de venta firmado tras la revisión del comprador, el banco y la operación. Los ejemplos del sitio son ilustrativos y no son instrucciones de pago.",
    "fr":"Les conditions de paiement figurent uniquement dans la facture pro forma ou le contrat de vente signé après examen de l'acheteur, de la banque et de l'opération. Les exemples du site sont illustratifs et ne constituent pas des instructions de paiement.",
    "id":"Ketentuan pembayaran hanya tercantum dalam Faktur Proforma atau Kontrak Penjualan yang ditandatangani setelah peninjauan pembeli, bank, dan transaksi. Contoh situs hanya ilustrasi dan bukan instruksi pembayaran.",
    "ms":"Syarat pembayaran hanya dinyatakan dalam Invois Proforma atau Kontrak Jualan yang ditandatangani selepas semakan pembeli, bank dan transaksi. Contoh laman hanyalah ilustrasi dan bukan arahan pembayaran.",
    "pt":"As condições de pagamento constam apenas da Fatura Proforma ou do Contrato de Venda assinado após análise do comprador, do banco e da operação. Os exemplos do site são ilustrativos e não constituem instruções de pagamento.",
    "ru":"Условия оплаты указываются только в подписанном счёте-проформе или договоре после проверки покупателя, банка и сделки. Примеры на сайте являются иллюстративными и не служат платёжными инструкциями.",
    "si":"ගැනුම්කරු, බැංකුව සහ ගනුදෙනුව සමාලෝචනයෙන් පසු අත්සන් කළ Proforma Invoice හෝ විකුණුම් ගිවිසුමේ පමණක් ගෙවීම් කොන්දේසි දක්වයි. වෙබ් අඩවි උදාහරණ නිදර්ශන පමණක් වන අතර ගෙවීම් උපදෙස් නොවේ.",
    "th":"เงื่อนไขการชำระเงินระบุเฉพาะในใบแจ้งหนี้ล่วงหน้าหรือสัญญาซื้อขายที่ลงนามหลังการตรวจสอบผู้ซื้อ ธนาคาร และธุรกรรม ตัวอย่างบนเว็บไซต์เป็นเพียงภาพประกอบและไม่ใช่คำสั่งชำระเงิน",
    "vi":"Điều khoản thanh toán chỉ được nêu trong Hóa đơn chiếu lệ hoặc Hợp đồng mua bán đã ký sau khi xem xét người mua, ngân hàng và giao dịch. Ví dụ trên trang chỉ mang tính minh họa, không phải chỉ dẫn thanh toán."
}
NOTICE_I18N = {
    "ar":"إشعار نموذج توضيحي: جميع المعرّفات والعناوين والبيانات المصرفية والمبالغ والنسب ومراجع الشحن أدناه وهمية أو عناصر نائبة. لا تستخدمها للشحن أو الدفع. استبدل كل حقل وتحقق من تعليمات الدفع عبر جهة اتصال معروفة للشركة.",
    "es":"AVISO DE PLANTILLA ILUSTRATIVA: todos los identificadores, direcciones, datos bancarios, importes, porcentajes y referencias de envío siguientes son ficticios o marcadores. No los utilice para envíos ni pagos. Sustituya cada campo y verifique las instrucciones de pago con un contacto conocido de la empresa.",
    "fr":"AVIS DE MODÈLE ILLUSTRATIF : tous les identifiants, adresses, coordonnées bancaires, montants, pourcentages et références d'expédition ci-dessous sont fictifs ou provisoires. Ne les utilisez pas pour un envoi ou un paiement. Remplacez chaque champ et vérifiez les instructions de paiement auprès d'un contact connu de l'entreprise.",
    "id":"PEMBERITAHUAN TEMPLATE ILUSTRATIF: semua identitas, alamat, data bank, jumlah, persentase, dan referensi pengiriman di bawah ini fiktif atau placeholder. Jangan gunakan untuk pengiriman atau pembayaran. Ganti setiap kolom dan verifikasi instruksi pembayaran melalui kontak perusahaan yang dikenal.",
    "ms":"NOTIS TEMPLAT ILUSTRASI: semua pengenalan, alamat, butiran bank, amaun, peratusan dan rujukan penghantaran di bawah adalah rekaan atau ruang letak. Jangan gunakannya untuk penghantaran atau pembayaran. Gantikan setiap medan dan sahkan arahan pembayaran melalui hubungan syarikat yang diketahui.",
    "pt":"AVISO DE MODELO ILUSTRATIVO: todos os identificadores, endereços, dados bancários, valores, percentuais e referências de embarque abaixo são fictícios ou marcadores. Não os use para remessas ou pagamentos. Substitua cada campo e verifique as instruções de pagamento com um contato conhecido da empresa.",
    "ru":"УВЕДОМЛЕНИЕ ОБ ИЛЛЮСТРАТИВНОМ ШАБЛОНЕ: все идентификаторы, адреса, банковские реквизиты, суммы, проценты и ссылки на отправку ниже вымышлены или являются заполнителями. Не используйте их для отправки или оплаты. Замените каждое поле и проверьте платёжные инструкции через известный контакт компании.",
    "si":"නිදර්ශන ආකෘති දැනුම්දීම: පහත සියලු හඳුනාගැනීම්, ලිපින, බැංකු විස්තර, මුදල්, ප්‍රතිශත සහ නැව් යොමු කල්පිත හෝ ස්ථාන සලකුණු වේ. නැව්ගත කිරීම හෝ ගෙවීම සඳහා භාවිත නොකරන්න. සෑම ක්ෂේත්‍රයක්ම ප්‍රතිස්ථාපනය කර දන්නා සමාගම් සම්බන්ධතාවයකින් ගෙවීම් උපදෙස් තහවුරු කරන්න.",
    "th":"ประกาศแม่แบบตัวอย่าง: ตัวระบุ ที่อยู่ รายละเอียดธนาคาร จำนวนเงิน เปอร์เซ็นต์ และข้อมูลการจัดส่งทั้งหมดด้านล่างเป็นข้อมูลสมมติหรือตัวยึดตำแหน่ง ห้ามใช้เพื่อการจัดส่งหรือชำระเงิน ให้แทนที่ทุกช่องและยืนยันคำสั่งชำระเงินกับผู้ติดต่อบริษัทที่รู้จัก",
    "vi":"THÔNG BÁO MẪU MINH HỌA: mọi mã định danh, địa chỉ, thông tin ngân hàng, số tiền, tỷ lệ và tham chiếu lô hàng dưới đây đều là hư cấu hoặc chỗ giữ chỗ. Không sử dụng để giao hàng hoặc thanh toán. Hãy thay thế mọi trường và xác minh chỉ dẫn thanh toán qua đầu mối công ty đã biết."
}
SAFE_HOME_FAQ = '''<script type="application/ld+json">{"@context":"https://schema.org","@type":"FAQPage","mainEntity":[{"@type":"Question","name":"How is the minimum order quantity confirmed?","acceptedAnswer":{"@type":"Answer","text":"MOQ and container payload are product-specific planning values. The written quotation confirms packing, payload, route and legal weight limits."}},{"@type":"Question","name":"How are payment terms agreed?","acceptedAnswer":{"@type":"Answer","text":"Payment terms are stated only in the signed Proforma Invoice or sales contract after buyer, banking and transaction review. Website examples are not binding instructions."}},{"@type":"Question","name":"Can a trade buyer request samples?","acceptedAnswer":{"@type":"Answer","text":"Qualified trade buyers may request a standard 250–500g evaluation sample per selected product. Final size, availability, courier cost and dispatch timing are confirmed before shipment."}},{"@type":"Question","name":"When is a Proforma Invoice issued?","acceptedAnswer":{"@type":"Answer","text":"Complete enquiries are reviewed during published business hours. Quotation timing depends on product specification, availability, packing, destination and freight confirmation."}}]}</script>'''


def replace_outer_line(line: str) -> str:
    if not re.search(r'30(?:\s|&nbsp;)*%', line) or not re.search(r'70(?:\s|&nbsp;)*%', line):
        return line
    newline = "\n" if line.endswith("\n") else ""
    core = line[:-1] if newline else line
    match = re.match(r'^(\s*<(?P<tag>p|li|td|div)\b[^>]*>).*?(</(?P=tag)>\s*)$', core, flags=re.I)
    if match:
        return f"{match.group(1)}{SAFE_PAYMENT}{match.group(3)}{newline}"
    if "<strong>JFT Agro" in core or "standard terms" in core.lower():
        indent = re.match(r'^\s*', core).group(0)
        return f"{indent}<strong>Payment terms:</strong> {SAFE_PAYMENT}{newline}"
    return re.sub(r'30(?:\s|&nbsp;)*%', '[ILLUSTRATIVE ADVANCE %]', re.sub(r'70(?:\s|&nbsp;)*%', '[ILLUSTRATIVE BALANCE %]', line))


def main() -> None:
    changed = 0
    for path in ROOT.rglob("*.html"):
        text = path.read_text(encoding="utf-8")
        # Repair placeholders from early versions of this migration. Percentage
        # values inside CSS are presentation values, not payment terms.
        updated = text.replace("[ILLUSTRATIVE ADVANCE %]", "30%").replace("[ILLUSTRATIVE BALANCE %]", "70%")
        if path.name == "index.html":
            updated = re.sub(r'<script type="application/ld\+json">\s*\{[^<]*"@type":"FAQPage"[^<]*"What is the minimum order quantity for JFT Agro Overseas\?"[^<]*\}\s*</script>', SAFE_HOME_FAQ, updated, count=1, flags=re.S)
        updated = updated.replace("30% Advance + 70% against Scan BL. Established clients may use Irrevocable LC at sight.", SAFE_PAYMENT)
        updated = updated.replace("Standard terms are 30% advance + 70% against Scan Bill of Lading. Established buyers may use 100% Irrevocable LC at sight from top-tier banks.", SAFE_PAYMENT)
        updated = re.sub(r'<div class="faq-a"><p>We work on .*?</p></div>', f'<div class="faq-a"><p>{SAFE_PAYMENT}</p></div>', updated, flags=re.S)
        updated = re.sub(r'<div class="faq-answer">(?=[^<]*(?:30%|30\s*%)).*?</div>', f'<div class="faq-answer">{SAFE_PAYMENT}</div>', updated, flags=re.S)
        updated = re.sub(r'<div class="reg-item"><h4>Payment Terms[^<]*</h4><p>.*?</p></div>', f'<div class="reg-item"><h4>Payment terms</h4><p>{SAFE_PAYMENT}</p></div>', updated, flags=re.S)
        if path.name == "terms.html":
            updated = re.sub(r'(<h2>2\.[^<]*</h2>).*?(?=<h2>3\.)', rf'\1\n        <p>{SAFE_PAYMENT}</p>\n\n        ', updated, count=1, flags=re.S)
        updated = ''.join(replace_outer_line(line) for line in updated.splitlines(keepends=True))
        updated = re.sub(r'100(?:\s|&nbsp;)*%\s+Irrevocable', 'Irrevocable', updated, flags=re.I)

        if path.name == "blog-how-to-export-india-to-africa.html" and "ILLUSTRATIVE TEMPLATE NOTICE" not in updated:
            notice = ('<div class="tip-box"><strong>ILLUSTRATIVE TEMPLATE NOTICE:</strong> Every company identifier, address, bank, account, SWIFT/BIC, amount, percentage and shipment reference in the templates below is fictional or a placeholder. Do not use it for a shipment or payment. Replace every field and independently verify payment instructions through a known company contact.</div>\n')
            updated = updated.replace('<div class="doc-widget">', notice + '<div class="doc-widget">', 1)

        locale = path.parts[len(ROOT.parts)] if len(path.parts) > len(ROOT.parts) + 1 and path.parts[len(ROOT.parts)] in PAYMENT_I18N else None
        if locale:
            updated = updated.replace(SAFE_PAYMENT, PAYMENT_I18N[locale])
            updated = re.sub(r'<div class="tip-box"><strong>ILLUSTRATIVE TEMPLATE NOTICE:</strong>.*?</div>', f'<div class="tip-box"><strong>{NOTICE_I18N[locale]}</strong></div>', updated, count=1, flags=re.S)

        if updated != text:
            path.write_text(updated, encoding="utf-8", newline="")
            changed += 1
    print(f"Updated {changed} HTML documents")


if __name__ == "__main__":
    main()
