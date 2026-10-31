"""Tests for the event sections of the medical history (perfil-eventos, grupo 1).

Interface contract (design.md, "## Interface contract"; base /api/v1/profile,
all behind a current consent; 422/409/404 carry a STRING detail in es-MX;
lists use {"data": [...], "count": N}):
- section: "past" | "surgeries" | "fractures" | "transfusions" (Story B adds
  "chronic", tested at the end of this file; "habits" is not valid yet).
- When: {kind: "age", value: int} | {kind: "stage", value: "before_primary" |
  "primary" | "secondary" | "high_school"} | {kind: "year", value: int} |
  {kind: "unknown"}. YesNoUnknown: "yes" | "no" | "unknown".
- blood_type: "A+" | "A-" | "B+" | "B-" | "AB+" | "AB-" | "O+" | "O-" | "unknown".
- GET /profile -> today's profile + blood_type: enum|null + sections_none: section[].
- PUT /profile -> today's body + blood_type? (null clears); 422 outside the enum.
- GET /profile/history -> {data: [HistoryEntry], count}, created_at ASC.
- POST /profile/history -> 201 HistoryEntry; removes section from sections_none.
  422 "Llena al menos un dato" when only `section` comes; 422 es-MX for a
  missing required field or an impossible `when`.
- PUT /profile/history/{id} -> 200; 422 if `section` changes; 404 "Registro no
  encontrado" identical for foreign and nonexistent.
- DELETE /profile/history/{id} -> 200 {message}; 404 identical.
- PUT /profile/history/sections/{section}/none {none: bool} -> 200 the profile;
  409 "No puedes marcar «ninguna» si la sección tiene registros"; 422 when the
  section is not one of this story.
- Tables: medical_history_entry(id, user_id, content = encrypted JSON of the
  entry WITH its section, created_at); patient_profile gains blood_type and
  sections_none (JSON list), both encrypted; ciphertext starts with "gAAAA".
"""

import json
import logging
import threading
import uuid
from collections.abc import Callable
from datetime import date, datetime, tzinfo
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app.api.routes import profile as profile_routes
from app.core.db import engine
from app.core.encrypted import decrypt_str
from app.models import MedicalHistoryEntry
from tests.api.routes.test_health_records import (
    diagnosis_payload,
    prescription_payload,
    record_url,
)
from tests.api.routes.test_health_records import (
    post_record as post_health_record,
)
from tests.api.routes.test_profile import (
    PROFILE_URL,
    consented_user,
    get_profile,
    put_profile,
    user_without_consent_headers,
)

HISTORY_URL = f"{PROFILE_URL}/history"
MX = ZoneInfo("America/Mexico_City")
BIRTH_DATE = "1990-03-15"


# --- helpers ----------------------------------------------------------------------


def mexico_today() -> date:
    return datetime.now(MX).date()


def age_on(birth: date, today: date) -> int:
    return (
        today.year - birth.year - ((today.month, today.day) < (birth.month, birth.day))
    )


def freeze_routes_clock(monkeypatch: pytest.MonkeyPatch, mexico_wall: datetime) -> None:
    """Freeze the routes module's clock at a Mexico City wall time; now(tz)
    still converts to the zone it is asked for."""
    instant = mexico_wall.replace(tzinfo=MX)

    class FrozenDatetime(datetime):
        @classmethod
        def now(cls, tz: tzinfo | None = None) -> datetime:  # type: ignore[override]
            return instant.astimezone(tz)

    monkeypatch.setattr(profile_routes, "datetime", FrozenDatetime)


def post_entry(
    client: TestClient, headers: dict[str, str], body: dict[str, Any]
) -> Any:
    return client.post(HISTORY_URL, headers=headers, json=body)


def list_entries(client: TestClient, headers: dict[str, str]) -> Any:
    return client.get(HISTORY_URL, headers=headers)


def entry_url(entry_id: Any) -> str:
    return f"{HISTORY_URL}/{entry_id}"


def none_url(section: str) -> str:
    return f"{HISTORY_URL}/sections/{section}/none"


def set_none(
    client: TestClient, headers: dict[str, str], section: str, none: bool
) -> Any:
    return client.put(none_url(section), headers=headers, json={"none": none})


def assert_history_empty(client: TestClient, headers: dict[str, str]) -> None:
    r = list_entries(client, headers)
    assert r.status_code == 200, r.text
    assert r.json()["count"] == 0, r.text
    assert r.json()["data"] == [], r.text


def sections_none(client: TestClient, headers: dict[str, str]) -> list[str]:
    r = get_profile(client, headers)
    assert r.status_code == 200, r.text
    value = r.json()["sections_none"]
    assert isinstance(value, list), value
    return value


def raw_rows(sql: str, params: dict[str, Any]) -> list[Any]:
    """Raw SQL on its OWN connection: a missing table/column must not leave the
    session-scoped `db` fixture in a failed transaction for other tests."""
    with engine.connect() as conn:
        return list(conn.execute(text(sql), params).mappings().all())


FRACTURE_RADIO: dict[str, Any] = {
    "section": "fractures",
    "what": "Radio",
    "side": "left",
    "when": {"kind": "age", "value": 10},
    "required_surgery": "yes",
    "implant": "Placa y tornillos",
}

SURGERY_FULL: dict[str, Any] = {
    "section": "surgeries",
    "kind": "surgery",
    "name": "Apendicectomía",
    "when": {"kind": "age", "value": 24},
    "reason": "Apendicitis",
    "place": "Hospital General de Zona",
    "physician": "Dra. Ruiz",
    "complications": "Sin complicaciones",
    "anesthesia_reaction": "yes",
    "anesthesia_reaction_detail": "Náusea fuerte",
    "implant": None,
}

TRANSFUSION_2015: dict[str, Any] = {
    "section": "transfusions",
    "when": {"kind": "year", "value": 2015},
    "reason": "Parto",
    "component": "blood",
    "reaction": "no",
}


# --- Escenario 3: Enfermedad pasada del catálogo ----------------------------------


def test_s03_past_illness_from_catalog(client: TestClient, db: Session) -> None:
    """POST past varicella, en la primaria, hospitalized no -> 201; GET la trae."""
    headers, _ = consented_user(client, db)
    body = {
        "section": "past",
        "condition": "varicella",
        "when": {"kind": "stage", "value": "primary"},
        "hospitalized": "no",
    }

    r = post_entry(client, headers, body)

    assert r.status_code == 201, r.text
    created = r.json()
    assert created["id"]
    assert created["section"] == "past"
    assert created["condition"] == "varicella"
    assert created["when"] == {"kind": "stage", "value": "primary"}
    assert created["hospitalized"] == "no"

    r_list = list_entries(client, headers)
    assert r_list.status_code == 200, r_list.text
    listed = r_list.json()
    assert listed["count"] == 1
    entry = listed["data"][0]
    assert str(entry["id"]) == str(created["id"])
    assert entry["section"] == "past"
    assert entry["condition"] == "varicella"
    assert entry["when"] == {"kind": "stage", "value": "primary"}
    assert entry["hospitalized"] == "no"


# --- Escenario 4: Enfermedad pasada fuera del catálogo ----------------------------


def test_s04_past_illness_other_with_text(client: TestClient, db: Session) -> None:
    """condition other + other_text Chikungunya -> 201 y GET la trae."""
    headers, _ = consented_user(client, db)

    r = post_entry(
        client,
        headers,
        {"section": "past", "condition": "other", "other_text": "Chikungunya"},
    )

    assert r.status_code == 201, r.text
    assert r.json()["condition"] == "other"
    assert r.json()["other_text"] == "Chikungunya"
    r_list = list_entries(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 1
    assert r_list.json()["data"][0]["other_text"] == "Chikungunya"


def test_s04_past_illness_other_without_text_rejected(
    client: TestClient, db: Session
) -> None:
    """condition other sin other_text -> 422 es-MX (string) y no se crea."""
    headers, _ = consented_user(client, db)

    r = post_entry(client, headers, {"section": "past", "condition": "other"})

    assert r.status_code == 422, r.text
    assert isinstance(r.json()["detail"], str), r.text
    assert_history_empty(client, headers)


# --- validaciones-hoy-y-texto-invisible: texto sin nada visible -------------------

INVISIBLE_TEXTS = ["​", "ㅤ⠀", " ​ "]
INVISIBLE_IDS = ["zero-width-space", "fillers-hangul-braille", "spaces-around-zwsp"]
PAST_CONDITION_REQUIRED = "Elige la condición o escribe cuál fue"


def entries_count(client: TestClient, headers: dict[str, str]) -> int:
    r = list_entries(client, headers)
    assert r.status_code == 200, r.text
    count: int = r.json()["count"]
    return count


@pytest.mark.parametrize("other_text", INVISIBLE_TEXTS, ids=INVISIBLE_IDS)
def test_past_other_invisible_text_is_required(
    client: TestClient, db: Session, other_text: str
) -> None:
    """«¿Cuál fue?» con un texto invisible: POST past/other con other_text sin
    nada visible -> 422 "Elige la condición o escribe cuál fue"; no se crea."""
    headers, _ = consented_user(client, db)
    before = entries_count(client, headers)

    r = post_entry(
        client,
        headers,
        {"section": "past", "condition": "other", "other_text": other_text},
    )

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == PAST_CONDITION_REQUIRED, r.text
    assert entries_count(client, headers) == before


def test_past_other_visible_text_with_zero_width_is_saved(
    client: TestClient, db: Session
) -> None:
    """Un texto visible con un invisible dentro sí cuenta: POST past/other con
    other_text "Zika" + U+200B -> 201."""
    headers, _ = consented_user(client, db)

    r = post_entry(
        client,
        headers,
        {"section": "past", "condition": "other", "other_text": "Zika​"},
    )

    assert r.status_code == 201, r.text
    assert entries_count(client, headers) == 1


# --- Escenario 5: Cirugía con todos sus datos -------------------------------------


def test_s05_surgery_with_all_fields_round_trip(
    client: TestClient, db: Session
) -> None:
    """Los 10 campos de surgeries vuelven tal cual en el POST y en el GET."""
    headers, _ = consented_user(client, db)

    r = post_entry(client, headers, SURGERY_FULL)

    assert r.status_code == 201, r.text
    created = r.json()
    r_list = list_entries(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 1
    listed = r_list.json()["data"][0]
    for entry in (created, listed):
        assert entry["section"] == "surgeries"
        for field, value in SURGERY_FULL.items():
            if field == "section":
                continue
            assert entry.get(field) == value, (field, entry)


# --- Escenario 8: Falta el dato requerido -----------------------------------------


def test_s08_surgery_without_name_rejected(client: TestClient, db: Session) -> None:
    """surgeries sin name -> 422 con detail exacto; GET sigue vacío."""
    headers, _ = consented_user(client, db)

    r = post_entry(
        client,
        headers,
        {"section": "surgeries", "kind": "surgery", "reason": "Apendicitis"},
    )

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == "Escribe qué cirugía u hospitalización fue"
    assert_history_empty(client, headers)


def test_s08_past_without_condition_rejected(client: TestClient, db: Session) -> None:
    """past sin condition -> 422 con detail exacto; GET sigue vacío."""
    headers, _ = consented_user(client, db)

    r = post_entry(client, headers, {"section": "past", "hospitalized": "no"})

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == "Elige la condición o escribe cuál fue"
    assert_history_empty(client, headers)


def test_s08_fracture_without_what_rejected(client: TestClient, db: Session) -> None:
    """fractures sin what -> 422 con detail exacto; GET sigue vacío."""
    headers, _ = consented_user(client, db)

    r = post_entry(client, headers, {"section": "fractures", "side": "left"})

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == "Escribe qué hueso o lesión fue"
    assert_history_empty(client, headers)


# --- Escenario 9: Registro vacío no se guarda -------------------------------------


def test_s09_empty_transfusion_rejected(client: TestClient, db: Session) -> None:
    """POST {section: transfusions} -> 422 "Llena al menos un dato"; nada persiste."""
    headers, user_id = consented_user(client, db)

    r = post_entry(client, headers, {"section": "transfusions"})

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == "Llena al menos un dato"
    assert_history_empty(client, headers)
    rows = raw_rows(
        "SELECT COUNT(*) AS n FROM medical_history_entry "
        "WHERE user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )
    assert rows[0]["n"] == 0


# --- Escenario 10: Editar y eliminar ----------------------------------------------


def test_s10_edit_fracture_side_then_delete(client: TestClient, db: Session) -> None:
    """PUT side right -> 200 y GET lo refleja; PUT con otra section -> 422;
    DELETE -> 200 con message; GET sin el registro y fila ausente en BD."""
    headers, _ = consented_user(client, db)
    r_create = post_entry(client, headers, FRACTURE_RADIO)
    assert r_create.status_code == 201, r_create.text
    entry_id = r_create.json()["id"]

    edited = {**FRACTURE_RADIO, "side": "right"}
    r_put = client.put(entry_url(entry_id), headers=headers, json=edited)
    assert r_put.status_code == 200, r_put.text
    assert r_put.json()["side"] == "right"
    assert r_put.json()["what"] == "Radio"

    r_list = list_entries(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 1
    assert r_list.json()["data"][0]["side"] == "right"

    r_other_section = client.put(
        entry_url(entry_id),
        headers=headers,
        json={"section": "surgeries", "name": "Apendicectomía"},
    )
    assert r_other_section.status_code == 422, r_other_section.text
    assert isinstance(r_other_section.json()["detail"], str), r_other_section.text
    r_after_bad_put = list_entries(client, headers)
    assert r_after_bad_put.json()["data"][0]["section"] == "fractures"

    r_delete = client.delete(entry_url(entry_id), headers=headers)
    assert r_delete.status_code == 200, r_delete.text
    message = r_delete.json()["message"]
    assert isinstance(message, str) and message, r_delete.text

    assert_history_empty(client, headers)
    rows = raw_rows(
        "SELECT COUNT(*) AS n FROM medical_history_entry WHERE id = CAST(:id AS uuid)",
        {"id": str(entry_id)},
    )
    assert rows[0]["n"] == 0


# --- Escenario 11: Edad con fecha de nacimiento -----------------------------------


def test_s11_age_when_stored_as_answered(client: TestClient, db: Session) -> None:
    """birth_date 1990-03-15; surgery when age 7 -> se devuelve kind age, value 7."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text

    r = post_entry(
        client,
        headers,
        {
            "section": "surgeries",
            "name": "Amigdalectomía",
            "when": {"kind": "age", "value": 7},
        },
    )

    assert r.status_code == 201, r.text
    assert r.json()["when"]["kind"] == "age"
    assert r.json()["when"]["value"] == 7
    r_list = list_entries(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["data"][0]["when"]["kind"] == "age"
    assert r_list.json()["data"][0]["when"]["value"] == 7


# --- Escenario 15: Edad o año imposibles ------------------------------------------


def _surgery_when(when: dict[str, Any]) -> dict[str, Any]:
    return {"section": "surgeries", "name": "Apendicectomía", "when": when}


def test_s15_impossible_when_with_birth_date(client: TestClient, db: Session) -> None:
    """Con birth_date 1990-03-15: edad > actual, año < nacimiento y año futuro
    (relativo a México) -> 422 con su mensaje exacto; ninguno crea registro."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text
    today = mexico_today()
    # 40 on 2026-10-20 (scenario data); stays beyond the current age later on.
    too_old = age_on(date(1990, 3, 15), today) + 4

    cases = [
        (
            {"kind": "age", "value": too_old},
            "La edad no puede ser mayor que tu edad actual",
        ),
        (
            {"kind": "year", "value": 1985},
            "El año no puede ser anterior a tu nacimiento",
        ),
        ({"kind": "year", "value": today.year + 1}, "El año no puede ser futuro"),
    ]
    for when, expected in cases:
        r = post_entry(client, headers, _surgery_when(when))
        assert r.status_code == 422, (when, r.text)
        assert r.json()["detail"] == expected, (when, r.text)

    assert_history_empty(client, headers)


def test_s15_impossible_age_without_birth_date(client: TestClient, db: Session) -> None:
    """Sin birth_date: edad 131 -> 422 "La edad debe estar entre 0 y 130 años"."""
    headers, _ = consented_user(client, db)

    r = post_entry(client, headers, _surgery_when({"kind": "age", "value": 131}))

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == "La edad debe estar entre 0 y 130 años"
    assert_history_empty(client, headers)


# Frozen Mexico City wall time for the edge cases (the tests never expire).
EDGE_NOW = datetime(2026, 10, 20, 12, 0)
EDGE_AGE = age_on(date(1990, 3, 15), EDGE_NOW.date())


@pytest.mark.parametrize(
    "when",
    [
        pytest.param({"kind": "age", "value": EDGE_AGE}, id="age-equals-current"),
        pytest.param({"kind": "year", "value": 1990}, id="year-equals-birth"),
        pytest.param(
            {"kind": "year", "value": EDGE_NOW.year}, id="year-equals-current"
        ),
    ],
)
def test_s15_when_edges_accepted(
    client: TestClient,
    db: Session,
    monkeypatch: pytest.MonkeyPatch,
    when: dict[str, Any],
) -> None:
    """Con birth_date 1990-03-15, los bordes son válidos: edad = edad actual,
    año = año de nacimiento y año = año actual en México -> 201 (review C9)."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text
    freeze_routes_clock(monkeypatch, EDGE_NOW)

    r = post_entry(client, headers, _surgery_when(when))

    assert r.status_code == 201, (when, r.text)
    assert r.json()["when"] == when


def test_s15_future_year_uses_mexico_today(
    client: TestClient, db: Session, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Reloj a 2026-12-31 20:00 en México (ya 2027-01-01 en UTC): el año 2027
    sigue siendo futuro -> 422 "El año no puede ser futuro" (review T2)."""
    headers, _ = consented_user(client, db)
    freeze_routes_clock(monkeypatch, datetime(2026, 12, 31, 20, 0))

    r = post_entry(client, headers, _surgery_when({"kind": "year", "value": 2027}))

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == "El año no puede ser futuro"
    assert_history_empty(client, headers)


# --- Escenario 16: Marcar "ninguna" -----------------------------------------------


def test_s16_mark_section_none(client: TestClient, db: Session) -> None:
    """PUT none true en surgeries sin registros -> 200; GET /profile la trae."""
    headers, _ = consented_user(client, db)

    r = set_none(client, headers, "surgeries", True)

    assert r.status_code == 200, r.text
    assert "surgeries" in r.json()["sections_none"]
    assert "surgeries" in sections_none(client, headers)


# --- Escenario 17: No se marca con registros --------------------------------------


def test_s17_cannot_mark_none_with_entries(client: TestClient, db: Session) -> None:
    """Con 1 fractura: PUT none true -> 409 exacto; sections_none sin cambio."""
    headers, _ = consented_user(client, db)
    r_create = post_entry(client, headers, FRACTURE_RADIO)
    assert r_create.status_code == 201, r_create.text
    before = sections_none(client, headers)

    r = set_none(client, headers, "fractures", True)

    assert r.status_code == 409, r.text
    assert r.json()["detail"] == (
        "No puedes marcar «ninguna» si la sección tiene registros"
    )
    after = sections_none(client, headers)
    assert after == before
    assert "fractures" not in after
    r_list = list_entries(client, headers)
    assert r_list.json()["count"] == 1


# --- Escenario 18: Agregar quita la marca -----------------------------------------


def test_s18_adding_entry_clears_none_mark(client: TestClient, db: Session) -> None:
    """transfusions marcada none -> POST una transfusión -> ya no está en sections_none."""
    headers, _ = consented_user(client, db)
    r_mark = set_none(client, headers, "transfusions", True)
    assert r_mark.status_code == 200, r_mark.text
    assert "transfusions" in sections_none(client, headers)

    r = post_entry(client, headers, TRANSFUSION_2015)

    assert r.status_code == 201, r.text
    assert "transfusions" not in sections_none(client, headers)
    r_list = list_entries(client, headers)
    assert r_list.json()["count"] == 1


# --- Escenario 19: Deshacer -------------------------------------------------------


def test_s19_undo_none_mark(client: TestClient, db: Session) -> None:
    """none true y luego none false -> la sección sale de sections_none."""
    headers, _ = consented_user(client, db)
    r_mark = set_none(client, headers, "surgeries", True)
    assert r_mark.status_code == 200, r_mark.text

    r_undo = set_none(client, headers, "surgeries", False)

    assert r_undo.status_code == 200, r_undo.text
    assert "surgeries" not in r_undo.json()["sections_none"]
    assert "surgeries" not in sections_none(client, headers)


def test_s19_none_on_section_outside_story_rejected(
    client: TestClient, db: Session
) -> None:
    """Sección aún no soportada (habits) -> 422; sections_none no la trae.
    (chronic ya es válida desde perfil-cronicas.)"""
    headers, _ = consented_user(client, db)

    r = set_none(client, headers, "habits", True)

    assert r.status_code == 422, r.text
    assert "habits" not in sections_none(client, headers)


# --- Escenario 20: Grupo sanguíneo ------------------------------------------------


def test_s20_blood_type_set_change_and_clear(client: TestClient, db: Session) -> None:
    """PUT blood_type O+ -> GET O+; unknown -> GET unknown; null -> GET null."""
    headers, _ = consented_user(client, db)

    for value in ("O+", "unknown", None):
        r_put = put_profile(client, headers, {"blood_type": value})
        assert r_put.status_code == 200, (value, r_put.text)
        assert r_put.json()["blood_type"] == value
        r_get = get_profile(client, headers)
        assert r_get.status_code == 200, r_get.text
        assert r_get.json()["blood_type"] == value


# --- Escenario 21: Grupo sanguíneo fuera del catálogo -----------------------------


def test_s21_blood_type_outside_catalog_rejected(
    client: TestClient, db: Session
) -> None:
    """PUT blood_type C+ -> 422 y GET conserva el valor previo (O+)."""
    headers, _ = consented_user(client, db)
    r_seed = put_profile(client, headers, {"blood_type": "O+"})
    assert r_seed.status_code == 200, r_seed.text

    r = put_profile(client, headers, {"blood_type": "C+"})

    assert r.status_code == 422, r.text
    r_get = get_profile(client, headers)
    assert r_get.status_code == 200, r_get.text
    assert r_get.json()["blood_type"] == "O+"


# --- Escenario 22: Registro ajeno indistinguible de inexistente -------------------


def test_s22_foreign_entry_indistinguishable_from_missing(
    client: TestClient, db: Session
) -> None:
    """A contra la cirugía de B y contra un uuid inexistente: 404 con el mismo
    cuerpo {"detail": "Registro no encontrado"}; la cirugía de B no cambia, el
    GET /history de A sigue vacío y A puede marcar surgeries como ninguna."""
    headers_a, _ = consented_user(client, db)
    headers_b, _ = consented_user(client, db)
    r_b = post_entry(client, headers_b, SURGERY_FULL)
    assert r_b.status_code == 201, r_b.text
    foreign_id = r_b.json()["id"]
    missing_id = str(uuid.uuid4())

    put_body = {**SURGERY_FULL, "name": "intento de edición ajena"}
    for method, kwargs in (("PUT", {"json": put_body}), ("DELETE", {})):
        r_foreign = client.request(
            method, entry_url(foreign_id), headers=headers_a, **kwargs
        )
        r_missing = client.request(
            method, entry_url(missing_id), headers=headers_a, **kwargs
        )
        assert r_foreign.status_code == 404, (method, r_foreign.text)
        assert r_missing.status_code == 404, (method, r_missing.text)
        assert r_foreign.json() == {"detail": "Registro no encontrado"}, (
            method,
            r_foreign.text,
        )
        assert r_foreign.json() == r_missing.json(), method
        assert "Apendicectomía" not in r_foreign.text, method

    # With B's surgery stored, A's list and A's "ninguna" only see A (review S5).
    assert_history_empty(client, headers_a)
    r_none_a = set_none(client, headers_a, "surgeries", True)
    assert r_none_a.status_code == 200, r_none_a.text
    assert "surgeries" in r_none_a.json()["sections_none"]

    r_list_b = list_entries(client, headers_b)
    assert r_list_b.status_code == 200, r_list_b.text
    assert r_list_b.json()["count"] == 1
    entry = r_list_b.json()["data"][0]
    assert str(entry["id"]) == str(foreign_id)
    assert entry["name"] == "Apendicectomía"
    assert entry["anesthesia_reaction_detail"] == "Náusea fuerte"


# --- Escenario 23: Cifrado en reposo ----------------------------------------------


def test_s23_history_none_mark_and_blood_type_encrypted_at_rest(
    client: TestClient, db: Session
) -> None:
    """Cirugía Apendicectomía + fractures none + blood_type O+: en BD ningún
    texto en claro; tokens Fernet que descifran al valor esperado."""
    headers, user_id = consented_user(client, db)
    r_entry = post_entry(client, headers, SURGERY_FULL)
    assert r_entry.status_code == 201, r_entry.text
    r_none = set_none(client, headers, "fractures", True)
    assert r_none.status_code == 200, r_none.text
    r_blood = put_profile(client, headers, {"blood_type": "O+"})
    assert r_blood.status_code == 200, r_blood.text

    plaintexts = ("Apendicectomía", "surgeries", "fractures", "O+")

    entries = raw_rows(
        "SELECT content FROM medical_history_entry WHERE user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )
    assert len(entries) == 1
    content = str(entries[0]["content"])
    assert content.startswith("gAAAA"), content
    for plain in plaintexts:
        assert plain not in content, plain
    decrypted_content = decrypt_str(content)
    assert decrypted_content is not None
    stored = json.loads(decrypted_content)
    assert stored["section"] == "surgeries"
    assert stored["name"] == "Apendicectomía"

    profiles = raw_rows(
        "SELECT blood_type, sections_none FROM patient_profile "
        "WHERE user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )
    assert len(profiles) == 1
    blood = str(profiles[0]["blood_type"])
    marks = str(profiles[0]["sections_none"])
    for column, raw in (("blood_type", blood), ("sections_none", marks)):
        assert raw.startswith("gAAAA"), (column, raw)
        for plain in plaintexts:
            assert plain not in raw, (column, plain)
    assert decrypt_str(blood) == "O+"
    decrypted_marks = decrypt_str(marks)
    assert decrypted_marks is not None
    assert json.loads(decrypted_marks) == ["fractures"]


# --- Review S4: registro ilegible -------------------------------------------------


def test_unreadable_entry_left_out_and_logged_by_id(
    client: TestClient, db: Session, caplog: pytest.LogCaptureFixture
) -> None:
    """Una fila cifrada cuyo contenido ya no valida (condition "zika"): GET
    /history -> 200 sin ella, "ninguna" de otra sección -> 200, y el log trae
    solo su id, nunca el contenido."""
    headers, user_id = consented_user(client, db)
    r_ok = post_entry(client, headers, FRACTURE_RADIO)
    assert r_ok.status_code == 201, r_ok.text
    bad = MedicalHistoryEntry(
        user_id=uuid.UUID(user_id),
        content=json.dumps({"section": "past", "condition": "zika"}),
    )
    db.add(bad)
    db.commit()
    db.refresh(bad)

    with caplog.at_level(logging.WARNING, logger=profile_routes.__name__):
        r_list = list_entries(client, headers)
        r_none = set_none(client, headers, "surgeries", True)

    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 1, r_list.text
    assert str(r_list.json()["data"][0]["id"]) == str(r_ok.json()["id"])
    assert r_none.status_code == 200, r_none.text
    assert "surgeries" in r_none.json()["sections_none"]
    assert str(bad.id) in caplog.text
    assert "zika" not in caplog.text


# --- Humo: sin consentimiento, el mismo rechazo que el resto del perfil -----------

_ANY_ID = "00000000-0000-0000-0000-000000000000"
_TRANSFUSION = {"section": "transfusions", "reason": "Parto"}
CONSENT_GATED_HISTORY_ROUTES: list[tuple[str, str, dict[str, Any] | None]] = [
    ("GET", HISTORY_URL, None),
    ("POST", HISTORY_URL, _TRANSFUSION),
    ("PUT", entry_url(_ANY_ID), _TRANSFUSION),
    ("DELETE", entry_url(_ANY_ID), None),
    ("PUT", none_url("transfusions"), {"none": True}),
]


def test_consent_history_routes_require_consent(
    client: TestClient, db: Session
) -> None:
    """Sin consentimiento, las rutas del historial responden 403 CONSENT_REQUIRED."""
    headers = user_without_consent_headers(client, db)

    for method, url, json_body in CONSENT_GATED_HISTORY_ROUTES:
        r = client.request(method, url, headers=headers, json=json_body)
        assert r.status_code == 403, (method, url, r.text)
        assert r.json()["detail"] == "CONSENT_REQUIRED", (method, url)


# ==================================================================================
# Story B (perfil-cronicas, grupo 1): sección "chronic".
#
# Contract: section "chronic" (first in canonical order); content = condition
# (required, catalog or "other" + other_text), sensitive (server default true
# for depression/anxiety/bipolar_disorder/substance_use, false otherwise,
# always returned), status active|resolved, since/until: When (until dropped
# unless status is resolved), treatment, note, diagnosis_id (a diagnosis of
# the same patient's records). Same operations and rules as Story A.
# ==================================================================================

CHRONIC_CONDITIONS = (
    "type2_diabetes",
    "hypertension",
    "asthma",
    "hypothyroidism",
    "high_cholesterol",
    "copd",
    "arthritis",
    "epilepsy",
    "depression",
    "anxiety",
    "bipolar_disorder",
    "substance_use",
)
SENSITIVE_BY_DEFAULT = {"depression", "anxiety", "bipolar_disorder", "substance_use"}

CONDITION_REQUIRED = "Elige la condición o escribe cuál es"
UNTIL_BEFORE_SINCE = "No puede ser antes de «desde cuándo»"
DIAGNOSIS_NOT_YOURS = "Ese diagnóstico no está en tu expediente"

HYPOTHYROIDISM_ACTIVE: dict[str, Any] = {
    "section": "chronic",
    "condition": "hypothyroidism",
    "status": "active",
    "since": {"kind": "age", "value": 31},
    "treatment": "Levotiroxina 50 mcg en ayunas",
}


def chronic(**fields: Any) -> dict[str, Any]:
    return {"section": "chronic", **fields}


def only_entry(client: TestClient, headers: dict[str, str]) -> dict[str, Any]:
    r = list_entries(client, headers)
    assert r.status_code == 200, r.text
    assert r.json()["count"] == 1, r.text
    entry: dict[str, Any] = r.json()["data"][0]
    return entry


def create_diagnosis(
    client: TestClient, headers: dict[str, str], **overrides: Any
) -> str:
    r = post_health_record(client, headers, diagnosis_payload(**overrides))
    assert r.status_code == 201, r.text
    return str(r.json()["id"])


def create_prescription(client: TestClient, headers: dict[str, str]) -> str:
    r = post_health_record(client, headers, prescription_payload())
    assert r.status_code == 201, r.text
    return str(r.json()["id"])


# --- Escenario 1 (B-1, B-3): crónica del catálogo, activa, con tratamiento --------


def test_b1_chronic_hypothyroidism_active_round_trip(
    client: TestClient, db: Session
) -> None:
    """Nacida 1990-03-15, sin crónicas: POST hipotiroidismo activo desde los 31
    con Levotiroxina -> 201; GET la trae con esos datos y sensitive false."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text
    assert_history_empty(client, headers)

    r = post_entry(client, headers, HYPOTHYROIDISM_ACTIVE)

    assert r.status_code == 201, r.text
    created = r.json()
    assert created["id"]
    listed = only_entry(client, headers)
    assert str(listed["id"]) == str(created["id"])
    for entry in (created, listed):
        assert entry["section"] == "chronic"
        assert entry["condition"] == "hypothyroidism"
        assert entry["status"] == "active"
        assert entry["since"] == {"kind": "age", "value": 31}
        assert entry["treatment"] == "Levotiroxina 50 mcg en ayunas"
        assert entry["sensitive"] is False
        assert entry.get("until") is None


# --- Escenario 2 (B-1b): "Sensible" por omisión según la condición ----------------


@pytest.mark.parametrize(
    "condition",
    [*CHRONIC_CONDITIONS, "other"],
)
def test_b1b_sensitive_default_by_condition(
    client: TestClient, db: Session, condition: str
) -> None:
    """Sin `sensitive`: true para depression/anxiety/bipolar_disorder/
    substance_use, false para el resto; siempre explícito en POST y GET."""
    headers, _ = consented_user(client, db)
    body = chronic(condition=condition, status="active")
    if condition == "other":
        body["other_text"] = "Migraña crónica"
    expected = condition in SENSITIVE_BY_DEFAULT

    r = post_entry(client, headers, body)

    assert r.status_code == 201, (condition, r.text)
    assert r.json()["sensitive"] is expected, (condition, r.text)
    assert only_entry(client, headers)["sensitive"] is expected, condition


def test_b1b_anxiety_sensitive_by_default(client: TestClient, db: Session) -> None:
    """POST anxiety sin `sensitive` -> sensitive true; hypertension -> false."""
    headers, _ = consented_user(client, db)

    r_anx = post_entry(client, headers, chronic(condition="anxiety"))
    r_hyp = post_entry(client, headers, chronic(condition="hypertension"))

    assert r_anx.status_code == 201, r_anx.text
    assert r_hyp.status_code == 201, r_hyp.text
    assert r_anx.json()["sensitive"] is True
    assert r_hyp.json()["sensitive"] is False
    r_list = list_entries(client, headers)
    by_id = {str(e["id"]): e for e in r_list.json()["data"]}
    assert by_id[str(r_anx.json()["id"])]["sensitive"] is True
    assert by_id[str(r_hyp.json()["id"])]["sensitive"] is False


# --- Escenario 3 (B-1b): el valor explícito de "Sensible" se respeta --------------


def test_b1b_explicit_sensitive_respected(client: TestClient, db: Session) -> None:
    """other "TOC" con sensitive true -> true; anxiety con false explícito -> false;
    hypertension (false) PUT sensitive true -> true, PUT false -> false."""
    headers, _ = consented_user(client, db)

    r_toc = post_entry(
        client, headers, chronic(condition="other", other_text="TOC", sensitive=True)
    )
    assert r_toc.status_code == 201, r_toc.text
    assert r_toc.json()["sensitive"] is True

    r_anx = post_entry(client, headers, chronic(condition="anxiety", sensitive=False))
    assert r_anx.status_code == 201, r_anx.text
    assert r_anx.json()["sensitive"] is False

    hyp = chronic(condition="hypertension", status="active")
    r_hyp = post_entry(client, headers, hyp)
    assert r_hyp.status_code == 201, r_hyp.text
    assert r_hyp.json()["sensitive"] is False
    hyp_id = r_hyp.json()["id"]

    r_on = client.put(
        entry_url(hyp_id), headers=headers, json={**hyp, "sensitive": True}
    )
    assert r_on.status_code == 200, r_on.text
    assert r_on.json()["sensitive"] is True
    r_list = list_entries(client, headers)
    by_id = {str(e["id"]): e for e in r_list.json()["data"]}
    assert by_id[str(hyp_id)]["sensitive"] is True

    r_off = client.put(
        entry_url(hyp_id), headers=headers, json={**hyp, "sensitive": False}
    )
    assert r_off.status_code == 200, r_off.text
    assert r_off.json()["sensitive"] is False

    r_list = list_entries(client, headers)
    by_id = {str(e["id"]): e for e in r_list.json()["data"]}
    assert by_id[str(r_toc.json()["id"])]["sensitive"] is True
    assert by_id[str(r_toc.json()["id"])]["other_text"] == "TOC"
    assert by_id[str(r_anx.json()["id"])]["sensitive"] is False
    assert by_id[str(hyp_id)]["sensitive"] is False


# --- Escenario 5 (B-2): "hasta" antes de "desde" ----------------------------------


def test_b2_until_age_before_since_age_rejected(
    client: TestClient, db: Session
) -> None:
    """since edad 20, until edad 12, resolved -> 422 exacto; nada se guarda."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text

    r = post_entry(
        client,
        headers,
        chronic(
            condition="asthma",
            status="resolved",
            since={"kind": "age", "value": 20},
            until={"kind": "age", "value": 12},
        ),
    )

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == UNTIL_BEFORE_SINCE
    assert_history_empty(client, headers)


# (since, until, with_birth_date, expected_status). Stage ranges (Story A):
# before_primary 0-5, primary 6-11, secondary 12-14, high_school 15-17.
UNTIL_SINCE_CASES = [
    pytest.param(
        {"kind": "stage", "value": "high_school"},
        {"kind": "age", "value": 12},
        False,
        422,
        id="stage-after-until-age-rejected",
    ),
    pytest.param(
        {"kind": "stage", "value": "secondary"},
        {"kind": "age", "value": 13},
        False,
        201,
        id="stage-overlapping-until-age-accepted",
    ),
    pytest.param(
        {"kind": "age", "value": 20},
        {"kind": "stage", "value": "high_school"},
        False,
        422,
        id="until-stage-before-since-age-rejected",
    ),
    pytest.param(
        {"kind": "age", "value": 13},
        {"kind": "stage", "value": "secondary"},
        False,
        201,
        id="until-stage-overlapping-since-age-accepted",
    ),
    pytest.param(
        {"kind": "year", "value": 2010},
        {"kind": "age", "value": 12},
        True,
        422,
        id="year-with-birth-date-rejected",
    ),
    pytest.param(
        {"kind": "age", "value": 20},
        {"kind": "year", "value": 2002},
        True,
        422,
        id="until-year-with-birth-date-rejected",
    ),
    pytest.param(
        {"kind": "year", "value": 2010},
        {"kind": "age", "value": 12},
        False,
        201,
        id="year-without-birth-date-not-compared",
    ),
    pytest.param(
        {"kind": "unknown"},
        {"kind": "age", "value": 12},
        True,
        201,
        id="since-unknown-never-rejected",
    ),
    pytest.param(
        {"kind": "age", "value": 20},
        {"kind": "unknown"},
        True,
        201,
        id="until-unknown-never-rejected",
    ),
    pytest.param(
        {"kind": "age", "value": 12},
        {"kind": "age", "value": 12},
        True,
        201,
        id="same-age-accepted",
    ),
    pytest.param(
        {"kind": "age", "value": 12},
        {"kind": "age", "value": 20},
        True,
        201,
        id="until-after-since-accepted",
    ),
]


@pytest.mark.parametrize(
    ("since", "until", "with_birth_date", "expected_status"), UNTIL_SINCE_CASES
)
def test_b2_until_vs_since_by_age_range(
    client: TestClient,
    db: Session,
    since: dict[str, Any],
    until: dict[str, Any],
    with_birth_date: bool,
    expected_status: int,
) -> None:
    """Comparación por rango de edad; se rechaza solo si max(until) < min(since)."""
    headers, _ = consented_user(client, db)
    if with_birth_date:
        r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
        assert r_profile.status_code == 200, r_profile.text

    r = post_entry(
        client,
        headers,
        chronic(condition="asthma", status="resolved", since=since, until=until),
    )

    assert r.status_code == expected_status, r.text
    if expected_status == 422:
        assert r.json()["detail"] == UNTIL_BEFORE_SINCE
        assert_history_empty(client, headers)
    else:
        entry = only_entry(client, headers)
        assert entry["since"] == since
        assert entry["until"] == until
        assert entry["status"] == "resolved"


def test_b2_year_is_an_age_range_with_birth_date(
    client: TestClient, db: Session
) -> None:
    """Review R11: nacido 1990-12-01, en 2022 tuvo 31 (enero) y 32 (diciembre);
    desde {year: 2022} hasta {age: 31} es posible -> 201."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": "1990-12-01"})
    assert r_profile.status_code == 200, r_profile.text
    since = {"kind": "year", "value": 2022}
    until = {"kind": "age", "value": 31}

    r = post_entry(
        client,
        headers,
        chronic(condition="asthma", status="resolved", since=since, until=until),
    )

    assert r.status_code == 201, r.text
    entry = only_entry(client, headers)
    assert entry["since"] == since
    assert entry["until"] == until


@pytest.mark.parametrize(
    ("since_year", "until_year", "expected_status"),
    [
        pytest.param(2015, 2005, 422, id="until-year-before-since-year-rejected"),
        pytest.param(2005, 2015, 201, id="until-year-after-since-year-accepted"),
    ],
)
def test_b2_year_vs_year_without_birth_date(
    client: TestClient,
    db: Session,
    since_year: int,
    until_year: int,
    expected_status: int,
) -> None:
    """Review R13: año contra año se compara directo, sin fecha de nacimiento."""
    headers, _ = consented_user(client, db)
    since = {"kind": "year", "value": since_year}
    until = {"kind": "year", "value": until_year}

    r = post_entry(
        client,
        headers,
        chronic(condition="asthma", status="resolved", since=since, until=until),
    )

    assert r.status_code == expected_status, r.text
    if expected_status == 422:
        assert r.json()["detail"] == UNTIL_BEFORE_SINCE
        assert_history_empty(client, headers)
    else:
        entry = only_entry(client, headers)
        assert entry["since"] == since
        assert entry["until"] == until


def test_b2_until_year_is_an_age_range_with_birth_date(
    client: TestClient, db: Session
) -> None:
    """Review R11, del lado de «hasta»: nacido 1990-12-01, en 2022 tuvo 31 y 32;
    desde {age: 32} hasta {year: 2022} es posible (el tope del rango) -> 201."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": "1990-12-01"})
    assert r_profile.status_code == 200, r_profile.text
    since = {"kind": "age", "value": 32}
    until = {"kind": "year", "value": 2022}

    r = post_entry(
        client,
        headers,
        chronic(condition="asthma", status="resolved", since=since, until=until),
    )

    assert r.status_code == 201, r.text
    entry = only_entry(client, headers)
    assert entry["since"] == since
    assert entry["until"] == until


def test_b2_year_vs_year_with_birth_date_rejected(
    client: TestClient, db: Session
) -> None:
    """Review R13 con fecha de nacimiento: nacido 1990-03-15, desde {year: 2015}
    hasta {year: 2014} -> 422 (los rangos de edad se traslapan, los años no)."""
    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text

    r = post_entry(
        client,
        headers,
        chronic(
            condition="asthma",
            status="resolved",
            since={"kind": "year", "value": 2015},
            until={"kind": "year", "value": 2014},
        ),
    )

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == UNTIL_BEFORE_SINCE
    assert_history_empty(client, headers)


def test_b2_since_until_use_story_a_when_validation(
    client: TestClient, db: Session
) -> None:
    """since/until pasan por la validación de "cuándo" de la Story A, con sus
    mensajes exactos; ninguno crea registro."""
    headers_no_birth, _ = consented_user(client, db)
    today = mexico_today()
    cases_no_birth = [
        (
            {"since": {"kind": "age", "value": 131}},
            "La edad debe estar entre 0 y 130 años",
        ),
        (
            {
                "since": {"kind": "age", "value": 20},
                "until": {"kind": "age", "value": 131},
            },
            "La edad debe estar entre 0 y 130 años",
        ),
        (
            {
                "since": {"kind": "age", "value": 20},
                "until": {"kind": "year", "value": today.year + 1},
            },
            "El año no puede ser futuro",
        ),
    ]
    for fields, expected in cases_no_birth:
        r = post_entry(
            client,
            headers_no_birth,
            chronic(condition="asthma", status="resolved", **fields),
        )
        assert r.status_code == 422, (fields, r.text)
        assert r.json()["detail"] == expected, (fields, r.text)
    assert_history_empty(client, headers_no_birth)

    headers, _ = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text
    too_old = age_on(date(1990, 3, 15), today) + 4
    cases_birth = [
        (
            {"since": {"kind": "age", "value": too_old}},
            "La edad no puede ser mayor que tu edad actual",
        ),
        (
            {"since": {"kind": "year", "value": 1985}},
            "El año no puede ser anterior a tu nacimiento",
        ),
        (
            {
                "since": {"kind": "age", "value": 20},
                "until": {"kind": "age", "value": too_old},
            },
            "La edad no puede ser mayor que tu edad actual",
        ),
    ]
    for fields, expected in cases_birth:
        r = post_entry(
            client, headers, chronic(condition="asthma", status="resolved", **fields)
        )
        assert r.status_code == 422, (fields, r.text)
        assert r.json()["detail"] == expected, (fields, r.text)
    assert_history_empty(client, headers)


# --- Escenario 6 (B-2): "hasta" solo con "Ya no la tengo" -------------------------


def test_b2_until_dropped_when_status_active(client: TestClient, db: Session) -> None:
    """Resuelta con until edad 16; PUT status active (aún enviando until) ->
    GET status active y sin until. POST active con until -> until descartado."""
    headers, _ = consented_user(client, db)
    resolved = chronic(
        condition="asthma",
        status="resolved",
        since={"kind": "age", "value": 8},
        until={"kind": "age", "value": 16},
    )
    r_create = post_entry(client, headers, resolved)
    assert r_create.status_code == 201, r_create.text
    assert r_create.json()["until"] == {"kind": "age", "value": 16}
    entry_id = r_create.json()["id"]

    r_put = client.put(
        entry_url(entry_id), headers=headers, json={**resolved, "status": "active"}
    )

    assert r_put.status_code == 200, r_put.text
    assert r_put.json()["status"] == "active"
    assert r_put.json().get("until") is None
    listed = only_entry(client, headers)
    assert listed["status"] == "active"
    assert listed.get("until") is None
    assert listed["since"] == {"kind": "age", "value": 8}

    headers_new, _ = consented_user(client, db)
    r_active = post_entry(
        client,
        headers_new,
        chronic(
            condition="epilepsy",
            status="active",
            since={"kind": "age", "value": 8},
            until={"kind": "age", "value": 16},
        ),
    )
    assert r_active.status_code == 201, r_active.text
    assert r_active.json().get("until") is None
    assert only_entry(client, headers_new).get("until") is None


# --- Escenario 8 (B-4): el diagnóstico enlazado es del propio expediente ----------


def test_b4_diagnosis_link_must_be_own_diagnosis(
    client: TestClient, db: Session
) -> None:
    """A enlaza el diagnóstico de B, su propia receta o un uuid inexistente ->
    422 con el mismo detail y nada persiste; su propio diagnóstico -> 201."""
    headers_a, _ = consented_user(client, db)
    headers_b, _ = consented_user(client, db)
    diag_b = create_diagnosis(client, headers_b)
    rx_a = create_prescription(client, headers_a)
    diag_a = create_diagnosis(client, headers_a)

    bodies = []
    for bad_id in (diag_b, rx_a, str(uuid.uuid4())):
        r = post_entry(
            client,
            headers_a,
            chronic(condition="hypothyroidism", diagnosis_id=bad_id),
        )
        assert r.status_code == 422, (bad_id, r.text)
        assert r.json()["detail"] == DIAGNOSIS_NOT_YOURS, (bad_id, r.text)
        bodies.append(r.json())
    assert bodies[0] == bodies[1] == bodies[2]
    assert_history_empty(client, headers_a)

    good = chronic(condition="hypothyroidism", status="active", diagnosis_id=diag_a)
    r_ok = post_entry(client, headers_a, good)
    assert r_ok.status_code == 201, r_ok.text
    assert str(r_ok.json()["diagnosis_id"]) == diag_a
    assert str(only_entry(client, headers_a)["diagnosis_id"]) == diag_a


def test_b4_put_diagnosis_link_must_be_own_diagnosis(
    client: TestClient, db: Session
) -> None:
    """PUT de una crónica de A con el diagnóstico de B o su receta -> 422 exacto;
    la crónica sigue enlazada al diagnóstico propio."""
    headers_a, _ = consented_user(client, db)
    headers_b, _ = consented_user(client, db)
    diag_a = create_diagnosis(client, headers_a)
    diag_b = create_diagnosis(client, headers_b)
    rx_a = create_prescription(client, headers_a)
    body = chronic(condition="hypothyroidism", status="active", diagnosis_id=diag_a)
    r_create = post_entry(client, headers_a, body)
    assert r_create.status_code == 201, r_create.text
    entry_id = r_create.json()["id"]

    for bad_id in (diag_b, rx_a, str(uuid.uuid4())):
        r = client.put(
            entry_url(entry_id),
            headers=headers_a,
            json={**body, "diagnosis_id": bad_id},
        )
        assert r.status_code == 422, (bad_id, r.text)
        assert r.json()["detail"] == DIAGNOSIS_NOT_YOURS, (bad_id, r.text)

    assert str(only_entry(client, headers_a)["diagnosis_id"]) == diag_a


# --- Escenario 9 (B-1): la condición es requerida ---------------------------------


def test_b1_chronic_without_condition_rejected(client: TestClient, db: Session) -> None:
    """Sin condition (con since y treatment) -> 422 exacto; nada se guarda."""
    headers, _ = consented_user(client, db)

    r = post_entry(
        client,
        headers,
        chronic(
            since={"kind": "age", "value": 31},
            treatment="Levotiroxina 50 mcg en ayunas",
        ),
    )

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == CONDITION_REQUIRED
    assert_history_empty(client, headers)


@pytest.mark.parametrize(
    "other_text", [None, "", "   "], ids=["absent", "empty", "blank"]
)
def test_b1_chronic_other_without_text_rejected(
    client: TestClient, db: Session, other_text: str | None
) -> None:
    """condition other sin other_text (o en blanco) -> 422 exacto; nada se guarda."""
    headers, _ = consented_user(client, db)
    body = chronic(condition="other", status="active")
    if other_text is not None:
        body["other_text"] = other_text

    r = post_entry(client, headers, body)

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == CONDITION_REQUIRED
    assert_history_empty(client, headers)


@pytest.mark.parametrize("other_text", INVISIBLE_TEXTS, ids=INVISIBLE_IDS)
def test_chronic_other_invisible_text_is_required(
    client: TestClient, db: Session, other_text: str
) -> None:
    """Texto sin nada visible también en crónicas: POST chronic/other con
    other_text invisible -> 422 "Elige la condición o escribe cuál es"; no se crea."""
    headers, _ = consented_user(client, db)
    before = entries_count(client, headers)

    r = post_entry(
        client,
        headers,
        chronic(condition="other", status="active", other_text=other_text),
    )

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == CONDITION_REQUIRED, r.text
    assert entries_count(client, headers) == before


def test_b1_empty_chronic_rejected(client: TestClient, db: Session) -> None:
    """POST {section: chronic} sin nada más -> 422 es-MX (string); nada persiste."""
    headers, _ = consented_user(client, db)

    r = post_entry(client, headers, {"section": "chronic"})

    assert r.status_code == 422, r.text
    assert r.json()["detail"] == "Llena al menos un dato"
    assert_history_empty(client, headers)


# --- Escenario 14 (B-0): "No tengo ninguna" en crónicas ---------------------------


def test_b0_chronic_none_mark_then_entry_clears_it(
    client: TestClient, db: Session
) -> None:
    """PUT none chronic -> sections_none la trae; POST una crónica la quita."""
    headers, _ = consented_user(client, db)

    r_mark = set_none(client, headers, "chronic", True)

    assert r_mark.status_code == 200, r_mark.text
    assert "chronic" in r_mark.json()["sections_none"]
    assert "chronic" in sections_none(client, headers)

    r = post_entry(client, headers, chronic(condition="hypertension"))
    assert r.status_code == 201, r.text
    assert "chronic" not in sections_none(client, headers)


def test_b0_chronic_none_undo(client: TestClient, db: Session) -> None:
    """none true y luego none false en chronic -> sale de sections_none."""
    headers, _ = consented_user(client, db)
    r_mark = set_none(client, headers, "chronic", True)
    assert r_mark.status_code == 200, r_mark.text

    r_undo = set_none(client, headers, "chronic", False)

    assert r_undo.status_code == 200, r_undo.text
    assert "chronic" not in r_undo.json()["sections_none"]
    assert "chronic" not in sections_none(client, headers)


def test_b0_cannot_mark_chronic_none_with_entries(
    client: TestClient, db: Session
) -> None:
    """Con 1 crónica: PUT none chronic -> el rechazo de la Story A (409 exacto);
    sections_none sin cambio y la crónica sigue."""
    headers, _ = consented_user(client, db)
    r_create = post_entry(client, headers, HYPOTHYROIDISM_ACTIVE)
    assert r_create.status_code == 201, r_create.text
    before = sections_none(client, headers)

    r = set_none(client, headers, "chronic", True)

    assert r.status_code == 409, r.text
    assert r.json()["detail"] == (
        "No puedes marcar «ninguna» si la sección tiene registros"
    )
    after = sections_none(client, headers)
    assert after == before
    assert "chronic" not in after
    assert list_entries(client, headers).json()["count"] == 1


# --- Escenario 15: aislamiento ----------------------------------------------------


def test_b_isolation_foreign_chronic_indistinguishable_from_missing(
    client: TestClient, db: Session
) -> None:
    """PUT/DELETE de A sobre la crónica de B = mismo status y cuerpo que un id
    inexistente; la crónica de B no cambia."""
    headers_a, _ = consented_user(client, db)
    headers_b, _ = consented_user(client, db)
    body_b = chronic(
        condition="anxiety",
        status="active",
        treatment="Sertralina 50 mg",
    )
    r_b = post_entry(client, headers_b, body_b)
    assert r_b.status_code == 201, r_b.text
    foreign_id = r_b.json()["id"]
    missing_id = str(uuid.uuid4())

    put_body = {**body_b, "treatment": "intento de edición ajena", "sensitive": False}
    for method, kwargs in (("PUT", {"json": put_body}), ("DELETE", {})):
        r_foreign = client.request(
            method, entry_url(foreign_id), headers=headers_a, **kwargs
        )
        r_missing = client.request(
            method, entry_url(missing_id), headers=headers_a, **kwargs
        )
        assert r_foreign.status_code == r_missing.status_code, method
        assert r_foreign.status_code == 404, (method, r_foreign.text)
        assert r_foreign.json() == r_missing.json(), method
        assert r_foreign.json() == {"detail": "Registro no encontrado"}, method
        assert "Sertralina" not in r_foreign.text, method

    assert_history_empty(client, headers_a)
    entry_b = only_entry(client, headers_b)
    assert str(entry_b["id"]) == str(foreign_id)
    assert entry_b["condition"] == "anxiety"
    assert entry_b["treatment"] == "Sertralina 50 mg"
    assert entry_b["sensitive"] is True


# --- Escenario 16 (B-6): cifrado en reposo de la crónica --------------------------


def test_b6_chronic_encrypted_at_rest(client: TestClient, db: Session) -> None:
    """Crónica anxiety, sensitive true, Sertralina, enlazada a un diagnóstico:
    medical_history_entry.content no contiene nada en claro y descifra al valor."""
    headers, user_id = consented_user(client, db)
    diag_id = create_diagnosis(client, headers, title="Trastorno de ansiedad")
    r = post_entry(
        client,
        headers,
        chronic(
            condition="anxiety",
            sensitive=True,
            status="active",
            treatment="Sertralina 50 mg",
            diagnosis_id=diag_id,
        ),
    )
    assert r.status_code == 201, r.text

    entries = raw_rows(
        "SELECT content FROM medical_history_entry WHERE user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )
    assert len(entries) == 1
    content = str(entries[0]["content"])
    assert content.startswith("gAAAA"), content
    for plain in ("anxiety", "Ansiedad", "Sertralina", "sensitive", diag_id, "chronic"):
        assert plain not in content, plain

    decrypted = decrypt_str(content)
    assert decrypted is not None
    stored = json.loads(decrypted)
    assert stored["section"] == "chronic"
    assert stored["condition"] == "anxiety"
    assert stored["sensitive"] is True
    assert stored["treatment"] == "Sertralina 50 mg"
    assert str(stored["diagnosis_id"]) == diag_id


# --- Review R1: las escrituras del historial toman el candado del perfil ----------

# How long a request must stay blocked behind a held lock to count as waiting,
# and the ceiling for it to finish once released (never hangs the suite).
LOCK_WAIT_S = 1.0
LOCK_RELEASE_TIMEOUT_S = 15.0


def assert_waits_for_profile_lock(user_id: str, call: Callable[[], Any]) -> Any:
    """Hold `SELECT … FROM patient_profile … FOR UPDATE` on a separate
    connection, fire `call` in a thread, assert it is still blocked after
    LOCK_WAIT_S, release, and return its response once it finishes."""
    result: dict[str, Any] = {}

    def run() -> None:
        try:
            result["response"] = call()
        except BaseException as e:  # surfaced in the main thread below
            result["error"] = e

    worker = threading.Thread(target=run, daemon=True)
    with engine.connect() as holder:
        locked = holder.execute(
            text(
                "SELECT id FROM patient_profile "
                "WHERE user_id = CAST(:uid AS uuid) FOR UPDATE"
            ),
            {"uid": user_id},
        ).all()
        assert len(locked) == 1, "the profile must exist to hold its lock"
        worker.start()
        worker.join(timeout=LOCK_WAIT_S)
        still_waiting = worker.is_alive()
        holder.rollback()  # releases the lock
    worker.join(timeout=LOCK_RELEASE_TIMEOUT_S)
    assert not worker.is_alive(), "the request did not finish after the release"
    assert still_waiting, "the request did not wait for the profile lock"
    if "error" in result:
        raise result["error"]
    return result["response"]


def test_r1_put_history_entry_waits_for_profile_lock(
    client: TestClient, db: Session
) -> None:
    """PUT /profile/history/{id} espera el candado del perfil y luego guarda."""
    headers, user_id = consented_user(client, db)
    r = post_entry(client, headers, HYPOTHYROIDISM_ACTIVE)
    assert r.status_code == 201, r.text
    entry_id = r.json()["id"]
    updated = {**HYPOTHYROIDISM_ACTIVE, "treatment": "Levotiroxina 75 mcg"}

    r_put = assert_waits_for_profile_lock(
        user_id, lambda: client.put(entry_url(entry_id), headers=headers, json=updated)
    )

    assert r_put.status_code == 200, r_put.text
    assert only_entry(client, headers)["treatment"] == "Levotiroxina 75 mcg"


def test_r1_delete_diagnosis_waits_for_profile_lock(
    client: TestClient, db: Session
) -> None:
    """DELETE /health-records/{id} de un diagnóstico espera el candado del
    perfil y luego desvincula la crónica que respaldaba."""
    headers, user_id = consented_user(client, db)
    diag_id = create_diagnosis(client, headers)
    r = post_entry(client, headers, {**HYPOTHYROIDISM_ACTIVE, "diagnosis_id": diag_id})
    assert r.status_code == 201, r.text

    r_delete = assert_waits_for_profile_lock(
        user_id, lambda: client.delete(record_url(diag_id), headers=headers)
    )

    assert r_delete.status_code == 200, r_delete.text
    assert only_entry(client, headers).get("diagnosis_id") is None


def test_r1_delete_history_entry_waits_for_profile_lock(
    client: TestClient, db: Session
) -> None:
    """DELETE /profile/history/{id} espera el candado del perfil y luego borra."""
    headers, user_id = consented_user(client, db)
    r = post_entry(client, headers, HYPOTHYROIDISM_ACTIVE)
    assert r.status_code == 201, r.text
    entry_id = r.json()["id"]

    r_delete = assert_waits_for_profile_lock(
        user_id, lambda: client.delete(entry_url(entry_id), headers=headers)
    )

    assert r_delete.status_code == 200, r_delete.text
    assert_history_empty(client, headers)


def test_r1_delete_diagnosis_does_not_create_profile(
    client: TestClient, db: Session
) -> None:
    """Sin perfil no hay crónicas que desvincular: borrar un diagnóstico -> 200
    y el perfil sigue sin existir (crud.lock_profile no lo crea)."""
    headers, user_id = consented_user(client, db)
    diag_id = create_diagnosis(client, headers)
    profile_sql = "SELECT id FROM patient_profile WHERE user_id = CAST(:uid AS uuid)"
    assert raw_rows(profile_sql, {"uid": user_id}) == []

    r = client.delete(record_url(diag_id), headers=headers)

    assert r.status_code == 200, r.text
    assert raw_rows(profile_sql, {"uid": user_id}) == []
