"""Tests for the habits questionnaire of the medical profile (perfil-habitos and
perfil-habitos-ajustes, grupo 1).

Interface contract (perfil-habitos-ajustes design.md, "## Interface contract";
base /api/v1/profile, behind a current consent; field names and values in
English):
- Habits (same object in the PUT body and the response; everything optional,
  extra="forbid"):
  - alcohol: {status: never|quit|current (required), start_age: 0..130|null,
    quit_age: 0..130|null, frequency: monthly_or_less|two_to_four_monthly|
    two_to_three_weekly|four_plus_weekly|null, typical_drinks: one_two|
    three_four|five_six|seven_nine|ten_plus|null, six_or_more: never|
    less_than_monthly|monthly|weekly|daily|null, mostly_weekends: bool|null}
    | null
  - tobacco: {status: never|former|current (required), cigarettes_per_day:
    1..100|null, start_age: 0..130|null, quit_age: 0..130|null} | null
  - vaping: {status: never|former|current (required), frequency: daily|
    some_days|null, days_last_30: 1..30|null, start_age: 0..130|null,
    quit_age: 0..130|null} | null   (before this change: the plain text)
  - secondhand_smoke: {exposed: bool (required), places: [home|work_school|
    other] (no repeats, in this order), days_per_week: 1..7|null} | null
  - wood_smoke: {status: never|former|current (required), start_age:
    0..130|null, quit_age: 0..130|null, hours_per_day: 1..24|null} | null
    (before this change: {status, years})
- Normalization (server, before encrypting): alcohol != current -> the AUDIT-C
  answers and mostly_weekends null; alcohol never -> start_age null; alcohol
  != quit -> quit_age null; tobacco never -> cigarettes_per_day, start_age,
  quit_age null; tobacco != former -> quit_age null; vaping never -> all null
  but status; vaping != current -> frequency and days_last_30 null; frequency
  != some_days -> days_last_30 null; vaping != former -> quit_age null; wood
  never -> start_age, quit_age, hours_per_day null; wood != former -> quit_age
  null; exposed false -> places [] and days_per_week null.
- Validation (server, after normalizing; "today" is Mexico City's, from
  app.api.routes.profile): every start_age and quit_age of alcohol, tobacco,
  vaping and wood above the current age -> "La edad no puede ser mayor que tu
  edad actual" on that field (not compared without a birth date); start_age >
  quit_age -> on start_age: alcohol, tobacco and vaping "No puede ser mayor que
  la edad en que lo dejaste", wood "No puede ser mayor que la edad en que
  terminó"; exposed true without places -> "Elige dónde, o «No me expongo»" on
  places. These 422s have FastAPI's validation shape:
  detail: [{"loc": ["body", <block>, <field>], "msg": <es-MX>, "type": "value_error"}].
- Stored in the previous shape: upgrade_stored_habits(raw: dict) -> dict in
  app.models, applied to the decrypted JSON before validating it (NOT to the
  PUT body): vaping as text -> {"status": <text>}; wood_smoke.years dropped.
- GET /profile/habits -> 200 Habits (all null when nothing is stored).
  PUT /profile/habits -> 200 the normalized Habits; replaces the questionnaire.
  Without consent: 403.
- Table: patient_profile.habits, EncryptedString (Fernet, "gAAAA" prefix) with
  the JSON of the normalized object.
"""

import json
import logging
import uuid
from datetime import datetime
from typing import Any

import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError
from sqlmodel import Session, select

from app.api.routes import profile as profile_routes
from app.core.encrypted import decrypt_str
from app.models import Habits, PatientProfile
from tests.api.routes.test_profile import (
    PROFILE_URL,
    consented_user,
    put_profile,
    user_without_consent_headers,
)
from tests.api.routes.test_profile_history import (
    BIRTH_DATE,
    freeze_routes_clock,
    raw_rows,
)

HABITS_URL = f"{PROFILE_URL}/habits"

# Frozen Mexico City wall time: born 1990-03-15, the patient is 36 today.
NOW = datetime(2026, 10, 20, 12, 0)

AGE_ABOVE_CURRENT = "La edad no puede ser mayor que tu edad actual"
START_AFTER_QUIT = "No puede ser mayor que la edad en que lo dejaste"
START_AFTER_END = "No puede ser mayor que la edad en que terminó"
PLACES_REQUIRED = "Elige dónde, o «No me expongo»"

TOP_LEVEL_KEYS = {"alcohol", "tobacco", "vaping", "secondhand_smoke", "wood_smoke"}
ALCOHOL_KEYS = {
    "status",
    "start_age",
    "quit_age",
    "frequency",
    "typical_drinks",
    "six_or_more",
    "mostly_weekends",
}
TOBACCO_KEYS = {"status", "cigarettes_per_day", "start_age", "quit_age"}
VAPING_KEYS = {"status", "frequency", "days_last_30", "start_age", "quit_age"}
SECONDHAND_KEYS = {"exposed", "places", "days_per_week"}
WOOD_KEYS = {"status", "start_age", "quit_age", "hours_per_day"}


# --- helpers ----------------------------------------------------------------------


def empty_habits() -> dict[str, Any]:
    return dict.fromkeys(TOP_LEVEL_KEYS)


def habits(**blocks: Any) -> dict[str, Any]:
    """A full Habits object: the given blocks, the rest null."""
    return {**empty_habits(), **blocks}


def alcohol(**fields: Any) -> dict[str, Any]:
    """A full (normalized) AlcoholHabit: the given fields, the rest null."""
    return {**dict.fromkeys(ALCOHOL_KEYS), **fields}


def tobacco(**fields: Any) -> dict[str, Any]:
    return {**dict.fromkeys(TOBACCO_KEYS), **fields}


def vaping(**fields: Any) -> dict[str, Any]:
    return {**dict.fromkeys(VAPING_KEYS), **fields}


def secondhand(**fields: Any) -> dict[str, Any]:
    return {"exposed": None, "places": [], "days_per_week": None, **fields}


def wood(**fields: Any) -> dict[str, Any]:
    return {**dict.fromkeys(WOOD_KEYS), **fields}


def get_habits(client: TestClient, headers: dict[str, str]) -> Any:
    return client.get(HABITS_URL, headers=headers)


def put_habits(
    client: TestClient, headers: dict[str, str], body: dict[str, Any]
) -> Any:
    return client.put(HABITS_URL, headers=headers, json=body)


def stored_habits(client: TestClient, headers: dict[str, str]) -> dict[str, Any]:
    r = get_habits(client, headers)
    assert r.status_code == 200, r.text
    body: dict[str, Any] = r.json()
    return body


def save(
    client: TestClient, headers: dict[str, str], body: dict[str, Any]
) -> dict[str, Any]:
    r = put_habits(client, headers, body)
    assert r.status_code == 200, r.text
    saved: dict[str, Any] = r.json()
    return saved


def born_1990_frozen(
    client: TestClient, headers: dict[str, str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """Birth date 1990-03-15 and the routes clock at 2026-10-20 (age 36)."""
    r = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r.status_code == 200, r.text
    freeze_routes_clock(monkeypatch, NOW)


def assert_single_error(r: Any, loc: list[str], msg: str) -> None:
    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, list), detail
    assert len(detail) == 1, detail
    assert detail[0]["loc"] == loc, detail
    assert detail[0]["msg"] == msg, detail
    assert detail[0]["type"] == "value_error", detail


def without_nulls(value: Any) -> Any:
    """Drop null keys recursively (the stored JSON may omit them)."""
    if isinstance(value, dict):
        return {k: without_nulls(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [without_nulls(v) for v in value]
    return value


def raw_habits(user_id: str) -> str:
    rows = raw_rows(
        "SELECT habits FROM patient_profile WHERE user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )
    assert len(rows) == 1, rows
    return str(rows[0]["habits"])


def store_raw_habits_json(db: Session, user_id: str, raw_json: str) -> PatientProfile:
    """Write a habits JSON straight into the profile row (encrypted by the
    column type), bypassing the PUT and its validation."""
    profile = db.exec(
        select(PatientProfile).where(PatientProfile.user_id == uuid.UUID(user_id))
    ).one()
    profile.habits = raw_json
    db.add(profile)
    db.commit()
    db.refresh(profile)
    assert raw_habits(user_id).startswith("gAAAA")
    return profile


# A previous answer to prove a rejected PUT leaves the habits as they were.
SEED: dict[str, Any] = {"vaping": {"status": "never"}}
SEED_STORED = habits(vaping=vaping(status="never"))


# --- Alcohol actual con las preguntas del AUDIT-C (C-1) ---------------------------


def test_c1_current_alcohol_with_audit_c_round_trip(
    client: TestClient, db: Session
) -> None:
    """Nacido 1990-03-15, sin hábitos: alcohol current, two_to_three_weekly,
    three_four, six_or_more monthly y mostly_weekends -> PUT y GET iguales."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text
    assert stored_habits(client, headers) == empty_habits()
    answers = {
        "status": "current",
        "frequency": "two_to_three_weekly",
        "typical_drinks": "three_four",
        "six_or_more": "monthly",
        "mostly_weekends": True,
    }
    expected = habits(alcohol=alcohol(**answers))

    saved = save(client, headers, {"alcohol": answers})

    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c1_mostly_weekends_false_round_trip(client: TestClient, db: Session) -> None:
    """Alcohol current con mostly_weekends False -> PUT y GET devuelven False,
    no None (el «No» es una respuesta; revisión, ronda 2, N3)."""
    headers, _ = consented_user(client, db)
    answers = {"status": "current", "mostly_weekends": False}
    expected = habits(alcohol=alcohol(**answers))

    saved = save(client, headers, {"alcohol": answers})
    stored = stored_habits(client, headers)

    assert saved == expected
    assert stored == expected
    assert saved["alcohol"]["mostly_weekends"] is False
    assert stored["alcohol"]["mostly_weekends"] is False


# --- Test plan row 2: Lo dejó, con la edad (C-1, C-10) ----------------------------


def test_c1_c10_quit_alcohol_with_start_and_quit_age_round_trip(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15: alcohol quit, empezó a los 17 y lo dejó a los 30 ->
    PUT y GET iguales (17 y 30), sin AUDIT-C."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    expected = habits(alcohol=alcohol(status="quit", start_age=17, quit_age=30))

    saved = save(
        client,
        headers,
        {"alcohol": {"status": "quit", "start_age": 17, "quit_age": 30}},
    )

    assert saved == expected
    assert stored_habits(client, headers) == expected


# --- Test plan rows 3, 7, 11: empezó después de dejarlo (C-2, C-10, C-12) ---------

START_AFTER_QUIT_CASES = [
    pytest.param(
        {"alcohol": {"status": "quit", "start_age": 30, "quit_age": 18}},
        ["body", "alcohol", "start_age"],
        START_AFTER_QUIT,
        id="alcohol",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "former",
                "cigarettes_per_day": 10,
                "start_age": 30,
                "quit_age": 18,
            }
        },
        ["body", "tobacco", "start_age"],
        START_AFTER_QUIT,
        id="tobacco",
    ),
    pytest.param(
        {"vaping": {"status": "former", "start_age": 30, "quit_age": 18}},
        ["body", "vaping", "start_age"],
        START_AFTER_QUIT,
        id="vaping",
    ),
    pytest.param(
        {
            "wood_smoke": {
                "status": "former",
                "start_age": 30,
                "quit_age": 18,
                "hours_per_day": 3,
            }
        },
        ["body", "wood_smoke", "start_age"],
        START_AFTER_END,
        id="wood_smoke",
    ),
]


@pytest.mark.parametrize(("body", "loc", "msg"), START_AFTER_QUIT_CASES)
def test_c2_c10_c12_start_age_after_quit_age_rejected(
    client: TestClient,
    db: Session,
    body: dict[str, Any],
    loc: list[str],
    msg: str,
) -> None:
    """Empezó a los 30 y lo dejó (o terminó) a los 18 -> 422 en start_age con
    el texto exacto de su bloque; nada se guarda."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(client, headers, body)

    assert_single_error(r, loc, msg)
    assert stored_habits(client, headers) == SEED_STORED


# --- Test plan row 4: Una edad mayor que la actual (C-1, C-2) ---------------------

AGE_ABOVE_CASES = [
    pytest.param(
        {"alcohol": {"status": "current", "start_age": 40}},
        ["body", "alcohol", "start_age"],
        id="alcohol-start_age",
    ),
    pytest.param(
        {"alcohol": {"status": "quit", "quit_age": 40}},
        ["body", "alcohol", "quit_age"],
        id="alcohol-quit_age",
    ),
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 5, "start_age": 40}},
        ["body", "tobacco", "start_age"],
        id="tobacco-start_age",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "former",
                "cigarettes_per_day": 5,
                "start_age": 18,
                "quit_age": 40,
            }
        },
        ["body", "tobacco", "quit_age"],
        id="tobacco-quit_age",
    ),
    pytest.param(
        {"vaping": {"status": "current", "frequency": "daily", "start_age": 40}},
        ["body", "vaping", "start_age"],
        id="vaping-start_age",
    ),
    pytest.param(
        {"vaping": {"status": "former", "start_age": 18, "quit_age": 40}},
        ["body", "vaping", "quit_age"],
        id="vaping-quit_age",
    ),
    pytest.param(
        {"wood_smoke": {"status": "current", "start_age": 40, "hours_per_day": 3}},
        ["body", "wood_smoke", "start_age"],
        id="wood_smoke-start_age",
    ),
    pytest.param(
        {
            "wood_smoke": {
                "status": "former",
                "start_age": 5,
                "quit_age": 40,
                "hours_per_day": 3,
            }
        },
        ["body", "wood_smoke", "quit_age"],
        id="wood_smoke-quit_age",
    ),
]


@pytest.mark.parametrize(("body", "loc"), AGE_ABOVE_CASES)
def test_c1_c2_age_above_current_rejected_nothing_saved(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    body: dict[str, Any],
    loc: list[str],
) -> None:
    """Nacido 1990-03-15, hoy 36: una edad de 40 en cualquiera de las ocho
    edades -> 422 con su loc y el texto exacto; los hábitos guardados no
    cambian."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    save(client, headers, SEED)

    r = put_habits(client, headers, body)

    assert_single_error(r, loc, AGE_ABOVE_CURRENT)
    assert stored_habits(client, headers) == SEED_STORED


@pytest.mark.parametrize(("body", "loc"), AGE_ABOVE_CASES)
def test_c1_c2_age_without_birth_date_accepted(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    body: dict[str, Any],
    loc: list[str],
) -> None:
    """Sin fecha de nacimiento la edad no se compara: 40 se acepta y se guarda."""
    headers, _ = consented_user(client, db)
    freeze_routes_clock(monkeypatch, NOW)
    block, field = loc[1], loc[2]

    saved = save(client, headers, body)

    assert saved[block][field] == 40, saved
    assert stored_habits(client, headers)[block][field] == 40


# Review R7: "mayor que" is strict; an age equal to the current one, or a start
# equal to the quit, is possible.
AGE_AT_LIMIT_CASES = [
    pytest.param(
        {"alcohol": {"status": "quit", "quit_age": 36}},
        habits(alcohol=alcohol(status="quit", quit_age=36)),
        id="alcohol-quit_age-equals-current",
    ),
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 5, "start_age": 36}},
        habits(tobacco=tobacco(status="current", cigarettes_per_day=5, start_age=36)),
        id="tobacco-start_age-equals-current",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "former",
                "cigarettes_per_day": 5,
                "start_age": 18,
                "quit_age": 36,
            }
        },
        habits(
            tobacco=tobacco(
                status="former", cigarettes_per_day=5, start_age=18, quit_age=36
            )
        ),
        id="tobacco-quit_age-equals-current",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "former",
                "cigarettes_per_day": 5,
                "start_age": 20,
                "quit_age": 20,
            }
        },
        habits(
            tobacco=tobacco(
                status="former", cigarettes_per_day=5, start_age=20, quit_age=20
            )
        ),
        id="tobacco-start_age-equals-quit_age",
    ),
]


@pytest.mark.parametrize(("body", "expected"), AGE_AT_LIMIT_CASES)
def test_c1_c2_age_at_the_limit_accepted(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    body: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    """Nacido 1990-03-15, hoy 36: una edad de 36, o empezó y dejó a la misma
    edad -> se acepta y se guarda."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)

    saved = save(client, headers, body)

    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c1_mexico_day_decides_the_current_age(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15; ahora 2026-03-14 21:00 en México = 2026-03-15 03:00
    UTC: en México aún tiene 35 (en UTC ya 36). quit_age 36 -> 422 y nada se
    guarda; quit_age 35 -> se guarda (review R8)."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text
    freeze_routes_clock(monkeypatch, datetime(2026, 3, 14, 21, 0))
    save(client, headers, SEED)

    r = put_habits(client, headers, {"alcohol": {"status": "quit", "quit_age": 36}})

    assert_single_error(r, ["body", "alcohol", "quit_age"], AGE_ABOVE_CURRENT)
    assert stored_habits(client, headers) == SEED_STORED
    saved = save(client, headers, {"alcohol": {"status": "quit", "quit_age": 35}})
    assert saved == habits(alcohol=alcohol(status="quit", quit_age=35))


# --- Test plan rows 5, 9: Lo que no aplica se descarta (C-1, C-11) ----------------

AUDIT_C = {
    "frequency": "four_plus_weekly",
    "typical_drinks": "five_six",
    "six_or_more": "weekly",
    "mostly_weekends": True,
}

ALL_VAPING = {
    "frequency": "some_days",
    "days_last_30": 12,
    "start_age": 25,
    "quit_age": 28,
}

ALL_WOOD = {"start_age": 5, "quit_age": 20, "hours_per_day": 8}

NORMALIZATION_CASES = [
    pytest.param(
        {"alcohol": {"status": "never", "start_age": 17, "quit_age": 30, **AUDIT_C}},
        habits(alcohol=alcohol(status="never")),
        id="alcohol-never-drops-start_age-quit_age-and-audit",
    ),
    pytest.param(
        {"alcohol": {"status": "quit", "start_age": 17, "quit_age": 30, **AUDIT_C}},
        habits(alcohol=alcohol(status="quit", start_age=17, quit_age=30)),
        id="alcohol-quit-keeps-start_age-drops-audit",
    ),
    pytest.param(
        {"alcohol": {"status": "current", "start_age": 17, "quit_age": 30, **AUDIT_C}},
        habits(alcohol=alcohol(status="current", start_age=17, **AUDIT_C)),
        id="alcohol-current-keeps-start_age-drops-quit_age",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "never",
                "cigarettes_per_day": 10,
                "start_age": 18,
                "quit_age": 30,
            }
        },
        habits(tobacco=tobacco(status="never")),
        id="tobacco-never-drops-cigarettes-and-ages",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "current",
                "cigarettes_per_day": 10,
                "start_age": 18,
                "quit_age": 30,
            }
        },
        habits(tobacco=tobacco(status="current", cigarettes_per_day=10, start_age=18)),
        id="tobacco-current-drops-quit_age",
    ),
    pytest.param(
        {"vaping": {"status": "never", **ALL_VAPING}},
        habits(vaping=vaping(status="never")),
        id="vaping-never-drops-all-but-status",
    ),
    pytest.param(
        {"vaping": {"status": "former", **ALL_VAPING}},
        habits(vaping=vaping(status="former", start_age=25, quit_age=28)),
        id="vaping-former-drops-frequency-and-days",
    ),
    pytest.param(
        {"vaping": {"status": "current", **ALL_VAPING}},
        habits(
            vaping=vaping(
                status="current", frequency="some_days", days_last_30=12, start_age=25
            )
        ),
        id="vaping-current-drops-quit_age",
    ),
    pytest.param(
        {"vaping": {"status": "current", **ALL_VAPING, "frequency": "daily"}},
        habits(vaping=vaping(status="current", frequency="daily", start_age=25)),
        id="vaping-daily-drops-days",
    ),
    pytest.param(
        {"vaping": {"status": "current", "days_last_30": 12, "start_age": 25}},
        habits(vaping=vaping(status="current", start_age=25)),
        id="vaping-no-frequency-drops-days",
    ),
    pytest.param(
        {"wood_smoke": {"status": "never", **ALL_WOOD}},
        habits(wood_smoke=wood(status="never")),
        id="wood-never-drops-ages-and-hours",
    ),
    pytest.param(
        {"wood_smoke": {"status": "current", **ALL_WOOD}},
        habits(wood_smoke=wood(status="current", start_age=5, hours_per_day=8)),
        id="wood-current-drops-quit_age",
    ),
    pytest.param(
        {
            "secondhand_smoke": {
                "exposed": False,
                "places": ["home", "work_school"],
                "days_per_week": 2,
            }
        },
        habits(secondhand_smoke=secondhand(exposed=False)),
        id="not-exposed-drops-places-and-days",
    ),
]


@pytest.mark.parametrize(("body", "expected"), NORMALIZATION_CASES)
def test_c1_c11_what_does_not_apply_is_dropped(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    body: dict[str, Any],
    expected: dict[str, Any],
) -> None:
    """Cada regla de normalización: PUT y GET devuelven el objeto sin lo que no
    aplica a la respuesta elegida."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)

    saved = save(client, headers, body)

    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c1_dropped_age_is_not_validated(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """La validación va después de normalizar: tabaco current con quit_age 40
    (nacido 1990, hoy 36) se acepta y quit_age se descarta."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)

    saved = save(
        client,
        headers,
        {"tobacco": {"status": "current", "cigarettes_per_day": 5, "quit_age": 40}},
    )

    expected = habits(tobacco=tobacco(status="current", cigarettes_per_day=5))
    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c1_switch_current_to_never_drops_stored_age_and_audit_c(
    client: TestClient, db: Session
) -> None:
    """Alcohol current con edad de inicio 17 y las tres preguntas del AUDIT-C,
    luego never -> GET sin edad ni AUDIT-C, y el JSON guardado (descifrado) no
    conserva esas respuestas."""
    headers, user_id = consented_user(client, db)
    first = save(
        client, headers, {"alcohol": {"status": "current", "start_age": 17, **AUDIT_C}}
    )
    assert first["alcohol"]["start_age"] == 17, first

    saved = save(
        client, headers, {"alcohol": {"status": "never", "start_age": 17, **AUDIT_C}}
    )

    expected = habits(alcohol=alcohol(status="never"))
    assert saved == expected
    assert stored_habits(client, headers) == expected
    decrypted = decrypt_str(raw_habits(user_id))
    assert decrypted is not None
    for answer in ("four_plus_weekly", "five_six", "weekly", "mostly_weekends"):
        assert answer not in decrypted, answer
    assert without_nulls(json.loads(decrypted)) == without_nulls(expected)


# --- Test plan row 6: Tabaco que dejó, y vapeador actual (C-2) --------------------


def test_c2_former_tobacco_and_current_daily_vaping_round_trip(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15: tabaco former, 10 al día, de 18 a 30, vaping current
    daily -> PUT y GET iguales."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    smoking = {
        "status": "former",
        "cigarettes_per_day": 10,
        "start_age": 18,
        "quit_age": 30,
    }
    vape = {"status": "current", "frequency": "daily"}
    expected = habits(tobacco=tobacco(**smoking), vaping=vaping(**vape))

    saved = save(client, headers, {"tobacco": smoking, "vaping": vape})

    assert saved == expected
    assert stored_habits(client, headers) == expected


# --- Test plan row 8: Vapeador actual algunos días (C-11) -------------------------


def test_c11_current_vaping_some_days_round_trip(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15: vapeador current, empezó a los 25, some_days, 12 días
    de los últimos 30 -> PUT y GET iguales."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    vape = {
        "status": "current",
        "start_age": 25,
        "frequency": "some_days",
        "days_last_30": 12,
    }
    expected = habits(vaping=vaping(**vape))

    saved = save(client, headers, {"vaping": vape})

    assert saved == expected
    assert stored_habits(client, headers) == expected


# --- Test plan row 9: Vapeador de antes, y luego todos los días (C-11) ------------


def test_c11_some_days_then_daily_then_former(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Vapeador current some_days con 12 días; luego daily (con los 12 días aún
    en el cuerpo) -> sin días; luego former 25/28 (con frecuencia y días en el
    cuerpo) -> former 25/28 sin frecuencia ni días."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    save(
        client,
        headers,
        {"vaping": {"status": "current", "frequency": "some_days", "days_last_30": 12}},
    )

    daily = save(
        client,
        headers,
        {"vaping": {"status": "current", "frequency": "daily", "days_last_30": 12}},
    )
    assert daily == habits(vaping=vaping(status="current", frequency="daily"))
    assert stored_habits(client, headers) == daily

    former = save(
        client,
        headers,
        {
            "vaping": {
                "status": "former",
                "frequency": "daily",
                "days_last_30": 12,
                "start_age": 25,
                "quit_age": 28,
            }
        },
    )
    expected = habits(vaping=vaping(status="former", start_age=25, quit_age=28))
    assert former == expected
    assert stored_habits(client, headers) == expected


# --- Humo ajeno en varios lugares, y después "No me expongo" (C-3) ----------------


def test_c3_secondhand_places_then_not_exposed(client: TestClient, db: Session) -> None:
    """Sin hábitos: home + work_school con 2 días -> GET los trae; después
    exposed false -> GET sin lugares ni días."""
    headers, _ = consented_user(client, db)
    exposed = {"exposed": True, "places": ["home", "work_school"], "days_per_week": 2}
    expected_exposed = habits(secondhand_smoke=secondhand(**exposed))

    assert save(client, headers, {"secondhand_smoke": exposed}) == expected_exposed
    assert stored_habits(client, headers) == expected_exposed

    saved = save(
        client,
        headers,
        {
            "secondhand_smoke": {
                "exposed": False,
                "places": ["home", "work_school"],
                "days_per_week": 2,
            }
        },
    )

    expected = habits(secondhand_smoke=secondhand(exposed=False))
    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c3_places_deduped_in_contract_order(client: TestClient, db: Session) -> None:
    """places desordenados y repetidos (other, home, other) -> PUT y GET con
    home, other: sin repetidos y en el orden del contrato (review R6)."""
    headers, _ = consented_user(client, db)
    expected = habits(
        secondhand_smoke=secondhand(
            exposed=True, places=["home", "other"], days_per_week=2
        )
    )

    saved = save(
        client,
        headers,
        {
            "secondhand_smoke": {
                "exposed": True,
                "places": ["other", "home", "other"],
                "days_per_week": 2,
            }
        },
    )

    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c3_exposed_without_places_rejected(client: TestClient, db: Session) -> None:
    """exposed true sin lugares -> 422 en places con el texto exacto; nada se
    guarda."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(
        client,
        headers,
        {"secondhand_smoke": {"exposed": True, "places": [], "days_per_week": 2}},
    )

    assert_single_error(r, ["body", "secondhand_smoke", "places"], PLACES_REQUIRED)
    assert stored_habits(client, headers) == SEED_STORED


# --- Test plan row 11: Humo de leña de antes (C-4, C-12) --------------------------


def test_c4_c12_former_wood_smoke_round_trip(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15: leña former, empezó a los 5, terminó a los 20, 3 horas
    al día -> PUT y GET iguales, sin ningún campo calculado."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    smoke = {"status": "former", "start_age": 5, "quit_age": 20, "hours_per_day": 3}
    expected = habits(wood_smoke=wood(**smoke))

    saved = save(client, headers, {"wood_smoke": smoke})

    assert saved == expected
    assert stored_habits(client, headers) == expected
    assert set(saved["wood_smoke"]) == WOOD_KEYS, saved["wood_smoke"]


# --- Contesta solo una cosa -------------------------------------------------------


def test_c_only_vaping_answered_rest_stays_null(
    client: TestClient, db: Session
) -> None:
    """Sin hábitos: solo vaping never -> vaping never y todo lo demás null."""
    headers, _ = consented_user(client, db)
    assert stored_habits(client, headers) == empty_habits()

    saved = save(client, headers, {"vaping": {"status": "never"}})

    expected = habits(vaping=vaping(status="never"))
    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c_all_null_put_stores_null(client: TestClient, db: Session) -> None:
    """Con hábitos guardados, un PUT todo null -> 200 todo null y la columna
    queda NULL (la tarjeta vuelve a "Sin llenar"; review R10)."""
    headers, user_id = consented_user(client, db)
    save(client, headers, SEED)

    saved = save(client, headers, empty_habits())

    assert saved == empty_habits()
    assert stored_habits(client, headers) == empty_habits()
    rows = raw_rows(
        "SELECT habits FROM patient_profile WHERE user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )
    assert len(rows) == 1, rows
    assert rows[0]["habits"] is None, rows


def test_c_get_does_not_create_the_profile(client: TestClient, db: Session) -> None:
    """Un usuario sin perfil: GET /profile/habits -> 200 todo null y no aparece
    fila en patient_profile (review R10)."""
    headers, user_id = consented_user(client, db)

    assert stored_habits(client, headers) == empty_habits()

    rows = raw_rows(
        "SELECT id FROM patient_profile WHERE user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )
    assert rows == [], rows


# --- Test plan row 13: Respuestas fuera de su escala ------------------------------

OUT_OF_SCALE_CASES = [
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 0}},
        id="cigarettes-0",
    ),
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 101}},
        id="cigarettes-101",
    ),
    pytest.param(
        {"secondhand_smoke": {"exposed": True, "places": ["home"], "days_per_week": 8}},
        id="secondhand-8-days",
    ),
    pytest.param({"alcohol": {"status": "quit", "quit_age": 131}}, id="age-131"),
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 5, "start_age": 131}},
        id="start_age-131",
    ),
    pytest.param(
        {"alcohol": {"status": "current", "start_age": 131}},
        id="alcohol-start_age-131",
    ),
    pytest.param(
        {"vaping": {"status": "current", "start_age": 131}},
        id="vaping-start_age-131",
    ),
    pytest.param(
        {"wood_smoke": {"status": "former", "start_age": 131}},
        id="wood-start_age-131",
    ),
    # Review R7: the lower bounds.
    pytest.param({"alcohol": {"status": "quit", "quit_age": -1}}, id="age--1"),
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 5, "start_age": -1}},
        id="start_age--1",
    ),
    pytest.param(
        {"tobacco": {"status": "former", "cigarettes_per_day": 5, "quit_age": -1}},
        id="tobacco-quit_age--1",
    ),
    pytest.param(
        {"vaping": {"status": "former", "quit_age": -1}},
        id="vaping-quit_age--1",
    ),
    pytest.param(
        {"wood_smoke": {"status": "former", "quit_age": -1}},
        id="wood-quit_age--1",
    ),
    pytest.param(
        {"secondhand_smoke": {"exposed": True, "places": ["home"], "days_per_week": 0}},
        id="secondhand-0-days",
    ),
    # perfil-habitos-ajustes: the new scales.
    pytest.param(
        {"vaping": {"status": "current", "frequency": "some_days", "days_last_30": 0}},
        id="vaping-days_last_30-0",
    ),
    pytest.param(
        {"vaping": {"status": "current", "frequency": "some_days", "days_last_30": 31}},
        id="vaping-days_last_30-31",
    ),
    pytest.param(
        {"wood_smoke": {"status": "current", "start_age": 5, "hours_per_day": 0}},
        id="wood-hours_per_day-0",
    ),
    pytest.param(
        {"wood_smoke": {"status": "current", "start_age": 5, "hours_per_day": 25}},
        id="wood-hours_per_day-25",
    ),
    pytest.param({"vaping": "current"}, id="vaping-as-plain-text-in-put"),
    pytest.param(
        {"wood_smoke": {"status": "former", "years": 12}},
        id="wood-years-in-put",
    ),
    pytest.param(
        {"vaping": {"status": "sometimes"}}, id="vaping-status-outside-enum"
    ),
    pytest.param(
        {"vaping": {"status": "current", "frequency": "weekly"}},
        id="vaping-frequency-outside-enum",
    ),
    pytest.param(
        {"alcohol": {"status": "sometimes"}}, id="alcohol-status-outside-enum"
    ),
    pytest.param(
        {"alcohol": {"status": "current", "frequency": "daily"}},
        id="frequency-outside-enum",
    ),
    pytest.param(
        {"secondhand_smoke": {"exposed": True, "places": ["car"], "days_per_week": 2}},
        id="place-outside-enum",
    ),
    pytest.param(
        {"vaping": {"status": "never"}, "drugs": "never"},
        id="unknown-top-level-field",
    ),
    pytest.param(
        {"alcohol": {"status": "never", "audit_c_score": 0}},
        id="unknown-nested-field",
    ),
]


@pytest.mark.parametrize("body", OUT_OF_SCALE_CASES)
def test_c_out_of_scale_answers_rejected_habits_unchanged(
    client: TestClient, db: Session, body: dict[str, Any]
) -> None:
    """Fuera de escala, fuera del catálogo, la forma anterior o un campo
    desconocido -> 422 y los hábitos guardados no cambian."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(client, headers, body)

    assert r.status_code == 422, r.text
    assert stored_habits(client, headers) == SEED_STORED


# --- Test plan row 14: Lo guardado antes de este cambio se sigue leyendo ----------

LEGACY_TOBACCO = {
    "status": "former",
    "cigarettes_per_day": 10,
    "start_age": 18,
    "quit_age": 30,
}


def test_legacy_stored_habits_still_read(
    client: TestClient, db: Session, caplog: pytest.LogCaptureFixture
) -> None:
    """Una fila cifrada con la forma anterior (vaping "current", leña former con
    years 12, tabaco former): GET -> vapeador {status current} sin frecuencia ni
    edades, leña former sin edades ni horas, tabaco igual, y sin aviso de fila
    ilegible en el log."""
    headers, user_id = consented_user(client, db)
    save(client, headers, {"tobacco": LEGACY_TOBACCO})
    legacy = json.dumps(
        {
            "alcohol": None,
            "tobacco": LEGACY_TOBACCO,
            "vaping": "current",
            "secondhand_smoke": None,
            "wood_smoke": {"status": "former", "years": 12},
        }
    )
    profile = store_raw_habits_json(db, user_id, legacy)

    with caplog.at_level(logging.WARNING, logger=profile_routes.__name__):
        r = get_habits(client, headers)

    assert r.status_code == 200, r.text
    assert r.json() == habits(
        tobacco=tobacco(**LEGACY_TOBACCO),
        vaping=vaping(status="current"),
        wood_smoke=wood(status="former"),
    )
    warnings = [
        rec
        for rec in caplog.records
        if rec.name == profile_routes.__name__ and rec.levelno >= logging.WARNING
    ]
    assert warnings == [], [rec.getMessage() for rec in warnings]
    assert "Unreadable habits" not in caplog.text
    assert str(profile.id) not in caplog.text


UPGRADE_CASES = [
    pytest.param(
        {"vaping": "current"},
        {"vaping": {"status": "current"}},
        id="vaping-text-current",
    ),
    pytest.param(
        {"vaping": "never"},
        {"vaping": {"status": "never"}},
        id="vaping-text-never",
    ),
    pytest.param(
        {"vaping": "former"},
        {"vaping": {"status": "former"}},
        id="vaping-text-former",
    ),
    pytest.param(
        {"wood_smoke": {"status": "former", "years": 12}},
        {"wood_smoke": {"status": "former"}},
        id="wood-years-dropped",
    ),
    pytest.param(
        {
            "tobacco": LEGACY_TOBACCO,
            "vaping": "current",
            "wood_smoke": {"status": "former", "years": 12},
            "secondhand_smoke": {
                "exposed": True,
                "places": ["home"],
                "days_per_week": 3,
            },
        },
        {
            "tobacco": LEGACY_TOBACCO,
            "vaping": {"status": "current"},
            "wood_smoke": {"status": "former"},
            "secondhand_smoke": {
                "exposed": True,
                "places": ["home"],
                "days_per_week": 3,
            },
        },
        id="full-legacy-row-rest-intact",
    ),
    pytest.param(
        {
            "alcohol": {"status": "quit", "start_age": 17, "quit_age": 30},
            "vaping": {"status": "current", "frequency": "daily", "start_age": 25},
            "wood_smoke": {"status": "former", "start_age": 5, "quit_age": 20},
        },
        {
            "alcohol": {"status": "quit", "start_age": 17, "quit_age": 30},
            "vaping": {"status": "current", "frequency": "daily", "start_age": 25},
            "wood_smoke": {"status": "former", "start_age": 5, "quit_age": 20},
        },
        id="new-shape-unchanged",
    ),
]


@pytest.mark.parametrize(("raw", "expected"), UPGRADE_CASES)
def test_upgrade_stored_habits_unit(
    raw: dict[str, Any], expected: dict[str, Any]
) -> None:
    """upgrade_stored_habits(raw) -> vaping como texto pasa a {"status": texto};
    wood_smoke.years se descarta; lo demás queda igual."""
    from app.models import upgrade_stored_habits

    result = upgrade_stored_habits(json.loads(json.dumps(raw)))

    assert isinstance(result, dict), result
    assert without_nulls(result) == without_nulls(expected)
    if isinstance(result.get("wood_smoke"), dict):
        assert "years" not in result["wood_smoke"], result
    Habits.model_validate(result)


# --- Test plan row 15: Sin puntaje ni riesgo (C-6) --------------------------------


def assert_contract_keys_only(body: dict[str, Any]) -> None:
    assert set(body) == TOP_LEVEL_KEYS, body
    assert set(body["alcohol"]) == ALCOHOL_KEYS, body["alcohol"]
    assert set(body["tobacco"]) == TOBACCO_KEYS, body["tobacco"]
    assert set(body["vaping"]) == VAPING_KEYS, body["vaping"]
    assert set(body["secondhand_smoke"]) == SECONDHAND_KEYS, body["secondhand_smoke"]
    assert set(body["wood_smoke"]) == WOOD_KEYS, body["wood_smoke"]


def test_c6_no_score_or_risk_in_the_response(client: TestClient, db: Session) -> None:
    """Caso extremo (alcohol four_plus_weekly, ten_plus, daily; tabaco current
    20 al día; leña current desde los 5 con 8 horas al día): PUT y GET traen
    exactamente las llaves del contrato nuevo, y ni "riesgo", ni "puntaje", ni
    "AUDIT", ni "horas-año"."""
    headers, _ = consented_user(client, db)
    body = {
        "alcohol": {
            "status": "current",
            "frequency": "four_plus_weekly",
            "typical_drinks": "ten_plus",
            "six_or_more": "daily",
        },
        "tobacco": {"status": "current", "cigarettes_per_day": 20},
        "vaping": {"status": "current", "frequency": "some_days", "days_last_30": 12},
        "secondhand_smoke": {"exposed": False},
        "wood_smoke": {"status": "current", "start_age": 5, "hours_per_day": 8},
    }

    r_put = put_habits(client, headers, body)
    assert r_put.status_code == 200, r_put.text
    r_get = get_habits(client, headers)
    assert r_get.status_code == 200, r_get.text

    for r in (r_put, r_get):
        assert_contract_keys_only(r.json())
        text_lower = r.text.lower()
        for word in ("riesgo", "puntaje", "audit", "horas-año", "horas-a\\u00f1o"):
            assert word not in text_lower, (word, r.text)


# --- Test plan row 22: Hábitos solo del paciente y cifrados -----------------------


def test_c_habits_isolated_and_encrypted_at_rest(
    client: TestClient, db: Session
) -> None:
    """A con alcohol current, vapeador some_days y humo ajeno en home: B recibe
    todo null; en BD los hábitos de A son un token Fernet sin respuestas ni
    nombres de campo en claro (tampoco "some_days"), que descifra al objeto
    normalizado."""
    headers_a, user_a = consented_user(client, db)
    headers_b, _ = consented_user(client, db)
    saved_a = save(
        client,
        headers_a,
        {
            "alcohol": {"status": "current", "frequency": "monthly_or_less"},
            "vaping": {
                "status": "current",
                "frequency": "some_days",
                "days_last_30": 12,
            },
            "secondhand_smoke": {
                "exposed": True,
                "places": ["home"],
                "days_per_week": 3,
            },
        },
    )

    r_b = get_habits(client, headers_b)
    assert r_b.status_code == 200, r_b.text
    assert r_b.json() == empty_habits()

    raw = raw_habits(user_a)
    assert raw.startswith("gAAAA"), raw
    for plain in (
        "current",
        "home",
        "alcohol",
        "monthly_or_less",
        "some_days",
        "vaping",
        "days_last_30",
    ):
        assert plain not in raw, plain
    decrypted = decrypt_str(raw)
    assert decrypted is not None
    assert without_nulls(json.loads(decrypted)) == without_nulls(saved_a)


# --- Review R2: hábitos guardados ilegibles ---------------------------------------


def test_unreadable_habits_read_as_null_and_logged_by_id(
    client: TestClient, db: Session, caplog: pytest.LogCaptureFixture
) -> None:
    """Una fila cifrada cuyos hábitos ya no validan (una llave desconocida, p. ej.
    de un C2 revertido): GET -> 200 todo null, el log trae solo el id del
    perfil, nunca las respuestas, y el error de validación tampoco las trae."""
    headers, user_id = consented_user(client, db)
    save(client, headers, SEED)
    unreadable = json.dumps({"vaping": "current", "physical_activity": "sedentary"})
    profile = store_raw_habits_json(db, user_id, unreadable)

    with caplog.at_level(logging.WARNING, logger=profile_routes.__name__):
        r = get_habits(client, headers)

    assert r.status_code == 200, r.text
    assert r.json() == empty_habits()
    assert str(profile.id) in caplog.text
    for answer in ("current", "physical_activity", "sedentary"):
        assert answer not in caplog.text, answer
    with pytest.raises(ValidationError) as exc_info:
        Habits.model_validate_json(unreadable)
    assert "sedentary" not in str(exc_info.value)


@pytest.mark.parametrize(
    ("method", "json_body"),
    [("GET", None), ("PUT", {"vaping": {"status": "never"}})],
    ids=["GET /profile/habits", "PUT /profile/habits"],
)
def test_c_habits_require_consent(
    client: TestClient,
    db: Session,
    method: str,
    json_body: dict[str, Any] | None,
) -> None:
    """Sin consentimiento: GET y PUT /profile/habits -> 403 CONSENT_REQUIRED."""
    headers = user_without_consent_headers(client, db)

    r = client.request(method, HABITS_URL, headers=headers, json=json_body)

    assert r.status_code == 403, (method, r.text)
    assert r.json()["detail"] == "CONSENT_REQUIRED"
