"""Minimal health-records router to exercise ``require_consent``.

Stub fixed in design.md §Interface contract (T3): it proves the consent
barrier and per-owner isolation end to end. E2 replaces it with the real
clinical records; keep the ``require_consent`` dependency when it does.
"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import select

from app.api.deps import ConsentedUser, SessionDep
from app.models import HealthRecordCreate, HealthRecordPublic, HealthRecordStub

router = APIRouter(prefix="/health-records", tags=["health-records"])


@router.post("", response_model=HealthRecordPublic, status_code=201)
def create_health_record(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    record_in: HealthRecordCreate,
) -> Any:
    """Persist a health-record stub owned by the session user (consent required)."""
    record = HealthRecordStub.model_validate(
        record_in, update={"owner_id": current_user.id}
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("", response_model=list[HealthRecordPublic])
def read_health_records(session: SessionDep, current_user: ConsentedUser) -> Any:
    """List ONLY the health-record stubs owned by the session user."""
    records = session.exec(
        select(HealthRecordStub).where(HealthRecordStub.owner_id == current_user.id)
    ).all()
    return records


@router.get("/{id}", response_model=HealthRecordPublic)
def read_health_record(
    session: SessionDep, current_user: ConsentedUser, id: uuid.UUID
) -> Any:
    """Get one health-record stub by id, only if owned by the session user.

    A missing record and a foreign record return the SAME 404 so the
    endpoint never reveals whether someone else's record exists.
    """
    record = session.get(HealthRecordStub, id)
    if not record or record.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Health record not found")
    return record
