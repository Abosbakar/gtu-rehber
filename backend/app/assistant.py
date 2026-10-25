"""Soru cevaplama akışı: sınıflandır → bilgi çıkar → madde bul → kısa cevap yaz.

Madde metni aramadan gelir, dil modeli sadece kısa açıklama cümlelerini yazar.
"""

import re
from dataclasses import asdict
from datetime import date

from . import deadlines, extract
from .classifier import classify, contains, fold_words
from .db import ExperienceStore
from .llm import LocalLLM
from .search import Hit, RegulationIndex
from .topics import Topic

DISCLAIMER = (
    "GTÜ Rehber resmi bir kaynak değildir. Başvurmadan önce bilgileri bölümünüzle "
    "veya Öğrenci İşleri Daire Başkanlığı ile doğrulayın."
)
UNKNOWN_ANSWER = (
    "Bu konuda emin değilim. Lütfen Öğrenci İşleri Daire Başkanlığı'na ya da bölüm "
    "sekreterliğine danışın."
)

INTRO_SYSTEM = (
    "Sen Gebze Teknik Üniversitesi öğrencilerine yardım eden GTÜ Rehber asistanısın. "
    "Öğrencinin durumuna uygun, 'siz' diye hitap eden, TEK cümlelik kısa ve nazik bir giriş yaz. "
    "Hastalık veya kayıp varsa 'Geçmiş olsun' ya da 'Başınız sağ olsun' de. "
    "Kural, tarih, sayı veya madde numarası yazma; 'ben' ağzından yazma."
)
# Modele istenen biçimi gösteren örnekler (few-shot)
INTRO_EXAMPLES = [
    ("Durum: Grip oldum, fizik vizesine giremedim.\nKonu: Mazeret sınavı",
     "Geçmiş olsun, bu durumda mazeret sınavı için başvurabilirsiniz."),
    ("Durum: Bu dönem çift anadala başlamak istiyorum.\nKonu: Çift anadal",
     "Çift anadal başvurusu için aşağıdaki kurallara göz atabilirsiniz."),
]
MAX_INTRO = 160
# Küçük modelin bozuk çıktılarını yakalamak için: rakam, madde, istem tekrarı, "ben" ağzından cümleler
_BAD_INTRO = re.compile(
    r"\d|madde|öğrencinin|konu:|durum:|\b\w+(?:[ıiuü]yorum|[ae]bilirim|[ae]mezim)\b|\b\w+[ıiuü]m[ıiuü]z\w*",
    re.I,
)
_SYMPATHY = re.compile(r"^(?:geçmiş olsun|başınız sağ olsun)[,.!]?\s*", re.I)
_ILLNESS = ("hasta", "rapor", "ameliyat", "kaza", "grip", "ateş", "hastane")
_LOSS = ("vefat", "cenaze", "kaybett", "öldü")


def _hit_dict(hit: Hit) -> dict:
    return asdict(hit)


def _intro(llm: LocalLLM, question: str, topic: Topic) -> str | None:
    """Dil modeli sadece kişiye özel tek cümlelik bir giriş yazar; kurallar koddan gelir."""
    text = llm.chat(
        INTRO_SYSTEM,
        f"Durum: {question}\nKonu: {topic.name}",
        max_tokens=48,
        temperature=0.2,
        examples=INTRO_EXAMPLES,
    )
    if not text:
        return None
    text = " ".join(text.split())
    first = re.split(r"(?<=[.!?])\s+", text)[0]
    if _BAD_INTRO.search(first) or len(first) > MAX_INTRO or not first.endswith((".", "!")):
        return None
    # Taziye/geçmiş olsun ifadesini modele bırakmayız: mesajdaki duruma göre kod seçer
    words = fold_words(question)
    rest = _SYMPATHY.sub("", first)
    rest = rest[:1].upper() + rest[1:]
    if any(contains(words, w) for w in _LOSS):
        return f"Başınız sağ olsun, {rest[:1].lower() + rest[1:]}"
    if any(contains(words, w) for w in _ILLNESS):
        return f"Geçmiş olsun, {rest[:1].lower() + rest[1:]}"
    return rest


def _article_summary(hit: Hit, sentences: int = 2) -> str:
    """Bilgi konularında maddenin ilk cümlelerini olduğu gibi aktarır."""
    body = re.sub(r"^(?:(?:GEÇİCİ|EK)\s+)?MADDE\s+\d+\s*[–—\-:]\s*(?:\(\d+\)\s*)?", "", hit.text, flags=re.I)
    parts = re.split(r"(?<=[.;])\s+(?=[A-ZÇĞİÖŞÜ(])", body.strip())
    summary = " ".join(parts[:sentences]).rstrip(";")
    if len(summary) > 600:
        summary = summary[:600].rsplit(" ", 1)[0] + "…"
    return f"{hit.title}, {hit.label.split(' –')[0]}: \"{summary}\""


def _write_answer(
    llm: LocalLLM, question: str, topic: Topic, hit: Hit | None, office: str, deadline: dict | None
) -> tuple[str, str]:
    intro = _intro(llm, question, topic)
    parts = [intro or f"Durumunuz \"{topic.name}\" kapsamında görünüyor."]
    if topic.key_facts:
        parts += topic.key_facts
    elif hit:
        parts.append(_article_summary(hit))
    if deadline:
        parts.append(deadlines.deadline_sentence(deadline))
    if office:
        parts.append(f"Başvuru yeri: {office}.")
    return " ".join(parts), ("dil_modeli+kural" if intro else "kural")


def answer(
    question: str,
    index: RegulationIndex,
    llm: LocalLLM,
    calendar: deadlines.Calendar,
    store: ExperienceStore,
    today: date,
) -> dict:
    result = classify(question, llm, index)
    topic = result.topic
    base = {
        "classification": {"method": result.method, "confidence": result.confidence},
        "model_status": llm.status,
        "disclaimer": DISCLAIMER,
    }
    if topic is None:
        return {**base, "topic": None, "answer": UNKNOWN_ANSWER, "answer_source": "kural", "sources": []}

    extracted = {"course_code": extract.course_code(question)}
    files = set(topic.files)
    if topic.id == "staj_basvurusu":
        dept = extract.department_files(question)
        if dept:
            files = dept
        extracted["department_matched"] = bool(dept)
    if topic.id in ("mazeret_sinavi", "kayit_dondurma"):
        extracted["reason"] = extract.reason(question, llm)

    hits = index.search(f"{question} {topic.query}", files=files, top_k=3)
    # Süre koddan hesaplanır, dil modeli tarih üretmez
    deadline = deadlines.compute(topic.id, question, calendar, today)
    text, source = _write_answer(llm, question, topic, hits[0] if hits else None, topic.office, deadline)

    related = []
    if topic.side_search:
        query, side_files, note = topic.side_search
        side_hits = index.search(query, files=set(side_files), top_k=1)
        if side_hits:
            related.append({"note": note, "source": _hit_dict(side_hits[0])})

    return {
        **base,
        "topic": {"id": topic.id, "name": topic.name, "level": topic.level},
        "answer": text,
        "answer_source": source,
        "sources": [_hit_dict(h) for h in hits],
        "office": topic.office or None,
        "required_documents": list(topic.required_documents),
        "notes": list(topic.notes),
        "related": related,
        "extracted": extracted,
        "deadline": deadline,
        "calendar": calendar.upcoming(deadlines.CALENDAR_KEYWORDS.get(topic.id, ()), today)
        if topic.id in deadlines.CALENDAR_KEYWORDS else [],
        "experiences": store.approved(topic.id),
        "petition_available": topic.level == "tam",
    }
