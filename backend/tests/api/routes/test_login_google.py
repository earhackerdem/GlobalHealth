"""Tests for Google OIDC login/signup (Authorization Code + PKCE + state).

Contract (openspec/changes/cuenta-consentimiento/design.md + approved review
findings H1/H2/H3 of /epe-4-review):
- GET /api/v1/login/google -> 307 to accounts.google.com with code_challenge
  (S256) AND a random ``state``; sets cookie g_pkce = Fernet of
  {"v": verifier, "s": state}.
- GET /api/v1/login/google/callback?code&state -> REQUIRES a valid g_pkce
  cookie and a matching state. Missing/undecipherable cookie or
  missing/mismatching state -> 400 "Solicitud de autorización inválida o
  expirada" and the cookie is deleted (Set-Cookie Max-Age=0, also on error).
  Success -> 307 RedirectResponse to
  {FRONTEND_HOST}/google-callback#access_token=<jwt>&token_type=bearer with
  Cache-Control: no-store and Pragma: no-cache, cookie deleted.
- exchange_code is called as exchange_code(code, code_verifier=<verifier>).
- The issued JWT carries claim amr: "google" (callback) or "password"
  (POST /login/access-token).
- Mock point: app.core.google_oauth.exchange_code. Google is NEVER called.
"""

import json
from urllib.parse import parse_qs, urlsplit

import jwt
import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, func, select

from app import crud
from app.core.config import settings
from app.core.encrypted import decrypt_str
from app.core.security import ALGORITHM
from app.models import User, UserCreate
from tests.utils.google import (
    DEFAULT_VERIFIER,
    PKCE_COOKIE,
    assert_pkce_cookie_deleted,
    google_callback,
    google_claims,
    make_pkce_cookie,
    patched_exchange_code,
    token_from_redirect,
)
from tests.utils.utils import random_email, random_lower_string

INVALID_AUTH_DETAIL = "Solicitud de autorización inválida o expirada"


def count_users(db: Session) -> int:
    return db.exec(select(func.count()).select_from(User)).one()


def decode_access_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])


# --- GET /login/google: redirect with PKCE + state and encrypted cookie ------


def test_contract_google_login_redirects_with_state_and_pkce_cookie(
    client: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Redirect to accounts.google.com carries state + S256 challenge and the
    g_pkce cookie holds Fernet({"v": verifier, "s": that same state})."""
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client-id")
    monkeypatch.setattr(
        settings,
        "GOOGLE_REDIRECT_URI",
        "http://localhost/api/v1/login/google/callback",
    )

    r = client.get(f"{settings.API_V1_STR}/login/google", follow_redirects=False)

    assert r.status_code in (302, 307)
    location = r.headers["location"]
    assert "accounts.google.com" in location
    assert "code_challenge=" in location
    assert "code_challenge_method=S256" in location
    assert "state=" in location

    cookie_value = r.cookies.get(PKCE_COOKIE)
    assert cookie_value, "login must set the g_pkce cookie"
    payload = decrypt_str(cookie_value)
    assert payload is not None, "g_pkce must be a valid Fernet token"
    data = json.loads(payload)
    assert data["v"], "cookie must carry the PKCE verifier"
    assert data["s"], "cookie must carry the state"

    # The state in the authorization URL is the one sealed in the cookie.
    query = parse_qs(urlsplit(location).query)
    assert query["state"] == [data["s"]]


# --- Callback: cookie + state are REQUIRED (findings H1/H2) ------------------


def test_callback_without_cookie_is_rejected_and_cookie_deleted(
    client: TestClient,
) -> None:
    """Callback with no g_pkce cookie: 400 and the cookie is deleted."""
    email = random_email()
    with patched_exchange_code(google_claims(email=email)) as recorder:
        r = google_callback(client, cookie=None)

    assert r.status_code == 400
    assert r.json()["detail"] == INVALID_AUTH_DETAIL
    assert_pkce_cookie_deleted(r)
    assert recorder.calls == [], "code must not be exchanged without PKCE proof"


def test_callback_with_undecipherable_cookie_is_rejected(
    client: TestClient,
) -> None:
    """Callback with a tampered/garbage g_pkce cookie: 400 and cookie deleted."""
    email = random_email()
    with patched_exchange_code(google_claims(email=email)) as recorder:
        r = google_callback(client, cookie="not-a-fernet-token")

    assert r.status_code == 400
    assert r.json()["detail"] == INVALID_AUTH_DETAIL
    assert_pkce_cookie_deleted(r)
    assert recorder.calls == []


def test_callback_with_mismatching_state_is_rejected(client: TestClient) -> None:
    """Valid cookie but a different state: 400 and cookie deleted."""
    email = random_email()
    with patched_exchange_code(google_claims(email=email)) as recorder:
        r = google_callback(
            client,
            cookie=make_pkce_cookie(state="expected-state"),
            state="attacker-state",
        )

    assert r.status_code == 400
    assert r.json()["detail"] == INVALID_AUTH_DETAIL
    assert_pkce_cookie_deleted(r)
    assert recorder.calls == []


def test_callback_without_state_is_rejected(client: TestClient) -> None:
    """Valid cookie but no state query param: 400 and cookie deleted."""
    email = random_email()
    with patched_exchange_code(google_claims(email=email)) as recorder:
        r = google_callback(client, state=None)

    assert r.status_code == 400
    assert r.json()["detail"] == INVALID_AUTH_DETAIL
    assert_pkce_cookie_deleted(r)
    assert recorder.calls == []


# --- Callback success: redirect with fragment token (contract B) -------------


def test_ac1_google_signup_creates_account_without_local_password(
    client: TestClient, db: Session
) -> None:
    """Alta con Google: new user, no local password, working session token."""
    email = random_email()
    assert crud.get_user_by_email(session=db, email=email) is None

    claims = google_claims(sub="google-sub-signup", email=email)
    with patched_exchange_code(claims) as recorder:
        r = google_callback(client)

    assert r.status_code == 307
    token = token_from_redirect(r)
    assert r.headers.get("cache-control") == "no-store"
    assert r.headers.get("pragma") == "no-cache"
    assert_pkce_cookie_deleted(r)

    # The PKCE verifier sealed in the cookie reached the code exchange (H3).
    assert recorder.calls == [
        {"code": "any-authorization-code", "code_verifier": DEFAULT_VERIFIER}
    ]

    db.expire_all()
    user = crud.get_user_by_email(session=db, email=email)
    assert user is not None
    assert user.hashed_password is None

    headers = {"Authorization": f"Bearer {token}"}
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

    claims = google_claims(sub="google-sub-linked", email=email)
    with patched_exchange_code(claims):
        r = google_callback(client)

    token = token_from_redirect(r)

    db.expire_all()
    assert count_users(db) == users_before

    headers = {"Authorization": f"Bearer {token}"}
    r_me = client.get(f"{settings.API_V1_STR}/users/me", headers=headers)
    assert r_me.status_code == 200
    me = r_me.json()
    assert me["email"] == email
    assert str(me["id"]) == str(user.id)


def test_ac3_unverified_google_email_is_rejected_and_no_user_created(
    client: TestClient, db: Session
) -> None:
    """Correo no verificado por Google: 400 es-MX and no account is created."""
    email = random_email()
    users_before = count_users(db)

    claims = google_claims(sub="google-sub-unverified", email=email, email_verified=False)
    with patched_exchange_code(claims):
        r = google_callback(client)

    assert r.status_code == 400
    assert r.json()["detail"] == "El correo de la cuenta de Google no está verificado"
    assert_pkce_cookie_deleted(r)

    db.expire_all()
    assert crud.get_user_by_email(session=db, email=email) is None
    assert count_users(db) == users_before


def test_callback_inactive_user_is_rejected(client: TestClient, db: Session) -> None:
    """Cuenta existente inactiva: 400 "Usuario inactivo" (es-MX)."""
    email = random_email()
    user = crud.create_user(
        session=db,
        user_create=UserCreate(email=email, password=random_lower_string()),
    )
    user.is_active = False
    db.add(user)
    db.commit()

    with patched_exchange_code(google_claims(sub="google-sub-inactive", email=email)):
        r = google_callback(client)

    assert r.status_code == 400
    assert r.json()["detail"] == "Usuario inactivo"


# --- amr claim (contract C) ---------------------------------------------------


def test_google_callback_token_carries_amr_google(client: TestClient) -> None:
    """The JWT issued by the Google callback carries amr: "google"."""
    email = random_email()
    with patched_exchange_code(google_claims(sub="google-sub-amr", email=email)):
        r = google_callback(client)

    token = token_from_redirect(r)
    payload = decode_access_token(token)
    assert payload["amr"] == "google"


def test_password_login_token_carries_amr_password(client: TestClient, db: Session) -> None:
    """The JWT issued by POST /login/access-token carries amr: "password"."""
    email = random_email()
    password = random_lower_string()
    crud.create_user(session=db, user_create=UserCreate(email=email, password=password))

    r = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200
    payload = decode_access_token(r.json()["access_token"])
    assert payload["amr"] == "password"
