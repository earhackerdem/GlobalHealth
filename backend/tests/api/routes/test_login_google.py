"""Tests for Google OIDC login/signup.

Contract (openspec/changes/cuenta-consentimiento/design.md):
- GET /api/v1/login/google -> redirect to Google (accounts.google.com).
- GET /api/v1/login/google/callback?code=... -> creates or links the account by
  Google-verified email and returns Token {access_token, token_type: "bearer"}.
  Unverified email -> 400.
- Mock point: app.core.google_oauth.exchange_code(code: str) -> GoogleClaims
  {sub: str, email: str, email_verified: bool}. Google is NEVER called in tests.
"""

from collections.abc import Generator
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, func, select

from app import crud
from app.core.config import settings
from app.models import User, UserCreate
from tests.utils.utils import random_email, random_lower_string


def google_claims(
    *, sub: str = "google-sub-1", email: str, email_verified: bool = True
) -> SimpleNamespace:
    """Stub with the GoogleClaims attributes fixed in the design contract."""
    return SimpleNamespace(sub=sub, email=email, email_verified=email_verified)


@contextmanager
def patched_exchange_code(claims: SimpleNamespace) -> Generator[None]:
    """Patch app.core.google_oauth.exchange_code to return the given claims.

    If the module does not exist yet (red phase), skip the patch so the test
    fails on the endpoint response (404) instead of erroring at collection.
    """

    async def fake_exchange_code(_code: str) -> Any:
        return claims

    try:
        patcher = patch(
            "app.core.google_oauth.exchange_code", new=fake_exchange_code, create=True
        )
        patcher.start()
    except ModuleNotFoundError, ImportError, AttributeError:
        yield
        return
    try:
        yield
    finally:
        patcher.stop()


def set_google_setting(monkeypatch: pytest.MonkeyPatch, name: str, value: str) -> None:
    """Patch a Google setting if the Settings model already defines it.

    In the red phase Settings has no Google fields (pydantic rejects unknown
    attributes); the test must then fail on the missing endpoint, not here.
    """
    try:
        monkeypatch.setattr(settings, name, value, raising=False)
    except ValueError:
        pass


def count_users(db: Session) -> int:
    return db.exec(select(func.count()).select_from(User)).one()


def test_ac1_google_signup_creates_account_without_local_password(
    client: TestClient, db: Session
) -> None:
    """Alta con Google: new user, no local password, working session token."""
    email = random_email()
    assert crud.get_user_by_email(session=db, email=email) is None

    claims = google_claims(sub="google-sub-signup", email=email, email_verified=True)
    with patched_exchange_code(claims):
        r = client.get(
            f"{settings.API_V1_STR}/login/google/callback",
            params={"code": "any-authorization-code"},
        )

    assert r.status_code == 200
    token = r.json()
    assert token["access_token"]
    assert token["token_type"] == "bearer"

    db.expire_all()
    user = crud.get_user_by_email(session=db, email=email)
    assert user is not None
    assert user.hashed_password is None

    headers = {"Authorization": f"Bearer {token['access_token']}"}
    r_me = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r_me.status_code == 200
    assert r_me.json()["email"] == email


def test_ac2_google_login_with_registered_email_links_same_account(
    client: TestClient, db: Session
) -> None:
    """Google con correo ya registrado: same user_id, no duplicate account."""
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db, user_create=UserCreate(email=email, password=password)
    )
    users_before = count_users(db)

    claims = google_claims(sub="google-sub-linked", email=email, email_verified=True)
    with patched_exchange_code(claims):
        r = client.get(
            f"{settings.API_V1_STR}/login/google/callback",
            params={"code": "any-authorization-code"},
        )

    assert r.status_code == 200
    token = r.json()
    assert token["access_token"]
    assert token["token_type"] == "bearer"

    db.expire_all()
    assert count_users(db) == users_before

    headers = {"Authorization": f"Bearer {token['access_token']}"}
    r_me = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r_me.status_code == 200
    me = r_me.json()
    assert me["email"] == email
    assert str(me["id"]) == str(user.id)


def test_ac3_unverified_google_email_is_rejected_and_no_user_created(
    client: TestClient, db: Session
) -> None:
    """Correo no verificado por Google: 400 and no account is created."""
    email = random_email()
    users_before = count_users(db)

    claims = google_claims(
        sub="google-sub-unverified", email=email, email_verified=False
    )
    with patched_exchange_code(claims):
        r = client.get(
            f"{settings.API_V1_STR}/login/google/callback",
            params={"code": "any-authorization-code"},
        )

    assert r.status_code == 400

    db.expire_all()
    assert crud.get_user_by_email(session=db, email=email) is None
    assert count_users(db) == users_before


def test_contract_google_login_redirects_to_google(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """GET /login/google responds with a redirect to accounts.google.com."""
    set_google_setting(monkeypatch, "GOOGLE_CLIENT_ID", "test-client-id")
    set_google_setting(
        monkeypatch,
        "GOOGLE_REDIRECT_URI",
        "http://localhost/api/v1/login/google/callback",
    )

    r = client.get(f"{settings.API_V1_STR}/login/google", follow_redirects=False)

    assert r.status_code in (302, 307)
    assert "accounts.google.com" in r.headers["location"]
