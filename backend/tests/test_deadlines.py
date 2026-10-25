"""Süre hesabı ve deneyim veritabanı testleri."""

from datetime import date
from pathlib import Path

import pytest

from app.db import ExperienceStore
from app.deadlines import Calendar, compute, format_date, parse_event_date

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
TODAY = date(2026, 10, 25)  # Pazar


@pytest.fixture(scope="module")
def cal() -> Calendar:
    return Calendar.load(DATA_DIR / "akademik-takvim-2026-2027.json")


def test_takvim_yuklenir(cal):
    assert len(cal.events) > 50
    assert date(2026, 10, 29) in cal.holidays  # Cumhuriyet Bayramı
    assert date(2027, 1, 1) in cal.holidays  # Yeni Yıl


@pytest.mark.parametrize(
    "text, expected",
    [
        ("Pazartesi AERO408 vizesine giremedim", date(2026, 10, 19)),
        ("geçen Cuma sınavım vardı", date(2026, 10, 16)),
        ("dün sınava giremedim", date(2026, 10, 24)),
        ("20 Ekim'deki sınava giremedim", date(2026, 10, 20)),
        ("sınav 21.10.2026 tarihindeydi", date(2026, 10, 21)),
        ("3 gün önce hastalandım", date(2026, 10, 22)),
        ("sınava giremedim", None),
    ],
)
def test_tarih_cikarilir(text, expected):
    assert parse_event_date(text, TODAY) == expected


def test_is_gunu_tatili_atlar(cal):
    # 26 Ekim Pzt sınavı: 27, 28, (29 tatil), 30 Ekim, 2, 3 Kasım -> 5. iş günü 3 Kasım
    assert cal.add_workdays(date(2026, 10, 26), 5) == date(2026, 11, 3)


def test_mazeret_son_gunu(cal):
    result = compute("mazeret_sinavi", "Pazartesi vizeye giremedim", cal, TODAY)
    assert result["last_day"] == "2026-10-26"
    assert result["status"] == "açık" and result["workdays_left"] == 1
    assert not result["event_date_assumed"]


def test_tarih_yoksa_bugun_esas_alinir(cal):
    result = compute("not_itirazi", "notuma itiraz etmek istiyorum", cal, TODAY)
    assert result["event_date_assumed"] and result["event_date"] == TODAY.isoformat()


def test_takvim_penceresi(cal):
    # Güz ekle-bırak (28 Eylül-2 Ekim) geçti, bahar penceresi gösterilir
    result = compute("ders_ekle_birak", "ders bırakmak istiyorum", cal, TODAY)
    assert result["window_start"] == "2027-02-22" and result["status"] == "henüz başlamadı"


def test_sure_kurali_olmayan_konu(cal):
    assert compute("staj_basvurusu", "staj", cal, TODAY) is None


def test_tarih_turkce_yazilir():
    assert format_date(date(2026, 10, 29)) == "29 Ekim 2026 Perşembe"


def test_sadece_onayli_deneyimler_gorunur(tmp_path):
    store = ExperienceStore(str(tmp_path / "test.db"))
    store.add("mazeret_sinavi", "Bekleyen deneyim")
    store.add("mazeret_sinavi", "Onaylı deneyim", status="approved")
    store.add("not_itirazi", "Başka konu", status="approved")
    shown = store.approved("mazeret_sinavi")
    assert [e["text"] for e in shown] == ["Onaylı deneyim"]
    assert shown[0]["label"].startswith("Resmi değil")
