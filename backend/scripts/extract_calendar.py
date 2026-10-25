"""GTÜ akademik takvim sayfasını yapılandırılmış JSON'a çevirir.

Geliştirme sırasında bir kez çalıştırılır; çıktı (data/akademik-takvim-2026-2027.json)
depoya eklenir. Uygulama çalışırken internete bağlanmaz.

Kullanım: python extract_calendar.py <çıktı.json>
"""

import html
import json
import re
import sys
import unicodedata
import urllib.request
from datetime import date

URL = "https://www.gtu.edu.tr/icerik/1318/436/akademik-takvim.aspx"
MONTHS = {
    "ocak": 1, "şubat": 2, "mart": 3, "nisan": 4, "mayıs": 5, "haziran": 6,
    "temmuz": 7, "ağustos": 8, "eylül": 9, "ekim": 10, "kasım": 11, "aralık": 12,
}
HOLIDAY = re.compile(
    r"Bayram|Yılbaşı|Yeni Yıl|Demokrasi ve Milli Birlik|Emek ve Dayanışma|Egemenlik ve Çocuk|"
    r"Atatürk.?ü Anma",
    re.I,
)
_TR_LOWER = str.maketrans({"I": "ı", "İ": "i"})


def _decode(raw: bytes) -> str:
    # Sayfada karışık kodlama var: bazı hücreler UTF-8, bazıları Windows-1254
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError:
        return raw.decode("cp1254", "replace")


def _cell(raw: bytes) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", _decode(raw))).replace("\xa0", " ")
    text = unicodedata.normalize("NFKC", text)  # "ﬁ" gibi bitişik harfleri ayırır
    return re.sub(r"\s+", " ", text).strip()


def parse_range(text: str) -> tuple[date, date] | None:
    """'14 Eylül–02 Ekim 2026', '08-19 Haziran 2026', '19 Haziran 2026' gibi metinleri çözer."""
    t = re.sub(r"\(.*?\)", " ", text).translate(_TR_LOWER).lower()
    t = re.sub(r"\s*[–—-]\s*", " - ", t)
    tokens = re.findall(r"\d+|[a-zçğıöşü]+|-", t)

    parts: list[list] = [[]]
    for tok in tokens:
        if tok == "-":
            parts.append([])
        elif tok.isdigit() or tok in MONTHS:
            parts[-1].append(int(tok) if tok.isdigit() else MONTHS[tok])
    parts = [p for p in parts if p][:2]
    if not parts:
        return None

    def complete(p: list, fallback: list) -> list:
        # [gün], [gün, ay] veya [gün, ay, yıl]; eksikler bitiş tarihinden tamamlanır
        p = p + fallback[len(p):]
        return p if len(p) == 3 else None

    end = parts[-1]
    if len(end) != 3:
        return None
    start = complete(parts[0], end)
    if not start:
        return None
    try:
        s, e = date(start[2], start[1], start[0]), date(end[2], end[1], end[0])
    except ValueError:
        return None
    if s > e:  # "14 Aralık - 14 Ocak 2027" gibi yıl atlayan aralıklar
        s = date(e.year - 1, s.month, s.day)
    return s, e


def extract(page: bytes) -> dict:
    table = re.search(rb"<table.*?</table>", page, re.S | re.I).group()
    events, holidays = [], []
    for row in re.findall(rb"<tr.*?</tr>", table, re.S | re.I):
        cells = [_cell(c) for c in re.findall(rb"<td.*?</td>", row, re.S | re.I)]
        if len(cells) != 3:
            continue
        undergrad, when, graduate = cells
        parsed = parse_range(when)
        if not parsed:
            continue
        start, end = parsed
        name = undergrad or graduate
        item = {"event": name, "date_text": when, "start": start.isoformat(), "end": end.isoformat()}
        if HOLIDAY.search(name):
            holidays.append(item)
        elif undergrad:
            events.append(item)
    return {
        "source": URL,
        "academic_year": "2026-2027",
        "level": "Lisans/Önlisans",
        "events": events,
        "holidays": holidays,
    }


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    raw = urllib.request.urlopen(URL, timeout=30).read()
    data = extract(raw)
    with open(sys.argv[1], "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"{len(data['events'])} etkinlik, {len(data['holidays'])} tatil yazıldı")
