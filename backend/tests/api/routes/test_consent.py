"""Tests for express consent with retained evidence (grupo 3).

Contract (openspec/changes/cuenta-consentimiento/design.md §Interface contract):
- POST /api/v1/consent body {"version": "v1"} -> 201 {version, granted_at,
  auth_method}; idempotent per version.
- GET /api/v1/consent -> 200 {version, granted_at} or 404 if never granted.
- Dependency require_consent: without current consent -> 403
  {"detail": "CONSENT_REQUIRED"}. Probed through the minimal test router:
  POST /api/v1/health-records {"note": str} -> 201 {"id", "note", "owner_id"}.
- Google signup (GET /api/v1/login/google/callback, mock point
  app.core.google_oauth.exchange_code) does NOT imply consent.

Spec: openspec/changes/cuenta-consentimiento/specs/privacy/consent/spec.md.
"""

from collections.abc import Generator
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.models import User, UserCreate
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


@contextmanager
def patched_exchange_code(claims: SimpleNamespace) -> Generator[None]:
    """Patch app.core.google_oauth.exchange_code (mock point fixed in design).

    If the module does not exist yet (red phase), skip the patch so the test
    fails on the endpoint response (404) instead of erroring at collection.
    """

    async def fake_exchange_code(code: str) -> Any:
        return claims

    try:
        patcher = patch(
            "app.core.google_oauth.exchange_code", new=fake_exchange_code, create=True
        )
        patcher.start()
    except (ModuleNotFoundError, ImportError, AttributeError):
        yield
        return
    try:
        yield
    finally:
        patcher.stop()


def post_health_record(
    client: TestClient, headers: dict[str, str], note: str = "diagnóstico x"
) -> Any:
    return client.post(
        f"{settings.API_V1_STR}/health-records",
        headers=headers,
        json={"note": note},
    )


def test_ac1_capture_without_consent_is_rejected_with_consent_required(
    client: TestClient, db: Session
) -> None:
    """Intento de captura sin consentimiento: 403 CONSENT_REQUIRED."""
    _user, headers = random_user_token_headers(client, db)

    r = post_health_record(client, headers, note="diagnóstico x")

    assert r.status_code == 403
    assert r.json()["detail"] == "CONSENT_REQUIRED"


def test_ac2_granting_consent_records_evidence_and_enables_capture(
    client: TestClient, db: Session
) -> None:
    """Otorgamiento en el alta: 201 con evidencia y la captura se habilita."""
    user, headers = random_user_token_headers(client, db)

    r = client.post(
        f"{settings.API_V1_STR}/consent", headers=headers, json={"version": "v1"}
    )

    assert r.status_code == 201
    grant = r.json()
    assert grant["version"] == "v1"
    assert grant["granted_at"]
    assert grant["auth_method"]

    r_record = post_health_record(client, headers, note="diagnóstico x")
    assert r_record.status_code == 201
    record = r_record.json()
    assert record["id"]
    assert record["note"] == "diagnóstico x"
    assert str(record["owner_id"]) == str(user.id)


def test_ac2_consent_is_idempotent_per_version(
    client: TestClient, db: Session
) -> None:
    """Segundo POST /consent v1 no crea un otorgamiento nuevo."""
    _user, headers = random_user_token_headers(client, db)

    r_first = client.post(
        f"{settings.API_V1_STR}/consent", headers=headers, json={"version": "v1"}
    )
    assert r_first.status_code == 201
    granted_at_first = r_first.json()["granted_at"]

    r_second = client.post(
        f"{settings.API_V1_STR}/consent", headers=headers, json={"version": "v1"}
    )
    assert r_second.status_code in (200, 201)

    r_get = client.get(f"{settings.API_V1_STR}/consent", headers=headers)
    assert r_get.status_code == 200
    current = r_get.json()
    assert current["version"] == "v1"
    assert current["granted_at"] == granted_at_first


def test_ac3_consent_is_queryable_by_its_owner(
    client: TestClient, db: Session
) -> None:
    """Consultable por el titular: GET devuelve versión y fecha tras otorgar."""
    _user, headers = random_user_token_headers(client, db)

    r_post = client.post(
        f"{settings.API_V1_STR}/consent", headers=headers, json={"version": "v1"}
    )
    assert r_post.status_code == 201
    granted_at = r_post.json()["granted_at"]

    r_get = client.get(f"{settings.API_V1_STR}/consent", headers=headers)

    assert r_get.status_code == 200
    body = r_get.json()
    assert body["version"] == "v1"
    assert body["granted_at"] == granted_at


def test_ac3_consent_query_without_grant_returns_404(
    client: TestClient, db: Session
) -> None:
    """Sin otorgamiento GET /consent es 404; tras otorgar deja de serlo.

    The second half guards against a vacuous pass: a missing route is also a
    404, but only a real endpoint flips to 200 once consent is granted.
    """
    _user, headers = random_user_token_headers(client, db)

    r_before = client.get(f"{settings.API_V1_STR}/consent", headers=headers)
    assert r_before.status_code == 404

    r_grant = client.post(
        f"{settings.API_V1_STR}/consent", headers=headers, json={"version": "v1"}
    )
    assert r_grant.status_code == 201

    r_after = client.get(f"{settings.API_V1_STR}/consent", headers=headers)
    assert r_after.status_code == 200


def test_ac4_google_signup_does_not_imply_consent(
    client: TestClient, db: Session
) -> None:
    """Alta con Google no implica consentimiento: la captura sigue bloqueada."""
    email = random_email()
    claims = SimpleNamespace(
        sub="google-sub-consent", email=email, email_verified=True
    )
    with patched_exchange_code(claims):
        r_callback = client.get(
            f"{settings.API_V1_STR}/login/google/callback",
            params={"code": "any-authorization-code"},
        )

    assert r_callback.status_code == 200
    token = r_callback.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    r = post_health_record(client, headers, note="diagnóstico x")

    assert r.status_code == 403
    assert r.json()["detail"] == "CONSENT_REQUIRED"
