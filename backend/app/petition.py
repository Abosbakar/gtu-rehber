"""Doldurulmuş dilekçeyi PDF olarak üretir.

Dilekçe metni şablondan gelir (dil modeli dilekçe yazmaz). Öğrencinin kişisel bilgileri
hiçbir yere kaydedilmez; sadece PDF'i oluşturmak için kullanılır.
"""

import io
import logging
from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re

from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle
from xml.sax.saxutils import escape

from .topics import TOPICS_BY_ID

logger = logging.getLogger("gtu_rehber.petition")

FONT_CANDIDATES = [
    "/usr/share/fonts/dejavu/DejaVuSans.ttf",  # Alpine (font-dejavu)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",  # Debian/Ubuntu
    "C:/Windows/Fonts/DejaVuSans.ttf",
]
FONT = "DejaVuSans"
YONETMELIK = "GTÜ Ön Lisans ve Lisans Eğitim-Öğretim Yönetmeliği"


@dataclass
class PetitionData:
    topic: str
    full_name: str
    student_no: str
    department: str
    course_code: str = ""
    event_date: str = ""  # GG.AA.YYYY
    reason: str = ""
    details: str = ""
    phone: str = ""
    email: str = ""


# Konu -> (hitap, metin şablonu, zorunlu alanlar)
TEMPLATES: dict[str, tuple[str, str, tuple[str, ...]]] = {
    "mazeret_sinavi": (
        "{department} Bölüm Başkanlığına",
        "Bölümünüz {student_no} numaralı öğrencisiyim. {event_date} tarihinde yapılan {course_code} dersinin "
        "sınavına {reason} nedeniyle giremedim. Mazeretimi gösteren belge ekte sunulmuştur. "
        f"{YONETMELIK}'nin 29. maddesi uyarınca tarafıma mazeret sınavı hakkı verilmesini talep ederim.",
        ("course_code", "event_date", "reason"),
    ),
    "not_itirazi": (
        "{department} Bölüm Başkanlığına",
        "Bölümünüz {student_no} numaralı öğrencisiyim. {course_code} dersinin {event_date} tarihinde ilan edilen "
        f"notuna itiraz ediyorum. {YONETMELIK}'nin 28. maddesi uyarınca sınav kâğıdımın ve notuma katkısı "
        "olan çalışmalarımın yeniden incelenmesini talep ederim.",
        ("course_code", "event_date"),
    ),
    "ders_ekle_birak": (
        "{department} Bölüm Başkanlığına",
        "Bölümünüz {student_no} numaralı öğrencisiyim. Bu yarıyıl {course_code} dersi için ders ekleme-çıkarma "
        f"talebimi bildiriyorum: {{details}}. {YONETMELIK}'nin 17. maddesi çerçevesinde talebimin "
        "değerlendirilmesini talep ederim.",
        ("course_code", "details"),
    ),
    "kayit_dondurma": (
        "{department} Bölüm Başkanlığına",
        "Bölümünüz {student_no} numaralı öğrencisiyim. {reason} nedeniyle {details} kaydımın dondurulmasını "
        f"(yarıyıl izni) talep ediyorum. Gerekçemi gösteren belge ekte sunulmuştur. {YONETMELIK}'nin "
        "19. maddesi uyarınca talebimin ilgili yönetim kuruluna iletilmesini talep ederim.",
        ("reason", "details"),
    ),
    "staj_basvurusu": (
        "{department} Bölümü Staj Komisyonu Başkanlığına",
        "Bölümünüz {student_no} numaralı öğrencisiyim. Zorunlu stajımı aşağıda bilgileri verilen kurumda "
        "yapmak istiyorum: {details}. Staj kabul belgesi ekte sunulmuştur. Staj başvurumun fakülte staj "
        "yönergesi ve bölüm staj uygulama esasları çerçevesinde değerlendirilmesini talep ederim.",
        ("details",),
    ),
}

# Dilekçeye eklenmesi gereken belgeler
ATTACHMENTS: dict[str, tuple[str, ...]] = {
    "mazeret_sinavi": ("Mazereti gösteren belge (ör. sağlık raporu)",),
    "kayit_dondurma": ("Gerekçeyi gösteren belge",),
    "staj_basvurusu": ("Staj kabul belgesi",),
}

FIELD_LABELS = {
    "course_code": "ders kodu",
    "event_date": "tarih",
    "reason": "gerekçe",
    "details": "açıklama",
}


class PetitionError(ValueError):
    pass


def _register_font() -> None:
    if FONT in pdfmetrics.getRegisteredFontNames():
        return
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            pdfmetrics.registerFont(TTFont(FONT, path))
            return
    raise PetitionError("Dilekçe için Türkçe yazı tipi bulunamadı.")


def _upper_tr(text: str) -> str:
    return text.replace("i", "İ").replace("ı", "I").upper()


def _format_date(value: str) -> str:
    # Tarayıcının tarih alanı YYYY-AA-GG gönderir; dilekçede GG.AA.YYYY yazılır
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value.strip())
    return f"{m.group(3)}.{m.group(2)}.{m.group(1)}" if m else value


def build_pdf(data: PetitionData, today: date) -> bytes:
    if data.topic not in TEMPLATES:
        raise PetitionError("Bu konu için dilekçe şablonu yok.")
    heading, body, required = TEMPLATES[data.topic]
    missing = [FIELD_LABELS[f] for f in required if not getattr(data, f).strip()]
    if missing:
        raise PetitionError(f"Dilekçe için eksik bilgi: {', '.join(missing)}.")

    _register_font()
    values = {k: escape(str(v).strip()) for k, v in data.__dict__.items()}
    values["event_date"] = _format_date(values["event_date"])
    text = body.format(**values)

    base = ParagraphStyle("base", fontName=FONT, fontSize=11.5, leading=17)
    centered = ParagraphStyle("center", parent=base, alignment=TA_CENTER)
    right = ParagraphStyle("right", parent=base, alignment=TA_RIGHT)
    body_style = ParagraphStyle("body", parent=base, alignment=TA_JUSTIFY, firstLineIndent=1.25 * cm)
    small = ParagraphStyle("small", parent=base, fontSize=8.5, leading=11, textColor="#666666")

    topic = TOPICS_BY_ID[data.topic]
    attachments = ATTACHMENTS.get(data.topic, ())

    info = [
        ["Adı Soyadı", values["full_name"]],
        ["Öğrenci No", values["student_no"]],
        ["Bölüm", values["department"]],
    ]
    if values["phone"]:
        info.append(["Telefon", values["phone"]])
    if values["email"]:
        info.append(["E-posta", values["email"]])
    info_table = Table(
        [[Paragraph(a, base), Paragraph(f": {b}", base)] for a, b in info],
        colWidths=[3.2 * cm, 9 * cm],
        hAlign="LEFT",
    )
    info_table.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 0)]))

    story = [
        Paragraph(today.strftime("%d.%m.%Y"), right),
        Spacer(1, 0.8 * cm),
        Paragraph("T.C.<br/>GEBZE TEKNİK ÜNİVERSİTESİ", centered),
        Paragraph(_upper_tr(heading.format(**values)), centered),
        Spacer(1, 1 * cm),
        Paragraph(text, body_style),
        Spacer(1, 0.4 * cm),
        Paragraph("Gereğini saygılarımla arz ederim.", body_style),
        Spacer(1, 1.2 * cm),
        Paragraph(f"{values['full_name']}<br/>İmza", right),
        Spacer(1, 1.2 * cm),
        info_table,
    ]
    if attachments:
        story += [Spacer(1, 0.6 * cm), Paragraph("Ekler:", base)]
        story += [Paragraph(f"{i}. {escape(a)}", base) for i, a in enumerate(attachments, 1)]
    story += [
        Spacer(1, 1.5 * cm),
        Paragraph(
            "Bu dilekçe GTÜ Rehber ile hazırlanmıştır. Bilgileri kontrol edip imzaladıktan sonra "
            f"ilgili birime teslim ediniz. Başvuru yeri: {escape(topic.office)}.",
            small,
        ),
    ]

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        title=f"Dilekçe - {topic.name}",
        author="GTÜ Rehber",
    )
    doc.build(story)
    return buffer.getvalue()
