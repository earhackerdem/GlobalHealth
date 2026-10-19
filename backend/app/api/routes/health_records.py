"""Clinical record book (expediente): diagnoses and prescriptions.

Contract in openspec/changes/receta-mexicana/design.md §Interface contract
(remodel of expediente-registros): everything behind ``ConsentedUser``;
per-owner isolation with the SAME 404 for a nonexistent id and a foreign
one; clinical text encrypted at rest by the model (EncryptedString,
NFR-001). A prescription carries ``medicines`` 1..N (child table, capture
order); PATCH with ``medicines`` present REPLACES the whole list; the
resultant state is validated by the shared discriminated helper and any
violation surfaces as a 422 with a STRING detail in es-MX.
"""

import urllib.parse
import uuid
from typing import Any, cast

from fastapi import APIRouter, HTTPException, Response, UploadFile
from sqlalchemy.orm import InstrumentedAttribute, load_only
from sqlmodel import col, delete, func, select

from app.api.deps import ConsentedUser, SessionDep
from app.models import (
    HealthRecord,
    HealthRecordAttachment,
    HealthRecordAttachmentPublic,
    HealthRecordAttachmentsPublic,
    HealthRecordCreate,
    HealthRecordMedicine,
    HealthRecordMedicineCreate,
    HealthRecordPublic,
    HealthRecordsPublic,
    HealthRecordUpdate,
    Message,
    get_datetime_utc,
    reject_legacy_health_record_fields,
    reject_null_update_fields,
    validate_health_record_fields_by_type,
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


def _build_medicines(
    medicines_in: list[HealthRecordMedicineCreate],
) -> list[HealthRecordMedicine]:
    """Child rows in capture order: ``position`` = arrival index."""
    return [
        HealthRecordMedicine(
            position=position,
            name=medicine.name,
            dose=medicine.dose,
            frequency=medicine.frequency,
            route=medicine.route,
        )
        for position, medicine in enumerate(medicines_in)
    ]


@router.post("/", response_model=HealthRecordPublic, status_code=201)
def create_health_record(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    record_in: HealthRecordCreate,
) -> Any:
    """Persist a clinical record owned by the session user (consent required).

    The discriminated validation runs HERE (not in a pydantic validator) so
    the 422 carries a string es-MX detail: a legacy payload (record-level
    dose/validity) is rejected by name; a diagnosis requires a title and no
    medicines; a prescription requires 1..N medicines and no title.
    """
    try:
        reject_legacy_health_record_fields(
            record_in.dose, record_in.valid_from, record_in.valid_to
        )
        validate_health_record_fields_by_type(
            record_in.record_type,
            record_in.title,
            record_in.diagnosis,
            [medicine.name for medicine in record_in.medicines],
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    record = HealthRecord(
        owner_id=current_user.id,
        record_type=record_in.record_type,
        occurred_on=record_in.occurred_on,
        title=record_in.title,
        professional=record_in.professional,
        diagnosis=record_in.diagnosis,
        notes=record_in.notes,
        # Informational only (no confirmation flow yet): a diagnosis is born
        # "unconfirmed"; a prescription carries no status.
        confirmation_status=(
            "unconfirmed" if record_in.record_type == "diagnosis" else None
        ),
        medicines=_build_medicines(record_in.medicines),
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
    """Partial update of an owned record; ``record_type`` is immutable.

    ``medicines`` present = FULL replacement of the list (delete + insert,
    Decision 2 of receta-mexicana design.md); ``archived`` archives or
    unarchives. The RESULTANT state after applying the partial update must
    satisfy the same discriminated contract as the Create (finding A1 of
    the adversarial review), raised as an HTTP 422 with the same es-MX
    string detail. ``confirmation_status`` has no operation to change it:
    the field is not part of the Update schema and gets ignored.
    """
    record = _get_owned_record(session, current_user, id)
    update_dict = record_in.model_dump(exclude_unset=True)
    replacement = update_dict.pop("medicines", None)
    try:
        reject_legacy_health_record_fields(
            record_in.dose, record_in.valid_from, record_in.valid_to
        )
        for legacy_field in ("dose", "valid_from", "valid_to"):
            update_dict.pop(legacy_field, None)
        # Explicit null on a NOT NULL column would be a 500 at flush time
        # (finding S3): reject it here as the same es-MX 422.
        reject_null_update_fields(update_dict)
        resultant_names = (
            [medicine["name"] for medicine in replacement]
            if replacement is not None
            else [medicine.name for medicine in record.medicines]
        )
        validate_health_record_fields_by_type(
            record.record_type,
            update_dict.get("title", record.title),
            update_dict.get("diagnosis", record.diagnosis),
            resultant_names,
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    record.sqlmodel_update(update_dict)
    if replacement is not None:
        # delete-orphan on the relationship removes the previous rows.
        record.medicines = _build_medicines(
            [HealthRecordMedicineCreate(**medicine) for medicine in replacement]
        )
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


def _check_owned_attachment(
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    attachment_id: uuid.UUID,
) -> None:
    """Validate that the attachment hangs from an owned record.

    A missing or foreign RECORD keeps the record-level 404 (indistinguishable
    from nonexistent); a missing attachment on an own record gets its own 404.
    The check queries a LIGHT projection (id/record_id) so it never
    materializes ``content`` (EncryptedBytes): decrypting before the
    ownership check is both a timing oracle and a per-request cost
    (finding A3 of the adversarial review). Callers load the full row only
    after this check, and only when they need the bytes.
    """
    record = _get_owned_record(session, current_user, id)
    owner_record_id = session.exec(
        select(HealthRecordAttachment.record_id).where(
            HealthRecordAttachment.id == attachment_id
        )
    ).first()
    if owner_record_id is None or owner_record_id != record.id:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")


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
    # Pre-check before reading the body into memory (finding C3): when the
    # multipart layer knows the size, reject oversize uploads without the
    # read. file.size can be None, so the post-read check below stays.
    if file.size is not None and file.size > _MAX_ATTACHMENT_BYTES:
        raise HTTPException(
            status_code=413, detail="El archivo excede el límite de 10 MB"
        )
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
    """List the attachments of an owned record (envelope {"data", "count"}).

    Selects ONLY the public columns: loading full rows would decrypt every
    ``content`` (EncryptedBytes) just to return metadata (finding A3).
    ``filename`` is EncryptedString and does get decrypted — that one is cheap.
    """
    record = _get_owned_record(session, current_user, id)
    public_columns = [
        cast("InstrumentedAttribute[Any]", column)
        for column in (
            HealthRecordAttachment.id,
            HealthRecordAttachment.record_id,
            HealthRecordAttachment.filename,
            HealthRecordAttachment.media_type,
            HealthRecordAttachment.size_bytes,
            HealthRecordAttachment.created_at,
        )
    ]
    rows = session.exec(
        select(HealthRecordAttachment)
        .where(HealthRecordAttachment.record_id == record.id)
        .order_by(col(HealthRecordAttachment.created_at).asc())
        .options(load_only(*public_columns))
    ).all()
    return HealthRecordAttachmentsPublic(
        data=[HealthRecordAttachmentPublic.model_validate(row) for row in rows],
        count=len(rows),
    )


@router.get("/{id}/attachments/{attachment_id}")
def download_health_record_attachment(
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    attachment_id: uuid.UUID,
) -> Response:
    """Download the original bytes with the stored media type and filename.

    Content-Disposition per RFC 6266/5987 (finding A2): an ASCII fallback
    ``filename`` (non-ASCII replaced, quote/backslash escaped — a raw name
    broke the latin-1 header encoding with a 500) plus ``filename*`` with
    the real UTF-8 name percent-encoded. ``nosniff`` per finding C1.
    """
    _check_owned_attachment(session, current_user, id, attachment_id)
    attachment = session.get(HealthRecordAttachment, attachment_id)
    if attachment is None:
        raise HTTPException(status_code=404, detail="Adjunto no encontrado")
    ascii_fallback = (
        attachment.filename.encode("ascii", errors="replace")
        .decode("ascii")
        .replace("\\", "\\\\")
        .replace('"', '\\"')
    )
    utf8_name = urllib.parse.quote(attachment.filename, safe="")
    return Response(
        content=attachment.content,
        media_type=attachment.media_type,
        headers={
            "Content-Disposition": (
                f'attachment; filename="{ascii_fallback}"; '
                f"filename*=UTF-8''{utf8_name}"
            ),
            "X-Content-Type-Options": "nosniff",
        },
    )


@router.delete("/{id}/attachments/{attachment_id}")
def delete_health_record_attachment(
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    attachment_id: uuid.UUID,
) -> Message:
    """Delete one attachment of an owned record.

    Deletes by id without materializing the row: loading it would decrypt
    ``content`` only to throw it away (finding A3).
    """
    _check_owned_attachment(session, current_user, id, attachment_id)
    session.exec(
        delete(HealthRecordAttachment).where(
            col(HealthRecordAttachment.id) == attachment_id
        )
    )
    session.commit()
    return Message(message="Adjunto eliminado")
