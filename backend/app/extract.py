"""Öğrencinin mesajından dilekçe ve arama için gereken bilgileri çıkarır."""

import re

from .classifier import contains, fold_words
from .llm import LocalLLM
from .topics import DEPARTMENT_STAJ_FILES

# "AERO408", "CSE 101", "MAT102" gibi ders kodları
COURSE_CODE = re.compile(r"\b([A-ZÇĞİÖŞÜ]{2,5})\s?(\d{3})\b")

REASONS = [
    (("hasta", "rapor", "ameliyat", "ateş", "grip", "hastane"), "Sağlık sorunu"),
    (("kaza",), "Kaza"),
    (("cenaze", "vefat", "kaybett", "öldü"), "Yakınının vefatı"),
    (("askerlik", "asker"), "Askerlik"),
    (("maddi", "para", "ekonomik"), "Maddi nedenler"),
    (("ailevi", "aile"), "Ailevi nedenler"),
    (("doğum",), "Doğum"),
]


def course_code(text: str) -> str | None:
    m = COURSE_CODE.search(text)
    return f"{m.group(1)}{m.group(2)}" if m else None


def department_files(text: str) -> set[str] | None:
    """Staj sorusunda bölüm geçiyorsa o bölümün staj belgelerini döner."""
    words = fold_words(text)
    files: set[str] = set()
    for keyword, docs in DEPARTMENT_STAJ_FILES.items():
        if contains(words, keyword):
            files |= docs
    return files or None


def reason(text: str, llm: LocalLLM) -> str | None:
    words = fold_words(text)
    for keywords, label in REASONS:
        if any(contains(words, k) for k in keywords):
            return label
    answer = llm.chat(
        "Öğrencinin mesajında başına gelen olayı (mazeretini) en fazla 4 kelimeyle yaz. "
        "Öğrenci sadece ne istediğini söylüyor ama nedenini söylemiyorsa 'yok' yaz.",
        text,
        max_tokens=16,
        temperature=0.0,
        examples=[
            ("Trafikte kaldım, sınava yetişemedim", "Trafik nedeniyle gecikme"),
            ("Bu dönem kaydımı dondurmak istiyorum", "yok"),
        ],
    )
    if not answer or answer.strip(" .").lower() == "yok":
        return None
    return answer.strip(" .\"'")[:60]
