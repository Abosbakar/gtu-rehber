"""Yerel dil modeli (Qwen2.5-1.5B-Instruct, GGUF) sarmalayıcısı.

Model sadece CPU'da, konteynerin içinde çalışır. Açılışta arka planda yüklenir;
yüklenene kadar uygulama dil modeli olmadan (anahtar kelime ve şablonlarla) cevap verir.
"""

import logging
import os
import threading
from pathlib import Path

logger = logging.getLogger("gtu_rehber.llm")


class LocalLLM:
    def __init__(self, model_path: str, threads: int, context: int):
        self.model_path = model_path
        # 0 = otomatik: fiziksel çekirdek sayısı kadar (en fazla 8)
        self.threads = threads or max(1, min(8, (os.cpu_count() or 2) // 2))
        self.context = context
        self.status = "loading"  # loading | ready | unavailable
        self._llama = None
        # llama.cpp aynı anda tek isteği güvenle işler
        self._lock = threading.Lock()

    def load_in_background(self) -> None:
        threading.Thread(target=self._load, daemon=True).start()

    def _load(self) -> None:
        if not Path(self.model_path).exists():
            logger.error("Model dosyası bulunamadı: %s", self.model_path)
            self.status = "unavailable"
            return
        try:
            from llama_cpp import Llama

            self._llama = Llama(
                model_path=self.model_path,
                n_ctx=self.context,
                n_threads=self.threads,
                verbose=False,
            )
            self.status = "ready"
            logger.info("Dil modeli yüklendi: %s", self.model_path)
        except Exception:
            logger.exception("Dil modeli yüklenemedi")
            self.status = "unavailable"

    @property
    def ready(self) -> bool:
        return self.status == "ready"

    def chat(
        self,
        system: str,
        user: str,
        max_tokens: int = 200,
        temperature: float = 0.2,
        choices: list[str] | None = None,
        examples: list[tuple[str, str]] = (),
    ) -> str | None:
        """Modelden cevap alır.

        choices verilirse cevap bu seçeneklerden biri olmak zorundadır.
        examples, modele istenen cevap biçimini gösteren (soru, cevap) çiftleridir.
        """
        if not self.ready:
            return None
        grammar = None
        if choices:
            from llama_cpp import LlamaGrammar

            options = " | ".join(f'"{c}"' for c in choices)
            grammar = LlamaGrammar.from_string(f"root ::= {options}", verbose=False)
        messages = [{"role": "system", "content": system}]
        for question, answer in examples:
            messages += [{"role": "user", "content": question}, {"role": "assistant", "content": answer}]
        messages.append({"role": "user", "content": user})
        try:
            with self._lock:
                result = self._llama.create_chat_completion(
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    repeat_penalty=1.15,
                    grammar=grammar,
                )
            return result["choices"][0]["message"]["content"].strip()
        except Exception:
            logger.exception("Dil modeli cevap üretemedi")
            return None
