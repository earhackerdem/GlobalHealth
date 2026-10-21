"""Tests for the habits questionnaire of the medical profile (perfil-habitos, grupo 1).

Interface contract (design.md, "## Interface contract"; base /api/v1/profile,
behind a current consent; field names and values in English):
- Habits (same object in the PUT body and the response; everything optional,
  extra="forbid"):
  - alcohol: {status: never|quit|current (required), quit_age: 0..130|null,
    frequency: monthly_or_less|two_to_four_monthly|two_to_three_weekly|
    four_plus_weekly|null, typical_drinks: one_two|three_four|five_six|
    seven_nine|ten_plus|null, six_or_more: never|less_than_monthly|monthly|
    weekly|daily|null, mostly_weekends: bool|null} | null
  - tobacco: {status: never|former|current (required), cigarettes_per_day:
    1..100|null, start_age: 0..130|null, quit_age: 0..130|null} | null
  - vaping: never|former|current|null
  - secondhand_smoke: {exposed: bool (required), places: [home|work_school|
    other] (no repeats, in this order), days_per_week: 1..7|null} | null
  - wood_smoke: {status: never|former|current (required), years: 0..130|null}
    | null
- Normalization (server, before encrypting): alcohol != current -> the AUDIT-C
  answers and mostly_weekends null; alcohol != quit -> quit_age null; tobacco
  never -> cigarettes_per_day, start_age, quit_age null; tobacco != former ->
  quit_age null; wood never -> years null; exposed false -> places [] and
  days_per_week null.
- Validation (server, after normalizing; "today" is Mexico City's, from
  app.api.routes.profile): alcohol.quit_age, tobacco.start_age,
  tobacco.quit_age above the current age -> "La edad no puede ser mayor que tu
  edad actual" (not compared without a birth date); tobacco.start_age >
  tobacco.quit_age -> "No puede ser mayor que la edad en que lo dejaste" on
  start_age; exposed true without places -> "Elige dónde, o «No me expongo»" on
  places. These 422s have FastAPI's validation shape:
  detail: [{"loc": ["body", <block>, <field>], "msg": <es-MX>, "type": "value_error"}].
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
PLACES_REQUIRED = "Elige dónde, o «No me expongo»"

TOP_LEVEL_KEYS = {"alcohol", "tobacco", "vaping", "secondhand_smoke", "wood_smoke"}
ALCOHOL_KEYS = {
    "status",
    "quit_age",
    "frequency",
    "typical_drinks",
    "six_or_more",
    "mostly_weekends",
}
TOBACCO_KEYS = {"status", "cigarettes_per_day", "start_age", "quit_age"}
SECONDHAND_KEYS = {"exposed", "places", "days_per_week"}
WOOD_KEYS = {"status", "years"}


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


def secondhand(**fields: Any) -> dict[str, Any]:
    return {"exposed": None, "places": [], "days_per_week": None, **fields}


def wood(**fields: Any) -> dict[str, Any]:
    return {"status": None, "years": None, **fields}


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


# A previous answer to prove a rejected PUT leaves the habits as they were.
SEED: dict[str, Any] = {"vaping": "never"}
SEED_STORED = habits(vaping="never")


# --- Row 1: Alcohol actual con las preguntas del AUDIT-C (C-1) --------------------


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


# --- Row 2: Lo dejó, con la edad (C-1) --------------------------------------------


def test_c1_quit_alcohol_with_age_round_trip(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15: alcohol quit con quit_age 30 -> GET igual, sin AUDIT-C."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    expected = habits(alcohol=alcohol(status="quit", quit_age=30))

    saved = save(client, headers, {"alcohol": {"status": "quit", "quit_age": 30}})

    assert saved == expected
    assert stored_habits(client, headers) == expected


# --- Row 3: Una edad mayor que la actual (C-1, C-2) -------------------------------

AGE_ABOVE_CASES = [
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
]


@pytest.mark.parametrize(("body", "loc"), AGE_ABOVE_CASES)
def test_c1_c2_age_above_current_rejected_nothing_saved(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    body: dict[str, Any],
    loc: list[str],
) -> None:
    """Nacido 1990-03-15, hoy 36: una edad de 40 -> 422 con su loc y el texto
    exacto; los hábitos guardados no cambian."""
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


# --- Row 4: Lo que no aplica se descarta (C-1) ------------------------------------

AUDIT_C = {
    "frequency": "four_plus_weekly",
    "typical_drinks": "five_six",
    "six_or_more": "weekly",
    "mostly_weekends": True,
}

NORMALIZATION_CASES = [
    pytest.param(
        {"alcohol": {"status": "never", "quit_age": 30, **AUDIT_C}},
        habits(alcohol=alcohol(status="never")),
        id="alcohol-never-drops-audit-and-quit_age",
    ),
    pytest.param(
        {"alcohol": {"status": "quit", "quit_age": 30, **AUDIT_C}},
        habits(alcohol=alcohol(status="quit", quit_age=30)),
        id="alcohol-quit-drops-audit",
    ),
    pytest.param(
        {"alcohol": {"status": "current", "quit_age": 30, **AUDIT_C}},
        habits(alcohol=alcohol(status="current", **AUDIT_C)),
        id="alcohol-current-drops-quit_age",
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
        {"wood_smoke": {"status": "never", "years": 12}},
        habits(wood_smoke=wood(status="never")),
        id="wood-never-drops-years",
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
def test_c1_what_does_not_apply_is_dropped(
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


def test_c1_switch_current_to_never_drops_stored_audit_c(
    client: TestClient, db: Session
) -> None:
    """Alcohol current con las tres preguntas del AUDIT-C, luego never -> GET
    sin AUDIT-C, y el JSON guardado (descifrado) no conserva esas respuestas."""
    headers, user_id = consented_user(client, db)
    save(client, headers, {"alcohol": {"status": "current", **AUDIT_C}})

    saved = save(client, headers, {"alcohol": {"status": "never", **AUDIT_C}})

    expected = habits(alcohol=alcohol(status="never"))
    assert saved == expected
    assert stored_habits(client, headers) == expected
    decrypted = decrypt_str(raw_habits(user_id))
    assert decrypted is not None
    for answer in ("four_plus_weekly", "five_six", "weekly", "mostly_weekends"):
        assert answer not in decrypted, answer
    assert without_nulls(json.loads(decrypted)) == without_nulls(expected)


# --- Row 5: Tabaco que dejó, y vapeador actual (C-2) ------------------------------


def test_c2_former_tobacco_and_current_vaping_round_trip(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nacido 1990-03-15: tabaco former, 10 al día, de 18 a 30, vaping current
    -> PUT y GET iguales."""
    headers, _ = consented_user(client, db)
    born_1990_frozen(client, headers, monkeypatch)
    smoking = {
        "status": "former",
        "cigarettes_per_day": 10,
        "start_age": 18,
        "quit_age": 30,
    }
    expected = habits(tobacco=tobacco(**smoking), vaping="current")

    saved = save(client, headers, {"tobacco": smoking, "vaping": "current"})

    assert saved == expected
    assert stored_habits(client, headers) == expected


# --- Row 6: Empezó después de dejarlo (C-2) ---------------------------------------


def test_c2_start_age_after_quit_age_rejected(client: TestClient, db: Session) -> None:
    """Tabaco former, empezó a los 30 y lo dejó a los 18 -> 422 en start_age con
    el texto exacto; nada se guarda."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(
        client,
        headers,
        {
            "tobacco": {
                "status": "former",
                "cigarettes_per_day": 10,
                "start_age": 30,
                "quit_age": 18,
            }
        },
    )

    assert_single_error(r, ["body", "tobacco", "start_age"], START_AFTER_QUIT)
    assert stored_habits(client, headers) == SEED_STORED


# --- Row 7: Humo ajeno en varios lugares, y después "No me expongo" (C-3) ---------


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


# --- Row 8: Humo de leña de antes (C-4) -------------------------------------------


def test_c4_former_wood_smoke_round_trip(client: TestClient, db: Session) -> None:
    """Leña former con 12 años -> PUT y GET iguales."""
    headers, _ = consented_user(client, db)
    expected = habits(wood_smoke=wood(status="former", years=12))

    saved = save(client, headers, {"wood_smoke": {"status": "former", "years": 12}})

    assert saved == expected
    assert stored_habits(client, headers) == expected


# --- Row 9: Contesta solo una cosa ------------------------------------------------


def test_c_only_vaping_answered_rest_stays_null(
    client: TestClient, db: Session
) -> None:
    """Sin hábitos: solo vaping never -> vaping never y todo lo demás null."""
    headers, _ = consented_user(client, db)
    assert stored_habits(client, headers) == empty_habits()

    saved = save(client, headers, {"vaping": "never"})

    expected = habits(vaping="never")
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


# --- Row 10: Respuestas fuera de su escala ----------------------------------------

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
    pytest.param({"wood_smoke": {"status": "former", "years": 131}}, id="years-131"),
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
    pytest.param({"wood_smoke": {"status": "former", "years": -1}}, id="years--1"),
    pytest.param(
        {"secondhand_smoke": {"exposed": True, "places": ["home"], "days_per_week": 0}},
        id="secondhand-0-days",
    ),
    pytest.param({"vaping": "sometimes"}, id="vaping-outside-enum"),
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
    pytest.param({"vaping": "never", "drugs": "never"}, id="unknown-top-level-field"),
    pytest.param(
        {"alcohol": {"status": "never", "audit_c_score": 0}},
        id="unknown-nested-field",
    ),
]


@pytest.mark.parametrize("body", OUT_OF_SCALE_CASES)
def test_c_out_of_scale_answers_rejected_habits_unchanged(
    client: TestClient, db: Session, body: dict[str, Any]
) -> None:
    """Fuera de escala, fuera del catálogo o un campo desconocido -> 422 y los
    hábitos guardados no cambian."""
    headers, _ = consented_user(client, db)
    save(client, headers, SEED)

    r = put_habits(client, headers, body)

    assert r.status_code == 422, r.text
    assert stored_habits(client, headers) == SEED_STORED


# --- Row 11: Sin puntaje ni riesgo (C-6) ------------------------------------------


def assert_contract_keys_only(body: dict[str, Any]) -> None:
    assert set(body) == TOP_LEVEL_KEYS, body
    assert set(body["alcohol"]) == ALCOHOL_KEYS, body["alcohol"]
    assert set(body["tobacco"]) == TOBACCO_KEYS, body["tobacco"]
    assert set(body["secondhand_smoke"]) == SECONDHAND_KEYS, body["secondhand_smoke"]
    assert set(body["wood_smoke"]) == WOOD_KEYS, body["wood_smoke"]


def test_c6_no_score_or_risk_in_the_response(client: TestClient, db: Session) -> None:
    """Caso extremo (alcohol four_plus_weekly, ten_plus, daily; tabaco current
    20 al día): PUT y GET traen exactamente las llaves del contrato, y ni
    "riesgo", ni "puntaje", ni "AUDIT"."""
    headers, _ = consented_user(client, db)
    body = {
        "alcohol": {
            "status": "current",
            "frequency": "four_plus_weekly",
            "typical_drinks": "ten_plus",
            "six_or_more": "daily",
        },
        "tobacco": {"status": "current", "cigarettes_per_day": 20},
        "secondhand_smoke": {"exposed": False},
        "wood_smoke": {"status": "never"},
    }

    r_put = put_habits(client, headers, body)
    assert r_put.status_code == 200, r_put.text
    r_get = get_habits(client, headers)
    assert r_get.status_code == 200, r_get.text

    for r in (r_put, r_get):
        assert_contract_keys_only(r.json())
        text_lower = r.text.lower()
        for word in ("riesgo", "puntaje", "audit"):
            assert word not in text_lower, (word, r.text)


# --- Row 16: Hábitos solo del paciente y cifrados ---------------------------------


def test_c_habits_isolated_and_encrypted_at_rest(
    client: TestClient, db: Session
) -> None:
    """A con alcohol current y humo ajeno en home: B recibe todo null; en BD los
    hábitos de A son un token Fernet sin respuestas ni nombres de campo en claro,
    que descifra al objeto normalizado."""
    headers_a, user_a = consented_user(client, db)
    headers_b, _ = consented_user(client, db)
    saved_a = save(
        client,
        headers_a,
        {
            "alcohol": {"status": "current", "frequency": "monthly_or_less"},
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
    for plain in ("current", "home", "alcohol", "monthly_or_less"):
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
    profile = db.exec(
        select(PatientProfile).where(PatientProfile.user_id == uuid.UUID(user_id))
    ).one()
    unreadable = json.dumps({"vaping": "current", "physical_activity": "sedentary"})
    profile.habits = unreadable
    db.add(profile)
    db.commit()
    db.refresh(profile)
    assert raw_habits(user_id).startswith("gAAAA")

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
    [("GET", None), ("PUT", {"vaping": "never"})],
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
