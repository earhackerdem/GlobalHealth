"""Shared helpers for the Google OIDC login tests (PKCE + state contract).

Contract (openspec/changes/cuenta-consentimiento/design.md + approved review
findings H1/H2/H3):
- GET /api/v1/login/google sets the ``g_pkce`` cookie: Fernet of a JSON
  ``{"v": <code_verifier>, "s": <state>}`` and sends ``state`` to Google.
- GET /api/v1/login/google/callback?code&state requires the cookie AND a
  matching state, calls ``exchange_code(code, code_verifier=<v>)`` and, on
  success, 307-redirects to ``{FRONTEND_HOST}/google-callback#access_token=…``.

The mock point is ``app.core.google_oauth.exchange_code``: it is patched
directly (no ``create=True``), so a missing symbol fails loudly with
AttributeError instead of silently testing nothing. Google is NEVER called.
"""

import json
from collections.abc import Generator
from contextlib import contextmanager
from types import SimpleNamespace
from typing import Any
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit

import httpx
from fastapi.testclient import TestClient

from app.core.config import settings
from app.core.encrypted import encrypt_str

PKCE_COOKIE = "g_pkce"

DEFAULT_VERIFIER = "test-code-verifier"
DEFAULT_STATE = "test-state"


def google_claims(
    *, sub: str = "google-sub-1", email: str, email_verified: bool = True
) -> SimpleNamespace:
    """Stub with the GoogleClaims attributes fixed in the design contract."""
    return SimpleNamespace(sub=sub, email=email, email_verified=email_verified)


class ExchangeCodeRecorder:
    """Fake exchange_code with the REAL signature that records its calls.

    Records (code, code_verifier) so tests can assert the PKCE verifier from
    the cookie actually reaches the Google exchange (finding H3).
    """

    def __init__(self, claims: Any) -> None:
        self.claims = claims
        self.calls: list[dict[str, Any]] = []

    async def __call__(self, code: str, code_verifier: str | None = None) -> Any:
        self.calls.append({"code": code, "code_verifier": code_verifier})
        return self.claims


@contextmanager
def patched_exchange_code(claims: Any) -> Generator[ExchangeCodeRecorder]:
    """Patch app.core.google_oauth.exchange_code (mock point fixed in design).

    No ``create=True``: if the symbol does not exist the patch raises
    AttributeError and the test errors, instead of passing vacuously.
    """
    recorder = ExchangeCodeRecorder(claims)
    with patch("app.core.google_oauth.exchange_code", new=recorder):
        yield recorder


def make_pkce_cookie(
    verifier: str = DEFAULT_VERIFIER, state: str = DEFAULT_STATE
) -> str:
    """Build a valid g_pkce cookie value: Fernet of {"v": verifier, "s": state}."""
    return encrypt_str(json.dumps({"v": verifier, "s": state}))


def clear_pkce_cookie(client: TestClient) -> None:
    """Remove any g_pkce cookie from the (module-scoped) client's jar."""
    jar = httpx.Cookies()
    for cookie in client.cookies.jar:
        if cookie.name != PKCE_COOKIE:
            jar.jar.set_cookie(cookie)
    client.cookies = jar


def set_pkce_cookie(client: TestClient, value: str) -> None:
    clear_pkce_cookie(client)
    client.cookies.set(PKCE_COOKIE, value)


def google_callback(
    client: TestClient,
    *,
    code: str = "any-authorization-code",
    state: str | None = DEFAULT_STATE,
    cookie: str | None = "default",
) -> httpx.Response:
    """GET the Google callback with explicit cookie/state control.

    cookie: "default" -> a valid cookie matching DEFAULT_STATE; None -> no
    cookie at all; any other string -> that literal cookie value.
    Redirects are NOT followed: the contract is a 307 with a URL fragment.
    """
    if cookie is None:
        clear_pkce_cookie(client)
    elif cookie == "default":
        set_pkce_cookie(client, make_pkce_cookie())
    else:
        set_pkce_cookie(client, cookie)

    params: dict[str, str] = {"code": code}
    if state is not None:
        params["state"] = state
    return client.get(
        f"{settings.API_V1_STR}/login/google/callback",
        params=params,
        follow_redirects=False,
    )


def token_from_redirect(response: httpx.Response) -> str:
    """Extract the access_token from the redirect's URL fragment (contract B)."""
    assert response.status_code == 307, response.text
    location = response.headers["location"]
    assert location.startswith(f"{settings.FRONTEND_HOST}/google-callback#"), location
    fragment = parse_qs(urlsplit(location).fragment)
    assert fragment.get("token_type") == ["bearer"], location
    (access_token,) = fragment["access_token"]
    assert access_token
    return access_token


def assert_pkce_cookie_deleted(response: httpx.Response) -> None:
    """The response must delete g_pkce (Set-Cookie with Max-Age=0), also on error."""
    set_cookies = [
        value
        for key, value in response.headers.multi_items()
        if key.lower() == "set-cookie" and value.startswith(f"{PKCE_COOKIE}=")
    ]
    assert set_cookies, f"no Set-Cookie for {PKCE_COOKIE}: {response.headers}"
    assert any("max-age=0" in c.lower() for c in set_cookies), (
        f"{PKCE_COOKIE} not deleted with Max-Age=0: {set_cookies}"
    )
