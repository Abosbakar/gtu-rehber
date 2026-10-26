import { useEffect, useState } from "react";
import { adminDecide, adminList } from "./api.js";

const KEY_STORAGE = "gtu-rehber-yonetici";
const TABS = [
  ["pending", "Onay bekleyenler"],
  ["approved", "Onaylananlar"],
  ["rejected", "Reddedilenler"],
];

function readKey() {
  try {
    return sessionStorage.getItem(KEY_STORAGE) || "";
  } catch {
    return "";
  }
}

export default function Admin() {
  const [key, setKey] = useState(readKey);
  const [input, setInput] = useState("");
  const [tab, setTab] = useState("pending");
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (!key) return;
    setLoading(true);
    setError("");
    adminList(key, tab)
      .then(setItems)
      .catch((err) => {
        setError(err.message);
        if (err.message.includes("anahtar")) logout();
      })
      .finally(() => setLoading(false));
  }, [key, tab]);

  function login(e) {
    e.preventDefault();
    try {
      sessionStorage.setItem(KEY_STORAGE, input);
    } catch {
      /* oturum depolaması kapalıysa anahtar sadece bu sayfada tutulur */
    }
    setKey(input);
  }

  function logout() {
    try {
      sessionStorage.removeItem(KEY_STORAGE);
    } catch {
      /* yok say */
    }
    setKey("");
  }

  async function decide(id, action) {
    try {
      await adminDecide(key, id, action);
      setItems((list) => list.filter((e) => e.id !== id));
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="page">
      <header className="header">
        <div className="brand">
          <img src="/favicon.svg" alt="" width="36" height="36" />
          <div>
            <h1>GTÜ Rehber · Yönetici</h1>
            <p>Öğrenci deneyimlerini onaylama</p>
          </div>
        </div>
      </header>

      <main className="chat">
        {!key ? (
          <form className="card admin-login" onSubmit={login}>
            <h3>Yönetici anahtarı</h3>
            <p className="muted">Anahtar .env dosyasındaki ADMIN_KEY değeridir.</p>
            <input
              type="password"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              aria-label="Yönetici anahtarı"
              autoComplete="current-password"
            />
            <button type="submit" disabled={!input}>
              Giriş
            </button>
            {error && <p className="form-error">{error}</p>}
          </form>
        ) : (
          <>
            <div className="tabs" role="tablist">
              {TABS.map(([id, label]) => (
                <button key={id} type="button" role="tab" aria-selected={tab === id} className={tab === id ? "active" : ""} onClick={() => setTab(id)}>
                  {label}
                </button>
              ))}
              <button type="button" className="ghost logout" onClick={logout}>
                Çıkış
              </button>
            </div>
            {error && <p className="form-error">{error}</p>}
            {loading ? (
              <p className="muted">Yükleniyor…</p>
            ) : items.length === 0 ? (
              <p className="muted">Bu listede deneyim yok.</p>
            ) : (
              items.map((e) => (
                <article key={e.id} className="card admin-item">
                  <div className="topic-line">
                    <span className="badge">{e.topic_name}</span>
                    <span className="level">
                      #{e.id} · {new Date(e.created_at).toLocaleString("tr-TR")}
                      {e.confirmations > 0 && ` · ${e.confirmations} kez "ben de yaşadım"`}
                    </span>
                  </div>
                  <p>{e.text}</p>
                  <div className="form-row">
                    {tab !== "approved" && (
                      <button type="button" onClick={() => decide(e.id, "approve")}>
                        Onayla
                      </button>
                    )}
                    {tab !== "rejected" && (
                      <button type="button" className="ghost" onClick={() => decide(e.id, "reject")}>
                        Reddet
                      </button>
                    )}
                  </div>
                </article>
              ))
            )}
          </>
        )}
      </main>
    </div>
  );
}
