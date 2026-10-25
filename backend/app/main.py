"""GTÜ Rehber arka uç API'si."""

import logging
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from . import assistant
from .config import get_settings
from .db import ExperienceStore
from .deadlines import Calendar
from .llm import LocalLLM
from .search import RegulationIndex

settings = get_settings()
logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger("gtu_rehber")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Belgeler açılışta bir kez okunur ve indekslenir
    app.state.index = RegulationIndex(settings.data_dir)
    app.state.calendar = Calendar.load(Path(settings.data_dir) / "akademik-takvim-2026-2027.json")
    app.state.store = ExperienceStore(settings.db_path)
    # Model arka planda yüklenir; bu sırada API anahtar kelimelerle çalışmaya devam eder
    app.state.llm = LocalLLM(settings.model_path, settings.llm_threads, settings.llm_context)
    app.state.llm.load_in_background()
    yield


app = FastAPI(title="GTÜ Rehber API", version="0.1.0", debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    # Eksik ya da hatalı girdide kullanıcıya anlaşılır Türkçe mesaj döner
    fields = [str(e["loc"][-1]) for e in exc.errors() if isinstance(e["loc"][-1], str) and e["loc"][-1] != "body"]
    message = (
        f"Gönderilen bilgiler eksik ya da hatalı: {', '.join(fields)}."
        if fields
        else "İstek okunamadı. Lütfen geçerli bir JSON gönderin."
    )
    return JSONResponse(status_code=422, content={"error": message})


@app.exception_handler(Exception)
async def unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Beklenmeyen hata", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Beklenmeyen bir hata oluştu. Lütfen biraz sonra tekrar deneyin."},
    )


@app.get("/health")
def health(request: Request) -> dict:
    index: RegulationIndex = request.app.state.index
    return {
        "status": "ok",
        "documents": index.loaded_documents,
        "articles": len(index.chunks),
        "model": request.app.state.llm.status,
        "calendar_events": len(request.app.state.calendar.events),
    }


class AskRequest(BaseModel):
    question: str = Field(min_length=3, max_length=1000)

    @field_validator("question")
    @classmethod
    def not_blank(cls, value: str) -> str:
        value = value.strip()
        if len(value) < 3:
            raise ValueError("Soru en az 3 karakter olmalı")
        return value


@app.post("/ask")
def ask(body: AskRequest, request: Request) -> dict:
    state = request.app.state
    return assistant.answer(body.question, state.index, state.llm, state.calendar, state.store, today())


def today() -> date:
    # Demo ve testlerde sabit bir gün kullanmak için REFERENCE_DATE ayarlanabilir
    return date.fromisoformat(settings.reference_date) if settings.reference_date else date.today()
