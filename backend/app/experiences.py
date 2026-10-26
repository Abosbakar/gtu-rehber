"""Öğrenci deneyimi paylaşma ve yönetici onayı uç noktaları.

Paylaşımlar kayıttan önce anonimleştirilir ve "onay bekliyor" durumunda saklanır;
sadece yöneticinin onayladıkları öğrencilere gösterilir.
"""

import secrets
from typing import Literal

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel, Field, field_validator

from .anonymize import anonymize
from .db import ExperienceStore
from .topics import TOPICS_BY_ID

router = APIRouter()


class ExperienceIn(BaseModel):
    topic: str
    text: str = Field(min_length=20, max_length=1500)

    @field_validator("topic")
    @classmethod
    def known_topic(cls, value: str) -> str:
        if value not in TOPICS_BY_ID:
            raise ValueError("Bilinmeyen konu")
        return value

    @field_validator("text")
    @classmethod
    def strip_text(cls, value: str) -> str:
        value = " ".join(value.split())
        if len(value) < 20:
            raise ValueError("Deneyim en az 20 karakter olmalı")
        return value


def _store(request: Request) -> ExperienceStore:
    return request.app.state.store


def _public(exp: dict) -> dict:
    topic = TOPICS_BY_ID.get(exp["topic"])
    return {**exp, "topic_name": topic.name if topic else exp["topic"]}


def _check_admin(request: Request, key: str | None) -> None:
    expected = request.app.state.admin_key
    if not key or not secrets.compare_digest(key, expected):
        raise HTTPException(status_code=401, detail="Yönetici anahtarı hatalı.")


@router.post("/experiences")
def share(body: ExperienceIn, request: Request) -> dict:
    cleaned, removed = anonymize(body.text, request.app.state.llm)
    exp_id = _store(request).add(body.topic, cleaned)
    return {
        "id": exp_id,
        "status": "pending",
        "text": cleaned,
        "removed_names": removed,
        "message": "Teşekkürler! Deneyiminiz kişisel bilgilerden arındırıldı ve yönetici onayından sonra yayınlanacak.",
    }


@router.get("/experiences")
def list_approved(request: Request, topic: str) -> list[dict]:
    if topic not in TOPICS_BY_ID:
        raise HTTPException(status_code=404, detail="Bilinmeyen konu.")
    return _store(request).approved(topic, limit=10)


@router.post("/experiences/{exp_id}/confirm")
def confirm(exp_id: int, request: Request) -> dict:
    count = _store(request).confirm(exp_id)
    if count is None:
        raise HTTPException(status_code=404, detail="Deneyim bulunamadı.")
    return {"id": exp_id, "confirmations": count}


@router.get("/admin/experiences")
def admin_list(
    request: Request,
    status: Literal["pending", "approved", "rejected"] = "pending",
    x_admin_key: str | None = Header(default=None),
) -> list[dict]:
    _check_admin(request, x_admin_key)
    return [_public(e) for e in _store(request).by_status(status)]


@router.post("/admin/experiences/{exp_id}/{action}")
def admin_decide(
    exp_id: int,
    action: Literal["approve", "reject"],
    request: Request,
    x_admin_key: str | None = Header(default=None),
) -> dict:
    _check_admin(request, x_admin_key)
    status = "approved" if action == "approve" else "rejected"
    if not _store(request).set_status(exp_id, status):
        raise HTTPException(status_code=404, detail="Deneyim bulunamadı.")
    return {"id": exp_id, "status": status}
