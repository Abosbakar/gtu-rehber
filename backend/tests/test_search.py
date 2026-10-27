"""Madde arama modülü testleri. Çalıştırma: backend klasöründe `pytest`."""

from pathlib import Path

import pytest

from app.search import RegulationIndex, normalize

DATA_DIR = Path(__file__).resolve().parents[2] / "data"


@pytest.fixture(scope="module")
def index() -> RegulationIndex:
    return RegulationIndex(str(DATA_DIR))


def test_normalize_turkce_karakterleri_sadelestirir():
    assert normalize("SINAV") == normalize("sınav") == normalize("sinav")
    assert normalize("İtiraz") == normalize("itiraz")


def test_tum_belgeler_okunur(index):
    assert index.loaded_documents == 34
    assert len(index.chunks) > 500


@pytest.mark.parametrize(
    "query, files, expected",
    [
        ("mazeret sınavı haklı geçerli neden", {"yonetmelik.pdf"}, "Madde 29"),
        ("notuma itiraz etmek istiyorum", None, "Madde 28"),
        ("ders ekleme çıkarma", {"yonetmelik.pdf"}, "Madde 17"),
        ("yarıyıl izni kayıt dondurma", {"yonetmelik.pdf"}, "Madde 19"),
    ],
)
def test_dogru_madde_bulunur(index, query, files, expected):
    hits = index.search(query, files=files, top_k=1)
    assert hits and hits[0].label.startswith(expected)


def test_bos_sorgu_hata_vermez(index):
    assert index.search("   ") == []
    assert index.search("ve ile bir") == []


def test_pdf_kopuk_harfleri_birlestirilir():
    from app.search import _fix_split_words

    assert _fix_split_words("öğrenciler e, başka b ir ders") == "öğrencilere, başka bir ders"
    assert _fix_split_words("o dönem için en az a) b)") == "o dönem için en az a) b)"
