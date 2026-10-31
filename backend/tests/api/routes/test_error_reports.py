"""Tests for privacy/error-reports (api-errores-sin-datos).

Interface contract (design.md, "## Interface contract"):
- Every 422 is {"detail": [{loc, msg, type, ...}]} WITHOUT "input", and its body
  is valid UTF-8 even when a key name carries a lone surrogate.
- app.main.SENTRY_OPTIONS: the kwargs sentry_sdk.init gets next to the DSN; an
  event never carries the request body, frame variables or the session token.
"""

import json
import logging
import uuid
from collections.abc import Generator
from typing import Any

import pytest
import sentry_sdk
from fastapi.testclient import TestClient
from sentry_sdk.transport import Transport
from sqlmodel import Session

from app import main
from app.api.routes import profile as profile_routes
from app.core.config import settings
from tests.api.routes.test_profile import consented_user
from tests.utils.utils import random_email

SIGNUP_URL = f"{settings.API_V1_STR}/users/signup"
HABITS_URL = f"{settings.API_V1_STR}/profile/habits"
HISTORY_URL = f"{settings.API_V1_STR}/profile/history"


@pytest.fixture
def lenient_client() -> Generator[TestClient]:
    """A 500 comes back as a response instead of being raised in the test."""
    with TestClient(main.app, raise_server_exceptions=False) as c:
        yield c


def post_raw(client: TestClient, url: str, raw: str, **kw: Any) -> Any:
    # A JSON escape (\ud800) in the bytes: the client never encodes the surrogate.
    return client.post(
        url,
        content=raw.encode("ascii"),
        headers={"content-type": "application/json", **kw.pop("headers", {})},
        **kw,
    )


def test_signup_lone_surrogate_is_422_without_echo_or_log(
    lenient_client: TestClient, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    marker = f"Dato-Prueba-B1-{uuid.uuid4().hex[:8]}"
    body = json.dumps(
        {"email": random_email(), "password": "contrasena-larga", "full_name": marker}
    )
    raw = body.replace(f'{marker}"', f'{marker}\\ud800"')
    r = post_raw(lenient_client, SIGNUP_URL, raw)
    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert [e["loc"] for e in detail] == [["body", "full_name"]]
    assert all("input" not in e for e in detail)
    assert marker not in r.text
    assert marker not in caplog.text


def test_ordinary_422_keeps_shape_without_input(client: TestClient) -> None:
    r = client.post(
        SIGNUP_URL, json={"email": "sin-arroba", "password": "x", "full_name": "ok"}
    )
    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert sorted(e["loc"] for e in detail) == [["body", "email"], ["body", "password"]]
    for e in detail:
        assert e["msg"] and e["type"]
        assert "input" not in e
    assert "sin-arroba" not in r.text


def test_unknown_key_with_lone_surrogate_is_valid_utf8_422(
    lenient_client: TestClient, db: Session
) -> None:
    headers, _ = consented_user(lenient_client, db)
    r = lenient_client.put(
        HABITS_URL,
        content=b'{"x\\ud800": 1}',
        headers={"content-type": "application/json", **headers},
    )
    assert r.status_code == 422, r.text
    r.content.decode("utf-8")  # strict: raises on an invalid byte
    assert isinstance(r.json()["detail"], list)


@pytest.fixture
def sentry_events() -> Generator[list[dict[str, Any]]]:
    events: list[dict[str, Any]] = []

    class Capture(Transport):
        def capture_envelope(self, envelope: Any) -> None:
            for item in envelope.items:
                if item.type == "event":
                    events.append(json.loads(item.payload.get_bytes()))

    sentry_sdk.init(
        dsn="https://key@o0.ingest.example.invalid/1",
        transport=Capture,
        # getattr: before the change the red is the leak, not a missing name.
        **getattr(main, "SENTRY_OPTIONS", {"enable_tracing": True}),
    )
    try:
        yield events
    finally:
        sentry_sdk.init()  # no DSN: reporting off again for the other tests


def test_sentry_event_has_no_body_locals_or_token(
    lenient_client: TestClient,
    db: Session,
    sentry_events: list[dict[str, Any]],
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    headers, _ = consented_user(lenient_client, db)
    token = headers["Authorization"].removeprefix("Bearer ")
    marker = f"OTRO-{uuid.uuid4().hex}"

    def fail(*_: Any) -> str:
        raise RuntimeError("guardado roto a propósito")

    monkeypatch.setattr(profile_routes, "_history_content_json", fail)
    r = lenient_client.post(
        HISTORY_URL,
        headers=headers,
        json={"section": "past", "condition": "other", "other_text": marker},
    )
    assert r.status_code == 500
    sentry_sdk.flush()
    assert sentry_events, "no event reached the transport"
    types = [
        v["type"]
        for ev in sentry_events
        for v in ev.get("exception", {}).get("values", [])
    ]
    assert "RuntimeError" in types
    blob = json.dumps(sentry_events)
    assert marker not in blob
    assert token not in blob


def test_production_sentry_init_uses_the_privacy_options(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The guarded init the app runs with a DSN (review M3/L10): the options,
    send_default_pii included, reach sentry_sdk.init; development never inits."""
    calls: list[dict[str, Any]] = []
    monkeypatch.setattr(main.sentry_sdk, "init", lambda **kw: calls.append(kw))
    monkeypatch.setattr(
        main.settings, "SENTRY_DSN", "https://key@o0.ingest.example.invalid/1"
    )
    monkeypatch.setattr(main.settings, "FASTAPI_ENV", "development")
    main.init_sentry()
    assert calls == []
    monkeypatch.setattr(main.settings, "FASTAPI_ENV", "production")
    main.init_sentry()
    assert len(calls) == 1
    kw = calls[0]
    assert kw["dsn"] == "https://key@o0.ingest.example.invalid/1"
    assert kw["max_request_body_size"] == "never"
    assert kw["include_local_variables"] is False
    assert kw["send_default_pii"] is False
