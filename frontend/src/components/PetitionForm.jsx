import { useState } from "react";
import { downloadPetition } from "../api.js";

// Konuya göre dilekçede istenen ek alanlar
const FIELDS = {
  mazeret_sinavi: [
    ["course_code", "Ders kodu", "AERO408"],
    ["event_date", "Sınav tarihi", "", "date"],
    ["reason", "Mazeret", "sağlık sorunu"],
  ],
  not_itirazi: [
    ["course_code", "Ders kodu", "MAT101"],
    ["event_date", "Notun ilan tarihi", "", "date"],
  ],
  ders_ekle_birak: [
    ["course_code", "Ders kodu", "CSE101"],
    ["details", "Talebiniz ve gerekçeniz", "dersi bırakmak istiyorum, çünkü…"],
  ],
  kayit_dondurma: [
    ["reason", "Gerekçe", "sağlık sorunu"],
    ["details", "Hangi yarıyıl", "2026-2027 bahar yarıyılında"],
  ],
  staj_basvurusu: [["details", "Staj yeri ve tarihleri", "ABC A.Ş., 6 Temmuz – 31 Temmuz 2027"]],
};

function initialValues(data) {
  const reason = data.extracted?.reason;
  return {
    full_name: "",
    student_no: "",
    department: "",
    phone: "",
    email: "",
    course_code: data.extracted?.course_code || "",
    event_date: data.deadline?.event_date && !data.deadline.event_date_assumed ? data.deadline.event_date : "",
    reason: reason ? reason.toLocaleLowerCase("tr-TR") : "",
    details: "",
  };
}

export default function PetitionForm({ data }) {
  const [values, setValues] = useState(() => initialValues(data));
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");
  const [done, setDone] = useState(false);
  const extra = FIELDS[data.topic.id] || [];

  const set = (key) => (e) => setValues((v) => ({ ...v, [key]: e.target.value }));

  async function submit(e) {
    e.preventDefault();
    setBusy(true);
    setError("");
    try {
      const blob = await downloadPetition({ topic: data.topic.id, ...values });
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `dilekce-${data.topic.id.replaceAll("_", "-")}.pdf`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(url), 1000);
      setDone(true);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <details className="card petition">
      <summary>Dilekçemi hazırla (PDF)</summary>
      <p className="muted">Bilgileriniz kaydedilmez; sadece dilekçeyi oluşturmak için kullanılır.</p>
      <form onSubmit={submit} className="petition-grid">
        <label>
          Ad Soyad
          <input required minLength={3} maxLength={80} value={values.full_name} onChange={set("full_name")} autoComplete="name" />
        </label>
        <label>
          Öğrenci numarası
          <input required pattern="\d{6,12}" inputMode="numeric" title="6-12 haneli numara" value={values.student_no} onChange={set("student_no")} />
        </label>
        <label>
          Bölüm
          <input required minLength={2} maxLength={80} placeholder="Bilgisayar Mühendisliği" value={values.department} onChange={set("department")} />
        </label>
        {extra.map(([key, label, placeholder, type]) => (
          <label key={key} className={key === "details" ? "wide" : ""}>
            {label}
            <input required type={type || "text"} placeholder={placeholder} maxLength={key === "details" ? 400 : 200} value={values[key]} onChange={set(key)} />
          </label>
        ))}
        <label>
          Telefon (isteğe bağlı)
          <input type="tel" maxLength={20} value={values.phone} onChange={set("phone")} autoComplete="tel" />
        </label>
        <label>
          E-posta (isteğe bağlı)
          <input type="email" maxLength={80} value={values.email} onChange={set("email")} autoComplete="email" />
        </label>
        <div className="form-row wide">
          {done ? <small className="ok-text">✓ Dilekçe indirildi. İmzalayıp ilgili birime teslim edin.</small> : <span />}
          <button type="submit" disabled={busy}>
            {busy ? "Hazırlanıyor…" : "PDF indir"}
          </button>
        </div>
        {error && <p className="form-error wide">{error}</p>}
      </form>
    </details>
  );
}
