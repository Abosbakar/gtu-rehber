"""API uç noktası testleri (dil modeli olmadan, geçici veritabanıyla)."""

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
KEY = "test-anahtari"


@pytest.fixture(scope="module")
def client(tmp_path_factory):
    mp = pytest.MonkeyPatch()
    mp.setenv("DATA_DIR", str(DATA_DIR))
    mp.setenv("DB_PATH", str(tmp_path_factory.mktemp("db") / "test.db"))
    mp.setenv("MODEL_PATH", "yok.gguf")
    mp.setenv("ADMIN_KEY", KEY)
    mp.setenv("REFERENCE_DATE", "2026-10-25")
    import app.config

    app.config.get_settings.cache_clear()
    import app.main

    importlib.reload(app.main)
    with TestClient(app.main.app) as c:
        yield c
    mp.undo()
    app.config.get_settings.cache_clear()


def test_health(client):
    body = client.get("/health").json()
    assert body["status"] == "ok" and body["documents"] == 34


def test_ask_mazeret(client):
    body = client.post("/ask", json={"question": "Hastalandım, Pazartesi AERO408 vizesine giremedim"}).json()
    assert body["topic"]["id"] == "mazeret_sinavi"
    assert body["deadline"]["last_day"] == "2026-10-26"
    assert body["sources"][0]["label"].startswith("Madde 29")


def test_hatali_girdi_turkce_mesaj(client):
    res = client.post("/ask", json={"question": " "})
    assert res.status_code == 422 and "error" in res.json()
    assert client.get("/olmayan-adres").json()["error"]


def test_deneyim_akisi(client):
    shared = client.post(
        "/experiences",
        json={"topic": "staj_basvurusu", "text": "Staj için Prof. Dr. Ayşe Yılmaz ile görüştüm, formu aynı gün imzaladı."},
    ).json()
    assert "Ayşe" not in shared["text"] and shared["status"] == "pending"

    # Onaylanmadan görünmez
    assert client.get("/experiences", params={"topic": "staj_basvurusu"}).json() == []

    # Yanlış anahtar reddedilir
    assert client.post(f"/admin/experiences/{shared['id']}/approve", headers={"X-Admin-Key": "yanlis"}).status_code == 401

    pending = client.get("/admin/experiences", headers={"X-Admin-Key": KEY}).json()
    assert [e["id"] for e in pending] == [shared["id"]]
    assert client.post(f"/admin/experiences/{shared['id']}/approve", headers={"X-Admin-Key": KEY}).status_code == 200

    shown = client.get("/experiences", params={"topic": "staj_basvurusu"}).json()
    assert shown[0]["label"].startswith("Resmi değil")

    assert client.post(f"/experiences/{shared['id']}/confirm").json()["confirmations"] == 1


def test_bilinmeyen_konu_reddedilir(client):
    res = client.post("/experiences", json={"topic": "yok", "text": "x" * 30})
    assert res.status_code == 422
