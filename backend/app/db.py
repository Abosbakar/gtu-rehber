"""Öğrenci deneyimlerinin saklandığı SQLite veritabanı.

Deneyimler resmi bilgi değildir; yalnızca yönetici onayından geçenler gösterilir.
Veritabanı dosyası Docker volume'unda durur, konteyner silinse de kaybolmaz.
"""

import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS experiences (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    text TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'approved', 'rejected')),
    confirmations INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_experiences_topic ON experiences (topic, status);
"""

LABEL = "Resmi değil – öğrenci deneyimi"


class ExperienceStore:
    def __init__(self, path: str):
        self.path = path
        Path(path).parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as conn:
            conn.executescript(SCHEMA)

    @contextmanager
    def _connect(self):
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def add(self, topic: str, text: str, status: str = "pending") -> int:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        with self._connect() as conn:
            cur = conn.execute(
                "INSERT INTO experiences (topic, text, status, created_at) VALUES (?, ?, ?, ?)",
                (topic, text, status, now),
            )
            return cur.lastrowid

    def approved(self, topic: str, limit: int = 3) -> list[dict]:
        """Onaylanmış deneyimler; en çok 'ben de yaşadım' alan önce gelir."""
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, text, confirmations, created_at FROM experiences "
                "WHERE topic = ? AND status = 'approved' "
                "ORDER BY confirmations DESC, created_at DESC LIMIT ?",
                (topic, limit),
            ).fetchall()
        return [{**dict(r), "label": LABEL} for r in rows]

    def count(self) -> int:
        with self._connect() as conn:
            return conn.execute("SELECT COUNT(*) FROM experiences").fetchone()[0]
