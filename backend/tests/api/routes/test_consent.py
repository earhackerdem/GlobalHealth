"""Tests for express consent with retained evidence (grupo 3).

Contract (openspec/changes/cuenta-consentimiento/design.md §Interface contract
+ approved review findings H6/H13):
- POST /api/v1/consent/ body {"version": "v1"} -> 201 {version, granted_at,
  auth_method}; idempotent per version (second POST -> exactly 200, ONE row).
- Unknown version -> 400 "Versión de consentimiento desconocida".
- GET /api/v1/consent/ -> 200 {version, granted_at} or 404 if never granted.
- auth_method comes from the token's ``amr`` claim ("google" | "password"),
  not from inferring on hashed_password.
- require_consent demands a grant of the CURRENT version (max of
  CONSENT_TEXTS): a v1 grant stops opening capture once v2 exists. Probed
  through POST /api/v1/health-records/ with a diagnosis payload
  {"record_type": "diagnosis", "title": str, "occurred_on": "YYYY-MM-DD"}
  -> 201 (expediente-registros design.md §Interface contract).
- Google signup (GET /api/v1/login/google/callback) does NOT imply consent.

Spec: openspec/changes/cuenta-consentimiento/specs/privacy/consent/spec.md.
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, select

from app import crud
from app.core.config import settings
from app.core.consent_text import CONSENT_TEXTS
from app.models import ConsentGrant, User, UserCreate
from tests.utils.google import (
    google_callback,
    google_claims,
    patched_exchange_code,
    token_from_redirect,
)
from tests.utils.utils import random_email, random_lower_string


def random_user_token_headers(
    client: TestClient, db: Session
) -> tuple[User, dict[str, str]]:
    """Create a fresh random user (no consent granted) and log it in.

    A new user per test keeps consent state from leaking between tests.
    """
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db, user_create=UserCreate(email=email, password=password)
    )
    r = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    token = r.json()["access_token"]
    return user, {"Authorization": f"Bearer {token}"}


def post_consent(
    client: TestClient, headers: dict[str, str], version: str = "v1"
) -> Any:
    return client.post(
        f"{settings.API_V1_STR}/consent/", headers=headers, json={"version": version}
    )


def get_consent(client: TestClient, headers: dict[str, str]) -> Any:
    return client.get(f"{settings.API_V1_STR}/consent/", headers=headers)


def post_health_record(
    client: TestClient, headers: dict[str, str], title: str = "diagnóstico x"
) -> Any:
    return client.post(
        f"{settings.API_V1_STR}/health-records/",
        headers=headers,
        json={
            "record_type": "diagnosis",
            "title": title,
            "occurred_on": "2026-09-30",
        },
    )


def test_ac1_capture_without_consent_is_rejected_with_consent_required(
    client: TestClient, db: Session
) -> None:
    """Intento de captura sin consentimiento: 403 CONSENT_REQUIRED."""
    _user, headers = random_user_token_headers(client, db)

    r = post_health_record(client, headers, title="diagnóstico x")

    assert r.status_code == 403
    assert r.json()["detail"] == "CONSENT_REQUIRED"


def test_ac2_granting_consent_records_evidence_and_enables_capture(
    client: TestClient, db: Session
) -> None:
    """Otorgamiento en el alta: 201 con evidencia y la captura se habilita."""
    user, headers = random_user_token_headers(client, db)

    r = post_consent(client, headers)

    assert r.status_code == 201
    grant = r.json()
    assert grant["version"] == "v1"
    assert grant["granted_at"]
    # Password login session: the amr claim fixes the auth method exactly.
    assert grant["auth_method"] == "password"

    r_record = post_health_record(client, headers, title="diagnóstico x")
    assert r_record.status_code == 201
    record = r_record.json()
    assert record["id"]
    assert record["title"] == "diagnóstico x"
    assert str(record["owner_id"]) == str(user.id)


def test_ac2_consent_is_idempotent_per_version(client: TestClient, db: Session) -> None:
    """Segundo POST /consent/ v1: exactamente 200 y UNA sola fila en la BD."""
    user, headers = random_user_token_headers(client, db)

    r_first = post_consent(client, headers)
    assert r_first.status_code == 201
    granted_at_first = r_first.json()["granted_at"]

    r_second = post_consent(client, headers)
    assert r_second.status_code == 200

    r_get = get_consent(client, headers)
    assert r_get.status_code == 200
    current = r_get.json()
    assert current["version"] == "v1"
    assert current["granted_at"] == granted_at_first

    db.expire_all()
    rows = db.exec(
        select(ConsentGrant)
        .where(ConsentGrant.user_id == user.id)
        .where(ConsentGrant.version == "v1")
    ).all()
    assert len(rows) == 1


def test_consent_unknown_version_is_rejected(client: TestClient, db: Session) -> None:
    """Versión desconocida: 400 con detail es-MX fijo."""
    _user, headers = random_user_token_headers(client, db)

    r = post_consent(client, headers, version="v999")

    assert r.status_code == 400
    assert r.json()["detail"] == "Versión de consentimiento desconocida"


def test_ac3_consent_is_queryable_by_its_owner(client: TestClient, db: Session) -> None:
    """Consultable por el titular: GET devuelve versión y fecha tras otorgar."""
    _user, headers = random_user_token_headers(client, db)

    r_post = post_consent(client, headers)
    assert r_post.status_code == 201
    granted_at = r_post.json()["granted_at"]

    r_get = get_consent(client, headers)

    assert r_get.status_code == 200
    body = r_get.json()
    assert body["version"] == "v1"
    assert body["granted_at"] == granted_at


def test_ac3_consent_query_without_grant_returns_404(
    client: TestClient, db: Session
) -> None:
    """Sin otorgamiento GET /consent/ es 404; tras otorgar deja de serlo.

    The second half guards against a vacuous pass: a missing route is also a
    404, but only a real endpoint flips to 200 once consent is granted.
    """
    _user, headers = random_user_token_headers(client, db)

    r_before = get_consent(client, headers)
    assert r_before.status_code == 404

    r_grant = post_consent(client, headers)
    assert r_grant.status_code == 201

    r_after = get_consent(client, headers)
    assert r_after.status_code == 200


def test_ac4_google_signup_does_not_imply_consent(client: TestClient) -> None:
    """Alta con Google no implica consentimiento: la captura sigue bloqueada."""
    email = random_email()
    with patched_exchange_code(google_claims(sub="google-sub-consent", email=email)):
        r_callback = google_callback(client)

    token = token_from_redirect(r_callback)
    headers = {"Authorization": f"Bearer {token}"}

    r = post_health_record(client, headers, title="diagnóstico x")

    assert r.status_code == 403
    assert r.json()["detail"] == "CONSENT_REQUIRED"


def test_consent_auth_method_from_google_session_on_linked_account(
    client: TestClient, db: Session
) -> None:
    """Cuenta creada por password + vinculada a Google + sesión Google:
    la fila registra auth_method == "google" (claim amr, no inferencia H6)."""
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db, user_create=UserCreate(email=email, password=password)
    )

    with patched_exchange_code(google_claims(sub="google-sub-h6", email=email)):
        r_callback = google_callback(client)
    token = token_from_redirect(r_callback)
    headers = {"Authorization": f"Bearer {token}"}

    r = post_consent(client, headers)

    assert r.status_code == 201
    assert r.json()["auth_method"] == "google"

    db.expire_all()
    grant = db.exec(select(ConsentGrant).where(ConsentGrant.user_id == user.id)).one()
    assert grant.auth_method == "google"


def test_consent_must_be_of_the_current_version(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vigencia (H13): al aparecer v2, un grant v1 ya no abre la captura."""
    _user, headers = random_user_token_headers(client, db)

    r_v1 = post_consent(client, headers, version="v1")
    assert r_v1.status_code == 201
    assert post_health_record(client, headers).status_code == 201

    monkeypatch.setitem(
        CONSENT_TEXTS, "v2", "Texto de consentimiento v2 de prueba (vigente)."
    )

    r_blocked = post_health_record(client, headers)
    assert r_blocked.status_code == 403
    assert r_blocked.json()["detail"] == "CONSENT_REQUIRED"

    r_v2 = post_consent(client, headers, version="v2")
    assert r_v2.status_code == 201
    assert post_health_record(client, headers).status_code == 201
