"""Anonimleştirme testleri (sadece kurallar, dil modeli olmadan)."""

import pytest

from app.anonymize import anonymize


@pytest.mark.parametrize(
    "text, gone, expected",
    [
        ("Staj için Prof. Dr. Ayşe Yılmaz ile görüştüm.", "Ayşe", "[bölüm staj komisyonu üyesi]"),
        ("Mehmet Hoca vize notumu düzeltti.", "Mehmet", "[dersin öğretim üyesi]"),
        ("Danışmanım Ali Bey dilekçemi onayladı.", "Ali", "Danışmanım [ad silindi]"),
        ("Bölüm sekreteri Fatma Hanım dilekçemi aldı.", "Fatma", "[ad silindi]"),
    ],
)
def test_isimler_rollere_cevrilir(text, gone, expected):
    cleaned, count = anonymize(text)
    assert gone not in cleaned and expected in cleaned and count == 1


def test_iletisim_bilgileri_silinir():
    cleaned, _ = anonymize("Numaram 171044012, telefonum 0532 123 45 67, mailim ali.veli@gtu.edu.tr")
    assert "171044012" not in cleaned and "0532" not in cleaned and "@" not in cleaned


def test_kurum_ve_gun_adlarina_dokunulmaz():
    text = "Pazartesi GTÜ Öğrenci İşleri raporumu aldı."
    assert anonymize(text) == (text, 0)


def test_ek_onunde_bosluk_kalmaz():
    cleaned, _ = anonymize("Belgemi Doç. Dr. Kemal Arıkan'a imzalattım, staj başladı.")
    assert "üyesi]'a imzalattım" in cleaned
