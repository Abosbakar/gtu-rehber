"""Yönetmelik metinlerinde madde arama (BM25).

PDF'ler açılışta bir kez okunur, maddelere bölünür ve bellekte indekslenir.
Madde metni öğrenciye olduğu gibi gösterilir; dil modeli metni değiştirmez.
"""

import logging
import math
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from .documents import DOCUMENTS, Document

logger = logging.getLogger("gtu_rehber.search")

# Maddeye bölünemeyen belgelerde parça uzunluğu (karakter)
WINDOW = 900
MAX_CHUNK = 2200

_TR_LOWER = str.maketrans({"I": "ı", "İ": "i"})
# Kullanıcı Türkçe karakter kullanmadan da yazabilir ("sinav", "itiraz")
_FOLD = str.maketrans("ıiğüşöçâîû", "iigusocaiu")

STOPWORDS = {
    "ve", "ile", "bir", "bu", "da", "de", "ki", "mi", "mu", "icin", "olan", "olarak",
    "veya", "ya", "gibi", "kadar", "daha", "en", "her", "ise", "ne", "nasil", "ben",
    "benim", "bana", "sen", "o", "biz", "sey", "var", "yok", "cok", "ama", "fakat",
    "madde", "fikra", "bendi", "ilgili", "tarafindan", "uzere", "sonra", "once",
}

_HEADER_PATTERNS = [
    re.compile(r"Doküman No.*?Sayfa\s*\d+\s*-\s*\d+", re.S),
    re.compile(r"Form No\s*:.*?(?:Değ\.?\s*Tarihi\s*:\s*\S+)", re.S),
]
_MADDE = re.compile(r"(?:GEÇİCİ\s+|EK\s+)?MADDE\s+\d+\s*[–—\-:]", re.I)


@dataclass
class Chunk:
    doc: Document
    label: str  # "Madde 29 – Mazeret sınavı" ya da "Bölüm 3"
    text: str
    tokens: list[str]


@dataclass
class Hit:
    file: str
    title: str
    code: str
    label: str
    text: str
    score: float


def normalize(text: str) -> list[str]:
    """Metni küçük harfe çevirir, Türkçe karakterleri sadeleştirir ve kök alır."""
    text = text.translate(_TR_LOWER).lower().translate(_FOLD)
    tokens = re.findall(r"[a-z0-9]+", text)
    # Türkçe ekleri kabaca atmak için ilk 5 harf kök kabul edilir (F5 kök bulma)
    return [t[:5] for t in tokens if len(t) > 1 and t not in STOPWORDS]


_LOW = "a-zçğıöşü"
_CONSONANT = "bcçdfgğhjklmnprsştvyz"
_VOWEL = "aeıiuüö"  # tek başına kelime olan "o" bilerek yok
# PDF'ten çıkarılan metinde kopmuş harfler: "b ir" -> "bir", "öğrenciler e" -> "öğrencilere"
_PREFIX_CONSONANT = re.compile(rf"(?<![{_LOW}\w])([{_CONSONANT}]) (?=[aeıioöuü][{_LOW}])")
_SUFFIX_CONSONANT = re.compile(rf"(?<=[{_LOW}]{{2}}) ([{_CONSONANT}])(?=[\s,.;:])")
_PREFIX_VOWEL = re.compile(rf"(?<![{_LOW}\w])([{_VOWEL}]) (?=ğ|[{_CONSONANT}]{{2}})")
_SUFFIX_VOWEL = re.compile(rf"(?<=[{_LOW}]{{2}}) ([{_VOWEL}])(?=[\s,.;:])")


def _fix_split_words(text: str) -> str:
    text = re.sub(r"\bi çin\b", "için", text)
    text = re.sub(r"\bv e\b", "ve", text)
    text = _PREFIX_CONSONANT.sub(r"\1", text)
    text = _PREFIX_VOWEL.sub(r"\1", text)
    text = _SUFFIX_CONSONANT.sub(r"\1", text)
    return _SUFFIX_VOWEL.sub(r"\1", text)


def _clean(text: str) -> str:
    for pattern in _HEADER_PATTERNS:
        text = pattern.sub(" ", text)
    text = re.sub(r"-\n(?=[a-zçğıöşü])", "", text)  # satır sonunda bölünmüş kelimeler
    return _fix_split_words(re.sub(r"[ \t]+", " ", text))


def _split_articles(doc: Document, text: str) -> list[tuple[str, str]]:
    matches = list(_MADDE.finditer(text))
    if len(matches) < 3:
        return _split_windows(text)

    # Madde başlığı ("Mazeret sınavı") genelde MADDE kelimesinden hemen önceki satırdadır
    title_starts = [_title_start(text, m.start()) for m in matches]
    parts = []
    for i, m in enumerate(matches):
        # Bir sonraki maddenin başlığı bu maddenin sonuna yapışmasın
        end = max(title_starts[i + 1], m.start()) if i + 1 < len(matches) else len(text)
        title = text[title_starts[i]:m.start()].strip()
        number = re.search(r"\d+", m.group()).group()
        head = m.group().upper()
        prefix = "Geçici Madde" if "GEÇİCİ" in head else "Ek Madde" if head.startswith("EK") else "Madde"
        label = f"{prefix} {number}" + (f" – {title}" if title else "")
        parts.extend((label, piece) for piece in _limit(text[m.start():end]))
    return parts


def _title_start(text: str, pos: int) -> int:
    """MADDE kelimesinden önceki satır kısa bir başlıksa o satırın başlangıcını döner."""
    seg_start = max(0, pos - 120)
    seg = text[seg_start:pos].rstrip()
    newline = seg.rfind("\n")
    if newline == -1:
        return pos
    candidate = seg[newline + 1:].strip()
    if candidate and len(candidate) < 80 and not candidate.endswith((".", ":", ";")):
        return seg_start + newline + 1
    return pos


def _split_windows(text: str) -> list[tuple[str, str]]:
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n|\n(?=\s*(?:\d+[.)]|[a-zçğıöşü]\)|•|-)\s)", text) if p.strip()]
    parts, current = [], ""
    for p in paragraphs:
        if current and len(current) + len(p) > WINDOW:
            parts.append(current)
            current = ""
        current = f"{current}\n{p}" if current else p
    if current:
        parts.append(current)
    return [(f"Bölüm {i + 1}", piece) for i, part in enumerate(parts) for piece in _limit(part)]


def _limit(text: str) -> list[str]:
    text = re.sub(r"\s*\n\s*", " ", text).strip()
    if len(text) <= MAX_CHUNK:
        return [text] if text else []
    sentences = re.split(r"(?<=[.;])\s+", text)
    pieces, current = [], ""
    for s in sentences:
        if current and len(current) + len(s) > MAX_CHUNK:
            pieces.append(current)
            current = ""
        current = f"{current} {s}".strip()
    if current:
        pieces.append(current)
    return pieces


class RegulationIndex:
    """Belgeler üzerinde BM25 arama indeksi."""

    k1 = 1.5
    b = 0.75

    def __init__(self, data_dir: str):
        self.chunks: list[Chunk] = []
        self.loaded_documents = 0
        self._load(Path(data_dir))
        self._build()

    def _load(self, data_dir: Path) -> None:
        for doc in DOCUMENTS:
            path = data_dir / doc.file
            if not path.exists():
                logger.warning("Belge bulunamadı: %s", path)
                continue
            try:
                reader = PdfReader(path)
                text = _clean("\n".join(page.extract_text() or "" for page in reader.pages))
            except Exception:
                logger.exception("Belge okunamadı: %s", path)
                continue
            for label, body in _split_articles(doc, text):
                tokens = normalize(f"{doc.title} {label} {body}")
                if tokens:
                    self.chunks.append(Chunk(doc, label, body, tokens))
            self.loaded_documents += 1
        logger.info("%d belgeden %d parça indekslendi", self.loaded_documents, len(self.chunks))

    def _build(self) -> None:
        self.term_freqs = [Counter(c.tokens) for c in self.chunks]
        self.lengths = [len(c.tokens) for c in self.chunks]
        self.avg_len = sum(self.lengths) / len(self.lengths) if self.lengths else 0
        df = Counter(term for tf in self.term_freqs for term in tf)
        n = len(self.chunks)
        self.idf = {t: math.log((n - f + 0.5) / (f + 0.5) + 1) for t, f in df.items()}

    def _score(self, i: int, query: list[str]) -> float:
        tf, length = self.term_freqs[i], self.lengths[i]
        score = 0.0
        for term in query:
            f = tf.get(term)
            if f:
                denom = f + self.k1 * (1 - self.b + self.b * length / self.avg_len)
                score += self.idf[term] * f * (self.k1 + 1) / denom
        return score

    def search(
        self,
        query: str,
        files: set[str] | None = None,
        top_k: int = 3,
    ) -> list[Hit]:
        """Sorguya en uygun maddeleri döner. files verilirse sadece o belgelerde arar."""
        terms = normalize(query)
        if not terms:
            return []
        scored = []
        for i, chunk in enumerate(self.chunks):
            if files is not None and chunk.doc.file not in files:
                continue
            score = self._score(i, terms)
            if score > 0:
                scored.append((score, chunk))
        scored.sort(key=lambda x: x[0], reverse=True)
        hits, seen = [], set()
        for s, c in scored:
            # Uzun maddeler parçalara bölünür; her maddeden sadece en iyi parça gösterilir
            if (c.doc.file, c.label) in seen:
                continue
            seen.add((c.doc.file, c.label))
            hits.append(Hit(c.doc.file, c.doc.title, c.doc.code, c.label, c.text, round(s, 2)))
            if len(hits) == top_k:
                break
        return hits
