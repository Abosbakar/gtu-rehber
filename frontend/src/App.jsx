import { useEffect, useRef, useState } from "react";
import { ask } from "./api.js";

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
  const endRef = useRef(null);

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
            <div key={i} className="bubble assistant">
              {m.data.topic && <span className="badge">{m.data.topic.name}</span>}
              <p>{m.data.answer}</p>
            </div>
          ),
        )}
        {busy && <div className="bubble assistant">Cevap hazırlanıyor…</div>}
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
