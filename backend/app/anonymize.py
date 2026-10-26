"""Öğrenci deneyimlerindeki kişisel bilgileri kayıttan önce temizler.

Kişi adları silinir ve bağlama göre bir role çevrilir ("bölüm staj komisyonu üyesi" gibi).
E-posta, telefon ve öğrenci/T.C. numaraları tamamen kaldırılır.
İki katman vardır: kurallar (unvan/hitap kalıpları) ve yerel dil modeli (kalan adlar).
Paylaşımlar yayınlanmadan önce yönetici tarafından ayrıca kontrol edilir.
"""

import json
import re

from .llm import LocalLLM

UPPER = "A-ZÇĞİÖŞÜ"
LOWER = "a-zçğıöşü"
NAME = rf"[{UPPER}][{LOWER}]+"
NAMES = rf"{NAME}(?:\s+{NAME}){{0,2}}"

TITLE = (
    r"(?:Prof\.?\s*Dr\.?|Doç\.?\s*Dr\.?|Dr\.?\s*Öğr\.?\s*Üyesi|Öğr\.?\s*Gör\.?|Arş\.?\s*Gör\.?"
    r"|Dr\.?|Prof\.?|Doç\.?)"
)
TITLED = re.compile(rf"{TITLE}\s+{NAMES}")
HONORIFIC = re.compile(rf"{NAMES}\s+(?=(?:[Hh]oca|[Bb]ey|[Hh]an[ıi]m)\w*)")
HONORIFIC_WORD = re.compile(r"\b(?:[Hh]oca|[Bb]ey|[Hh]an[ıi]m)\w*")

EMAIL = re.compile(r"[\w.+-]+@[\w-]+\.[\w.]+")
PHONE = re.compile(r"(?:\+?90[\s-]?)?0?5\d{2}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}")
NUMBER = re.compile(r"\b\d{8,11}\b")  # öğrenci no, T.C. kimlik no

# Ad sanılabilecek ama ad olmayan kelimeler
NOT_NAMES = {
    "gtü", "gebze", "teknik", "üniversitesi", "obs", "öibs", "kyk", "erasmus", "türkiye", "istanbul",
    "kocaeli", "mühendislik", "fakültesi", "bölüm", "bölümü", "dekanlık", "rektörlük", "öğrenci",
    "işleri", "pazartesi", "salı", "çarşamba", "perşembe", "cuma", "cumartesi", "pazar", "ocak",
    "şubat", "mart", "nisan", "mayıs", "haziran", "temmuz", "ağustos", "eylül", "ekim", "kasım",
    "aralık", "e-nabız", "nabız", "sgk", "ben", "biz", "hoca", "hocam",
}

ROLES = [
    (("staj",), "bölüm staj komisyonu üyesi"),
    (("danışman",), "danışman"),
    (("sekreter",), "bölüm sekreteri"),
    (("bölüm başkan", "başkan"), "bölüm başkanı"),
    (("dekan",), "dekanlık yetkilisi"),
    (("öğrenci işleri", "memur"), "öğrenci işleri görevlisi"),
    (("arkadaş",), "bir arkadaşım"),
    (("hoca", "ders", "sınav", "vize", "final", "not", "prof", "doç", "dr"), "dersin öğretim üyesi"),
]
DEFAULT_ROLE = "ilgili görevli"


def _role(text: str, start: int, end: int) -> str:
    context = text[max(0, start - 60):end + 60].lower()
    for keywords, role in ROLES:
        if any(k in context for k in keywords):
            return role
    return DEFAULT_ROLE


ROLE_WORDS = ("danışman", "sekreter", "başkan", "dekan", "hoca", "müdür", "memur", "komisyon")


def _placeholder(text: str, start: int, end: int) -> str:
    # Önünde zaten rol yazıyorsa ("bölüm sekreteri Fatma Hanım") sadece adı sil
    before = text[max(0, start - 25):start].lower()
    if any(w in before for w in ROLE_WORDS):
        return "[ad silindi]"
    return f"[{_role(text, start, end)}]"


def _replace_spans(text: str, pattern: re.Pattern) -> tuple[str, int]:
    count = 0

    def repl(m: re.Match) -> str:
        nonlocal count
        words = m.group().split()
        # Baştaki rol kelimelerini koru ("Danışmanım Ali Bey" -> "Danışmanım [ad silindi]")
        kept = []
        while words and words[0].lower().startswith(ROLE_WORDS):
            kept.append(words.pop(0))
        if not [w for w in words if w.lower().strip(".") not in NOT_NAMES]:
            return m.group()
        count += 1
        if kept:
            return " ".join(kept) + " [ad silindi] "
        return _placeholder(text, m.start(), m.end()) + " "

    return pattern.sub(repl, text), count


def _model_names(llm: LocalLLM, text: str) -> list[str]:
    answer = llm.chat(
        "Metinde geçen gerçek kişi adlarını (ad ve soyad) JSON listesi olarak yaz. "
        "Kurum, şehir, ders veya gün adlarını yazma. Kişi adı yoksa [] yaz.",
        text,
        max_tokens=60,
        temperature=0.0,
        examples=[
            ("Staj için Ahmet Kaya ile görüştüm, GTÜ onay verdi.", '["Ahmet Kaya"]'),
            ("Bölüm sekreterliği dilekçemi aynı gün aldı.", "[]"),
        ],
    )
    try:
        names = json.loads(answer or "[]")
    except ValueError:
        return []
    return [n for n in names if isinstance(n, str)]


def anonymize(text: str, llm: LocalLLM | None = None) -> tuple[str, int]:
    """Metni temizler; (temiz metin, değiştirilen kişi sayısı) döner."""
    text = EMAIL.sub("[e-posta silindi]", text)
    text = PHONE.sub("[telefon silindi]", text)
    text = NUMBER.sub("[numara silindi]", text)

    text, titled = _replace_spans(text, TITLED)
    text, honored = _replace_spans(text, HONORIFIC)
    # "[dersin öğretim üyesi] hoca" gibi kalıntıları temizle
    text = re.sub(r"(\])\s+" + HONORIFIC_WORD.pattern, r"\1", text)
    count = titled + honored

    if llm is not None and llm.ready:
        for name in _model_names(llm, text):
            name = name.strip()
            # Model sadece metinde birebir geçen, büyük harfle başlayan adları değiştirebilir
            if not name or not name[0].isupper() or name.lower() in NOT_NAMES:
                continue
            for m in list(re.finditer(re.escape(name), text))[::-1]:
                text = f"{text[:m.start()]}{_placeholder(text, m.start(), m.end())}{text[m.end():]}"
                count += 1

    # "[rol] 'a" -> "[rol]'a": ad silinince ekten önce boşluk kalmasın
    text = re.sub(r"\]\s+(?=['’]\w)", "]", text)
    return re.sub(r"\s{2,}", " ", text).strip(), count
