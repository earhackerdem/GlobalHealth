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

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.encrypted import decrypt_str
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
    assert detail == "Una receta requiere al menos una medicina"

    r_no_name = post_record(
        client,
        headers,
        prescription_payload(medicines=[{"name": "", "dose": "1 tableta"}]),
    )
    assert r_no_name.status_code == 422, r_no_name.text
    assert r_no_name.json()["detail"] == "Cada medicina requiere un nombre"

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
    assert detail == (
        "El registro ya no lleva dosis ni vigencia a nivel de receta "
        "(campos retirados: dose, valid_from, valid_to); captura cada "
        "medicina en la lista medicines"
    )

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

    rx_notes = "Notas clínicas sensibles de la receta"
    rx_route = "oral sublingual"
    r_rx = post_record(
        client,
        headers,
        prescription_payload(
            diagnosis="Hipotiroidismo subclínico",
            notes=rx_notes,
            medicines=[
                {
                    "name": "Levotiroxina 50 µg",
                    "dose": "1 tableta en ayunas",
                    "frequency": "cada 24 h",
                    "route": rx_route,
                },
                {"name": "Omeprazol 20 mg"},
            ],
        ),
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
    for column in ("professional", "diagnosis", "notes"):
        assert str(rx_row[column]).startswith("gAAAA"), (column, rx_row[column])
    for column in ("title", "professional", "notes"):
        assert str(diag_row[column]).startswith("gAAAA"), (column, diag_row[column])

    # Medicine clinical columns are ciphertext (optional ones only when set).
    for row in medicine_rows:
        for column in ("name", "dose", "frequency", "route"):
            value = row.get(column)
            if value is not None:
                assert str(value).startswith("gAAAA"), (column, value)

    # Review S4: prescription ``notes`` and medicine ``route`` round-trip —
    # what is stored is not the plaintext AND decrypts back to the value.
    assert decrypt_str(str(rx_row["notes"])) == rx_notes
    route_raw = medicine_rows[0]["route"]
    assert route_raw is not None
    assert str(route_raw).startswith("gAAAA"), route_raw
    assert decrypt_str(str(route_raw)) == rx_route

    # No raw column anywhere leaks the clinical terms in the clear.
    for row in (rx_row, diag_row, *medicine_rows):
        for value in row.values():
            assert "Levotiroxina" not in str(value)
            assert "Hipotiroidismo" not in str(value)
            assert "Notas clínicas" not in str(value)
            assert "sublingual" not in str(value)


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
        assert r_foreign.json() == {"detail": "Registro no encontrado"}, (
            method,
            kwargs,
        )
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
    assert detail == "Una receta requiere al menos una medicina"

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


# --- Review coverage (PR #13, T2): ramas del estado resultante del PATCH ----------


@pytest.mark.parametrize(
    ("record_kind", "body", "expected_detail"),
    [
        ("diagnosis", {"title": None}, "Un diagnóstico requiere un título"),
        (
            "diagnosis",
            {"medicines": [{"name": "Paracetamol 500 mg"}]},
            "Un diagnóstico no admite medicinas",
        ),
        (
            "diagnosis",
            {"diagnosis": "texto en el campo diagnosis"},
            "Un diagnóstico no admite el campo diagnosis; usa el título",
        ),
        (
            "prescription",
            {"title": "Receta con título"},
            "Una receta no admite título; captura sus medicinas",
        ),
    ],
)
def test_review_t2_patch_resultant_state_branches(
    client: TestClient,
    db: Session,
    record_kind: str,
    body: dict[str, Any],
    expected_detail: str,
) -> None:
    """Cada rama viva de la validación del estado resultante: 422 con es-MX."""
    headers = consented_user_headers(client, db)
    payload = (
        diagnosis_payload() if record_kind == "diagnosis" else prescription_payload()
    )
    r_create = post_record(client, headers, payload)
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]

    r_patch = patch_record(client, headers, record_id, body)

    assert r_patch.status_code == 422, r_patch.text
    assert r_patch.json()["detail"] == expected_detail

    # The rejected PATCH leaves the record untouched.
    r_get = get_record(client, headers, record_id)
    assert r_get.status_code == 200, r_get.text
    record = r_get.json()
    if record_kind == "diagnosis":
        assert record["title"] == "Hipotiroidismo subclínico"
        assert record["medicines"] == []
        assert record.get("diagnosis") is None
    else:
        assert record.get("title") is None
        assert len(record["medicines"]) == 2


# --- Review coverage (PR #13, C3): payload híbrido rechazado por su nombre --------


def test_review_c3_hybrid_payload_rejected_by_name(
    client: TestClient, db: Session
) -> None:
    """medicines válidas + campos retirados: 422 que NOMBRA los campos legacy."""
    headers = consented_user_headers(client, db)

    hybrid = prescription_payload(dose="1 tableta en ayunas", valid_from="2026-10-01")
    r_post = post_record(client, headers, hybrid)
    assert r_post.status_code == 422, r_post.text
    detail = r_post.json()["detail"]
    assert isinstance(detail, str), detail
    assert detail == (
        "El registro ya no lleva dosis ni vigencia a nivel de receta "
        "(campos retirados: dose, valid_from); captura cada medicina en "
        "la lista medicines"
    )
    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0

    # Same rejection on PATCH, and the stored medicines stay untouched.
    r_create = post_record(client, headers, prescription_payload())
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]
    r_patch = patch_record(
        client,
        headers,
        record_id,
        {
            "medicines": [{"name": "Ibuprofeno 400 mg"}],
            "dose": "1 tableta",
            "valid_to": "2026-12-30",
        },
    )
    assert r_patch.status_code == 422, r_patch.text
    assert r_patch.json()["detail"] == (
        "El registro ya no lleva dosis ni vigencia a nivel de receta "
        "(campos retirados: dose, valid_to); captura cada medicina en "
        "la lista medicines"
    )
    r_get = get_record(client, headers, record_id)
    assert r_get.status_code == 200, r_get.text
    assert [m["name"] for m in r_get.json()["medicines"]] == [
        "Levotiroxina 50 µg",
        "Omeprazol 20 mg",
    ]


# --- Review coverage (PR #13, S3): null explícito en campos no anulables ----------


def test_review_s3_patch_explicit_null_on_non_nullable_fields(
    client: TestClient, db: Session
) -> None:
    """PATCH {"archived": null} o {"occurred_on": null}: 422 es-MX, nunca 500."""
    headers = consented_user_headers(client, db)
    r_create = post_record(client, headers, prescription_payload())
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]

    for field in ("archived", "occurred_on"):
        r_null = patch_record(client, headers, record_id, {field: None})
        assert r_null.status_code == 422, (field, r_null.text)
        detail = r_null.json()["detail"]
        assert detail == (
            f"No se admite null en {field}; envía un valor o no incluyas el campo"
        ), (field, detail)

    # The record is untouched after the rejected nulls.
    r_get = get_record(client, headers, record_id)
    assert r_get.status_code == 200, r_get.text
    assert r_get.json()["archived"] is False
    assert r_get.json()["occurred_on"] == "2026-10-12"

    # Documented leniency (Saúl's call): a RETIRED field with explicit null
    # keeps being ignored instead of rejected.
    r_legacy_null = patch_record(client, headers, record_id, {"dose": None})
    assert r_legacy_null.status_code == 200, r_legacy_null.text


# --- Review coverage (PR #13, S1): tope de medicinas por receta -------------------


def test_review_s1_medicines_capped_at_20(client: TestClient, db: Session) -> None:
    """21 medicinas: 422 es-MX en POST y PATCH; 20 exactas: 201."""
    headers = consented_user_headers(client, db)
    too_many = [{"name": f"Medicina {i}"} for i in range(21)]

    r_over = post_record(client, headers, prescription_payload(medicines=too_many))
    assert r_over.status_code == 422, r_over.text
    assert r_over.json()["detail"] == "Una receta admite como máximo 20 medicinas"

    r_cap = post_record(client, headers, prescription_payload(medicines=too_many[:20]))
    assert r_cap.status_code == 201, r_cap.text
    record_id = r_cap.json()["id"]
    assert len(r_cap.json()["medicines"]) == 20

    r_patch_over = patch_record(client, headers, record_id, {"medicines": too_many})
    assert r_patch_over.status_code == 422, r_patch_over.text
    assert r_patch_over.json()["detail"] == "Una receta admite como máximo 20 medicinas"
    r_after = get_record(client, headers, record_id)
    assert r_after.status_code == 200, r_after.text
    assert len(r_after.json()["medicines"]) == 20


# --- perfil-cronicas (B-5): borrar un diagnóstico desenlaza las crónicas ----------
#
# Contract: DELETE /health-records/{id} of a diagnosis unlinks it from the
# patient's chronic entries in the same transaction (response unchanged);
# crud.unlink_diagnosis(session, owner_id, diagnosis_id) -> int (entries changed).

HISTORY_URL = f"{settings.API_V1_STR}/profile/history"


def post_chronic(
    client: TestClient, headers: dict[str, str], **fields: Any
) -> dict[str, Any]:
    r = client.post(HISTORY_URL, headers=headers, json={"section": "chronic", **fields})
    assert r.status_code == 201, r.text
    entry: dict[str, Any] = r.json()
    return entry


def chronic_entries(client: TestClient, headers: dict[str, str]) -> dict[str, Any]:
    r = client.get(HISTORY_URL, headers=headers)
    assert r.status_code == 200, r.text
    return {str(e["id"]): e for e in r.json()["data"] if e.get("section") == "chronic"}


def user_id_of(client: TestClient, headers: dict[str, str]) -> uuid.UUID:
    r = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r.status_code == 200, r.text
    return uuid.UUID(str(r.json()["id"]))


def test_b5_delete_diagnosis_unlinks_chronic_entries(
    client: TestClient, db: Session
) -> None:
    """A borra "Hipotiroidismo subclínico": respuesta de siempre; su crónica
    hypothyroidism sigue, sin diagnosis_id; la crónica de B sigue enlazada."""
    headers_a = consented_user_headers(client, db)
    headers_b = consented_user_headers(client, db)
    r_diag_a = post_record(client, headers_a, diagnosis_payload())
    assert r_diag_a.status_code == 201, r_diag_a.text
    diag_a = str(r_diag_a.json()["id"])
    r_diag_b = post_record(client, headers_b, diagnosis_payload())
    assert r_diag_b.status_code == 201, r_diag_b.text
    diag_b = str(r_diag_b.json()["id"])
    entry_a = post_chronic(
        client,
        headers_a,
        condition="hypothyroidism",
        status="active",
        treatment="Levotiroxina 50 mcg en ayunas",
        diagnosis_id=diag_a,
    )
    entry_b = post_chronic(
        client, headers_b, condition="hypothyroidism", diagnosis_id=diag_b
    )

    r_delete = client.delete(record_url(diag_a), headers=headers_a)

    assert r_delete.status_code == 200, r_delete.text
    assert r_delete.json() == {"message": "Registro eliminado"}
    assert get_record(client, headers_a, diag_a).status_code == 404

    mine = chronic_entries(client, headers_a)
    assert str(entry_a["id"]) in mine
    kept = mine[str(entry_a["id"])]
    assert kept.get("diagnosis_id") is None
    assert kept["condition"] == "hypothyroidism"
    assert kept["status"] == "active"
    assert kept["treatment"] == "Levotiroxina 50 mcg en ayunas"

    theirs = chronic_entries(client, headers_b)
    assert str(theirs[str(entry_b["id"])]["diagnosis_id"]) == diag_b
    assert get_record(client, headers_b, diag_b).status_code == 200


def test_b5_delete_diagnosis_backing_nothing_unchanged(
    client: TestClient, db: Session
) -> None:
    """Borrar un diagnóstico que no respalda ninguna crónica: misma respuesta y la
    crónica enlazada a OTRO diagnóstico no cambia."""
    headers = consented_user_headers(client, db)
    r_unused = post_record(client, headers, diagnosis_payload(title="Faringitis"))
    assert r_unused.status_code == 201, r_unused.text
    unused_id = str(r_unused.json()["id"])
    r_used = post_record(client, headers, diagnosis_payload())
    assert r_used.status_code == 201, r_used.text
    used_id = str(r_used.json()["id"])
    entry = post_chronic(
        client, headers, condition="hypothyroidism", diagnosis_id=used_id
    )

    r_delete = client.delete(record_url(unused_id), headers=headers)

    assert r_delete.status_code == 200, r_delete.text
    assert r_delete.json() == {"message": "Registro eliminado"}
    assert get_record(client, headers, unused_id).status_code == 404
    mine = chronic_entries(client, headers)
    assert str(mine[str(entry["id"])]["diagnosis_id"]) == used_id


def test_b5_crud_unlink_diagnosis_counts_and_scopes_by_owner(
    client: TestClient, db: Session
) -> None:
    """crud.unlink_diagnosis devuelve 1 para la crónica enlazada del dueño y 0
    para el diagnóstico de otro paciente (cuya crónica no se toca)."""
    headers_a = consented_user_headers(client, db)
    headers_b = consented_user_headers(client, db)
    owner_a = user_id_of(client, headers_a)
    r_diag_a = post_record(client, headers_a, diagnosis_payload())
    assert r_diag_a.status_code == 201, r_diag_a.text
    diag_a = str(r_diag_a.json()["id"])
    r_diag_b = post_record(client, headers_b, diagnosis_payload())
    assert r_diag_b.status_code == 201, r_diag_b.text
    diag_b = str(r_diag_b.json()["id"])
    entry_a = post_chronic(
        client, headers_a, condition="hypothyroidism", diagnosis_id=diag_a
    )
    entry_b = post_chronic(
        client, headers_b, condition="hypothyroidism", diagnosis_id=diag_b
    )

    changed_foreign = crud.unlink_diagnosis(
        session=db, owner_id=owner_a, diagnosis_id=uuid.UUID(diag_b)
    )
    changed_own = crud.unlink_diagnosis(
        session=db, owner_id=owner_a, diagnosis_id=uuid.UUID(diag_a)
    )
    db.commit()

    assert changed_foreign == 0
    assert changed_own == 1
    assert (
        chronic_entries(client, headers_a)[str(entry_a["id"])].get("diagnosis_id")
        is None
    )
    assert (
        str(chronic_entries(client, headers_b)[str(entry_b["id"])]["diagnosis_id"])
        == diag_b
    )


def _setup_several_chronics(
    client: TestClient, headers: dict[str, str]
) -> tuple[str, dict[str, str]]:
    """Two chronic entries backed by D1, one by D2, one with no backing.
    Returns D1's id and the entry ids by role."""
    r_d1 = post_record(client, headers, diagnosis_payload())
    assert r_d1.status_code == 201, r_d1.text
    d1 = str(r_d1.json()["id"])
    r_d2 = post_record(client, headers, diagnosis_payload(title="Asma bronquial"))
    assert r_d2.status_code == 201, r_d2.text
    d2 = str(r_d2.json()["id"])
    ids = {
        "d1_first": post_chronic(
            client, headers, condition="hypothyroidism", diagnosis_id=d1
        )["id"],
        "d1_second": post_chronic(
            client, headers, condition="hypertension", diagnosis_id=d1
        )["id"],
        "d2": post_chronic(client, headers, condition="asthma", diagnosis_id=d2)["id"],
        "none": post_chronic(client, headers, condition="arthritis")["id"],
    }
    return d1, {role: str(entry_id) for role, entry_id in ids.items()} | {"d2_id": d2}


def test_b5_delete_diagnosis_unlinks_every_chronic_it_backs(
    client: TestClient, db: Session
) -> None:
    """Review R12, B-5 "una o más": dos crónicas respaldadas por D1 quedan sin
    respaldo; la de D2 y la que no tiene respaldo no cambian. Directo,
    crud.unlink_diagnosis devuelve 2."""
    headers = consented_user_headers(client, db)
    d1, ids = _setup_several_chronics(client, headers)

    r_delete = client.delete(record_url(d1), headers=headers)

    assert r_delete.status_code == 200, r_delete.text
    assert r_delete.json() == {"message": "Registro eliminado"}
    mine = chronic_entries(client, headers)
    assert len(mine) == 4
    assert mine[ids["d1_first"]].get("diagnosis_id") is None
    assert mine[ids["d1_second"]].get("diagnosis_id") is None
    assert str(mine[ids["d2"]]["diagnosis_id"]) == ids["d2_id"]
    assert mine[ids["none"]].get("diagnosis_id") is None
    assert mine[ids["d1_second"]]["condition"] == "hypertension"

    headers_direct = consented_user_headers(client, db)
    d1_direct, ids_direct = _setup_several_chronics(client, headers_direct)
    changed = crud.unlink_diagnosis(
        session=db,
        owner_id=user_id_of(client, headers_direct),
        diagnosis_id=uuid.UUID(d1_direct),
    )
    db.commit()

    assert changed == 2
    direct = chronic_entries(client, headers_direct)
    assert direct[ids_direct["d1_first"]].get("diagnosis_id") is None
    assert direct[ids_direct["d1_second"]].get("diagnosis_id") is None
    assert str(direct[ids_direct["d2"]]["diagnosis_id"]) == ids_direct["d2_id"]
