"""GTÜ Rehber arka uç API'si."""

import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import get_settings

settings = get_settings()
logging.basicConfig(level=logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger("gtu_rehber")

app = FastAPI(title="GTÜ Rehber API", version="0.1.0", debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
async def validation_error(_: Request, exc: RequestValidationError) -> JSONResponse:
    # Eksik ya da hatalı girdide kullanıcıya anlaşılır Türkçe mesaj döner
    fields = ", ".join(str(e["loc"][-1]) for e in exc.errors())
    return JSONResponse(
        status_code=422,
        content={"error": f"Gönderilen bilgiler eksik ya da hatalı: {fields}."},
    )


@app.exception_handler(Exception)
async def unexpected_error(_: Request, exc: Exception) -> JSONResponse:
    logger.exception("Beklenmeyen hata", exc_info=exc)
    return JSONResponse(
        status_code=500,
        content={"error": "Beklenmeyen bir hata oluştu. Lütfen biraz sonra tekrar deneyin."},
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}
