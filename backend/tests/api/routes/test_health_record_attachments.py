"""Tests for clinical record attachments (expediente-registros, US-04, grupo 2).

Contract (openspec/changes/expediente-registros/design.md §Interface contract):
- POST /api/v1/health-records/{id}/attachments — multipart field ``file``
  (filename + declared content-type) -> 201 {id, record_id, filename,
  media_type, size_bytes, created_at} (no content in the body). Allowed types
  application/pdf, image/jpeg, image/png verified by MAGIC BYTES of the
  content (%PDF, \xff\xd8, \x89PNG\r\n\x1a\n), not by the declared
  content-type -> otherwise 415 {"detail": "Tipo de archivo no permitido
  (solo PDF, JPEG o PNG)"}. Size limit 10 MB inclusive (10 * 1024 * 1024
  bytes; exactly 10 MB passes) -> above it 413 {"detail": "El archivo excede
  el límite de 10 MB"}.
- GET /api/v1/health-records/{id}/attachments -> {"data": [...], "count": N}
  only for the owner's record.
- GET /api/v1/health-records/{id}/attachments/{attachment_id} -> 200, body =
  the original bytes, content-type = stored media_type, content-disposition
  carrying the filename.
- DELETE /api/v1/health-records/{id}/attachments/{attachment_id} -> 200
  {"message": "Adjunto eliminado"}.
- Nonexistent or foreign record on ANY of these -> 404
  {"detail": "Registro no encontrado"}; missing attachment on an own record
  -> 404 {"detail": "Adjunto no encontrado"}.
- Attachments encrypted at rest in table ``health_record_attachment``; deleting
  the record cascades over its attachment rows.

Spec: openspec/changes/expediente-registros/specs/records/clinical-records/spec.md
(attachments requirement).
"""

import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app.core.config import settings
from tests.api.routes.test_health_records import (
    consented_user_headers,
    diagnosis_payload,
    post_record,
    user_without_consent_headers,
)

TEN_MB = 10 * 1024 * 1024

PDF_BYTES = (
    b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\n"
    b"perfil tiroideo: TSH 6.8, T4 libre 0.9\n%%EOF"
)
EXE_BYTES = b"MZ\x90\x00\x03\x00\x00\x00\x04\x00\x00\x00\xff\xff" + b"\x00" * 64


def attachments_url(record_id: Any) -> str:
    return f"{settings.API_V1_STR}/health-records/{record_id}/attachments"


def attachment_url(record_id: Any, attachment_id: Any) -> str:
    return f"{attachments_url(record_id)}/{attachment_id}"


def own_diagnosis(client: TestClient, db: Session) -> tuple[dict[str, str], str]:
    """Fresh consented user with one diagnosis record of their own."""
    headers = consented_user_headers(client, db)
    r = post_record(client, headers, diagnosis_payload())
    assert r.status_code == 201, r.text
    return headers, r.json()["id"]


def upload(
    client: TestClient,
    headers: dict[str, str],
    record_id: Any,
    filename: str,
    content: bytes,
    content_type: str,
) -> Any:
    return client.post(
        attachments_url(record_id),
        headers=headers,
        files={"file": (filename, content, content_type)},
    )


# --- Scenario 1: Adjuntar y descargar un PDF ----------------------------------


def test_ac1_attach_pdf_returns_metadata_lists_and_downloads_identical_bytes(
    client: TestClient, db: Session
) -> None:
    """Attach perfil-tiroideo.pdf: 201 metadata, listed, download = same bytes."""
    headers, record_id = own_diagnosis(client, db)

    r = upload(
        client, headers, record_id, "perfil-tiroideo.pdf", PDF_BYTES, "application/pdf"
    )

    assert r.status_code == 201, r.text
    meta = r.json()
    assert meta["id"]
    assert str(meta["record_id"]) == str(record_id)
    assert meta["filename"] == "perfil-tiroideo.pdf"
    assert meta["media_type"] == "application/pdf"
    assert meta["size_bytes"] == len(PDF_BYTES)
    assert meta["created_at"]
    # Metadata only: the response never carries the content itself.
    assert "content" not in meta
    assert "%PDF" not in r.text
    attachment_id = meta["id"]

    # The attachment shows up when listing the record's attachments.
    r_list = client.get(attachments_url(record_id), headers=headers)
    assert r_list.status_code == 200, r_list.text
    body = r_list.json()
    assert body["count"] == 1
    assert len(body["data"]) == 1
    listed = body["data"][0]
    assert str(listed["id"]) == str(attachment_id)
    assert listed["filename"] == "perfil-tiroideo.pdf"
    assert listed["media_type"] == "application/pdf"

    # Download returns bytes IDENTICAL to the upload, as application/pdf.
    r_down = client.get(attachment_url(record_id, attachment_id), headers=headers)
    assert r_down.status_code == 200
    assert r_down.content == PDF_BYTES
    assert r_down.headers["content-type"] == "application/pdf"
    assert "perfil-tiroideo.pdf" in r_down.headers["content-disposition"]


# --- Scenario 2: Tipo o tamaño fuera de contrato se rechaza --------------------


def test_ac2_renamed_exe_is_rejected_415_and_nothing_persists(
    client: TestClient, db: Session
) -> None:
    """MZ bytes declared as application/pdf: 415 by magic bytes, list unchanged."""
    headers, record_id = own_diagnosis(client, db)

    r = upload(
        client, headers, record_id, "resultados.pdf", EXE_BYTES, "application/pdf"
    )

    assert r.status_code == 415, r.text
    assert r.json() == {"detail": "Tipo de archivo no permitido (solo PDF, JPEG o PNG)"}

    r_list = client.get(attachments_url(record_id), headers=headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
    assert r_list.json()["data"] == []


def test_ac2_file_over_10mb_is_rejected_413_and_nothing_persists(
    client: TestClient, db: Session
) -> None:
    """Valid %PDF magic but > 10 MB: 413 with the es-MX detail, list unchanged."""
    headers, record_id = own_diagnosis(client, db)
    oversize = b"%PDF-" + b"0" * TEN_MB  # TEN_MB + 5 bytes > inclusive limit

    r = upload(client, headers, record_id, "mega.pdf", oversize, "application/pdf")

    assert r.status_code == 413, r.text
    assert r.json() == {"detail": "El archivo excede el límite de 10 MB"}

    r_list = client.get(attachments_url(record_id), headers=headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
    assert r_list.json()["data"] == []


def test_ac2_exactly_10mb_is_accepted(client: TestClient, db: Session) -> None:
    """The limit is inclusive: a file of exactly 10 MB (10*1024*1024) passes."""
    headers, record_id = own_diagnosis(client, db)
    exact = b"%PDF-" + b"0" * (TEN_MB - 5)
    assert len(exact) == TEN_MB

    r = upload(client, headers, record_id, "justo.pdf", exact, "application/pdf")

    assert r.status_code == 201, r.text
    assert r.json()["size_bytes"] == TEN_MB


# --- Scenario 3: Adjuntos cifrados en reposo -----------------------------------


def test_ac3_attachment_is_encrypted_at_rest(client: TestClient, db: Session) -> None:
    """Raw row of health_record_attachment: no clear %PDF, filename is ciphertext."""
    headers, record_id = own_diagnosis(client, db)
    r = upload(
        client, headers, record_id, "perfil-tiroideo.pdf", PDF_BYTES, "application/pdf"
    )
    assert r.status_code == 201, r.text
    attachment_id = r.json()["id"]

    db.expire_all()
    row = (
        db.execute(
            text("SELECT * FROM health_record_attachment WHERE id = CAST(:id AS uuid)"),
            {"id": str(attachment_id)},
        )
        .mappings()
        .one()
    )

    # The stored filename is a Fernet token, not the clear name.
    assert str(row["filename"]).startswith("gAAAA"), row["filename"]
    assert "perfil-tiroideo" not in str(row["filename"])

    # No raw column of the row contains the %PDF magic in the clear.
    for column, value in row.items():
        raw = (
            bytes(value)
            if isinstance(value, (bytes, bytearray, memoryview))
            else str(value).encode()
        )
        assert b"%PDF" not in raw, column


# --- Scenario 4: Un adjunto de un registro ajeno no existe para mí --------------


def test_ac4_foreign_record_attachments_are_indistinguishable_from_nonexistent(
    client: TestClient, db: Session
) -> None:
    """B attaching/listing/downloading/deleting over A's record: the SAME 404.

    Same status AND same {"detail": "Registro no encontrado"} body as the one
    a nonexistent record UUID produces, for every attachment operation.
    """
    headers_a, record_a = own_diagnosis(client, db)
    r_att = upload(
        client, headers_a, record_a, "perfil-tiroideo.pdf", PDF_BYTES, "application/pdf"
    )
    assert r_att.status_code == 201, r_att.text
    attachment_a = r_att.json()["id"]

    headers_b = consented_user_headers(client, db)
    missing_record = str(uuid.uuid4())
    missing_attachment = str(uuid.uuid4())

    probes = [
        (
            "POST",
            attachments_url(record_a),
            attachments_url(missing_record),
            {"files": {"file": ("x.pdf", PDF_BYTES, "application/pdf")}},
        ),
        ("GET", attachments_url(record_a), attachments_url(missing_record), {}),
        (
            "GET",
            attachment_url(record_a, attachment_a),
            attachment_url(missing_record, missing_attachment),
            {},
        ),
        (
            "DELETE",
            attachment_url(record_a, attachment_a),
            attachment_url(missing_record, missing_attachment),
            {},
        ),
    ]
    for method, foreign_url, missing_url, kwargs in probes:
        r_foreign = client.request(method, foreign_url, headers=headers_b, **kwargs)
        r_missing = client.request(method, missing_url, headers=headers_b, **kwargs)
        assert r_foreign.status_code == 404, (method, foreign_url, r_foreign.text)
        assert r_missing.status_code == 404, (method, missing_url, r_missing.text)
        assert r_foreign.json() == {"detail": "Registro no encontrado"}, method
        assert r_foreign.json() == r_missing.json(), method
        assert "%PDF" not in r_foreign.text, method
        assert "perfil-tiroideo" not in r_foreign.text, method

    # A's attachment is intact after B's attempts: A can still download it.
    r_down = client.get(attachment_url(record_a, attachment_a), headers=headers_a)
    assert r_down.status_code == 200, r_down.text
    assert r_down.content == PDF_BYTES


def test_ac4_missing_attachment_on_own_record_is_404_adjunto(
    client: TestClient, db: Session
) -> None:
    """Own record, nonexistent attachment id: 404 'Adjunto no encontrado'."""
    headers, record_id = own_diagnosis(client, db)
    missing_attachment = str(uuid.uuid4())

    for method in ("GET", "DELETE"):
        r = client.request(
            method,
            attachment_url(record_id, missing_attachment),
            headers=headers,
        )
        assert r.status_code == 404, (method, r.text)
        assert r.json() == {"detail": "Adjunto no encontrado"}, method


# --- Scenario 5: DELETE del registro arrastra sus adjuntos ----------------------


def test_ac5_deleting_record_cascades_over_attachment_rows(
    client: TestClient, db: Session
) -> None:
    """DELETE of the record: its health_record_attachment rows disappear (count=0)."""
    headers, record_id = own_diagnosis(client, db)
    r_att = upload(
        client, headers, record_id, "perfil-tiroideo.pdf", PDF_BYTES, "application/pdf"
    )
    assert r_att.status_code == 201, r_att.text
    attachment_id = r_att.json()["id"]

    r_delete = client.delete(
        f"{settings.API_V1_STR}/health-records/{record_id}", headers=headers
    )
    assert r_delete.status_code == 200, r_delete.text
    assert r_delete.json() == {"message": "Registro eliminado"}

    db.expire_all()
    count = db.execute(
        text(
            "SELECT COUNT(*) FROM health_record_attachment "
            "WHERE record_id = CAST(:rid AS uuid)"
        ),
        {"rid": str(record_id)},
    ).scalar_one()
    assert count == 0

    # The DELETE contract for a lone attachment is also observable upstream:
    # downloading it after the cascade is the nonexistent-record 404.
    r_down = client.get(attachment_url(record_id, attachment_id), headers=headers)
    assert r_down.status_code == 404
    assert r_down.json() == {"detail": "Registro no encontrado"}


def test_ac5_delete_own_attachment_returns_adjunto_eliminado(
    client: TestClient, db: Session
) -> None:
    """DELETE of an own attachment: 200 'Adjunto eliminado' and gone from the list."""
    headers, record_id = own_diagnosis(client, db)
    r_att = upload(
        client, headers, record_id, "perfil-tiroideo.pdf", PDF_BYTES, "application/pdf"
    )
    assert r_att.status_code == 201, r_att.text
    attachment_id = r_att.json()["id"]

    r_delete = client.delete(attachment_url(record_id, attachment_id), headers=headers)
    assert r_delete.status_code == 200, r_delete.text
    assert r_delete.json() == {"message": "Adjunto eliminado"}

    r_list = client.get(attachments_url(record_id), headers=headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
    assert r_list.json()["data"] == []


# --- Review coverage (PR #6): consent gate over attachment endpoints -------------


@pytest.mark.parametrize(
    "method,url_builder,kwargs",
    [
        pytest.param(
            "POST",
            lambda rid, aid: attachments_url(rid),
            {"files": {"file": ("x.pdf", PDF_BYTES, "application/pdf")}},
            id="post-upload",
        ),
        pytest.param("GET", lambda rid, aid: attachments_url(rid), {}, id="get-list"),
        pytest.param(
            "GET", lambda rid, aid: attachment_url(rid, aid), {}, id="get-download"
        ),
        pytest.param(
            "DELETE", lambda rid, aid: attachment_url(rid, aid), {}, id="delete"
        ),
    ],
)
def test_review_b1_attachment_endpoints_without_consent_are_403_consent_required(
    client: TestClient,
    db: Session,
    method: str,
    url_builder: Any,
    kwargs: dict[str, Any],
) -> None:
    """Los 4 endpoints de adjuntos sin consentimiento: 403 CONSENT_REQUIRED."""
    headers = user_without_consent_headers(client, db)
    record_id = str(uuid.uuid4())
    attachment_id = str(uuid.uuid4())

    r = client.request(
        method, url_builder(record_id, attachment_id), headers=headers, **kwargs
    )

    assert r.status_code == 403, (method, r.text)
    assert r.json()["detail"] == "CONSENT_REQUIRED", (method, r.text)


# --- Review coverage (PR #6): image types by magic bytes -------------------------


def test_review_b3_minimal_jpeg_is_accepted_as_image_jpeg(
    client: TestClient, db: Session
) -> None:
    """JPEG mínimo (magic \\xff\\xd8\\xff\\xe0) como image/jpeg: 201 image/jpeg."""
    headers, record_id = own_diagnosis(client, db)
    jpeg_bytes = b"\xff\xd8\xff\xe0" + b"\x00" * 64

    r = upload(client, headers, record_id, "radiografia.jpg", jpeg_bytes, "image/jpeg")

    assert r.status_code == 201, r.text
    meta = r.json()
    assert meta["media_type"] == "image/jpeg"
    assert meta["filename"] == "radiografia.jpg"
    assert meta["size_bytes"] == len(jpeg_bytes)


def test_review_b3_minimal_png_is_accepted_as_image_png(
    client: TestClient, db: Session
) -> None:
    """PNG mínimo (firma \\x89PNG\\r\\n\\x1a\\n) como image/png: 201 image/png."""
    headers, record_id = own_diagnosis(client, db)
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64

    r = upload(client, headers, record_id, "ultrasonido.png", png_bytes, "image/png")

    assert r.status_code == 201, r.text
    meta = r.json()
    assert meta["media_type"] == "image/png"
    assert meta["filename"] == "ultrasonido.png"
    assert meta["size_bytes"] == len(png_bytes)


def test_review_b3_pdf_content_declared_as_png_is_rejected_415(
    client: TestClient, db: Session
) -> None:
    """Contenido %PDF declarado image/png: 415 (los magic bytes mandan)."""
    headers, record_id = own_diagnosis(client, db)

    r = upload(client, headers, record_id, "captura.png", PDF_BYTES, "image/png")

    assert r.status_code == 415, r.text
    assert r.json() == {"detail": "Tipo de archivo no permitido (solo PDF, JPEG o PNG)"}

    r_list = client.get(attachments_url(record_id), headers=headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
