"""Akademik takvime göre son başvuru gününü hesaplar.

Süreler dil modeline bırakılmaz: tarih metinden kurallarla çıkarılır, iş günleri
hafta sonu ve takvimdeki resmi tatiller atlanarak Python ile sayılır.
"""

import json
import logging
import re
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path

from .classifier import fold_words

logger = logging.getLogger("gtu_rehber.deadlines")

MONTHS = {
    "ocak": 1, "subat": 2, "mart": 3, "nisan": 4, "mayis": 5, "haziran": 6,
    "temmuz": 7, "agustos": 8, "eylul": 9, "ekim": 10, "kasim": 11, "aralik": 12,
}
MONTH_NAMES = ["", "Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz",
               "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]
WEEKDAYS = {"pazartesi": 0, "sali": 1, "carsamba": 2, "persembe": 3, "cuma": 4, "cumartesi": 5, "pazar": 6}
WEEKDAY_NAMES = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]

# İş günü ile hesaplanan süreler: konu -> (iş günü, olay adı, madde)
WORKDAY_RULES = {
    "mazeret_sinavi": (5, "sınav tarihi", "Madde 29"),
    "not_itirazi": (5, "notun ilan tarihi", "Madde 28"),
}
# Takvimdeki pencereye göre hesaplanan süreler: konu -> takvimdeki etkinlik adı
WINDOW_RULES = {
    "ders_ekle_birak": "Ders Ekleme ve Çıkarma",
    "kayit_dondurma": "Kayıt Dondurma",
}
# Bilgi konularında gösterilecek takvim etkinlikleri
CALENDAR_KEYWORDS = {
    "yatay_gecis": ("Yatay Geçiş",),
    "cift_anadal": ("Çift Anadal",),
    "yandal": ("Yandal",),
    "yaz_okulu": ("Yaz Okulu",),
    "erasmus": ("Erasmus",),
    "azami_sure": ("Ek Sınav",),
    "ingilizce_hazirlik": ("İngilizce",),
    "muafiyet_intibak": ("Ders Saydırma",),
    "mezuniyet_diploma": ("Tek Ders",),
    "staj_basvurusu": (),
}


def format_date(d: date) -> str:
    return f"{d.day} {MONTH_NAMES[d.month]} {d.year} {WEEKDAY_NAMES[d.weekday()]}"


def parse_event_date(text: str, today: date) -> date | None:
    """Mesajdaki olay tarihini bulur: '20 Ekim', '20.10.2026', 'dün', 'Pazartesi' gibi."""
    words = fold_words(text)
    joined = " ".join(words)

    # 20 Ekim (2026)
    m = re.search(r"\b(\d{1,2}) (" + "|".join(MONTHS) + r")[a-z]*(?: (\d{4}))?", joined)
    if m:
        year = int(m.group(3)) if m.group(3) else today.year
        try:
            return date(year, MONTHS[m.group(2)], int(m.group(1)))
        except ValueError:
            return None
    # 20.10.2026 ya da 20/10
    m = re.search(r"\b(\d{1,2})[./](\d{1,2})(?:[./](\d{2,4}))?\b", text)
    if m:
        year = int(m.group(3)) if m.group(3) else today.year
        year = year + 2000 if year < 100 else year
        try:
            return date(year, int(m.group(2)), int(m.group(1)))
        except ValueError:
            return None
    # Göreli ifadeler
    if "bugun" in words:
        return today
    if "dun" in words:
        return today - timedelta(days=1)
    if re.search(r"\b(?:evvelsi|onceki) gun", joined):
        return today - timedelta(days=2)
    m = re.search(r"\b(\d{1,2}) gun once", joined)
    if m:
        return today - timedelta(days=int(m.group(1)))
    # Haftanın günü: en yakın geçmiş gün ("geçen" varsa bir hafta önce)
    for i, w in enumerate(words):
        if w in WEEKDAYS:
            back = (today.weekday() - WEEKDAYS[w]) % 7
            if i > 0 and words[i - 1] == "gecen":
                back += 7
            return today - timedelta(days=back)
    return None


@dataclass
class Calendar:
    events: list[dict]
    holidays: set[date]
    source: str

    @classmethod
    def load(cls, path: Path) -> "Calendar":
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            logger.warning("Akademik takvim okunamadı: %s", path)
            return cls([], set(), "")
        holidays = set()
        for h in data.get("holidays", []):
            d, end = date.fromisoformat(h["start"]), date.fromisoformat(h["end"])
            while d <= end:
                holidays.add(d)
                d += timedelta(days=1)
        events = [
            {**e, "start": date.fromisoformat(e["start"]), "end": date.fromisoformat(e["end"])}
            for e in data.get("events", [])
        ]
        return cls(events, holidays, data.get("source", ""))

    def is_workday(self, d: date) -> bool:
        return d.weekday() < 5 and d not in self.holidays

    def add_workdays(self, start: date, n: int) -> date:
        """start gününden sonraki n. iş gününü döner (start günü sayılmaz)."""
        d = start
        while n > 0:
            d += timedelta(days=1)
            if self.is_workday(d):
                n -= 1
        return d

    def workdays_between(self, start: date, end: date) -> int:
        """start'tan sonra end dahil kalan iş günü sayısı."""
        count, d = 0, start
        while d < end:
            d += timedelta(days=1)
            if self.is_workday(d):
                count += 1
        return count

    def windows(self, name: str) -> list[dict]:
        return sorted((e for e in self.events if name.lower() in e["event"].lower()), key=lambda e: e["start"])

    def upcoming(self, keywords: tuple[str, ...], today: date, limit: int = 3) -> list[dict]:
        found = [
            e for e in self.events
            if e["end"] >= today and any(k.lower() in e["event"].lower() for k in keywords)
        ]
        found.sort(key=lambda e: e["start"])
        return [_event_dict(e) for e in found[:limit]]


def _event_dict(e: dict) -> dict:
    return {"event": e["event"], "date_text": e["date_text"], "start": e["start"].isoformat(), "end": e["end"].isoformat()}


def _status(cal: Calendar, last_day: date, today: date) -> tuple[str, int]:
    if last_day < today:
        return "geçti", 0
    if last_day == today:
        return "son gün bugün", 0
    return "açık", cal.workdays_between(today, last_day)


def compute(topic_id: str, question: str, cal: Calendar, today: date) -> dict | None:
    """Konuya göre son başvuru gününü hesaplar. Süre kuralı olmayan konularda None döner."""
    if topic_id in WORKDAY_RULES:
        days, event_name, article = WORKDAY_RULES[topic_id]
        event_date = parse_event_date(question, today)
        assumed = event_date is None
        event_date = event_date or today
        last_day = cal.add_workdays(event_date, days)
        status, left = _status(cal, last_day, today)
        explanation = (
            f"{event_name.capitalize()} ({format_date(event_date)}) itibarıyla {days} iş günü "
            f"(hafta sonu ve resmi tatiller hariç) sayıldı ({article})."
        )
        if assumed:
            explanation += f" Mesajınızda {event_name} olmadığı için bugün esas alındı; farklıysa tarihi yazın."
        return {
            "type": "iş_günü",
            "event_date": event_date.isoformat(),
            "event_date_assumed": assumed,
            "last_day": last_day.isoformat(),
            "last_day_text": format_date(last_day),
            "status": status,
            "workdays_left": left,
            "explanation": explanation,
        }

    if topic_id in WINDOW_RULES:
        windows = cal.windows(WINDOW_RULES[topic_id])
        if not windows:
            return None
        current = next((w for w in windows if w["end"] >= today), None)
        window = current or windows[-1]
        status, left = _status(cal, window["end"], today)
        if window["start"] > today:
            status = "henüz başlamadı"
        explanation = f"Akademik takvime göre: {window['event']} ({window['date_text']})."
        if current is None:
            explanation += " Bu akademik yılın başvuru dönemleri geçti."
        elif window is not windows[0] and windows[0]["end"] < today:
            explanation += f" Güz dönemi penceresi ({windows[0]['date_text']}) geçti; bir sonraki dönem gösteriliyor."
        return {
            "type": "takvim",
            "window_start": window["start"].isoformat(),
            "window_end": window["end"].isoformat(),
            "window_start_text": format_date(window["start"]),
            "last_day": window["end"].isoformat(),
            "last_day_text": format_date(window["end"]),
            "status": status,
            "workdays_left": left,
            "explanation": explanation,
        }
    return None


def deadline_sentence(deadline: dict) -> str:
    text = deadline["last_day_text"]
    status = deadline["status"]
    if status == "geçti":
        return f"Son başvuru günü {text} idi ve geçmiş görünüyor; geç başvuru için bölümünüze danışın."
    if status == "son gün bugün":
        return f"Son başvuru gününüz bugün ({text})."
    if status == "henüz başlamadı":
        return f"Bir sonraki başvuru dönemi {deadline['window_start_text']} günü başlıyor, son gün {text}."
    return f"Son başvuru gününüz {text} ({deadline['workdays_left']} iş günü kaldı)."
