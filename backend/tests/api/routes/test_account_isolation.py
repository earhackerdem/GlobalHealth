"""Tests for account isolation + email signup scenarios (grupo 4).

Spec: openspec/changes/cuenta-consentimiento/specs/identity/user-auth/spec.md
(scenarios "Alta exitosa con correo", "Correo ya registrado", "Acceso a
recurso ajeno por identificador", "Listados solo propios").

Contract (openspec/changes/cuenta-consentimiento/design.md §Interface contract
+ approved review findings H7/H13):
- POST /api/v1/users/signup and POST /api/v1/login/access-token (template).
- POST /api/v1/health-records/ {"note": str} -> auth + consent required ->
  201 {"id", "note", "owner_id"} persisted with the session user's owner_id.
- GET /api/v1/health-records/ -> template envelope {"data": [...], "count": N}
  with skip/limit, listing ONLY the session user's records.
- Foreign record by id -> not-found/not-authorized, resource never exposed.
- HealthRecordStub.note is encrypted at rest (EncryptedString): the ORM/API
  read plaintext, the raw column holds only ciphertext.

Email scenarios already partially covered by the template
(tests/api/routes/test_users.py): this file adds only the observable
behaviour those tests do not assert (login via API after signup; no data
leak on duplicate signup).
"""

from typing import Any

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import UserCreate
from tests.utils.utils import random_email, random_lower_string


def signup_via_api(client: TestClient, full_name: str | None = None) -> tuple[str, str]:
    """Register a fresh account through the public signup endpoint."""
    email = random_email()
    password = random_lower_string()
    data: dict[str, str] = {"email": email, "password": password}
    if full_name is not None:
        data["full_name"] = full_name
    r = client.post(f"{settings.API_V1_STR}/users/signup", json=data)
    assert 200 <= r.status_code < 300, r.text
    return email, password


def login_headers(client: TestClient, email: str, password: str) -> dict[str, str]:
    r = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def consented_user_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Fresh random user, logged in, with consent v1 granted."""
    email = random_email()
    password = random_lower_string()
    crud.create_user(session=db, user_create=UserCreate(email=email, password=password))
    headers = login_headers(client, email, password)
    r = client.post(
        f"{settings.API_V1_STR}/consent/", headers=headers, json={"version": "v1"}
    )
    assert r.status_code == 201, r.text
    return headers


def create_record(
    client: TestClient, headers: dict[str, str], note: str
) -> dict[str, Any]:
    r = client.post(
        f"{settings.API_V1_STR}/health-records/",
        headers=headers,
        json={"note": note},
    )
    assert r.status_code == 201, r.text
    record = r.json()
    assert record["id"]
    assert record["note"] == note
    return record


# --- Scenario: Alta exitosa con correo -------------------------------------
# Account creation itself is already covered by the template:
# tests/api/routes/test_users.py::test_register_user. What that test does NOT
# assert is the THEN's second observable: the person can log in through the
# API with those credentials.


def test_ac_email_signup_then_login_succeeds(client: TestClient) -> None:
    """Alta exitosa con correo: tras el signup se puede iniciar sesión."""
    email, password = signup_via_api(client)

    headers = login_headers(client, email, password)

    r_me = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r_me.status_code == 200
    assert r_me.json()["email"] == email


# --- Scenario: Correo ya registrado -----------------------------------------
# The rejection (400) is covered by the template:
# tests/api/routes/test_users.py::test_register_user_already_exists_error.
# What that test does NOT assert is the THEN's "sin revelar datos de la
# cuenta existente".


def test_ac_email_duplicate_signup_rejected_without_leaking_data(
    client: TestClient,
) -> None:
    """Correo ya registrado: rechazo sin datos de la cuenta existente."""
    secret_name = f"titular-{random_lower_string()}"
    email, _password = signup_via_api(client, full_name=secret_name)

    r = client.post(
        f"{settings.API_V1_STR}/users/signup",
        json={
            "email": email,
            "password": random_lower_string(),
            "full_name": "otro nombre",
        },
    )

    assert r.status_code == 400
    body = r.json()
    # Only a generic error message: no id, no profile data of the holder.
    assert set(body.keys()) == {"detail"}
    assert secret_name not in r.text


# --- Scenario: Acceso a recurso ajeno por identificador ----------------------


def test_ac_isolation_owner_reads_own_record_detail(
    client: TestClient, db: Session
) -> None:
    """El dueño sí accede a su recurso por id (GET detalle -> 200).

    Guard against a vacuous pass of the foreign-access test: a missing
    detail route is also a 404. The detail endpoint must exist and return
    200 with the note for its owner.
    """
    headers_b = consented_user_headers(client, db)
    record = create_record(client, headers_b, note="nota propia de B")

    r = client.get(
        f"{settings.API_V1_STR}/health-records/{record['id']}", headers=headers_b
    )

    assert r.status_code == 200, r.text
    body = r.json()
    assert str(body["id"]) == str(record["id"])
    assert body["note"] == "nota propia de B"
    assert str(body["owner_id"]) == str(record["owner_id"])


def test_ac_isolation_foreign_record_by_id_not_exposed(
    client: TestClient, db: Session
) -> None:
    """Acceso a recurso ajeno por id: 404/403 y el recurso no se expone."""
    headers_a = consented_user_headers(client, db)
    headers_b = consented_user_headers(client, db)
    secret_note = f"diagnóstico-confidencial-{random_lower_string()}"
    record_b = create_record(client, headers_b, note=secret_note)

    r = client.get(
        f"{settings.API_V1_STR}/health-records/{record_b['id']}", headers=headers_a
    )

    assert r.status_code in (403, 404)
    assert secret_note not in r.text


# --- Scenario: Listados solo propios -----------------------------------------


def test_ac_isolation_list_returns_only_own_records(
    client: TestClient, db: Session
) -> None:
    """A con 2 registros y B con 3: A lista exactamente sus 2, ninguno de B.

    Contract H13: the list endpoint returns the template envelope
    {"data": [...], "count": N} and honours skip/limit.
    """
    headers_a = consented_user_headers(client, db)
    headers_b = consented_user_headers(client, db)

    notes_a = [f"nota-A-{i}-{random_lower_string()}" for i in range(2)]
    notes_b = [f"nota-B-{i}-{random_lower_string()}" for i in range(3)]
    records_a = [create_record(client, headers_a, note) for note in notes_a]
    for note in notes_b:
        create_record(client, headers_b, note)

    r = client.get(f"{settings.API_V1_STR}/health-records/", headers=headers_a)

    assert r.status_code == 200, r.text
    body = r.json()
    assert body["count"] == 2
    listed = body["data"]
    assert len(listed) == 2
    assert {str(item["id"]) for item in listed} == {str(rec["id"]) for rec in records_a}
    assert {item["note"] for item in listed} == set(notes_a)
    for note in notes_b:
        assert note not in r.text

    # skip/limit: one page of 1, count still reports the owner's total.
    r_page = client.get(
        f"{settings.API_V1_STR}/health-records/",
        headers=headers_a,
        params={"skip": 1, "limit": 1},
    )
    assert r_page.status_code == 200, r_page.text
    page = r_page.json()
    assert page["count"] == 2
    assert len(page["data"]) == 1


# --- NFR-001: health data encrypted at rest (finding H7) ----------------------


def test_health_record_note_is_encrypted_at_rest(
    client: TestClient, db: Session
) -> None:
    """La nota se guarda cifrada: el SQL crudo no contiene el plaintext."""
    headers = consented_user_headers(client, db)
    secret_note = f"nota-en-reposo-{random_lower_string()}"
    record = create_record(client, headers, note=secret_note)

    raw_rows = db.execute(
        text("SELECT note FROM healthrecordstub WHERE id = CAST(:id AS uuid)"),
        {"id": str(record["id"])},
    ).all()
    assert len(raw_rows) == 1
    raw_note = raw_rows[0][0]
    assert raw_note != secret_note
    assert secret_note not in str(raw_note)
    # Fernet tokens are versioned with the 0x80 byte: urlsafe-b64 "gAAAA".
    assert str(raw_note).startswith("gAAAA")

    # And the ORM/API still read the plaintext back.
    r = client.get(
        f"{settings.API_V1_STR}/health-records/{record['id']}", headers=headers
    )
    assert r.status_code == 200
    assert r.json()["note"] == secret_note
