import { useEffect, useRef, useState } from "react";
import { ask, health } from "./api.js";
import AnswerCard from "./components/AnswerCard.jsx";
import Loading from "./components/Loading.jsx";

const EXAMPLES = [
  "Hastalandım, Pazartesi AERO408 vizesine giremedim",
  "Notuma itiraz etmek istiyorum",
  "Bu dönem kaydımı dondurmak istiyorum",
  "Bilgisayar mühendisliğinde staj başvurusu nasıl yapılır?",
];

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const [status, setStatus] = useState(null); // /health cevabı ya da "offline"
  const endRef = useRef(null);

  // Model yüklenene kadar durumu birkaç saniyede bir kontrol et
  useEffect(() => {
    let timer;
    const check = () =>
      health()
        .then((h) => {
          setStatus(h);
          if (h.model === "loading") timer = setTimeout(check, 3000);
        })
        .catch(() => {
          setStatus("offline");
          timer = setTimeout(check, 5000);
        });
    check();
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, busy]);

  async function send(text) {
    const question = text.trim();
    if (!question || busy) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setBusy(true);
    try {
      const data = await ask(question);
      setMessages((m) => [...m, { role: "assistant", data }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "error", text: err.message }]);
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="page">
      <header className="header">
        <div className="brand">
          <img src="/favicon.svg" alt="" width="36" height="36" />
          <div>
            <h1>GTÜ Rehber</h1>
            <p>Yönetmelik, akademik takvim ve dilekçe asistanı</p>
          </div>
        </div>
      </header>

      {status === "offline" && (
        <div className="banner error">Sunucuya ulaşılamıyor. Arka uç başlatılıyor olabilir, birkaç saniye içinde tekrar denenecek.</div>
      )}
      {status?.model === "loading" && (
        <div className="banner">Yapay zekâ modeli yükleniyor; bu sırada cevaplar yalnızca kurallarla hazırlanır.</div>
      )}
      {status?.model === "unavailable" && (
        <div className="banner">Yapay zekâ modeli kullanılamıyor; cevaplar yalnızca kurallarla hazırlanıyor.</div>
      )}

      <main className="chat">
        {messages.length === 0 && (
          <section className="welcome">
            <h2>Durumunuzu yazın, ne yapmanız gerektiğini birlikte bulalım.</h2>
            <p>Örnek sorular:</p>
            <div className="examples">
              {EXAMPLES.map((e) => (
                <button key={e} type="button" onClick={() => send(e)}>
                  {e}
                </button>
              ))}
            </div>
          </section>
        )}

        {messages.map((m, i) =>
          m.role === "user" ? (
            <div key={i} className="bubble user">{m.text}</div>
          ) : m.role === "error" ? (
            <div key={i} className="bubble error">{m.text}</div>
          ) : (
            <AnswerCard key={i} data={m.data} />
          ),
        )}
        {busy && <Loading />}
        <div ref={endRef} />
      </main>

      <form
        className="composer"
        onSubmit={(e) => {
          e.preventDefault();
          send(input);
        }}
      >
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === "Enter" && !e.shiftKey) {
              e.preventDefault();
              send(input);
            }
          }}
          placeholder="Örn. Hastalandım, vizeye giremedim…"
          rows={2}
          maxLength={1000}
          aria-label="Sorunuz"
        />
        <button type="submit" disabled={busy || input.trim().length < 3}>
          Gönder
        </button>
      </form>
    </div>
  );
}
