"""Clinical record book (expediente): diagnoses and prescriptions.

Contract in openspec/changes/expediente-registros/design.md §Interface
contract: everything behind ``ConsentedUser``; per-owner isolation with the
SAME 404 for a nonexistent id and a foreign one; clinical text encrypted at
rest by the model (EncryptedString, NFR-001).
"""

import uuid
from typing import Any

from fastapi import APIRouter, HTTPException, Response, UploadFile
from sqlmodel import col, func, select

from app.api.deps import ConsentedUser, SessionDep
from app.models import (
    HealthRecord,
    HealthRecordAttachment,
    HealthRecordAttachmentPublic,
    HealthRecordAttachmentsPublic,
    HealthRecordCreate,
    HealthRecordPublic,
    HealthRecordsPublic,
    HealthRecordUpdate,
    Message,
    get_datetime_utc,
)

router = APIRouter(prefix="/health-records", tags=["health-records"])

# Attachment validation contract (design.md §Interface contract): whitelist
# verified by MAGIC BYTES of the content matching the declared content-type,
# never by the declared type alone (a renamed .exe gets a 415).
_ALLOWED_MAGIC: dict[str, bytes] = {
    "application/pdf": b"%PDF",
    "image/jpeg": b"\xff\xd8",
    "image/png": b"\x89PNG\r\n\x1a\n",
}
_MAX_ATTACHMENT_BYTES = 10 * 1024 * 1024  # inclusive: exactly 10 MB passes


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


def _get_owned_attachment(
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    attachment_id: uuid.UUID,
) -> HealthRecordAttachment:
    """Fetch an attachment only through an owned record.

    A missing or foreign RECORD keeps the record-level 404 (indistinguishable
    from nonexistent); a missing attachment on an own record gets its own 404.
    """
    record = _get_owned_record(session, current_user, id)
    attachment = session.get(HealthRecordAttachment, attachment_id)
    if not attachment or attachment.record_id != record.id:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    return attachment


@router.post(
    "/{id}/attachments",
    response_model=HealthRecordAttachmentPublic,
    status_code=201,
)
def create_health_record_attachment(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    file: UploadFile,
) -> Any:
    """Attach a file to an owned record (multipart field ``file``).

    Type verified by magic bytes against the declared content-type within
    the whitelist (415 otherwise); size limited to 10 MB inclusive (413).
    """
    record = _get_owned_record(session, current_user, id)
    content = file.file.read()
    magic = _ALLOWED_MAGIC.get(file.content_type or "")
    if magic is None or not content.startswith(magic):
        raise HTTPException(
            status_code=415,
            detail="Tipo de archivo no permitido (solo PDF, JPEG o PNG)",
        )
    if len(content) > _MAX_ATTACHMENT_BYTES:
        raise HTTPException(
            status_code=413, detail="El archivo excede el límite de 10 MB"
        )
    attachment = HealthRecordAttachment(
        record_id=record.id,
        filename=file.filename or "archivo",
        media_type=file.content_type or "",
        size_bytes=len(content),
        content=content,
    )
    session.add(attachment)
    session.commit()
    session.refresh(attachment)
    return attachment


@router.get("/{id}/attachments", response_model=HealthRecordAttachmentsPublic)
def read_health_record_attachments(
    session: SessionDep, current_user: ConsentedUser, id: uuid.UUID
) -> Any:
    """List the attachments of an owned record (envelope {"data", "count"})."""
    record = _get_owned_record(session, current_user, id)
    attachments = session.exec(
        select(HealthRecordAttachment)
        .where(HealthRecordAttachment.record_id == record.id)
        .order_by(col(HealthRecordAttachment.created_at).asc())
    ).all()
    return HealthRecordAttachmentsPublic(
        data=[
            HealthRecordAttachmentPublic.model_validate(attachment)
            for attachment in attachments
        ],
        count=len(attachments),
    )


@router.get("/{id}/attachments/{attachment_id}")
def download_health_record_attachment(
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    attachment_id: uuid.UUID,
) -> Response:
    """Download the original bytes with the stored media type and filename."""
    attachment = _get_owned_attachment(session, current_user, id, attachment_id)
    return Response(
        content=attachment.content,
        media_type=attachment.media_type,
        headers={
            "Content-Disposition": f'attachment; filename="{attachment.filename}"'
        },
    )


@router.delete("/{id}/attachments/{attachment_id}")
def delete_health_record_attachment(
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    attachment_id: uuid.UUID,
) -> Message:
    """Delete one attachment of an owned record."""
    attachment = _get_owned_attachment(session, current_user, id, attachment_id)
    session.delete(attachment)
    session.commit()
    return Message(message="Adjunto eliminado")
