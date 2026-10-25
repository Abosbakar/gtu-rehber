"""Öğrencinin mesajını konulardan birine atar.

Önce anahtar kelimelere bakılır; sonuç net değilse yerel dil modeline sorulur.
Dil modelinin cevabı dilbilgisi kısıtıyla sadece geçerli konu kodlarından biri olabilir.
"""

import re
from dataclasses import dataclass

from .llm import LocalLLM
from .search import RegulationIndex
from .topics import TOPICS, TOPICS_BY_ID, Topic

UNKNOWN = "belirsiz"
STRONG, WEAK = 3, 1
# Anahtar kelime yoksa dil modelinin seçimini doğrulamak için gereken en düşük arama puanı
MIN_SEARCH_SCORE = 6.0

_TR_LOWER = str.maketrans({"I": "ı", "İ": "i"})
_FOLD = str.maketrans("ıiğüşöçâîû", "iigusocaiu")


@dataclass
class Classification:
    topic: Topic | None
    method: str  # "anahtar_kelime" | "dil_modeli" | "yok"
    confidence: str  # "yüksek" | "orta" | "düşük"


def fold_words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.translate(_TR_LOWER).lower().translate(_FOLD))


def contains(words: list[str], phrase: str) -> bool:
    parts = fold_words(phrase)
    for i in range(len(words) - len(parts) + 1):
        ok = True
        for j, p in enumerate(parts):
            w = words[i + j]
            # Kısa kelimeler ("ek", "ara") tam eşleşmeli; uzunlar ek almış olabilir
            if (len(p) <= 3 and w != p) or (len(p) > 3 and not w.startswith(p)):
                ok = False
                break
        if ok:
            return True
    return False


def keyword_scores(text: str) -> list[tuple[int, Topic]]:
    words = fold_words(text)
    scores = []
    for topic in TOPICS:
        score = sum(STRONG for k in topic.strong if contains(words, k))
        score += sum(WEAK for k in topic.weak if contains(words, k))
        if score:
            scores.append((score, topic))
    return sorted(scores, key=lambda x: x[0], reverse=True)


def _ask_model(llm: LocalLLM, text: str) -> Topic | None:
    options = "\n".join(f"- {t.id}: {t.description}" for t in TOPICS)
    system = (
        "Sen Gebze Teknik Üniversitesi öğrenci işleri asistanısın. "
        "Öğrencinin mesajını aşağıdaki konulardan birine ata. "
        f"Mesaj bu konulardan hiçbirine uymuyorsa '{UNKNOWN}' yaz.\n\n{options}"
    )
    answer = llm.chat(
        system,
        f"Öğrencinin mesajı: {text}\n\nKonu kodu:",
        max_tokens=12,
        temperature=0.0,
        choices=[t.id for t in TOPICS] + [UNKNOWN],
    )
    return TOPICS_BY_ID.get(answer or "")


def classify(text: str, llm: LocalLLM, index: RegulationIndex) -> Classification:
    scores = keyword_scores(text)
    best = scores[0][0] if scores else 0
    second = scores[1][0] if len(scores) > 1 else 0

    if best >= STRONG and best - second >= 2:
        return Classification(scores[0][1], "anahtar_kelime", "yüksek")

    topic = _ask_model(llm, text) if llm.ready else None
    if topic:
        if best > 0 and topic in {t for _, t in scores}:
            return Classification(topic, "dil_modeli", "yüksek")
        # Anahtar kelime desteği yoksa seçimi madde aramasıyla doğrula
        hits = index.search(f"{text} {topic.query}", files=set(topic.files), top_k=1)
        if hits and hits[0].score >= MIN_SEARCH_SCORE:
            return Classification(topic, "dil_modeli", "orta")
        return Classification(None, "dil_modeli", "düşük")

    # Dil modeli hazır değilse anahtar kelimelerle yetin
    if best >= STRONG or (best >= 2 and best > second):
        return Classification(scores[0][1], "anahtar_kelime", "orta")
    return Classification(None, "yok", "düşük")
