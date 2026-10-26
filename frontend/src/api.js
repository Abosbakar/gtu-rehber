// API adresi derleme sırasında VITE_API_URL ile verilir (varsayılan: http://localhost:8000)
export const API_URL = (import.meta.env.VITE_API_URL || "http://localhost:8000").replace(/\/$/, "");

export async function ask(question) {
  const res = await fetch(`${API_URL}/ask`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ question }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || "Bir hata oluştu.");
  return data;
}
