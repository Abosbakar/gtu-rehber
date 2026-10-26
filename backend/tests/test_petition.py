"""Dilekçe PDF testleri. DejaVu yazı tipi yoksa (ör. Windows) atlanır; Docker içinde çalışır."""

from datetime import date
from pathlib import Path

import pytest
from pypdf import PdfReader

from app.petition import FONT_CANDIDATES, PetitionData, PetitionError, build_pdf

HAS_FONT = any(Path(p).exists() for p in FONT_CANDIDATES)
TODAY = date(2026, 10, 26)


def _text(pdf: bytes) -> str:
    import io

    return "\n".join(p.extract_text() for p in PdfReader(io.BytesIO(pdf)).pages)


@pytest.mark.skipif(not HAS_FONT, reason="DejaVu yazı tipi yok")
def test_mazeret_dilekcesi_turkce_karakterlerle_uretilir():
    pdf = build_pdf(
        PetitionData(
            topic="mazeret_sinavi",
            full_name="Öğrenci Çağrı Şeker",
            student_no="171044012",
            department="Bilgisayar Mühendisliği",
            course_code="AERO408",
            event_date="2026-10-19",
            reason="sağlık sorunu",
        ),
        TODAY,
    )
    assert pdf.startswith(b"%PDF")
    text = _text(pdf)
    for part in ("Öğrenci Çağrı Şeker", "AERO408", "19.10.2026", "29. maddesi", "BİLGİSAYAR MÜHENDİSLİĞİ"):
        assert part in text


def test_eksik_bilgi_anlasilir_hata_verir():
    with pytest.raises(PetitionError, match="ders kodu"):
        build_pdf(PetitionData("not_itirazi", "Ad Soyad", "123456", "Makine", event_date="2026-10-20"), TODAY)


def test_sablonu_olmayan_konu_reddedilir():
    with pytest.raises(PetitionError):
        build_pdf(PetitionData("erasmus", "Ad Soyad", "123456", "Makine"), TODAY)
