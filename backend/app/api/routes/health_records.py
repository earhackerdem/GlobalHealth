"""Clinical record book (expediente): diagnoses and prescriptions.

Contract in openspec/changes/expediente-registros/design.md §Interface
contract: everything behind ``ConsentedUser``; per-owner isolation with the
SAME 404 for a nonexistent id and a foreign one; clinical text encrypted at
rest by the model (EncryptedString, NFR-001).
"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from sqlmodel import col, func, select

from app.api.deps import ConsentedUser, SessionDep
from app.models import (
    HealthRecord,
    HealthRecordCreate,
    HealthRecordPublic,
    HealthRecordsPublic,
    HealthRecordUpdate,
    Message,
    get_datetime_utc,
)

router = APIRouter(prefix="/health-records", tags=["health-records"])


def _get_owned_record(
    session: SessionDep, current_user: ConsentedUser, id: uuid.UUID
) -> HealthRecord:
    """Fetch a record only if owned by the session user.

    A missing record and a foreign record raise the SAME 404 so the
    endpoint never reveals whether someone else's record exists.
    """
    record = session.get(HealthRecord, id)
    if not record or record.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return record


@router.post("/", response_model=HealthRecordPublic, status_code=201)
def create_health_record(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    record_in: HealthRecordCreate,
) -> Any:
    """Persist a clinical record owned by the session user (consent required)."""
    record = HealthRecord.model_validate(
        record_in, update={"owner_id": current_user.id}
    )
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.get("/", response_model=HealthRecordsPublic)
def read_health_records(
    session: SessionDep, current_user: ConsentedUser, skip: int = 0, limit: int = 100
) -> Any:
    """List ONLY the session user's records, newest ``occurred_on`` first
    (template envelope {"data": [...], "count": N}, like items)."""
    count_statement = (
        select(func.count())
        .select_from(HealthRecord)
        .where(HealthRecord.owner_id == current_user.id)
    )
    count = session.exec(count_statement).one()
    records = session.exec(
        select(HealthRecord)
        .where(HealthRecord.owner_id == current_user.id)
        .order_by(col(HealthRecord.occurred_on).desc())
        .offset(skip)
        .limit(limit)
    ).all()
    records_public = [HealthRecordPublic.model_validate(record) for record in records]
    return HealthRecordsPublic(data=records_public, count=count)


@router.get("/{id}", response_model=HealthRecordPublic)
def read_health_record(
    session: SessionDep, current_user: ConsentedUser, id: uuid.UUID
) -> Any:
    """Get one record by id, only if owned by the session user."""
    return _get_owned_record(session, current_user, id)


@router.patch("/{id}", response_model=HealthRecordPublic)
def update_health_record(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    record_in: HealthRecordUpdate,
) -> Any:
    """Partial update of an owned record; ``record_type`` is immutable."""
    record = _get_owned_record(session, current_user, id)
    update_dict = record_in.model_dump(exclude_unset=True)
    record.sqlmodel_update(update_dict)
    record.updated_at = get_datetime_utc()
    session.add(record)
    session.commit()
    session.refresh(record)
    return record


@router.delete("/{id}")
def delete_health_record(
    session: SessionDep, current_user: ConsentedUser, id: uuid.UUID
) -> Message:
    """Delete an owned record (cancelación ARCO)."""
    record = _get_owned_record(session, current_user, id)
    session.delete(record)
    session.commit()
    return Message(message="Registro eliminado")
