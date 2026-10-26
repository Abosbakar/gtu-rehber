// API adresi derleme sırasında VITE_API_URL ile verilir (varsayılan: http://localhost:8000)
export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

const TIMEOUT_MS = 90_000;

async function request(path, options = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  let res;
  try {
    res = await fetch(`${API_URL}${path}`, { ...options, signal: controller.signal });
  } catch (err) {
    if (err.name === "AbortError") {
      throw new Error("Cevap çok uzun sürdü. Lütfen biraz sonra tekrar deneyin.");
    }
    throw new Error("Sunucuya ulaşılamadı. Uygulamanın çalıştığından emin olup tekrar deneyin.");
  } finally {
    clearTimeout(timer);
  }
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.error || "Beklenmeyen bir hata oluştu.");
  return data;
}

export function ask(question) {
  return request("/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
}

export function health() {
  return request("/health");
}
