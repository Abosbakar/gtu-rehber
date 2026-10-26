import { useEffect, useState } from "react";

const STEPS = [
  "Durumunuz anlaşılıyor…",
  "Yönetmelikte ilgili madde aranıyor…",
  "Akademik takvime göre süre hesaplanıyor…",
  "Cevap hazırlanıyor…",
];

export default function Loading() {
  const [seconds, setSeconds] = useState(0);

  useEffect(() => {
    const id = setInterval(() => setSeconds((s) => s + 1), 1000);
    return () => clearInterval(id);
  }, []);

  const step = STEPS[Math.min(Math.floor(seconds / 2), STEPS.length - 1)];
  return (
    <div className="bubble assistant loading" role="status" aria-live="polite">
      <span className="dots" aria-hidden="true">
        <i />
        <i />
        <i />
      </span>
      <span>{step}</span>
      <span className="elapsed">{seconds} sn</span>
    </div>
  );
}
