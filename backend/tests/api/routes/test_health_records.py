"""Tests for the clinical record book, receta mexicana model (receta-mexicana, grupo 1).

Contract (openspec/changes/receta-mexicana/design.md §Interface contract):
- POST /api/v1/health-records/ (auth + consent, 403 CONSENT_REQUIRED without):
  - prescription: {record_type, occurred_on, professional?, diagnosis?, notes?,
    medicines: [{name (1..255, required), dose?, frequency?, route?}]} with 1..N
    medicines. NO dose/valid_from/valid_to at record level (legacy payload -> 422).
  - diagnosis: {record_type, title (required), occurred_on, professional?, notes?}.
  - 201 HealthRecordPublic | 422 (detail: STRING es-MX) | 403 CONSENT_REQUIRED.
- HealthRecordPublic: {id, record_type, occurred_on, title: str|None, professional,
  diagnosis: str|None, notes, archived: bool, confirmation_status:
  "unconfirmed"|None (diagnosis only), medicines: [{id, name, dose, frequency,
  route}] in capture order, created_at, updated_at}.
- PATCH /{id}: partial; ``medicines`` present = FULL replacement (resulting list
  validated 1..N); ``archived: bool`` archives/unarchives; resulting state
  validated -> 422 detail string es-MX.
- GET / -> {"data": [...], "count": N} (archived included), only own records.
- GET|PATCH|DELETE /{id} -> 404 {"detail": "Registro no encontrado"}, identical
  for a nonexistent id and someone else's. DELETE -> {"message": "Registro
  eliminado"}; deleting a record cascades over its medicines and attachments.
- Encrypted at rest: healthrecord clinical columns and the new
  healthrecordmedicine table (name/dose/frequency/route are Fernet ciphertext,
  prefix "gAAAA").

Spec: openspec/changes/receta-mexicana/specs/records/clinical-records/spec.md.
"""

import uuid
from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import UserCreate
from tests.utils.utils import random_email, random_lower_string

# Minimal valid PNG (magic bytes) for attachment-cascade/archive scenarios.
PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64

LEGACY_RECORD_FIELDS = ("dose", "valid_from", "valid_to")


def consented_user_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Fresh random user, logged in, with consent v1 granted."""
    email = random_email()
    password = random_lower_string()
    crud.create_user(session=db, user_create=UserCreate(email=email, password=password))
    r = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200, r.text
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r_consent = client.post(
        f"{settings.API_V1_STR}/consent/", headers=headers, json={"version": "v1"}
    )
    assert r_consent.status_code == 201, r_consent.text
    return headers


def user_without_consent_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Fresh random user, logged in, WITHOUT consent."""
    email = random_email()
    password = random_lower_string()
    crud.create_user(session=db, user_create=UserCreate(email=email, password=password))
    r = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def diagnosis_payload(**overrides: Any) -> dict[str, Any]:
    """Scenario 'Registrar un diagnóstico' concrete data."""
    payload: dict[str, Any] = {
        "record_type": "diagnosis",
        "title": "Hipotiroidismo subclínico",
        "occurred_on": "2026-09-30",
        "professional": "Dra. Islas (endocrinología)",
        "notes": "TSH 6.8; repetir perfil en 3 meses",
    }
    payload.update(overrides)
    return payload


def prescription_payload(**overrides: Any) -> dict[str, Any]:
    """Scenario 'Registrar una receta con varias medicinas' (AC-1) concrete data."""
    payload: dict[str, Any] = {
        "record_type": "prescription",
        "occurred_on": "2026-10-12",
        "professional": "Dra. Islas (endocrinología)",
        "medicines": [
            {
                "name": "Levotiroxina 50 µg",
                "dose": "1 tableta en ayunas",
                "frequency": "cada 24 h",
            },
            {
                "name": "Omeprazol 20 mg",
                "dose": "1 cápsula antes del desayuno por 14 días",
            },
        ],
    }
    payload.update(overrides)
    return payload


def legacy_prescription_payload() -> dict[str, Any]:
    """The RETIRED model: dose + validity at record level, no medicines list."""
    return {
        "record_type": "prescription",
        "title": "Levotiroxina 50 µg",
        "occurred_on": "2026-10-01",
        "dose": "1 tableta en ayunas cada 24 h",
        "valid_from": "2026-10-01",
        "valid_to": "2026-12-30",
    }


def post_record(
    client: TestClient, headers: dict[str, str], payload: dict[str, Any]
) -> Any:
    return client.post(
        f"{settings.API_V1_STR}/health-records/", headers=headers, json=payload
    )


def list_records(client: TestClient, headers: dict[str, str]) -> Any:
    return client.get(f"{settings.API_V1_STR}/health-records/", headers=headers)


def record_url(record_id: Any) -> str:
    return f"{settings.API_V1_STR}/health-records/{record_id}"


def get_record(client: TestClient, headers: dict[str, str], record_id: Any) -> Any:
    return client.get(record_url(record_id), headers=headers)


def patch_record(
    client: TestClient, headers: dict[str, str], record_id: Any, body: dict[str, Any]
) -> Any:
    return client.patch(record_url(record_id), headers=headers, json=body)


def upload_png(
    client: TestClient, headers: dict[str, str], record_id: Any, filename: str
) -> Any:
    return client.post(
        f"{record_url(record_id)}/attachments",
        headers=headers,
        files={"file": (filename, PNG_BYTES, "image/png")},
    )


def assert_no_legacy_fields(record: dict[str, Any]) -> None:
    """The public record carries no record-level dose/validity, absent or null."""
    for field in LEGACY_RECORD_FIELDS:
        assert record.get(field) is None, (field, record.get(field))


# --- Scenario: Registrar una receta con varias medicinas (AC-1) -----------------


def test_create_prescription_with_medicines(client: TestClient, db: Session) -> None:
    """Receta 2026-10-12 con 2 medicinas: 201, en orden, sin campo de vigencia."""
    headers = consented_user_headers(client, db)

    r = post_record(client, headers, prescription_payload())

    assert r.status_code == 201, r.text
    record = r.json()
    assert record["id"]
    assert record["record_type"] == "prescription"
    assert record["occurred_on"] == "2026-10-12"
    assert record["professional"] == "Dra. Islas (endocrinología)"
    assert record.get("diagnosis") is None
    assert record["archived"] is False
    # confirmation_status applies to diagnosis only.
    assert record.get("confirmation_status") is None
    assert_no_legacy_fields(record)
    medicines = record["medicines"]
    assert len(medicines) == 2
    first, second = medicines
    assert first["id"]
    assert first["name"] == "Levotiroxina 50 µg"
    assert first["dose"] == "1 tableta en ayunas"
    assert first["frequency"] == "cada 24 h"
    assert second["id"]
    assert second["name"] == "Omeprazol 20 mg"
    assert second["dose"] == "1 cápsula antes del desayuno por 14 días"
    assert second.get("frequency") is None
    assert record["created_at"]
    assert record["updated_at"]

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    body = r_list.json()
    assert body["count"] == 1
    listed = body["data"][0]
    assert str(listed["id"]) == str(record["id"])
    assert listed["record_type"] == "prescription"
    assert listed["occurred_on"] == "2026-10-12"
    assert [m["name"] for m in listed["medicines"]] == [
        "Levotiroxina 50 µg",
        "Omeprazol 20 mg",
    ]
    assert_no_legacy_fields(listed)


# --- Scenario: Diagnóstico opcional (AC-3) y frecuencia opcional (AC-9) ----------


def test_prescription_optional_diagnosis_and_frequency(
    client: TestClient, db: Session
) -> None:
    """Sin diagnóstico/frecuencia: nulos, nunca inventados; con ellos: exactos."""
    headers = consented_user_headers(client, db)

    bare = prescription_payload(
        medicines=[{"name": "Paracetamol 500 mg", "dose": "1 tableta"}]
    )
    bare.pop("diagnosis", None)
    r_bare = post_record(client, headers, bare)
    assert r_bare.status_code == 201, r_bare.text

    full = prescription_payload(
        diagnosis="faringitis",
        medicines=[
            {
                "name": "Paracetamol 500 mg",
                "dose": "1 tableta",
                "frequency": "cada 8 h",
                "route": "oral",
            }
        ],
    )
    r_full = post_record(client, headers, full)
    assert r_full.status_code == 201, r_full.text

    r_get_bare = get_record(client, headers, r_bare.json()["id"])
    assert r_get_bare.status_code == 200, r_get_bare.text
    bare_record = r_get_bare.json()
    assert bare_record.get("diagnosis") is None
    assert len(bare_record["medicines"]) == 1
    bare_med = bare_record["medicines"][0]
    assert bare_med["name"] == "Paracetamol 500 mg"
    assert bare_med["dose"] == "1 tableta"
    # Absent or null, never invented.
    assert bare_med.get("frequency") is None
    assert bare_med.get("route") is None

    r_get_full = get_record(client, headers, r_full.json()["id"])
    assert r_get_full.status_code == 200, r_get_full.text
    full_record = r_get_full.json()
    assert full_record["diagnosis"] == "faringitis"
    full_med = full_record["medicines"][0]
    assert full_med["name"] == "Paracetamol 500 mg"
    assert full_med["dose"] == "1 tableta"
    assert full_med["frequency"] == "cada 8 h"
    assert full_med["route"] == "oral"


# --- Scenario: Una receta sin medicinas se rechaza (AC-1) ------------------------


def test_prescription_requires_medicines(client: TestClient, db: Session) -> None:
    """Lista de medicinas vacía o medicina sin nombre: 422 y nada persiste."""
    headers = consented_user_headers(client, db)

    r_empty = post_record(client, headers, prescription_payload(medicines=[]))
    assert r_empty.status_code == 422, r_empty.text
    detail = r_empty.json()["detail"]
    assert isinstance(detail, str), detail

    r_no_name = post_record(
        client,
        headers,
        prescription_payload(medicines=[{"name": "", "dose": "1 tableta"}]),
    )
    assert r_no_name.status_code == 422, r_no_name.text

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
    assert r_list.json()["data"] == []


# --- Scenario: Registrar un diagnóstico ------------------------------------------


def test_create_diagnosis(client: TestClient, db: Session) -> None:
    """Diagnóstico suelto: 201 con el id y aparece en el expediente como diagnosis."""
    headers = consented_user_headers(client, db)

    r = post_record(client, headers, diagnosis_payload())

    assert r.status_code == 201, r.text
    record = r.json()
    assert record["id"]
    assert record["record_type"] == "diagnosis"
    assert record["title"] == "Hipotiroidismo subclínico"
    assert record["occurred_on"] == "2026-09-30"
    assert record["professional"] == "Dra. Islas (endocrinología)"
    assert record["notes"] == "TSH 6.8; repetir perfil en 3 meses"
    assert record["archived"] is False
    assert record["medicines"] == []
    assert_no_legacy_fields(record)

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    body = r_list.json()
    assert body["count"] == 1
    assert str(body["data"][0]["id"]) == str(record["id"])
    assert body["data"][0]["record_type"] == "diagnosis"
    assert body["data"][0]["title"] == "Hipotiroidismo subclínico"


# --- Scenario: Registrar una receta con dosis y vigencia (modelo retirado) -------


def test_legacy_prescription_payload_rejected(client: TestClient, db: Session) -> None:
    """Payload viejo (dose/valid_from/valid_to a nivel registro): 422 es-MX."""
    headers = consented_user_headers(client, db)

    r = post_record(client, headers, legacy_prescription_payload())

    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, str), detail

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
    assert r_list.json()["data"] == []


# --- Scenario: El contenido clínico queda cifrado en reposo ----------------------


def test_clinical_content_encrypted_at_rest(client: TestClient, db: Session) -> None:
    """healthrecord y healthrecordmedicine en crudo: ciphertext Fernet (gAAAA).

    Nombre y dosis de cada medicina, médico, diagnóstico y notas son Fernet
    tokens; ninguna columna de ninguna fila contiene "Levotiroxina" ni
    "Hipotiroidismo" en claro.
    """
    headers = consented_user_headers(client, db)

    r_rx = post_record(
        client, headers, prescription_payload(diagnosis="Hipotiroidismo subclínico")
    )
    assert r_rx.status_code == 201, r_rx.text
    rx_id = r_rx.json()["id"]

    r_diag = post_record(client, headers, diagnosis_payload())
    assert r_diag.status_code == 201, r_diag.text
    diag_id = r_diag.json()["id"]

    db.expire_all()
    rx_row = (
        db.execute(
            text("SELECT * FROM healthrecord WHERE id = CAST(:id AS uuid)"),
            {"id": str(rx_id)},
        )
        .mappings()
        .one()
    )
    diag_row = (
        db.execute(
            text("SELECT * FROM healthrecord WHERE id = CAST(:id AS uuid)"),
            {"id": str(diag_id)},
        )
        .mappings()
        .one()
    )
    medicine_rows = (
        db.execute(
            text(
                "SELECT * FROM healthrecordmedicine "
                "WHERE record_id = CAST(:rid AS uuid) ORDER BY position"
            ),
            {"rid": str(rx_id)},
        )
        .mappings()
        .all()
    )
    assert len(medicine_rows) == 2

    # Clinical columns of the record rows are ciphertext.
    for column in ("professional", "diagnosis"):
        assert str(rx_row[column]).startswith("gAAAA"), (column, rx_row[column])
    for column in ("title", "professional", "notes"):
        assert str(diag_row[column]).startswith("gAAAA"), (column, diag_row[column])

    # Medicine clinical columns are ciphertext (optional ones only when set).
    for row in medicine_rows:
        for column in ("name", "dose", "frequency", "route"):
            value = row.get(column)
            if value is not None:
                assert str(value).startswith("gAAAA"), (column, value)

    # No raw column anywhere leaks the clinical terms in the clear.
    for row in (rx_row, diag_row, *medicine_rows):
        for value in row.values():
            assert "Levotiroxina" not in str(value)
            assert "Hipotiroidismo" not in str(value)


# --- Scenario: Sin consentimiento no entra ni un dato ----------------------------


def test_consent_required(client: TestClient, db: Session) -> None:
    """Sin consentimiento: registrar o listar -> 403 CONSENT_REQUIRED, nada persiste."""
    headers = user_without_consent_headers(client, db)

    for payload in (prescription_payload(), diagnosis_payload()):
        r_post = post_record(client, headers, payload)
        assert r_post.status_code == 403, r_post.text
        assert r_post.json()["detail"] == "CONSENT_REQUIRED"

    r_get = list_records(client, headers)
    assert r_get.status_code == 403
    assert r_get.json()["detail"] == "CONSENT_REQUIRED"

    # Nothing persisted: once consent is granted, the list is still empty.
    r_consent = client.post(
        f"{settings.API_V1_STR}/consent/", headers=headers, json={"version": "v1"}
    )
    assert r_consent.status_code == 201, r_consent.text
    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
    assert r_list.json()["data"] == []


# --- Scenario: Un registro ajeno no existe para mí -------------------------------


def test_foreign_record_indistinguishable_404(client: TestClient, db: Session) -> None:
    """GET/PATCH/archivar/DELETE ajenos: el MISMO 404 que un UUID inexistente."""
    headers_a = consented_user_headers(client, db)
    headers_b = consented_user_headers(client, db)

    r_a = post_record(client, headers_a, prescription_payload())
    assert r_a.status_code == 201, r_a.text
    foreign_id = r_a.json()["id"]
    missing_id = str(uuid.uuid4())

    # B's list does not contain A's prescription.
    r_list_b = list_records(client, headers_b)
    assert r_list_b.status_code == 200, r_list_b.text
    assert r_list_b.json()["count"] == 0
    assert str(foreign_id) not in r_list_b.text
    assert "Levotiroxina" not in r_list_b.text

    probes = (
        ("GET", {}),
        ("PATCH", {"json": {"notes": "intento de edición ajena"}}),
        ("PATCH", {"json": {"archived": True}}),  # archivar ajeno
        ("DELETE", {}),
    )
    for method, kwargs in probes:
        r_foreign = client.request(
            method, record_url(foreign_id), headers=headers_b, **kwargs
        )
        r_missing = client.request(
            method, record_url(missing_id), headers=headers_b, **kwargs
        )
        assert r_foreign.status_code == 404, (method, kwargs, r_foreign.text)
        assert r_missing.status_code == 404, (method, kwargs, r_missing.text)
        assert r_foreign.json() == {"detail": "Registro no encontrado"}, (method, kwargs)
        assert r_foreign.json() == r_missing.json(), (method, kwargs)
        assert "Levotiroxina" not in r_foreign.text, (method, kwargs)

    # A's prescription is untouched: still there, not archived, not deleted.
    r_get_a = get_record(client, headers_a, foreign_id)
    assert r_get_a.status_code == 200, r_get_a.text
    assert r_get_a.json()["archived"] is False
    assert len(r_get_a.json()["medicines"]) == 2


# --- Scenario: Corregir las medicinas de una receta propia (AC-6) ----------------


def test_patch_replaces_medicines_validates_result(
    client: TestClient, db: Session
) -> None:
    """`medicines` en PATCH reemplaza la lista completa; dejarla vacía: 422."""
    headers = consented_user_headers(client, db)
    r_create = post_record(client, headers, prescription_payload())
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]

    replacement = [
        {
            "name": "Levotiroxina 50 µg",
            "dose": "1 tableta en ayunas",
            "frequency": "cada 24 h, lunes a sábado",
        },
        {
            "name": "Ibuprofeno 400 mg",
            "dose": "1 tableta por 5 días",
            "frequency": "cada 8 h",
        },
    ]
    r_patch = patch_record(client, headers, record_id, {"medicines": replacement})
    assert r_patch.status_code == 200, r_patch.text

    r_get = get_record(client, headers, record_id)
    assert r_get.status_code == 200, r_get.text
    medicines = r_get.json()["medicines"]
    assert len(medicines) == 2
    assert [m["name"] for m in medicines] == ["Levotiroxina 50 µg", "Ibuprofeno 400 mg"]
    assert medicines[0]["frequency"] == "cada 24 h, lunes a sábado"
    assert medicines[1]["dose"] == "1 tableta por 5 días"
    assert medicines[1]["frequency"] == "cada 8 h"
    # Omeprazol was replaced away.
    assert "Omeprazol" not in r_get.text

    # Leaving the prescription without medicines is rejected, state untouched.
    r_empty = patch_record(client, headers, record_id, {"medicines": []})
    assert r_empty.status_code == 422, r_empty.text
    detail = r_empty.json()["detail"]
    assert isinstance(detail, str), detail

    r_after = get_record(client, headers, record_id)
    assert r_after.status_code == 200, r_after.text
    assert len(r_after.json()["medicines"]) == 2
    assert [m["name"] for m in r_after.json()["medicines"]] == [
        "Levotiroxina 50 µg",
        "Ibuprofeno 400 mg",
    ]


# --- Scenario: Corregir y eliminar un registro propio ----------------------------


def test_update_and_delete_own_diagnosis(client: TestClient, db: Session) -> None:
    """PATCH de la nota se refleja; DELETE lo saca de la lista y del GET (404)."""
    headers = consented_user_headers(client, db)
    r_create = post_record(client, headers, diagnosis_payload())
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]
    new_note = "TSH 6.8; repetir perfil en 3 meses, ayunas"

    r_patch = patch_record(client, headers, record_id, {"notes": new_note})
    assert r_patch.status_code == 200, r_patch.text
    assert r_patch.json()["notes"] == new_note

    r_get = get_record(client, headers, record_id)
    assert r_get.status_code == 200, r_get.text
    assert r_get.json()["notes"] == new_note
    # Partial update: untouched fields keep their values.
    assert r_get.json()["title"] == "Hipotiroidismo subclínico"

    r_delete = client.delete(record_url(record_id), headers=headers)
    assert r_delete.status_code == 200, r_delete.text
    assert r_delete.json() == {"message": "Registro eliminado"}

    r_gone = get_record(client, headers, record_id)
    assert r_gone.status_code == 404
    assert r_gone.json() == {"detail": "Registro no encontrado"}

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
    assert str(record_id) not in r_list.text


# --- Scenario: Eliminar una receta arrastra medicinas y adjuntos -----------------


def test_delete_cascades_medicines_and_attachments(
    client: TestClient, db: Session
) -> None:
    """DELETE de la receta: 404 después, y 0 filas de medicinas y adjuntos en BD."""
    headers = consented_user_headers(client, db)
    r_create = post_record(client, headers, prescription_payload())
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]
    assert len(r_create.json()["medicines"]) == 2

    r_att = upload_png(client, headers, record_id, "receta.png")
    assert r_att.status_code == 201, r_att.text

    r_delete = client.delete(record_url(record_id), headers=headers)
    assert r_delete.status_code == 200, r_delete.text
    assert r_delete.json() == {"message": "Registro eliminado"}

    r_gone = get_record(client, headers, record_id)
    assert r_gone.status_code == 404
    assert r_gone.json() == {"detail": "Registro no encontrado"}

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert str(record_id) not in r_list.text

    db.expire_all()
    medicine_count = db.execute(
        text(
            "SELECT COUNT(*) FROM healthrecordmedicine "
            "WHERE record_id = CAST(:rid AS uuid)"
        ),
        {"rid": str(record_id)},
    ).scalar_one()
    assert medicine_count == 0
    attachment_count = db.execute(
        text(
            "SELECT COUNT(*) FROM healthrecordattachment "
            "WHERE record_id = CAST(:rid AS uuid)"
        ),
        {"rid": str(record_id)},
    ).scalar_one()
    assert attachment_count == 0


# --- Scenario: Archivar una receta activa (AC-8) ---------------------------------


def test_archive_prescription(client: TestClient, db: Session) -> None:
    """PATCH archived=true: fuera de activas, consultable con medicinas y adjuntos."""
    headers = consented_user_headers(client, db)
    r_create = post_record(client, headers, prescription_payload())
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]
    r_att = upload_png(client, headers, record_id, "receta.png")
    assert r_att.status_code == 201, r_att.text

    r_patch = patch_record(client, headers, record_id, {"archived": True})
    assert r_patch.status_code == 200, r_patch.text
    assert r_patch.json()["archived"] is True

    # The list still carries it (archived included), flagged archived: it no
    # longer counts among the active ones.
    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    body = r_list.json()
    mine = [item for item in body["data"] if str(item["id"]) == str(record_id)]
    assert len(mine) == 1
    assert mine[0]["archived"] is True
    active = [item for item in body["data"] if item["archived"] is False]
    assert str(record_id) not in [str(item["id"]) for item in active]

    # Still readable by id with its medicines and attachments intact.
    r_get = get_record(client, headers, record_id)
    assert r_get.status_code == 200, r_get.text
    archived_record = r_get.json()
    assert archived_record["archived"] is True
    assert [m["name"] for m in archived_record["medicines"]] == [
        "Levotiroxina 50 µg",
        "Omeprazol 20 mg",
    ]
    r_att_list = client.get(f"{record_url(record_id)}/attachments", headers=headers)
    assert r_att_list.status_code == 200, r_att_list.text
    assert r_att_list.json()["count"] == 1


# --- Scenario: Desarchivar devuelve la receta a activas --------------------------


def test_unarchive_prescription(client: TestClient, db: Session) -> None:
    """PATCH archived=false sobre una archivada: vuelve a activas sin pérdida."""
    headers = consented_user_headers(client, db)
    r_create = post_record(client, headers, prescription_payload())
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]
    r_archive = patch_record(client, headers, record_id, {"archived": True})
    assert r_archive.status_code == 200, r_archive.text
    assert r_archive.json()["archived"] is True

    r_unarchive = patch_record(client, headers, record_id, {"archived": False})

    assert r_unarchive.status_code == 200, r_unarchive.text
    assert r_unarchive.json()["archived"] is False

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    active = [item for item in r_list.json()["data"] if item["archived"] is False]
    assert str(record_id) in [str(item["id"]) for item in active]

    # No data loss: fields and medicines survive the round trip.
    r_get = get_record(client, headers, record_id)
    assert r_get.status_code == 200, r_get.text
    record = r_get.json()
    assert record["archived"] is False
    assert record["occurred_on"] == "2026-10-12"
    assert record["professional"] == "Dra. Islas (endocrinología)"
    assert [m["name"] for m in record["medicines"]] == [
        "Levotiroxina 50 µg",
        "Omeprazol 20 mg",
    ]


# --- Scenario: Un diagnóstico nuevo nace sin confirmar ---------------------------


def test_diagnosis_confirmation_status_unconfirmed(
    client: TestClient, db: Session
) -> None:
    """El diagnóstico expone confirmation_status 'unconfirmed' y no hay op para cambiarlo."""
    headers = consented_user_headers(client, db)

    r = post_record(client, headers, diagnosis_payload())
    assert r.status_code == 201, r.text
    record_id = r.json()["id"]
    assert r.json()["confirmation_status"] == "unconfirmed"

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    listed = [
        item for item in r_list.json()["data"] if str(item["id"]) == str(record_id)
    ]
    assert len(listed) == 1
    assert listed[0]["confirmation_status"] == "unconfirmed"

    r_get = get_record(client, headers, record_id)
    assert r_get.status_code == 200, r_get.text
    assert r_get.json()["confirmation_status"] == "unconfirmed"

    # No operation exists to confirm it: trying via PATCH never flips the state
    # (the API either rejects the field or ignores it; it must not confirm).
    r_patch = patch_record(
        client, headers, record_id, {"confirmation_status": "confirmed"}
    )
    assert r_patch.status_code in (200, 422), r_patch.text
    r_after = get_record(client, headers, record_id)
    assert r_after.status_code == 200, r_after.text
    assert r_after.json()["confirmation_status"] == "unconfirmed"


# --- Review coverage (PR #6, still in force): listing order ----------------------


def test_review_b2_list_returns_records_in_occurred_on_desc_order(
    client: TestClient, db: Session
) -> None:
    """GET /health-records/ devuelve los registros en occurred_on DESC."""
    headers = consented_user_headers(client, db)
    for occurred_on, title in (
        ("2026-05-10", "Control intermedio"),
        ("2026-09-01", "Control reciente"),
        ("2026-01-15", "Control antiguo"),
    ):
        r = post_record(
            client, headers, diagnosis_payload(title=title, occurred_on=occurred_on)
        )
        assert r.status_code == 201, r.text

    r_list = list_records(client, headers)

    assert r_list.status_code == 200, r_list.text
    body = r_list.json()
    assert body["count"] == 3
    assert [item["occurred_on"] for item in body["data"]] == [
        "2026-09-01",
        "2026-05-10",
        "2026-01-15",
    ]
    assert [item["title"] for item in body["data"]] == [
        "Control reciente",
        "Control intermedio",
        "Control antiguo",
    ]
