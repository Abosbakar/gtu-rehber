"""Anahtar kelimeyle konu belirleme testleri (dil modeli olmadan)."""

from pathlib import Path

import pytest

from app.classifier import classify
from app.extract import course_code, department_files
from app.llm import LocalLLM
from app.search import RegulationIndex

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@pytest.fixture(scope="module")
def index() -> RegulationIndex:
    return RegulationIndex(str(DATA_DIR))


@pytest.fixture
def no_llm() -> LocalLLM:
    llm = LocalLLM("yok.gguf", 1, 512)
    llm.status = "unavailable"
    return llm


@pytest.mark.parametrize(
    "question, expected",
    [
        ("Hastalandım, AERO408 vizesine giremedim", "mazeret_sinavi"),
        ("Final sınavına giremedim, raporum var", "mazeret_sinavi"),
        ("Notuma itiraz etmek istiyorum", "not_itirazi"),
        ("Bu dönem kaydımı dondurmak istiyorum", "kayit_dondurma"),
        ("Dersi bırakmak istiyorum, ekle bırak ne zaman?", "ders_ekle_birak"),
        ("Yaz stajımı nereye başvurarak yapacağım?", "staj_basvurusu"),
        ("Yatay geçiş şartları neler?", "yatay_gecis"),
        ("KYK bursum kesilir mi?", "kyk_burs_kredi"),
        ("Erasmus başvurusu nasıl yapılır?", "erasmus"),
        ("Yaz okulunda kaç kredi alabilirim?", "yaz_okulu"),
    ],
)
def test_konu_belirlenir(index, no_llm, question, expected):
    result = classify(question, no_llm, index)
    assert result.topic is not None and result.topic.id == expected


def test_ilgisiz_soru_belirsiz_kalir(index, no_llm):
    assert classify("Kantinde bugün yemek ne?", no_llm, index).topic is None


def test_ders_kodu_cikarilir():
    assert course_code("Hastalandım, AERO408 vizesine giremedim") == "AERO408"
    assert course_code("CSE 101 dersinden") == "CSE101"
    assert course_code("dersime giremedim") is None


def test_bolum_staj_belgesi_secilir():
    assert "staj-esaslari-bilgisayar.pdf" in department_files("Bilgisayar mühendisliği stajı")
    assert department_files("stajım hakkında") is None
