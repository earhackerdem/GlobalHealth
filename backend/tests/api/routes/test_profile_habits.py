"""Tests for the habits questionnaire of the medical profile (perfil-habitos,
perfil-habitos-ajustes, grupo 1, and perfil-habitos-completitud).

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

perfil-habitos-completitud (design.md, "## Interface contract"):
- start_age and quit_age of alcohol, tobacco, vaping and wood_smoke:
  0..130 | "unknown" | null; tobacco.cigarettes_per_day: 1..100 | "unknown" |
  null; wood_smoke.hours_per_day: 1..24 | "unknown" | null. "unknown" = "No
  recuerdo"; any other string, or "unknown" in any other field, is a schema 422.
- Normalization unchanged; an "unknown" that does not apply is dropped like a
  number.
- Validation after normalizing (one error per field, same 422 shape):
  alcohol quit -> start_age, quit_age (admit "unknown"); alcohol current ->
  frequency, typical_drinks, six_or_more, mostly_weekends (no "unknown") and
  start_age (admits it); tobacco former -> cigarettes_per_day, start_age,
  quit_age (admit it); tobacco current -> cigarettes_per_day (no) and start_age
  (admits); vaping former -> start_age, quit_age (admit); vaping current ->
  frequency, days_last_30 with some_days (no) and start_age (admits);
  secondhand exposed -> places, days_per_week (no); wood former -> start_age,
  quit_age, hours_per_day (admit); wood current -> hours_per_day (no) and
  start_age (admits). Missing without "unknown" -> "Contesta esta pregunta.";
  missing where admitted -> "Contesta esta pregunta o marca «No recuerdo».";
  "unknown" in cigarettes_per_day or hours_per_day with current -> "Esta
  pregunta no admite «No recuerdo».". The age rules compare numbers only.
- Rows saved before with partial data stay readable; nothing comes back as
  "unknown" unless it was saved as "unknown".

perfil-habitos-actividad-sueno (design.md, "## Interface contract"): Habits
gains three optional blocks, each null when unanswered:
- exercise: {does_exercise: bool, activities: {walking | running | cycling |
  swimming | weights_gym | football_other_sport | yoga_pilates | dance:
  {days_per_week: 1..7|null, minutes_per_session: 1..600|null} | null, other:
  {name: str 1..60 (trimmed)|null, days_per_week, minutes_per_session} | null}}
  | null (closed: one property per type, null when not chosen)
- daily_movement: {main_activity: sitting|standing_walking|light_loads|
  heavy_work|null, active_travel: bool|null, active_travel_days: 1..7|null,
  sitting_hours: 0..24|null} | null
- sleep: {hours: 1..24|null, trouble_falling_asleep and trouble_staying_asleep:
  never|some_days|most_days|every_day|null} | null
- No new field admits "unknown" nor text outside its scale (schema 422).
- Normalization: does_exercise false -> every activity null; active_travel not
  true -> active_travel_days null; other.name trimmed, empty -> null.
- Validation after normalizing (value_error, same 422 shape): does_exercise true
  without any activity -> "Elige al menos una actividad, o «No hago ejercicio»"
  at ["body", "exercise", "activities"]; a chosen activity without days or
  minutes -> "Contesta esta pregunta." at ["body", "exercise", "activities",
  <type>, <field>]; other chosen without name -> "Escribe cuál." on its name;
  active_travel true without days -> "Contesta esta pregunta." on
  active_travel_days.
- The weekly total is neither stored nor returned.
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
ANSWER_REQUIRED = "Contesta esta pregunta."
ANSWER_OR_UNKNOWN_REQUIRED = "Contesta esta pregunta o marca «No recuerdo»."
UNKNOWN_NOT_ADMITTED = "Esta pregunta no admite «No recuerdo»."

ACTIVITY_REQUIRED = "Elige al menos una actividad, o «No hago ejercicio»"
NAME_REQUIRED = "Escribe cuál."

UNKNOWN = "unknown"

TOP_LEVEL_KEYS = {
    "alcohol",
    "tobacco",
    "vaping",
    "secondhand_smoke",
    "wood_smoke",
    "exercise",
    "daily_movement",
    "sleep",
}
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

# perfil-habitos-actividad-sueno
ACTIVITY_TYPES = [
    "walking",
    "running",
    "cycling",
    "swimming",
    "weights_gym",
    "football_other_sport",
    "yoga_pilates",
    "dance",
    "other",
]
EXERCISE_KEYS = {"does_exercise", "activities"}
ACTIVITY_KEYS = {"days_per_week", "minutes_per_session"}
OTHER_ACTIVITY_KEYS = {"name", "days_per_week", "minutes_per_session"}
DAILY_MOVEMENT_KEYS = {
    "main_activity",
    "active_travel",
    "active_travel_days",
    "sitting_hours",
}
SLEEP_KEYS = {"hours", "trouble_falling_asleep", "trouble_staying_asleep"}
MAIN_ACTIVITY_LEVELS = ["sitting", "standing_walking", "light_loads", "heavy_work"]
SLEEP_FREQUENCIES = ["never", "some_days", "most_days", "every_day"]


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


def activity(activity_type: str, **fields: Any) -> dict[str, Any]:
    """A full (normalized) activity of the given type: the given fields, the
    rest null ("other" also has a name)."""
    keys = OTHER_ACTIVITY_KEYS if activity_type == "other" else ACTIVITY_KEYS
    return {**dict.fromkeys(keys), **fields}


def exercise(does_exercise: bool, **chosen: dict[str, Any]) -> dict[str, Any]:
    """A full (normalized) exercise block: every activity type present, the
    chosen ones with their fields, the rest null."""
    return {
        "does_exercise": does_exercise,
        "activities": {
            **dict.fromkeys(ACTIVITY_TYPES),
            **{t: activity(t, **fields) for t, fields in chosen.items()},
        },
    }


def movement(**fields: Any) -> dict[str, Any]:
    return {**dict.fromkeys(DAILY_MOVEMENT_KEYS), **fields}


def sleep_block(**fields: Any) -> dict[str, Any]:
    return {**dict.fromkeys(SLEEP_KEYS), **fields}


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
    """Nacido 1990-03-15, sin hábitos: alcohol current desde los 18,
    two_to_three_weekly, three_four, six_or_more monthly y mostly_weekends ->
    PUT y GET iguales."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text
    assert stored_habits(client, headers) == empty_habits()
    answers = {
        "status": "current",
        "start_age": 18,
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
    answers = {
        "status": "current",
        "start_age": 18,
        "frequency": "monthly_or_less",
        "typical_drinks": "one_two",
        "six_or_more": "never",
        "mostly_weekends": False,
    }
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
        {
            "alcohol": {
                "status": "current",
                "start_age": 40,
                "frequency": "monthly_or_less",
                "typical_drinks": "one_two",
                "six_or_more": "never",
                "mostly_weekends": False,
            }
        },
        ["body", "alcohol", "start_age"],
        id="alcohol-start_age",
    ),
    pytest.param(
        {"alcohol": {"status": "quit", "start_age": 18, "quit_age": 40}},
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
        {"alcohol": {"status": "quit", "start_age": 18, "quit_age": 36}},
        habits(alcohol=alcohol(status="quit", start_age=18, quit_age=36)),
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

    r = put_habits(
        client,
        headers,
        {"alcohol": {"status": "quit", "start_age": 18, "quit_age": 36}},
    )

    assert_single_error(r, ["body", "alcohol", "quit_age"], AGE_ABOVE_CURRENT)
    assert stored_habits(client, headers) == SEED_STORED
    saved = save(
        client,
        headers,
        {"alcohol": {"status": "quit", "start_age": 18, "quit_age": 35}},
    )
    assert saved == habits(alcohol=alcohol(status="quit", start_age=18, quit_age=35))


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
    # perfil-habitos-completitud: an "unknown" that does not apply is dropped
    # like a number.
    pytest.param(
        {"alcohol": {"status": "never", "start_age": UNKNOWN, "quit_age": UNKNOWN}},
        habits(alcohol=alcohol(status="never")),
        id="alcohol-never-drops-unknown-ages",
    ),
    pytest.param(
        {
            "alcohol": {
                "status": "current",
                "start_age": 17,
                "quit_age": UNKNOWN,
                **AUDIT_C,
            }
        },
        habits(alcohol=alcohol(status="current", start_age=17, **AUDIT_C)),
        id="alcohol-current-drops-unknown-quit_age",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "never",
                "cigarettes_per_day": UNKNOWN,
                "start_age": UNKNOWN,
                "quit_age": UNKNOWN,
            }
        },
        habits(tobacco=tobacco(status="never")),
        id="tobacco-never-drops-unknown-cigarettes-and-ages",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "current",
                "cigarettes_per_day": 10,
                "start_age": UNKNOWN,
                "quit_age": UNKNOWN,
            }
        },
        habits(
            tobacco=tobacco(status="current", cigarettes_per_day=10, start_age=UNKNOWN)
        ),
        id="tobacco-current-drops-unknown-quit_age",
    ),
    pytest.param(
        {"vaping": {"status": "never", "start_age": UNKNOWN, "quit_age": UNKNOWN}},
        habits(vaping=vaping(status="never")),
        id="vaping-never-drops-unknown-ages",
    ),
    pytest.param(
        {
            "wood_smoke": {
                "status": "never",
                "start_age": UNKNOWN,
                "quit_age": UNKNOWN,
                "hours_per_day": UNKNOWN,
            }
        },
        habits(wood_smoke=wood(status="never")),
        id="wood-never-drops-unknown-ages-and-hours",
    ),
    pytest.param(
        {
            "wood_smoke": {
                "status": "current",
                "start_age": 5,
                "quit_age": UNKNOWN,
                "hours_per_day": 8,
            }
        },
        habits(wood_smoke=wood(status="current", start_age=5, hours_per_day=8)),
        id="wood-current-drops-unknown-quit_age",
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
        {
            "tobacco": {
                "status": "current",
                "cigarettes_per_day": 5,
                "start_age": 18,
                "quit_age": 40,
            }
        },
    )

    expected = habits(
        tobacco=tobacco(status="current", cigarettes_per_day=5, start_age=18)
    )
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
    desde los 30, daily -> PUT y GET iguales."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    smoking = {
        "status": "former",
        "cigarettes_per_day": 10,
        "start_age": 18,
        "quit_age": 30,
    }
    vape = {"status": "current", "start_age": 30, "frequency": "daily"}
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
    """Vapeador current desde los 25, some_days con 12 días; luego daily (con
    los 12 días aún en el cuerpo) -> sin días; luego former 25/28 (con
    frecuencia y días en el cuerpo) -> former 25/28 sin frecuencia ni días."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    save(
        client,
        headers,
        {
            "vaping": {
                "status": "current",
                "start_age": 25,
                "frequency": "some_days",
                "days_last_30": 12,
            }
        },
    )

    daily = save(
        client,
        headers,
        {
            "vaping": {
                "status": "current",
                "start_age": 25,
                "frequency": "daily",
                "days_last_30": 12,
            }
        },
    )
    assert daily == habits(
        vaping=vaping(status="current", start_age=25, frequency="daily")
    )
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

# Each body is otherwise complete (perfil-habitos-completitud C-15), so the field
# outside its scale is the only problem: a schema 422 on that loc, never the
# required-answer value_error.
OUT_OF_SCALE_CASES = [
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 0, "start_age": 18}},
        ["body", "tobacco", "cigarettes_per_day"],
        id="cigarettes-0",
    ),
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 101, "start_age": 18}},
        ["body", "tobacco", "cigarettes_per_day"],
        id="cigarettes-101",
    ),
    pytest.param(
        {"secondhand_smoke": {"exposed": True, "places": ["home"], "days_per_week": 8}},
        ["body", "secondhand_smoke", "days_per_week"],
        id="secondhand-8-days",
    ),
    pytest.param(
        {"alcohol": {"status": "quit", "start_age": 18, "quit_age": 131}},
        ["body", "alcohol", "quit_age"],
        id="age-131",
    ),
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 5, "start_age": 131}},
        ["body", "tobacco", "start_age"],
        id="start_age-131",
    ),
    pytest.param(
        {"alcohol": {"status": "current", "start_age": 131, **AUDIT_C}},
        ["body", "alcohol", "start_age"],
        id="alcohol-start_age-131",
    ),
    pytest.param(
        {"vaping": {"status": "current", "frequency": "daily", "start_age": 131}},
        ["body", "vaping", "start_age"],
        id="vaping-start_age-131",
    ),
    pytest.param(
        {"wood_smoke": {"status": "current", "start_age": 131, "hours_per_day": 8}},
        ["body", "wood_smoke", "start_age"],
        id="wood-start_age-131",
    ),
    # Review R7: the lower bounds. A start age of "unknown" so it is never
    # compared with the quit age of -1.
    pytest.param(
        {"alcohol": {"status": "quit", "start_age": UNKNOWN, "quit_age": -1}},
        ["body", "alcohol", "quit_age"],
        id="age--1",
    ),
    pytest.param(
        {"tobacco": {"status": "current", "cigarettes_per_day": 5, "start_age": -1}},
        ["body", "tobacco", "start_age"],
        id="start_age--1",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "former",
                "cigarettes_per_day": 5,
                "start_age": UNKNOWN,
                "quit_age": -1,
            }
        },
        ["body", "tobacco", "quit_age"],
        id="tobacco-quit_age--1",
    ),
    pytest.param(
        {"vaping": {"status": "former", "start_age": UNKNOWN, "quit_age": -1}},
        ["body", "vaping", "quit_age"],
        id="vaping-quit_age--1",
    ),
    pytest.param(
        {
            "wood_smoke": {
                "status": "former",
                "start_age": UNKNOWN,
                "quit_age": -1,
                "hours_per_day": 8,
            }
        },
        ["body", "wood_smoke", "quit_age"],
        id="wood-quit_age--1",
    ),
    pytest.param(
        {"secondhand_smoke": {"exposed": True, "places": ["home"], "days_per_week": 0}},
        ["body", "secondhand_smoke", "days_per_week"],
        id="secondhand-0-days",
    ),
    # perfil-habitos-ajustes: the new scales.
    pytest.param(
        {
            "vaping": {
                "status": "current",
                "frequency": "some_days",
                "days_last_30": 0,
                "start_age": 25,
            }
        },
        ["body", "vaping", "days_last_30"],
        id="vaping-days_last_30-0",
    ),
    pytest.param(
        {
            "vaping": {
                "status": "current",
                "frequency": "some_days",
                "days_last_30": 31,
                "start_age": 25,
            }
        },
        ["body", "vaping", "days_last_30"],
        id="vaping-days_last_30-31",
    ),
    pytest.param(
        {"wood_smoke": {"status": "current", "start_age": 5, "hours_per_day": 0}},
        ["body", "wood_smoke", "hours_per_day"],
        id="wood-hours_per_day-0",
    ),
    pytest.param(
        {"wood_smoke": {"status": "current", "start_age": 5, "hours_per_day": 25}},
        ["body", "wood_smoke", "hours_per_day"],
        id="wood-hours_per_day-25",
    ),
    pytest.param(
        {"vaping": "current"}, ["body", "vaping"], id="vaping-as-plain-text-in-put"
    ),
    pytest.param(
        {"wood_smoke": {**ALL_WOOD, "status": "former", "years": 12}},
        ["body", "wood_smoke", "years"],
        id="wood-years-in-put",
    ),
    pytest.param(
        {"vaping": {"status": "sometimes"}},
        ["body", "vaping", "status"],
        id="vaping-status-outside-enum",
    ),
    pytest.param(
        {"vaping": {"status": "current", "frequency": "weekly", "start_age": 25}},
        ["body", "vaping", "frequency"],
        id="vaping-frequency-outside-enum",
    ),
    pytest.param(
        {"alcohol": {"status": "sometimes"}},
        ["body", "alcohol", "status"],
        id="alcohol-status-outside-enum",
    ),
    pytest.param(
        {
            "alcohol": {
                "status": "current",
                "start_age": 18,
                **AUDIT_C,
                "frequency": "daily",
            }
        },
        ["body", "alcohol", "frequency"],
        id="frequency-outside-enum",
    ),
    pytest.param(
        {"secondhand_smoke": {"exposed": True, "places": ["car"], "days_per_week": 2}},
        ["body", "secondhand_smoke", "places"],
        id="place-outside-enum",
    ),
    pytest.param(
        {"vaping": {"status": "never"}, "drugs": "never"},
        ["body", "drugs"],
        id="unknown-top-level-field",
    ),
    pytest.param(
        {"alcohol": {"status": "never", "audit_c_score": 0}},
        ["body", "alcohol", "audit_c_score"],
        id="unknown-nested-field",
    ),
    # perfil-habitos-completitud: any string other than "unknown" in a number.
    # ("unknown" in a current amount is a value_error by design, C-16:
    # test_c16_unknown_in_current_amount_rejected.)
    pytest.param(
        {"alcohol": {"status": "quit", "start_age": "no recuerdo", "quit_age": 30}},
        ["body", "alcohol", "start_age"],
        id="age-other-string",
    ),
    pytest.param(
        {"alcohol": {"status": "quit", "start_age": "Unknown", "quit_age": 30}},
        ["body", "alcohol", "start_age"],
        id="age-unknown-capitalized",
    ),
    pytest.param(
        {
            "tobacco": {
                "status": "former",
                "cigarettes_per_day": "unknown ",
                "start_age": 18,
                "quit_age": 30,
            }
        },
        ["body", "tobacco", "cigarettes_per_day"],
        id="cigarettes-unknown-with-space",
    ),
    pytest.param(
        {
            "wood_smoke": {
                "status": "former",
                "start_age": 5,
                "quit_age": 20,
                "hours_per_day": "",
            }
        },
        ["body", "wood_smoke", "hours_per_day"],
        id="hours-empty-string",
    ),
]


@pytest.mark.parametrize(("body", "loc"), OUT_OF_SCALE_CASES)
def test_c_out_of_scale_answers_rejected_habits_unchanged(
    client: TestClient, db: Session, body: dict[str, Any], loc: list[str]
) -> None:
    """Fuera de escala, fuera del catálogo, la forma anterior o un campo
    desconocido -> 422 del esquema en ese campo (no la regla de respuesta
    obligatoria) y los hábitos guardados no cambian."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(client, headers, body)

    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, list), detail
    assert detail, detail
    assert all(
        e["loc"][: len(loc)] == loc and e["type"] != "value_error" for e in detail
    ), detail
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
    assert UNKNOWN not in r.text, r.text
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


# --- perfil-habitos-completitud, row 2: Falta una pregunta de lo que eligió (C-15) -

BLOCK_HELPERS = {
    "alcohol": alcohol,
    "tobacco": tobacco,
    "vaping": vaping,
    "secondhand_smoke": secondhand,
    "wood_smoke": wood,
}

# One complete answer per row of the required table, with the fields it
# requires and the message each one gets when it is missing.
COMPLETE_ANSWERS: list[tuple[str, str, dict[str, Any], list[tuple[str, str]]]] = [
    (
        "alcohol",
        "quit",
        {"status": "quit", "start_age": 17, "quit_age": 30},
        [
            ("start_age", ANSWER_OR_UNKNOWN_REQUIRED),
            ("quit_age", ANSWER_OR_UNKNOWN_REQUIRED),
        ],
    ),
    (
        "alcohol",
        "current",
        {
            "status": "current",
            "start_age": 18,
            "frequency": "two_to_three_weekly",
            "typical_drinks": "three_four",
            "six_or_more": "monthly",
            "mostly_weekends": True,
        },
        [
            ("start_age", ANSWER_OR_UNKNOWN_REQUIRED),
            ("frequency", ANSWER_REQUIRED),
            ("typical_drinks", ANSWER_REQUIRED),
            ("six_or_more", ANSWER_REQUIRED),
            ("mostly_weekends", ANSWER_REQUIRED),
        ],
    ),
    (
        "tobacco",
        "former",
        {"status": "former", "cigarettes_per_day": 10, "start_age": 18, "quit_age": 30},
        [
            ("cigarettes_per_day", ANSWER_OR_UNKNOWN_REQUIRED),
            ("start_age", ANSWER_OR_UNKNOWN_REQUIRED),
            ("quit_age", ANSWER_OR_UNKNOWN_REQUIRED),
        ],
    ),
    (
        "tobacco",
        "current",
        {"status": "current", "cigarettes_per_day": 10, "start_age": 18},
        [
            ("cigarettes_per_day", ANSWER_REQUIRED),
            ("start_age", ANSWER_OR_UNKNOWN_REQUIRED),
        ],
    ),
    (
        "vaping",
        "former",
        {"status": "former", "start_age": 25, "quit_age": 28},
        [
            ("start_age", ANSWER_OR_UNKNOWN_REQUIRED),
            ("quit_age", ANSWER_OR_UNKNOWN_REQUIRED),
        ],
    ),
    (
        "vaping",
        "current-daily",
        {"status": "current", "frequency": "daily", "start_age": 25},
        [
            ("frequency", ANSWER_REQUIRED),
            ("start_age", ANSWER_OR_UNKNOWN_REQUIRED),
        ],
    ),
    (
        "vaping",
        "current-some_days",
        {
            "status": "current",
            "frequency": "some_days",
            "days_last_30": 12,
            "start_age": 25,
        },
        [("days_last_30", ANSWER_REQUIRED)],
    ),
    (
        "secondhand_smoke",
        "exposed",
        {"exposed": True, "places": ["home"], "days_per_week": 2},
        [
            # Today's rule for an exposure without places keeps its message.
            ("places", PLACES_REQUIRED),
            ("days_per_week", ANSWER_REQUIRED),
        ],
    ),
    (
        "wood_smoke",
        "former",
        {"status": "former", "start_age": 5, "quit_age": 20, "hours_per_day": 3},
        [
            ("start_age", ANSWER_OR_UNKNOWN_REQUIRED),
            ("quit_age", ANSWER_OR_UNKNOWN_REQUIRED),
            ("hours_per_day", ANSWER_OR_UNKNOWN_REQUIRED),
        ],
    ),
    (
        "wood_smoke",
        "current",
        {"status": "current", "start_age": 5, "hours_per_day": 8},
        [
            ("hours_per_day", ANSWER_REQUIRED),
            ("start_age", ANSWER_OR_UNKNOWN_REQUIRED),
        ],
    ),
]

COMPLETE_ANSWER_CASES = [
    pytest.param(block, answers, id=f"{block}-{label}")
    for block, label, answers, _ in COMPLETE_ANSWERS
]

MISSING_ANSWER_CASES = [
    pytest.param(block, answers, field, msg, how, id=f"{block}-{label}-{field}-{how}")
    for block, label, answers, required in COMPLETE_ANSWERS
    for field, msg in required
    for how in ("omitted", "null")
]


def without_answer(answers: dict[str, Any], field: str, how: str) -> dict[str, Any]:
    """The answers with one field left unanswered: omitted, or sent as null
    (places: an empty list)."""
    rest = {k: v for k, v in answers.items() if k != field}
    if how == "omitted":
        return rest
    return {**rest, field: [] if field == "places" else None}


@pytest.mark.parametrize(("block", "answers"), COMPLETE_ANSWER_CASES)
def test_c15_complete_answers_saved(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    block: str,
    answers: dict[str, Any],
) -> None:
    """Nacido 1990-03-15: cada respuesta con todas sus preguntas contestadas ->
    PUT y GET iguales (el control de los casos sin una pregunta)."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    expected = habits(**{block: BLOCK_HELPERS[block](**answers)})

    saved = save(client, headers, {block: answers})

    assert saved == expected
    assert stored_habits(client, headers) == expected


@pytest.mark.parametrize(
    ("block", "answers", "field", "msg", "how"), MISSING_ANSWER_CASES
)
def test_c15_missing_required_answer_rejected_habits_unchanged(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    block: str,
    answers: dict[str, Any],
    field: str,
    msg: str,
    how: str,
) -> None:
    """Nacido 1990-03-15, con hábitos guardados: por cada pregunta obligatoria
    de la respuesta elegida, el PUT sin ella (omitida o null) -> 422 en su loc
    con su mensaje exacto, y los hábitos guardados no cambian."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    save(client, headers, SEED)

    r = put_habits(client, headers, {block: without_answer(answers, field, how)})

    assert_single_error(r, ["body", block, field], msg)
    assert stored_habits(client, headers) == SEED_STORED


def test_c15_quit_alcohol_with_only_quit_age_rejected(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15, sin hábitos: alcohol quit con 30 en la edad en que lo
    dejó y sin edad de inicio -> 422 "Contesta esta pregunta o marca «No
    recuerdo»." en start_age, y nada se guarda."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)

    r = put_habits(client, headers, {"alcohol": {"status": "quit", "quit_age": 30}})

    assert_single_error(r, ["body", "alcohol", "start_age"], ANSWER_OR_UNKNOWN_REQUIRED)
    assert stored_habits(client, headers) == empty_habits()


def test_c15_current_alcohol_without_frequency_questions_four_errors(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15, sin hábitos: alcohol current con 18 de edad de inicio
    y sin las preguntas de frecuencia ni la de fines de semana -> 422 con
    "Contesta esta pregunta." en cada una de las cuatro, y nada se guarda."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)

    r = put_habits(client, headers, {"alcohol": {"status": "current", "start_age": 18}})

    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, list), detail
    errors = sorted((tuple(e["loc"]), e["msg"], e["type"]) for e in detail)
    assert errors == sorted(
        (("body", "alcohol", field), ANSWER_REQUIRED, "value_error")
        for field in ("frequency", "typical_drinks", "six_or_more", "mostly_weekends")
    ), detail
    assert stored_habits(client, headers) == empty_habits()


# --- perfil-habitos-completitud, rows 7, 9: Lo guardado a medias (C-15) -----------

PARTIAL_ALCOHOL = {"status": "quit", "quit_age": 30}


def test_c15_partial_row_saved_before_read_with_null(
    client: TestClient, db: Session, caplog: pytest.LogCaptureFixture
) -> None:
    """Una fila cifrada guardada antes con alcohol quit y solo la edad en que lo
    dejó: GET -> 200 con start_age null (nunca "unknown") y sin aviso de fila
    ilegible."""
    headers, user_id = consented_user(client, db)
    save(client, headers, SEED)
    store_raw_habits_json(db, user_id, json.dumps({"alcohol": PARTIAL_ALCOHOL}))

    with caplog.at_level(logging.WARNING, logger=profile_routes.__name__):
        r = get_habits(client, headers)

    assert r.status_code == 200, r.text
    assert r.json() == habits(alcohol=alcohol(**PARTIAL_ALCOHOL))
    assert r.json()["alcohol"]["start_age"] is None, r.text
    assert UNKNOWN not in r.text, r.text
    assert "Unreadable habits" not in caplog.text


def test_c15_partial_row_saved_before_resaved_as_is_rejected(
    client: TestClient, db: Session
) -> None:
    """La misma fila a medias: un PUT con lo que devolvió el GET, sin cambiar
    nada -> 422 "Contesta esta pregunta o marca «No recuerdo»." en start_age,
    y el GET sigue devolviendo lo guardado a medias."""
    headers, user_id = consented_user(client, db)
    save(client, headers, SEED)
    store_raw_habits_json(db, user_id, json.dumps({"alcohol": PARTIAL_ALCOHOL}))
    as_read = stored_habits(client, headers)

    r = put_habits(client, headers, as_read)

    assert_single_error(r, ["body", "alcohol", "start_age"], ANSWER_OR_UNKNOWN_REQUIRED)
    assert stored_habits(client, headers) == habits(alcohol=alcohol(**PARTIAL_ALCOHOL))


# --- perfil-habitos-completitud, row 4: No recuerda cuándo empezó (C-16) -----------


def test_c16_unknown_start_age_with_quit_age_18_saved_and_read_back(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15: alcohol quit con "No recuerdo" en la edad de inicio y
    18 en la de fin -> 200 (la edad de inicio no se compara) y el GET devuelve
    "unknown" y 18."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    expected = habits(alcohol=alcohol(status="quit", start_age=UNKNOWN, quit_age=18))

    saved = save(
        client,
        headers,
        {"alcohol": {"status": "quit", "start_age": UNKNOWN, "quit_age": 18}},
    )

    assert saved == expected
    assert stored_habits(client, headers) == expected


# Every field that admits "No recuerdo", next to numbers that would fail the
# age rules if "unknown" were compared (born 1990, today 36).
UNKNOWN_ADMITTED_CASES = [
    pytest.param(
        "alcohol",
        {"status": "quit", "start_age": 30, "quit_age": UNKNOWN},
        id="alcohol-quit-quit_age",
    ),
    pytest.param(
        "alcohol",
        {"status": "quit", "start_age": UNKNOWN, "quit_age": UNKNOWN},
        id="alcohol-quit-both-ages",
    ),
    pytest.param(
        "alcohol",
        {"status": "current", "start_age": UNKNOWN, **AUDIT_C},
        id="alcohol-current-start_age",
    ),
    pytest.param(
        "tobacco",
        {
            "status": "former",
            "cigarettes_per_day": UNKNOWN,
            "start_age": UNKNOWN,
            "quit_age": UNKNOWN,
        },
        id="tobacco-former-cigarettes-and-ages",
    ),
    pytest.param(
        "tobacco",
        {
            "status": "former",
            "cigarettes_per_day": 10,
            "start_age": 36,
            "quit_age": UNKNOWN,
        },
        id="tobacco-former-quit_age-beside-36",
    ),
    pytest.param(
        "tobacco",
        {"status": "current", "cigarettes_per_day": 10, "start_age": UNKNOWN},
        id="tobacco-current-start_age",
    ),
    pytest.param(
        "vaping",
        {"status": "former", "start_age": UNKNOWN, "quit_age": 18},
        id="vaping-former-start_age",
    ),
    pytest.param(
        "vaping",
        {"status": "current", "frequency": "daily", "start_age": UNKNOWN},
        id="vaping-current-start_age",
    ),
    pytest.param(
        "wood_smoke",
        {
            "status": "former",
            "start_age": UNKNOWN,
            "quit_age": UNKNOWN,
            "hours_per_day": UNKNOWN,
        },
        id="wood-former-ages-and-hours",
    ),
    pytest.param(
        "wood_smoke",
        {"status": "former", "start_age": 30, "quit_age": UNKNOWN, "hours_per_day": 3},
        id="wood-former-quit_age",
    ),
    pytest.param(
        "wood_smoke",
        {"status": "current", "start_age": UNKNOWN, "hours_per_day": 8},
        id="wood-current-start_age",
    ),
]


@pytest.mark.parametrize(("block", "answers"), UNKNOWN_ADMITTED_CASES)
def test_c16_unknown_admitted_saved_and_never_compared(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    block: str,
    answers: dict[str, Any],
) -> None:
    """Nacido 1990-03-15: "No recuerdo" en cada pregunta que lo admite -> 200,
    sin "≤ edad actual" ni "inicio ≤ fin", y el GET lo devuelve igual."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    expected = habits(**{block: BLOCK_HELPERS[block](**answers)})

    saved = save(client, headers, {block: answers})

    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c16_number_beside_unknown_still_checked_against_current_age(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15, hoy 36: alcohol quit con 40 de edad de inicio y "No
    recuerdo" en la de fin -> 422 "La edad no puede ser mayor que tu edad
    actual" en start_age (el número sí se compara), y nada cambia."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    save(client, headers, SEED)

    r = put_habits(
        client,
        headers,
        {"alcohol": {"status": "quit", "start_age": 40, "quit_age": UNKNOWN}},
    )

    assert_single_error(r, ["body", "alcohol", "start_age"], AGE_ABOVE_CURRENT)
    assert stored_habits(client, headers) == SEED_STORED


# --- perfil-habitos-completitud, rows 5, 8: "No recuerdo" solo en lo que pasó (C-16)

UNKNOWN_IN_CURRENT_AMOUNT_CASES = [
    pytest.param(
        "tobacco",
        {"status": "current", "cigarettes_per_day": UNKNOWN, "start_age": 18},
        "cigarettes_per_day",
        id="tobacco-current-cigarettes",
    ),
    pytest.param(
        "wood_smoke",
        {"status": "current", "start_age": 5, "hours_per_day": UNKNOWN},
        "hours_per_day",
        id="wood-current-hours",
    ),
]


@pytest.mark.parametrize(("block", "answers", "field"), UNKNOWN_IN_CURRENT_AMOUNT_CASES)
def test_c16_unknown_in_current_amount_rejected(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    block: str,
    answers: dict[str, Any],
    field: str,
) -> None:
    """Tabaco current con "No recuerdo" en cigarros, o leña current con "No
    recuerdo" en horas -> 422 "Esta pregunta no admite «No recuerdo»." en ese
    campo, y los hábitos guardados no cambian."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    save(client, headers, SEED)

    r = put_habits(client, headers, {block: answers})

    assert_single_error(r, ["body", block, field], UNKNOWN_NOT_ADMITTED)
    assert stored_habits(client, headers) == SEED_STORED


COMPLETE_CURRENT_ALCOHOL = {
    "status": "current",
    "start_age": 18,
    "frequency": "two_to_three_weekly",
    "typical_drinks": "three_four",
    "six_or_more": "monthly",
    "mostly_weekends": True,
}

UNKNOWN_SCHEMA_CASES = [
    *[
        pytest.param(
            "alcohol",
            {**COMPLETE_CURRENT_ALCOHOL, field: UNKNOWN},
            field,
            id=f"alcohol-{field}",
        )
        for field in ("frequency", "typical_drinks", "six_or_more", "mostly_weekends")
    ],
    pytest.param("alcohol", {"status": UNKNOWN}, "status", id="alcohol-status"),
    pytest.param(
        "vaping",
        {"status": "current", "frequency": UNKNOWN, "start_age": 25},
        "frequency",
        id="vaping-frequency",
    ),
    pytest.param(
        "vaping",
        {
            "status": "current",
            "frequency": "some_days",
            "days_last_30": UNKNOWN,
            "start_age": 25,
        },
        "days_last_30",
        id="vaping-days_last_30",
    ),
    pytest.param(
        "secondhand_smoke",
        {"exposed": True, "places": ["home"], "days_per_week": UNKNOWN},
        "days_per_week",
        id="secondhand-days_per_week",
    ),
    pytest.param(
        "secondhand_smoke",
        {"exposed": True, "places": [UNKNOWN], "days_per_week": 2},
        "places",
        id="secondhand-places",
    ),
    pytest.param(
        "secondhand_smoke",
        {"exposed": UNKNOWN},
        "exposed",
        id="secondhand-exposed",
    ),
]


@pytest.mark.parametrize(("block", "answers", "field"), UNKNOWN_SCHEMA_CASES)
def test_c16_unknown_where_never_admitted_is_schema_error(
    client: TestClient,
    db: Session,
    block: str,
    answers: dict[str, Any],
    field: str,
) -> None:
    """Un "unknown" en una pregunta del AUDIT-C, en fines de semana, en la
    frecuencia o los días del vapeador, o en el humo ajeno -> 422 del esquema
    en ese campo, y los hábitos guardados no cambian."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(client, headers, {block: answers})

    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, list), detail
    assert any(
        e["loc"][:3] == ["body", block, field] and e["type"] != "value_error"
        for e in detail
    ), detail
    assert stored_habits(client, headers) == SEED_STORED


# --- perfil-habitos-actividad-sueno -----------------------------------------------

WALKING_5X30 = {"days_per_week": 5, "minutes_per_session": 30}


def complete_activity(activity_type: str) -> dict[str, Any]:
    """A chosen activity with every question answered (3 days, 30 minutes;
    "other" also named)."""
    answers: dict[str, Any] = {"days_per_week": 3, "minutes_per_session": 30}
    if activity_type == "other":
        answers["name"] = "Senderismo"
    return answers


def doing(**chosen: dict[str, Any]) -> dict[str, Any]:
    """A PUT body that does exercise with the given activities (only the chosen
    ones are sent)."""
    return {"exercise": {"does_exercise": True, "activities": chosen}}


# --- row 1: Dos actividades con su total (C-5) ------------------------------------


def test_c5_two_activities_round_trip_without_total(
    client: TestClient, db: Session
) -> None:
    """Sin hábitos: caminar 5 días × 30 minutos y pesas o gimnasio 2 × 45 ->
    200, PUT y GET iguales, y ni la respuesta ni el GET traen un total (ni la
    llave ni 240)."""
    headers, _ = consented_user(client, db)
    expected = habits(
        exercise=exercise(
            True,
            walking=WALKING_5X30,
            weights_gym={"days_per_week": 2, "minutes_per_session": 45},
        )
    )

    r_put = put_habits(
        client,
        headers,
        doing(
            walking=WALKING_5X30,
            weights_gym={"days_per_week": 2, "minutes_per_session": 45},
        ),
    )
    assert r_put.status_code == 200, r_put.text
    r_get = get_habits(client, headers)
    assert r_get.status_code == 200, r_get.text

    for r in (r_put, r_get):
        assert r.json() == expected
        assert set(r.json()["exercise"]) == EXERCISE_KEYS, r.text
        assert "total" not in r.text.lower(), r.text
        assert "240" not in r.text, r.text


@pytest.mark.parametrize("activity_type", ACTIVITY_TYPES)
def test_c5_each_activity_type_complete_saved(
    client: TestClient, db: Session, activity_type: str
) -> None:
    """Cada tipo de actividad del catálogo, con sus días y minutos (y "Otra" con
    su nombre) -> 200, PUT y GET iguales (el control de los casos sin un
    dato)."""
    headers, _ = consented_user(client, db)
    answers = complete_activity(activity_type)
    expected = habits(exercise=exercise(True, **{activity_type: answers}))

    saved = save(client, headers, doing(**{activity_type: answers}))

    assert saved == expected
    assert stored_habits(client, headers) == expected


# --- row 2: Otra actividad con su nombre (C-5) ------------------------------------


@pytest.mark.parametrize(
    "other",
    [
        pytest.param({"days_per_week": 1, "minutes_per_session": 90}, id="omitted"),
        pytest.param(
            {"name": None, "days_per_week": 1, "minutes_per_session": 90}, id="null"
        ),
        pytest.param(
            {"name": "   ", "days_per_week": 1, "minutes_per_session": 90},
            id="whitespace-only",
        ),
    ],
)
def test_c5_other_without_name_rejected_habits_unchanged(
    client: TestClient, db: Session, other: dict[str, Any]
) -> None:
    """Elige "Otra" con 1 día y 90 minutos sin escribir cuál (omitido, null o
    solo espacios) -> 422 "Escribe cuál." en su nombre, y nada cambia."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(client, headers, doing(other=other))

    assert_single_error(
        r, ["body", "exercise", "activities", "other", "name"], NAME_REQUIRED
    )
    assert stored_habits(client, headers) == SEED_STORED


def test_c5_other_name_saved_trimmed(client: TestClient, db: Session) -> None:
    """Elige "Otra" con "  Senderismo ", 1 día y 90 minutos -> 200 y PUT y GET
    traen "Senderismo" recortado."""
    headers, _ = consented_user(client, db)
    expected = habits(
        exercise=exercise(
            True,
            other={"name": "Senderismo", "days_per_week": 1, "minutes_per_session": 90},
        )
    )

    saved = save(
        client,
        headers,
        doing(
            other={
                "name": "  Senderismo ",
                "days_per_week": 1,
                "minutes_per_session": 90,
            }
        ),
    )

    assert saved == expected
    assert stored_habits(client, headers) == expected
    assert saved["exercise"]["activities"]["other"]["name"] == "Senderismo"


# --- row 3: Falta un dato de una actividad (C-5, C-15) ----------------------------

MISSING_ACTIVITY_FIELD_CASES = [
    pytest.param(t, field, how, id=f"{t}-{field}-{how}")
    for t in ACTIVITY_TYPES
    for field in ("days_per_week", "minutes_per_session")
    for how in ("omitted", "null")
]


@pytest.mark.parametrize(
    ("activity_type", "field", "how"), MISSING_ACTIVITY_FIELD_CASES
)
def test_c5_c15_activity_without_days_or_minutes_rejected_habits_unchanged(
    client: TestClient, db: Session, activity_type: str, field: str, how: str
) -> None:
    """Por cada actividad y por cada dato (días, minutos), elegida sin él
    (omitido o null; p. ej. correr con 3 días y sin minutos) -> 422 "Contesta
    esta pregunta." en su loc de cuatro niveles, y nada cambia."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)
    answers = without_answer(complete_activity(activity_type), field, how)

    r = put_habits(client, headers, doing(**{activity_type: answers}))

    assert_single_error(
        r, ["body", "exercise", "activities", activity_type, field], ANSWER_REQUIRED
    )
    assert stored_habits(client, headers) == SEED_STORED


# --- row 4: No hago ejercicio (C-5) -----------------------------------------------


def test_c5_no_exercise_drops_saved_activities(client: TestClient, db: Session) -> None:
    """Con caminar 5 × 30 guardado: "No hago ejercicio" (con caminar aún en el
    cuerpo) -> 200, PUT y GET con does_exercise false y ninguna actividad."""
    headers, _ = consented_user(client, db)
    first = save(client, headers, doing(walking=WALKING_5X30))
    assert first["exercise"] == exercise(True, walking=WALKING_5X30), first

    saved = save(
        client,
        headers,
        {"exercise": {"does_exercise": False, "activities": {"walking": WALKING_5X30}}},
    )

    expected = habits(exercise=exercise(False))
    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c5_no_exercise_drops_incomplete_activities_before_validating(
    client: TestClient, db: Session
) -> None:
    """Elige "No hago ejercicio" con correr sin minutos y "Otra" sin nombre en
    el cuerpo -> 200 (se descartan antes de validar) y ninguna actividad."""
    headers, _ = consented_user(client, db)

    saved = save(
        client,
        headers,
        {
            "exercise": {
                "does_exercise": False,
                "activities": {
                    "running": {"days_per_week": 3},
                    "other": {"days_per_week": 1, "minutes_per_session": 90},
                },
            }
        },
    )

    expected = habits(exercise=exercise(False))
    assert saved == expected
    assert stored_habits(client, headers) == expected


@pytest.mark.parametrize(
    "chosen",
    [
        pytest.param({}, id="empty-object"),
        pytest.param(dict.fromkeys(ACTIVITY_TYPES), id="all-null"),
    ],
)
def test_c5_exercise_without_any_activity_rejected_habits_unchanged(
    client: TestClient, db: Session, chosen: dict[str, Any]
) -> None:
    """Hace ejercicio sin ninguna actividad -> 422 "Elige al menos una
    actividad, o «No hago ejercicio»" en exercise.activities, y nada cambia."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(client, headers, doing(**chosen))

    assert_single_error(r, ["body", "exercise", "activities"], ACTIVITY_REQUIRED)
    assert stored_habits(client, headers) == SEED_STORED


# --- row 5: Movimiento del día aparte del ejercicio (C-7) -------------------------

MOVEMENT_ROUND_TRIP_CASES = [
    *[
        pytest.param(
            {
                "main_activity": level,
                "active_travel": True,
                "active_travel_days": 5,
                "sitting_hours": 9,
            },
            id=f"{level}-travel-5-days-9-hours",
        )
        for level in MAIN_ACTIVITY_LEVELS
    ],
    pytest.param(
        {"main_activity": "heavy_work", "active_travel": False, "sitting_hours": 0},
        id="no-travel-0-hours",
    ),
    pytest.param(
        {
            "main_activity": "sitting",
            "active_travel": True,
            "active_travel_days": 7,
            "sitting_hours": 24,
        },
        id="travel-7-days-24-hours",
    ),
    pytest.param(
        {"active_travel": True, "active_travel_days": 1}, id="only-travel-1-day"
    ),
]


@pytest.mark.parametrize("answers", MOVEMENT_ROUND_TRIP_CASES)
def test_c7_daily_movement_round_trip(
    client: TestClient, db: Session, answers: dict[str, Any]
) -> None:
    """Los cuatro niveles de la actividad principal, el desplazamiento (Sí con
    días, No) y 0 y 24 horas sentado -> 200, PUT y GET iguales."""
    headers, _ = consented_user(client, db)
    expected = habits(daily_movement=movement(**answers))

    saved = save(client, headers, {"daily_movement": answers})

    assert saved == expected
    assert stored_habits(client, headers) == expected


def test_c7_daily_movement_apart_from_exercise(client: TestClient, db: Session) -> None:
    """Caminar 5 × 30, "Casi todo sentado", Sí al desplazamiento con 5 días y 9
    horas sentado -> 200; el ejercicio queda igual (el movimiento no se suma),
    sin total, y el GET trae las tres respuestas del movimiento."""
    headers, _ = consented_user(client, db)
    day = {
        "main_activity": "sitting",
        "active_travel": True,
        "active_travel_days": 5,
        "sitting_hours": 9,
    }
    expected = habits(
        exercise=exercise(True, walking=WALKING_5X30), daily_movement=movement(**day)
    )

    r_put = put_habits(
        client, headers, {**doing(walking=WALKING_5X30), "daily_movement": day}
    )
    assert r_put.status_code == 200, r_put.text
    r_get = get_habits(client, headers)
    assert r_get.status_code == 200, r_get.text

    for r in (r_put, r_get):
        assert r.json() == expected
        assert "total" not in r.text.lower(), r.text
        assert "150" not in r.text, r.text


# --- row 6: Desplazamiento sin días (C-7, C-15) -----------------------------------


@pytest.mark.parametrize("how", ["omitted", "null"])
def test_c7_c15_active_travel_without_days_rejected_habits_unchanged(
    client: TestClient, db: Session, how: str
) -> None:
    """Sí a caminar o ir en bici para ir a algún lado sin los días (omitidos o
    null) -> 422 "Contesta esta pregunta." en active_travel_days, y nada
    cambia."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)
    answers = without_answer(
        {"main_activity": "sitting", "active_travel": True, "active_travel_days": 5},
        "active_travel_days",
        how,
    )

    r = put_habits(client, headers, {"daily_movement": answers})

    assert_single_error(
        r, ["body", "daily_movement", "active_travel_days"], ANSWER_REQUIRED
    )
    assert stored_habits(client, headers) == SEED_STORED


@pytest.mark.parametrize(
    "active_travel",
    [pytest.param(False, id="no"), pytest.param(None, id="unanswered")],
)
def test_c7_active_travel_not_yes_drops_days(
    client: TestClient, db: Session, active_travel: bool | None
) -> None:
    """Desplazamiento No (o sin contestar) con 5 días en el cuerpo -> 200 y los
    días se descartan."""
    headers, _ = consented_user(client, db)

    saved = save(
        client,
        headers,
        {
            "daily_movement": {
                "main_activity": "sitting",
                "active_travel": active_travel,
                "active_travel_days": 5,
            }
        },
    )

    expected = habits(
        daily_movement=movement(main_activity="sitting", active_travel=active_travel)
    )
    assert saved == expected
    assert stored_habits(client, headers) == expected


# --- row 7: Sueño con las dos frecuencias (C-8) -----------------------------------


def test_c8_sleep_with_both_frequencies_round_trip(
    client: TestClient, db: Session
) -> None:
    """6 horas, "Algunos días" a que le costó dormirse y "Casi todos los días" a
    que le costó seguir durmiendo -> 200, PUT y GET iguales, cada una en su
    campo."""
    headers, _ = consented_user(client, db)
    answers = {
        "hours": 6,
        "trouble_falling_asleep": "some_days",
        "trouble_staying_asleep": "most_days",
    }
    expected = habits(sleep=sleep_block(**answers))

    saved = save(client, headers, {"sleep": answers})

    assert saved == expected
    assert stored_habits(client, headers) == expected


@pytest.mark.parametrize("frequency", SLEEP_FREQUENCIES)
def test_c8_each_sleep_frequency_accepted(
    client: TestClient, db: Session, frequency: str
) -> None:
    """Cada valor de la escala (nunca · algunos días · casi todos · todos) en las
    dos frecuencias, con 1 y 24 horas -> 200 y GET igual."""
    headers, _ = consented_user(client, db)
    for hours in (1, 24):
        answers = {
            "hours": hours,
            "trouble_falling_asleep": frequency,
            "trouble_staying_asleep": frequency,
        }
        expected = habits(sleep=sleep_block(**answers))

        saved = save(client, headers, {"sleep": answers})

        assert saved == expected
        assert stored_habits(client, headers) == expected


# --- row 8: Fuera de escala en los bloques nuevos ---------------------------------

COMPLETE_MOVEMENT = {
    "main_activity": "sitting",
    "active_travel": True,
    "active_travel_days": 5,
    "sitting_hours": 9,
}
COMPLETE_SLEEP = {
    "hours": 6,
    "trouble_falling_asleep": "some_days",
    "trouble_staying_asleep": "most_days",
}
COMPLETE_OTHER = complete_activity("other")

ACTIVITY_LOC = ["body", "exercise", "activities"]
MOVEMENT_LOC = ["body", "daily_movement"]
SLEEP_LOC = ["body", "sleep"]


def walking_with(**fields: Any) -> dict[str, Any]:
    return doing(walking={**WALKING_5X30, **fields})


def other_with(**fields: Any) -> dict[str, Any]:
    return doing(other={**COMPLETE_OTHER, **fields})


def moving_with(**fields: Any) -> dict[str, Any]:
    return {"daily_movement": {**COMPLETE_MOVEMENT, **fields}}


def sleeping_with(**fields: Any) -> dict[str, Any]:
    return {"sleep": {**COMPLETE_SLEEP, **fields}}


# Each body is otherwise complete, so the field outside its scale is the only
# problem: a schema 422 on that loc, never the required-answer value_error.
NEW_BLOCKS_OUT_OF_SCALE_CASES = [
    # Exercise: days 1..7, minutes 1..600, the name 1..60.
    pytest.param(
        walking_with(days_per_week=0),
        [*ACTIVITY_LOC, "walking", "days_per_week"],
        id="walking-days-0",
    ),
    pytest.param(
        walking_with(days_per_week=8),
        [*ACTIVITY_LOC, "walking", "days_per_week"],
        id="walking-days-8",
    ),
    pytest.param(
        other_with(days_per_week=8),
        [*ACTIVITY_LOC, "other", "days_per_week"],
        id="other-days-8",
    ),
    pytest.param(
        walking_with(minutes_per_session=0),
        [*ACTIVITY_LOC, "walking", "minutes_per_session"],
        id="walking-minutes-0",
    ),
    pytest.param(
        walking_with(minutes_per_session=601),
        [*ACTIVITY_LOC, "walking", "minutes_per_session"],
        id="walking-minutes-601",
    ),
    pytest.param(
        other_with(minutes_per_session=601),
        [*ACTIVITY_LOC, "other", "minutes_per_session"],
        id="other-minutes-601",
    ),
    pytest.param(
        other_with(name="a" * 61),
        [*ACTIVITY_LOC, "other", "name"],
        id="other-name-61-chars",
    ),
    # Daily movement: travel days 1..7, sitting hours 0..24.
    pytest.param(
        moving_with(active_travel_days=0),
        [*MOVEMENT_LOC, "active_travel_days"],
        id="travel-days-0",
    ),
    pytest.param(
        moving_with(active_travel_days=8),
        [*MOVEMENT_LOC, "active_travel_days"],
        id="travel-days-8",
    ),
    pytest.param(
        moving_with(sitting_hours=-1),
        [*MOVEMENT_LOC, "sitting_hours"],
        id="sitting-hours--1",
    ),
    pytest.param(
        moving_with(sitting_hours=25),
        [*MOVEMENT_LOC, "sitting_hours"],
        id="sitting-hours-25",
    ),
    # Sleep: whole hours 1..24.
    pytest.param(sleeping_with(hours=0), [*SLEEP_LOC, "hours"], id="sleep-hours-0"),
    pytest.param(sleeping_with(hours=25), [*SLEEP_LOC, "hours"], id="sleep-hours-25"),
    pytest.param(
        sleeping_with(hours=6.5), [*SLEEP_LOC, "hours"], id="sleep-hours-not-whole"
    ),
    # "No recuerdo" in any new question.
    pytest.param(
        walking_with(days_per_week=UNKNOWN),
        [*ACTIVITY_LOC, "walking", "days_per_week"],
        id="walking-days-unknown",
    ),
    pytest.param(
        walking_with(minutes_per_session=UNKNOWN),
        [*ACTIVITY_LOC, "walking", "minutes_per_session"],
        id="walking-minutes-unknown",
    ),
    pytest.param(
        other_with(days_per_week=UNKNOWN),
        [*ACTIVITY_LOC, "other", "days_per_week"],
        id="other-days-unknown",
    ),
    pytest.param(
        other_with(minutes_per_session=UNKNOWN),
        [*ACTIVITY_LOC, "other", "minutes_per_session"],
        id="other-minutes-unknown",
    ),
    pytest.param(
        {
            "exercise": {
                "does_exercise": UNKNOWN,
                "activities": {"walking": WALKING_5X30},
            }
        },
        ["body", "exercise", "does_exercise"],
        id="does_exercise-unknown",
    ),
    pytest.param(
        moving_with(active_travel_days=UNKNOWN),
        [*MOVEMENT_LOC, "active_travel_days"],
        id="travel-days-unknown",
    ),
    pytest.param(
        moving_with(sitting_hours=UNKNOWN),
        [*MOVEMENT_LOC, "sitting_hours"],
        id="sitting-hours-unknown",
    ),
    pytest.param(
        moving_with(active_travel=UNKNOWN),
        [*MOVEMENT_LOC, "active_travel"],
        id="active_travel-unknown",
    ),
    pytest.param(
        moving_with(main_activity=UNKNOWN),
        [*MOVEMENT_LOC, "main_activity"],
        id="main_activity-unknown",
    ),
    pytest.param(
        sleeping_with(hours=UNKNOWN), [*SLEEP_LOC, "hours"], id="sleep-hours-unknown"
    ),
    pytest.param(
        sleeping_with(trouble_falling_asleep=UNKNOWN),
        [*SLEEP_LOC, "trouble_falling_asleep"],
        id="falling-asleep-unknown",
    ),
    pytest.param(
        sleeping_with(trouble_staying_asleep=UNKNOWN),
        [*SLEEP_LOC, "trouble_staying_asleep"],
        id="staying-asleep-unknown",
    ),
    # Outside the catalogs.
    pytest.param(
        doing(walking=WALKING_5X30, hiking=WALKING_5X30),
        [*ACTIVITY_LOC, "hiking"],
        id="activity-type-outside-catalog",
    ),
    pytest.param(
        {"exercise": {"does_exercise": True, "activities": ["walking"]}},
        ACTIVITY_LOC,
        id="activities-as-a-list",
    ),
    pytest.param(
        moving_with(main_activity="sedentary"),
        [*MOVEMENT_LOC, "main_activity"],
        id="main_activity-outside-scale",
    ),
    pytest.param(
        sleeping_with(trouble_falling_asleep="always"),
        [*SLEEP_LOC, "trouble_falling_asleep"],
        id="falling-asleep-outside-scale",
    ),
    pytest.param(
        sleeping_with(trouble_staying_asleep="sometimes"),
        [*SLEEP_LOC, "trouble_staying_asleep"],
        id="staying-asleep-outside-scale",
    ),
    # Closed blocks: an extra property.
    pytest.param(
        {
            "exercise": {
                "does_exercise": True,
                "activities": {"walking": WALKING_5X30},
                "total_minutes_per_week": 150,
            }
        },
        ["body", "exercise", "total_minutes_per_week"],
        id="exercise-extra-property",
    ),
    pytest.param(
        walking_with(total=150),
        [*ACTIVITY_LOC, "walking", "total"],
        id="activity-extra-property",
    ),
    pytest.param(
        other_with(notes="con mi perro"),
        [*ACTIVITY_LOC, "other", "notes"],
        id="other-extra-property",
    ),
    pytest.param(
        moving_with(level="sedentary"),
        [*MOVEMENT_LOC, "level"],
        id="daily_movement-extra-property",
    ),
    pytest.param(
        sleeping_with(quality="bad"),
        [*SLEEP_LOC, "quality"],
        id="sleep-extra-property",
    ),
]


@pytest.mark.parametrize(("body", "loc"), NEW_BLOCKS_OUT_OF_SCALE_CASES)
def test_c5_c7_c8_out_of_scale_in_new_blocks_rejected_habits_unchanged(
    client: TestClient, db: Session, body: dict[str, Any], loc: list[str]
) -> None:
    """8 días, 601 minutos, 25 horas sentado, 0 horas de sueño, un nombre de 61,
    "No recuerdo", un valor fuera del catálogo o una propiedad extra en los
    bloques nuevos -> 422 del esquema en ese campo (no la regla de respuesta
    obligatoria), y los hábitos guardados no cambian."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(client, headers, body)

    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, list), detail
    assert detail, detail
    assert all(
        e["loc"][: len(loc)] == loc and e["type"] != "value_error" for e in detail
    ), detail
    assert stored_habits(client, headers) == SEED_STORED


# --- row 9: Solo el sueño ---------------------------------------------------------


def test_c8_only_sleep_hours_answered_rest_stays_null(
    client: TestClient, db: Session
) -> None:
    """Sin hábitos: solo 7 horas de sueño -> 200, sleep con 7 horas y todos los
    demás bloques null."""
    headers, _ = consented_user(client, db)
    assert stored_habits(client, headers) == empty_habits()

    saved = save(client, headers, {"sleep": {"hours": 7}})

    expected = habits(sleep=sleep_block(hours=7))
    assert saved == expected
    assert stored_habits(client, headers) == expected
    assert all(saved[key] is None for key in TOP_LEVEL_KEYS - {"sleep"}), saved


# --- Test plan row 15: Sin puntaje ni riesgo (C-6) --------------------------------


def assert_contract_keys_only(body: dict[str, Any]) -> None:
    assert set(body) == TOP_LEVEL_KEYS, body
    assert set(body["alcohol"]) == ALCOHOL_KEYS, body["alcohol"]
    assert set(body["tobacco"]) == TOBACCO_KEYS, body["tobacco"]
    assert set(body["vaping"]) == VAPING_KEYS, body["vaping"]
    assert set(body["secondhand_smoke"]) == SECONDHAND_KEYS, body["secondhand_smoke"]
    assert set(body["wood_smoke"]) == WOOD_KEYS, body["wood_smoke"]


def test_c6_no_score_or_risk_in_the_response(client: TestClient, db: Session) -> None:
    """Caso extremo (alcohol current desde los 15, four_plus_weekly, ten_plus,
    daily, no en fines de semana; tabaco current 20 al día desde "No
    recuerdo"; leña current desde los 5 con 8 horas al día): PUT y GET traen
    exactamente las llaves del contrato nuevo, "No recuerdo" tal cual, y ni
    "riesgo", ni "puntaje", ni "AUDIT", ni "horas-año"."""
    headers, _ = consented_user(client, db)
    body = {
        "alcohol": {
            "status": "current",
            "start_age": 15,
            "frequency": "four_plus_weekly",
            "typical_drinks": "ten_plus",
            "six_or_more": "daily",
            "mostly_weekends": False,
        },
        "tobacco": {
            "status": "current",
            "cigarettes_per_day": 20,
            "start_age": UNKNOWN,
        },
        "vaping": {
            "status": "current",
            "start_age": 20,
            "frequency": "some_days",
            "days_last_30": 12,
        },
        "secondhand_smoke": {"exposed": False},
        "wood_smoke": {"status": "current", "start_age": 5, "hours_per_day": 8},
    }

    r_put = put_habits(client, headers, body)
    assert r_put.status_code == 200, r_put.text
    r_get = get_habits(client, headers)
    assert r_get.status_code == 200, r_get.text

    for r in (r_put, r_get):
        assert_contract_keys_only(r.json())
        assert r.json()["tobacco"]["start_age"] == UNKNOWN, r.text
        text_lower = r.text.lower()
        for word in ("riesgo", "puntaje", "audit", "horas-año", "horas-a\\u00f1o"):
            assert word not in text_lower, (word, r.text)


def assert_new_blocks_keys_only(body: dict[str, Any]) -> None:
    """The three new blocks carry exactly the contract's keys (no total, no
    derived field)."""
    assert set(body) == TOP_LEVEL_KEYS, body
    assert set(body["exercise"]) == EXERCISE_KEYS, body["exercise"]
    activities = body["exercise"]["activities"]
    assert set(activities) == set(ACTIVITY_TYPES), activities
    for activity_type, answers in activities.items():
        if answers is not None:
            keys = OTHER_ACTIVITY_KEYS if activity_type == "other" else ACTIVITY_KEYS
            assert set(answers) == keys, (activity_type, answers)
    assert set(body["daily_movement"]) == DAILY_MOVEMENT_KEYS, body["daily_movement"]
    assert set(body["sleep"]) == SLEEP_KEYS, body["sleep"]


def test_c5_c6_weekly_total_without_verdict(client: TestClient, db: Session) -> None:
    """Caminar 1 día × 20 minutos, "Casi todo sentado", 12 horas sentado, 4
    horas de sueño y "Todos los días" en las dos frecuencias: PUT y GET traen
    exactamente las llaves del contrato, sin total guardado, y ni "150", "OMS",
    "recomend", "insuficiente", "sedentari", "insomnio", "riesgo" ni
    "puntaje"."""
    headers, _ = consented_user(client, db)
    body = {
        "exercise": {
            "does_exercise": True,
            "activities": {"walking": {"days_per_week": 1, "minutes_per_session": 20}},
        },
        "daily_movement": {"main_activity": "sitting", "sitting_hours": 12},
        "sleep": {
            "hours": 4,
            "trouble_falling_asleep": "every_day",
            "trouble_staying_asleep": "every_day",
        },
    }
    expected = habits(
        exercise=exercise(
            True, walking={"days_per_week": 1, "minutes_per_session": 20}
        ),
        daily_movement=movement(main_activity="sitting", sitting_hours=12),
        sleep=sleep_block(
            hours=4,
            trouble_falling_asleep="every_day",
            trouble_staying_asleep="every_day",
        ),
    )

    r_put = put_habits(client, headers, body)
    assert r_put.status_code == 200, r_put.text
    r_get = get_habits(client, headers)
    assert r_get.status_code == 200, r_get.text

    for r in (r_put, r_get):
        assert r.json() == expected
        assert_new_blocks_keys_only(r.json())
        text_lower = r.text.lower()
        for word in (
            "total",
            "150",
            "oms",
            "recomend",
            "insuficiente",
            "sedentari",
            "insomnio",
            "riesgo",
            "puntaje",
        ):
            assert word not in text_lower, (word, r.text)


# --- Test plan row 22: Hábitos solo del paciente y cifrados -----------------------


def test_c_habits_isolated_and_encrypted_at_rest(
    client: TestClient, db: Session
) -> None:
    """A con alcohol current, vapeador some_days (ambos desde "No recuerdo") y
    humo ajeno en home, "Otra: Senderismo", movimiento y sueño: B recibe todo
    null; en BD los hábitos de A son un token Fernet sin respuestas ni nombres
    de campo en claro (tampoco "some_days", "unknown", "Senderismo" ni
    "trouble_falling_asleep"), que descifra al objeto normalizado."""
    headers_a, user_a = consented_user(client, db)
    headers_b, _ = consented_user(client, db)
    saved_a = save(
        client,
        headers_a,
        {
            "alcohol": {
                "status": "current",
                "start_age": UNKNOWN,
                "frequency": "monthly_or_less",
                "typical_drinks": "one_two",
                "six_or_more": "never",
                "mostly_weekends": False,
            },
            "vaping": {
                "status": "current",
                "start_age": UNKNOWN,
                "frequency": "some_days",
                "days_last_30": 12,
            },
            "secondhand_smoke": {
                "exposed": True,
                "places": ["home"],
                "days_per_week": 3,
            },
            # perfil-habitos-actividad-sueno: the new blocks, same treatment.
            "exercise": {
                "does_exercise": True,
                "activities": {
                    "other": {
                        "name": "Senderismo",
                        "days_per_week": 1,
                        "minutes_per_session": 90,
                    }
                },
            },
            "daily_movement": {"main_activity": "light_loads", "sitting_hours": 6},
            "sleep": {
                "hours": 6,
                "trouble_falling_asleep": "most_days",
                "trouble_staying_asleep": "never",
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
        UNKNOWN,
        "start_age",
        "Senderismo",
        "exercise",
        "minutes_per_session",
        "light_loads",
        "sleep",
        "trouble_falling_asleep",
        "most_days",
    ):
        assert plain not in raw, plain
    decrypted = decrypt_str(raw)
    assert decrypted is not None
    assert UNKNOWN in decrypted
    assert "Senderismo" in decrypted
    assert "trouble_falling_asleep" in decrypted
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
    "unreadable",
    [
        '{"tobacco": ',
        json.dumps([{"status": "never"}]),
        # json.loads raises RecursionError (not a ValueError) at this depth.
        "[" * 100_000 + "]" * 100_000,
    ],
    ids=["JSON inválido", "una lista", "anidado 100 000 niveles"],
)
def test_unreadable_habits_json_read_as_null_not_500(
    client: TestClient,
    db: Session,
    caplog: pytest.LogCaptureFixture,
    unreadable: str,
) -> None:
    """Review B1 (perfil-habitos-ajustes, fila 14): an encrypted row that is not
    a readable JSON object is read as all null with the unreadable-row warning,
    never a 500."""
    headers, user_id = consented_user(client, db)
    save(client, headers, SEED)
    profile = store_raw_habits_json(db, user_id, unreadable)

    with caplog.at_level(logging.WARNING, logger=profile_routes.__name__):
        r = get_habits(client, headers)

    assert r.status_code == 200, r.text
    assert r.json() == empty_habits()
    assert f"Unreadable habits of patient profile {profile.id}" in caplog.text


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
