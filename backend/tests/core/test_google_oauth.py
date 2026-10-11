"""Unit tests for app.core.google_oauth.exchange_code (finding H12).

ZERO real network: httpx is replaced by a MockTransport-backed AsyncClient
factory monkeypatched onto the module, and the id_token validation (JWKS +
decode) by a fake jwt namespace. The tests pin:
- the POST payload to Google (code_verifier sent iff provided),
- the error branches (settings missing, exchange failure, no/invalid
  id_token, wrong issuer),
- the claims mapping (email_verified passthrough).
"""

import asyncio
from types import SimpleNamespace
from typing import Any
from urllib.parse import parse_qs

import httpx
import jwt as real_jwt
import pytest
from fastapi import HTTPException

from app.core import google_oauth
from app.core.config import settings

GOOGLE_SETTINGS = {
    "GOOGLE_CLIENT_ID": "test-client-id",
    "GOOGLE_CLIENT_SECRET": "test-client-secret",
    "GOOGLE_REDIRECT_URI": "http://localhost/api/v1/login/google/callback",
}


def configure_google(monkeypatch: pytest.MonkeyPatch) -> None:
    for name, value in GOOGLE_SETTINGS.items():
        monkeypatch.setattr(settings, name, value)


def mock_token_endpoint(
    monkeypatch: pytest.MonkeyPatch,
    *,
    status_code: int = 200,
    json_body: dict[str, Any] | None = None,
) -> list[dict[str, list[str]]]:
    """Replace httpx.AsyncClient in google_oauth with a MockTransport client.

    Returns the list of form payloads POSTed to the token endpoint.
    """
    requests: list[dict[str, list[str]]] = []

    def handler(request: httpx.Request) -> httpx.Response:
        assert str(request.url) == google_oauth.GOOGLE_TOKEN_URL
        requests.append(parse_qs(request.content.decode()))
        return httpx.Response(
            status_code, json=json_body if json_body is not None else {}
        )

    transport = httpx.MockTransport(handler)

    def client_factory(*args: Any, **kwargs: Any) -> httpx.AsyncClient:
        kwargs["transport"] = transport
        return httpx.AsyncClient(*args, **kwargs)

    monkeypatch.setattr(
        google_oauth, "httpx", SimpleNamespace(AsyncClient=client_factory)
    )
    return requests


def mock_id_token_validation(
    monkeypatch: pytest.MonkeyPatch,
    *,
    claims: dict[str, Any] | None = None,
    decode_error: bool = False,
) -> None:
    """Replace the jwt namespace in google_oauth: no JWKS fetch, fixed claims."""

    class FakeJWKClient:
        def __init__(self, url: str) -> None:
            assert url == google_oauth.GOOGLE_JWKS_URL

        def get_signing_key_from_jwt(self, token: str) -> Any:
            return SimpleNamespace(key="fake-signing-key")

    def decode(
        _token: str,
        _key: Any,
        algorithms: Any = None,
        audience: Any = None,  # noqa: ARG001
    ) -> dict[str, Any]:
        if decode_error:
            raise real_jwt.PyJWTError("invalid signature")
        assert audience == settings.GOOGLE_CLIENT_ID
        return dict(claims or {})

    monkeypatch.setattr(
        google_oauth,
        "jwt",
        SimpleNamespace(
            PyJWKClient=FakeJWKClient, decode=decode, PyJWTError=real_jwt.PyJWTError
        ),
    )


def valid_claims(**overrides: Any) -> dict[str, Any]:
    claims: dict[str, Any] = {
        "iss": "https://accounts.google.com",
        "sub": "google-sub-unit",
        "email": "unit@example.com",
        "email_verified": True,
    }
    claims.update(overrides)
    return claims


def run(coro: Any) -> Any:
    return asyncio.run(coro)


def test_exchange_code_happy_path_sends_code_verifier(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """With a verifier: the POST carries code_verifier and claims come back."""
    configure_google(monkeypatch)
    requests = mock_token_endpoint(monkeypatch, json_body={"id_token": "fake-id-token"})
    mock_id_token_validation(monkeypatch, claims=valid_claims())

    claims = run(google_oauth.exchange_code("the-code", code_verifier="the-verifier"))

    assert claims.sub == "google-sub-unit"
    assert claims.email == "unit@example.com"
    assert claims.email_verified is True

    assert len(requests) == 1
    sent = requests[0]
    assert sent["code"] == ["the-code"]
    assert sent["code_verifier"] == ["the-verifier"]
    assert sent["client_id"] == [GOOGLE_SETTINGS["GOOGLE_CLIENT_ID"]]
    assert sent["grant_type"] == ["authorization_code"]


def test_exchange_code_without_verifier_omits_the_field(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_google(monkeypatch)
    requests = mock_token_endpoint(monkeypatch, json_body={"id_token": "fake-id-token"})
    mock_id_token_validation(monkeypatch, claims=valid_claims())

    run(google_oauth.exchange_code("the-code"))

    assert len(requests) == 1
    assert "code_verifier" not in requests[0]


def test_exchange_code_requires_google_settings(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_google(monkeypatch)
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_SECRET", None)
    requests = mock_token_endpoint(monkeypatch, json_body={"id_token": "x"})

    with pytest.raises(HTTPException) as exc_info:
        run(google_oauth.exchange_code("the-code"))

    assert exc_info.value.status_code == 500
    assert requests == [], "no request may leave without configuration"


def test_exchange_code_token_endpoint_error_is_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_google(monkeypatch)
    mock_token_endpoint(monkeypatch, status_code=400, json_body={"error": "bad_grant"})

    with pytest.raises(HTTPException) as exc_info:
        run(google_oauth.exchange_code("the-code"))

    assert exc_info.value.status_code == 400


def test_exchange_code_missing_id_token_is_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_google(monkeypatch)
    mock_token_endpoint(monkeypatch, json_body={"access_token": "no-id-token"})

    with pytest.raises(HTTPException) as exc_info:
        run(google_oauth.exchange_code("the-code"))

    assert exc_info.value.status_code == 400


def test_exchange_code_invalid_id_token_is_400(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    configure_google(monkeypatch)
    mock_token_endpoint(monkeypatch, json_body={"id_token": "tampered"})
    mock_id_token_validation(monkeypatch, decode_error=True)

    with pytest.raises(HTTPException) as exc_info:
        run(google_oauth.exchange_code("the-code"))

    assert exc_info.value.status_code == 400


def test_exchange_code_wrong_issuer_is_400(monkeypatch: pytest.MonkeyPatch) -> None:
    configure_google(monkeypatch)
    mock_token_endpoint(monkeypatch, json_body={"id_token": "fake-id-token"})
    mock_id_token_validation(
        monkeypatch, claims=valid_claims(iss="https://evil.example.com")
    )

    with pytest.raises(HTTPException) as exc_info:
        run(google_oauth.exchange_code("the-code"))

    assert exc_info.value.status_code == 400


def test_exchange_code_email_verified_defaults_to_false(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing email_verified claim maps to False (never trusted by default)."""
    configure_google(monkeypatch)
    mock_token_endpoint(monkeypatch, json_body={"id_token": "fake-id-token"})
    claims_in = valid_claims()
    del claims_in["email_verified"]
    mock_id_token_validation(monkeypatch, claims=claims_in)

    claims = run(google_oauth.exchange_code("the-code"))

    assert claims.email_verified is False
