"""Tests for the event sections of the medical history (perfil-eventos, grupo 1).

Interface contract (design.md, "## Interface contract"; base /api/v1/profile,
all behind a current consent; 422/409/404 carry a STRING detail in es-MX;
lists use {"data": [...], "count": N}):
- section: "past" | "surgeries" | "fractures" | "transfusions".
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
import uuid
from datetime import date, datetime
from typing import Any
from zoneinfo import ZoneInfo

from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app.core.db import engine
from app.core.encrypted import decrypt_str
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
    """Sección fuera de esta story (chronic) -> 422; sections_none no la trae."""
    headers, _ = consented_user(client, db)

    r = set_none(client, headers, "chronic", True)

    assert r.status_code == 422, r.text
    assert "chronic" not in sections_none(client, headers)


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
    cuerpo {"detail": "Registro no encontrado"}; la cirugía de B no cambia."""
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
