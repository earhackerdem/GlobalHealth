"""Tests for the clinical record book (expediente-registros, US-04, grupo 1).

Contract (openspec/changes/expediente-registros/design.md §Interface contract):
- POST /api/v1/health-records/ with a payload discriminated by ``record_type``:
  - diagnosis: {record_type, title, occurred_on, professional?, notes?};
    title and occurred_on required.
  - prescription: {record_type, title, occurred_on, dose, valid_from,
    valid_to, notes?, professional?}; dose, valid_from and valid_to required.
  - Fields of the other type present -> 422.
  - 201 response: {id, record_type, occurred_on, title, professional, notes,
    dose, valid_from, valid_to, owner_id, created_at, updated_at} (fields
    that do not apply come back null).
- GET /api/v1/health-records/ -> envelope {"data": [...], "count": N}, ONLY
  the session user's records.
- GET|PATCH|DELETE /{id} -> 404 {"detail": "Registro no encontrado"},
  identical for a nonexistent id and for someone else's id. PATCH is partial;
  DELETE -> 200 {"message": "Registro eliminado"}.
- Everything behind auth + consent (403 CONSENT_REQUIRED without consent).
- Clinical content encrypted at rest in table ``healthrecord``.

Spec: openspec/changes/expediente-registros/specs/records/clinical-records/spec.md.
"""

import uuid
from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import UserCreate
from tests.utils.utils import random_email, random_lower_string


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
    """Scenario 'Registrar una receta con dosis y vigencia' concrete data."""
    payload: dict[str, Any] = {
        "record_type": "prescription",
        "title": "Levotiroxina 50 µg",
        "occurred_on": "2026-10-01",
        "dose": "1 tableta en ayunas cada 24 h",
        "valid_from": "2026-10-01",
        "valid_to": "2026-12-30",
    }
    payload.update(overrides)
    return payload


def post_record(
    client: TestClient, headers: dict[str, str], payload: dict[str, Any]
) -> Any:
    return client.post(
        f"{settings.API_V1_STR}/health-records/", headers=headers, json=payload
    )


def list_records(client: TestClient, headers: dict[str, str]) -> Any:
    return client.get(f"{settings.API_V1_STR}/health-records/", headers=headers)


# --- Scenario: Registrar un diagnóstico --------------------------------------


def test_ac1_register_diagnosis_returns_201_and_appears_in_list(
    client: TestClient, db: Session
) -> None:
    """Registrar un diagnóstico: 201 con sus campos y aparece al listar."""
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
    # Prescription-only fields do not apply to a diagnosis: they come back null.
    assert record["dose"] is None
    assert record["valid_from"] is None
    assert record["valid_to"] is None
    assert record["owner_id"]
    assert record["created_at"]
    assert record["updated_at"]

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    body = r_list.json()
    assert body["count"] == 1
    listed = body["data"]
    assert len(listed) == 1
    assert str(listed[0]["id"]) == str(record["id"])
    assert listed[0]["title"] == "Hipotiroidismo subclínico"


# --- Scenario: Registrar una receta con dosis y vigencia ----------------------


def test_ac2_register_prescription_with_dose_and_validity(
    client: TestClient, db: Session
) -> None:
    """Registrar una receta: 201 tipo prescription con medicamento, dosis y vigencia."""
    headers = consented_user_headers(client, db)

    r = post_record(client, headers, prescription_payload())

    assert r.status_code == 201, r.text
    record = r.json()
    assert record["id"]
    assert record["record_type"] == "prescription"
    assert record["title"] == "Levotiroxina 50 µg"
    assert record["dose"] == "1 tableta en ayunas cada 24 h"
    assert record["valid_from"] == "2026-10-01"
    assert record["valid_to"] == "2026-12-30"


@pytest.mark.parametrize("missing_field", ["dose", "valid_from", "valid_to"])
def test_ac2_prescription_without_dose_or_validity_is_rejected(
    client: TestClient, db: Session, missing_field: str
) -> None:
    """Receta sin dosis o sin vigencia: 422."""
    headers = consented_user_headers(client, db)
    payload = prescription_payload()
    del payload[missing_field]

    r = post_record(client, headers, payload)

    assert r.status_code == 422, r.text


def test_ac2_diagnosis_with_prescription_fields_is_rejected(
    client: TestClient, db: Session
) -> None:
    """Diagnóstico con campos de receta (dose/valid_from/valid_to): 422."""
    headers = consented_user_headers(client, db)
    payload = diagnosis_payload(
        dose="1 tableta cada 24 h",
        valid_from="2026-10-01",
        valid_to="2026-12-30",
    )

    r = post_record(client, headers, payload)

    assert r.status_code == 422, r.text


# --- Scenario: Contenido clínico cifrado en reposo ----------------------------


def test_ac3_clinical_content_is_encrypted_at_rest(
    client: TestClient, db: Session
) -> None:
    """title, professional, notes y dose son ciphertext en la tabla healthrecord.

    Raw SQL over the ``healthrecord`` table: the clinical columns hold Fernet
    tokens (urlsafe-b64 of the 0x80 version byte: "gAAAA") and no column of
    either row contains the plaintext clinical terms.
    """
    headers = consented_user_headers(client, db)

    r_diag = post_record(client, headers, diagnosis_payload())
    assert r_diag.status_code == 201, r_diag.text
    diag_id = r_diag.json()["id"]

    r_rx = post_record(client, headers, prescription_payload())
    assert r_rx.status_code == 201, r_rx.text
    rx_id = r_rx.json()["id"]

    db.expire_all()
    diag_row = (
        db.execute(
            text("SELECT * FROM healthrecord WHERE id = CAST(:id AS uuid)"),
            {"id": str(diag_id)},
        )
        .mappings()
        .one()
    )
    rx_row = (
        db.execute(
            text("SELECT * FROM healthrecord WHERE id = CAST(:id AS uuid)"),
            {"id": str(rx_id)},
        )
        .mappings()
        .one()
    )

    # Clinical columns are ciphertext, never the plaintext.
    for column in ("title", "professional", "notes"):
        assert str(diag_row[column]).startswith("gAAAA"), (column, diag_row[column])
    for column in ("title", "dose"):
        assert str(rx_row[column]).startswith("gAAAA"), (column, rx_row[column])

    # No column of either raw row leaks the clinical terms in the clear.
    for value in diag_row.values():
        assert "Hipotiroidismo" not in str(value)
    for value in rx_row.values():
        assert "Levotiroxina" not in str(value)


# --- Scenario: Sin consentimiento no entra ni un dato --------------------------
# The POST probe lives in test_consent.py (migrated payload). This test covers
# the rest of the THEN: GET is also 403 CONSENT_REQUIRED and nothing persists.


def test_ac4_without_consent_get_and_post_are_blocked_and_nothing_persists(
    client: TestClient, db: Session
) -> None:
    """Sin consentimiento: POST y GET -> 403 CONSENT_REQUIRED y nada persiste."""
    headers = user_without_consent_headers(client, db)

    r_post = post_record(client, headers, diagnosis_payload())
    assert r_post.status_code == 403
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


# --- Scenario: Un registro ajeno no existe para mí -----------------------------


def test_ac5_foreign_record_is_indistinguishable_from_nonexistent(
    client: TestClient, db: Session
) -> None:
    """GET, PATCH y DELETE de un id ajeno: el MISMO 404 que un UUID inexistente.

    Same status AND same {"detail": "Registro no encontrado"} body, so an
    attacker cannot tell a foreign record apart from one that does not exist.
    B (with consent) also never sees A's record in their own list.
    """
    headers_a = consented_user_headers(client, db)
    headers_b = consented_user_headers(client, db)

    r_a = post_record(client, headers_a, diagnosis_payload())
    assert r_a.status_code == 201, r_a.text
    foreign_id = r_a.json()["id"]
    missing_id = str(uuid.uuid4())

    # B's list does not contain A's record.
    r_list_b = list_records(client, headers_b)
    assert r_list_b.status_code == 200, r_list_b.text
    assert r_list_b.json()["count"] == 0
    assert str(foreign_id) not in r_list_b.text
    assert "Hipotiroidismo" not in r_list_b.text

    patch_body = {"notes": "intento de edición ajena"}
    for method, kwargs in (
        ("GET", {}),
        ("PATCH", {"json": patch_body}),
        ("DELETE", {}),
    ):
        r_foreign = client.request(
            method,
            f"{settings.API_V1_STR}/health-records/{foreign_id}",
            headers=headers_b,
            **kwargs,
        )
        r_missing = client.request(
            method,
            f"{settings.API_V1_STR}/health-records/{missing_id}",
            headers=headers_b,
            **kwargs,
        )
        assert r_foreign.status_code == 404, (method, r_foreign.text)
        assert r_missing.status_code == 404, (method, r_missing.text)
        assert r_foreign.json() == {"detail": "Registro no encontrado"}, method
        assert r_foreign.json() == r_missing.json(), method
        assert "Hipotiroidismo" not in r_foreign.text, method


# --- Scenario: Corregir y eliminar un registro propio --------------------------


def test_ac6_patch_own_prescription_dose_is_reflected(
    client: TestClient, db: Session
) -> None:
    """PATCH parcial de la dosis: 200 y se refleja al reconsultar."""
    headers = consented_user_headers(client, db)
    r_create = post_record(client, headers, prescription_payload())
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]
    new_dose = "1 tableta en ayunas cada 24 h, lunes a sábado"

    r_patch = client.patch(
        f"{settings.API_V1_STR}/health-records/{record_id}",
        headers=headers,
        json={"dose": new_dose},
    )

    assert r_patch.status_code == 200, r_patch.text
    assert r_patch.json()["dose"] == new_dose

    r_get = client.get(
        f"{settings.API_V1_STR}/health-records/{record_id}", headers=headers
    )
    assert r_get.status_code == 200, r_get.text
    body = r_get.json()
    assert body["dose"] == new_dose
    # Partial update: untouched fields keep their values.
    assert body["title"] == "Levotiroxina 50 µg"
    assert body["valid_from"] == "2026-10-01"
    assert body["valid_to"] == "2026-12-30"


def test_ac6_delete_own_record_then_gone(client: TestClient, db: Session) -> None:
    """DELETE propio: 200 'Registro eliminado'; luego GET 404 y fuera de la lista."""
    headers = consented_user_headers(client, db)
    r_create = post_record(client, headers, diagnosis_payload())
    assert r_create.status_code == 201, r_create.text
    record_id = r_create.json()["id"]

    r_delete = client.delete(
        f"{settings.API_V1_STR}/health-records/{record_id}", headers=headers
    )

    assert r_delete.status_code == 200, r_delete.text
    assert r_delete.json() == {"message": "Registro eliminado"}

    r_get = client.get(
        f"{settings.API_V1_STR}/health-records/{record_id}", headers=headers
    )
    assert r_get.status_code == 404
    assert r_get.json() == {"detail": "Registro no encontrado"}

    r_list = list_records(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
    assert str(record_id) not in r_list.text
