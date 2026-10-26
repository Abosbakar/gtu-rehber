import { useState } from "react";
import { confirmExperience, shareExperience } from "../api.js";

const CONFIRMED_KEY = "gtu-rehber-onaylananlar";

// Aynı tarayıcıdan iki kez "ben de yaşadım" denmesin diye (tarayıcı izin vermezse sessizce geçilir)
function loadConfirmed() {
  try {
    return new Set(JSON.parse(localStorage.getItem(CONFIRMED_KEY) || "[]"));
  } catch {
    return new Set();
  }
}

function saveConfirmed(set) {
  try {
    localStorage.setItem(CONFIRMED_KEY, JSON.stringify([...set]));
  } catch {
    /* depolama kapalıysa sayaç yine de sunucuda artar */
  }
}

export function ExperienceList({ items }) {
  const [counts, setCounts] = useState(() => Object.fromEntries(items.map((e) => [e.id, e.confirmations])));
  const [confirmed, setConfirmed] = useState(loadConfirmed);
  const [error, setError] = useState("");

  async function confirm(id) {
    setError("");
    try {
      const res = await confirmExperience(id);
      setCounts((c) => ({ ...c, [id]: res.confirmations }));
      const next = new Set(confirmed).add(id);
      setConfirmed(next);
      saveConfirmed(next);
    } catch (err) {
      setError(err.message);
    }
  }

  if (!items.length) return null;
  return (
    <section className="card experiences">
      <h3>Diğer öğrencilerin deneyimleri</h3>
      {items.map((e) => (
        <blockquote key={e.id}>
          <span className="unofficial">{e.label}</span>
          <p>{e.text}</p>
          <div className="confirm-row">
            <button type="button" className="ghost" disabled={confirmed.has(e.id)} onClick={() => confirm(e.id)}>
              {confirmed.has(e.id) ? "✓ Teşekkürler" : "Ben de yaşadım"}
            </button>
            {counts[e.id] > 0 && <small>{counts[e.id]} öğrenci "ben de yaşadım" dedi</small>}
          </div>
        </blockquote>
      ))}
      {error && <p className="form-error">{error}</p>}
    </section>
  );
}

export function ShareExperience({ topic }) {
  const [text, setText] = useState("");
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      setResult(await shareExperience(topic.id, text));
      setText("");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <details className="card share">
      <summary>Bu durumu yaşadınız mı? Deneyiminizi paylaşın</summary>
      {result ? (
        <div className="share-result">
          <p>{result.message}</p>
          <p className="muted">Kaydedilen hali: “{result.text}”</p>
        </div>
      ) : (
        <form onSubmit={submit}>
          <p className="muted">
            Kişi adları, telefon ve öğrenci numaraları kaydedilmeden önce otomatik silinir. Paylaşımınız yönetici
            onayından sonra "resmi değil" etiketiyle gösterilir.
          </p>
          <textarea
            value={text}
            onChange={(e) => setText(e.target.value)}
            rows={3}
            minLength={20}
            maxLength={1500}
            placeholder="Örn. Raporumu e-Nabız çıktısıyla teslim ettim, bölüm sekreterliği aynı gün kabul etti."
            aria-label="Deneyiminiz"
          />
          <div className="form-row">
            <small className="muted">{text.trim().length}/1500</small>
            <button type="submit" disabled={busy || text.trim().length < 20}>
              {busy ? "Gönderiliyor…" : "Paylaş"}
            </button>
          </div>
          {error && <p className="form-error">{error}</p>}
        </form>
      )}
    </details>
  );
}
