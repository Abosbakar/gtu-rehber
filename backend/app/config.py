"""Uygulama ayarları. Tüm değerler ortam değişkenlerinden (.env) okunur."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    # Virgülle ayrılmış izinli ön yüz adresleri
    cors_origins: str = "http://localhost:3000"

    # Yerel dil modeli
    model_path: str = "/models/qwen2.5-1.5b-instruct-q4_k_m.gguf"
    llm_threads: int = 0  # 0 = otomatik
    llm_context: int = 4096

    # Veri ve veritabanı
    data_dir: str = "/app/data"
    db_path: str = "/app/db/rehber.db"

    # Yönetici paneli anahtarı
    admin_key: str = ""

    # Boşsa bugünün tarihi kullanılır (YYYY-AA-GG)
    reference_date: str = ""

    debug: bool = False

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
