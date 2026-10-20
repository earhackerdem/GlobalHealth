"""Tests for the patient profile & onboarding (onboarding-perfil, grupo 1).

Interface contract (base /api/v1/profile, all behind a current consent; 422
errors carry a STRING detail in es-MX; lists use {"data": [...], "count": N}):
- GET /profile -> {birth_date: date|null, sex: "female"|"male"|"unspecified"|null,
  allergies: str|null, onboarding: "pending"|"completed"|"skipped",
  latest_weight: {value: float, measured_on: date}|null, latest_height: idem|null}.
- PUT /profile — partial body {birth_date?, sex?, allergies?} (null clears) ->
  the profile as GET. Validation: birth_date in [1900-01-01, today].
- POST /profile/onboarding {outcome: "completed"|"skipped"} -> 200 profile;
  409 when no longer "pending".
- POST /profile/measurements {type: "weight"|"height", value: float} -> 201
  {id, type, value, measured_on} (measured_on = today, server-set). Validation:
  weight in (0, 400] kg; height in [30, 250] cm -> out of range 422 es-MX.
- GET /profile/measurements?type=weight -> {data, count}, measured_on DESC.
- POST /profile/family-history {condition, other_text?, relatives: [...],
  note?} -> 201 the entry with id. PUT /{id} -> 200; DELETE /{id} -> 200 with
  es-MX message; GET /profile/family-history -> {data, count}. Someone else's
  resource and a nonexistent one: indistinguishable responses (same status and
  body).
- Encrypted at rest (Fernet ciphertext, prefix "gAAAA", verified by
  decrypt-and-compare): patient_profile (birth_date, sex, allergies),
  body_measurement (value), family_history (condition, other_text, relatives,
  note). Tables: patient_profile(user_id unique, ...),
  body_measurement(user_id, type, value, measured_on),
  family_history(user_id, condition, other_text, relatives, note).
- Duplicated condition (!= "other") for the same user -> 409 es-MX; "other"
  admits several entries (review G3).
"""

import uuid
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlmodel import Session

from app import crud
from app.core.config import settings
from app.core.encrypted import decrypt_str
from app.models import UserCreate
from tests.utils.utils import random_email, random_lower_string

PROFILE_URL = f"{settings.API_V1_STR}/profile"


def consented_user(client: TestClient, db: Session) -> tuple[dict[str, str], str]:
    """Fresh random user, logged in, with consent v1 granted -> (headers, user_id)."""
    email = random_email()
    password = random_lower_string()
    user = crud.create_user(
        session=db, user_create=UserCreate(email=email, password=password)
    )
    r = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200, r.text
    headers = {"Authorization": f"Bearer {r.json()['access_token']}"}
    r_consent = client.post(
        f"{settings.API_V1_STR}/consent/", headers=headers, json={"version": "v1"}
    )
    assert r_consent.status_code == 201, r_consent.text
    return headers, str(user.id)


def user_without_consent_headers(client: TestClient, db: Session) -> dict[str, str]:
    """Fresh random user, logged in, WITHOUT consent."""
    email = random_email()
    password = random_lower_string()
    crud.create_user(session=db, user_create=UserCreate(email=email, password=password))
    r = client.post(
        f"{settings.API_V1_STR}/login/access-token",
        data={"username": email, "password": password},
    )
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def get_profile(client: TestClient, headers: dict[str, str]) -> Any:
    return client.get(PROFILE_URL, headers=headers)


def put_profile(
    client: TestClient, headers: dict[str, str], body: dict[str, Any]
) -> Any:
    return client.put(PROFILE_URL, headers=headers, json=body)


def post_measurement(
    client: TestClient, headers: dict[str, str], type_: str, value: float
) -> Any:
    return client.post(
        f"{PROFILE_URL}/measurements",
        headers=headers,
        json={"type": type_, "value": value},
    )


def list_measurements(client: TestClient, headers: dict[str, str], type_: str) -> Any:
    return client.get(
        f"{PROFILE_URL}/measurements", headers=headers, params={"type": type_}
    )


def family_history_payload(**overrides: Any) -> dict[str, Any]:
    """Scenario 6 (AHF con línea y detalle) concrete data."""
    payload: dict[str, Any] = {
        "condition": "diabetes",
        "relatives": ["paternal_grandfather", "mother"],
        "note": "abuelo diagnosticado a los 50",
    }
    payload.update(overrides)
    return payload


def post_family_history(
    client: TestClient, headers: dict[str, str], payload: dict[str, Any]
) -> Any:
    return client.post(f"{PROFILE_URL}/family-history", headers=headers, json=payload)


def list_family_history(client: TestClient, headers: dict[str, str]) -> Any:
    return client.get(f"{PROFILE_URL}/family-history", headers=headers)


def family_history_url(entry_id: Any) -> str:
    return f"{PROFILE_URL}/family-history/{entry_id}"


def profile_row(db: Session, user_id: str) -> Any:
    db.expire_all()
    return (
        db.execute(
            text("SELECT * FROM patient_profile WHERE user_id = CAST(:uid AS uuid)"),
            {"uid": user_id},
        )
        .mappings()
        .one()
    )


# --- Escenario 1: Guardar perfil básico y ver datos -------------------------------


def test_ac1_save_basic_profile_and_read_back_encrypted_at_rest(
    client: TestClient, db: Session
) -> None:
    """PUT del perfil básico: 200, GET lo devuelve, y en BD es ciphertext Fernet."""
    headers, user_id = consented_user(client, db)

    r_put = put_profile(
        client,
        headers,
        {"birth_date": "1990-03-15", "sex": "female", "allergies": "penicilina"},
    )
    assert r_put.status_code == 200, r_put.text
    body = r_put.json()
    assert body["birth_date"] == "1990-03-15"
    assert body["sex"] == "female"
    assert body["allergies"] == "penicilina"

    r_get = get_profile(client, headers)
    assert r_get.status_code == 200, r_get.text
    profile = r_get.json()
    assert profile["birth_date"] == "1990-03-15"
    assert profile["sex"] == "female"
    assert profile["allergies"] == "penicilina"

    row = profile_row(db, user_id)
    expected_plaintext = {
        "birth_date": "1990-03-15",
        "sex": "female",
        "allergies": "penicilina",
    }
    for column, plaintext in expected_plaintext.items():
        value = str(row[column])
        assert value.startswith("gAAAA"), (column, value)
        # Determinista (review G4/M13): descifrar y comparar, no la ausencia
        # probabilística de un substring en el token.
        assert decrypt_str(value) == plaintext, column

    # null borra (review G12/M6): PUT explícito con null limpia el campo.
    r_clear = put_profile(client, headers, {"allergies": None})
    assert r_clear.status_code == 200, r_clear.text
    assert r_clear.json()["allergies"] is None
    r_get_cleared = get_profile(client, headers)
    assert r_get_cleared.status_code == 200, r_get_cleared.text
    cleared = r_get_cleared.json()
    assert cleared["allergies"] is None
    assert cleared["birth_date"] == "1990-03-15"  # lo no enviado no se toca
    assert cleared["sex"] == "female"


# --- Escenario 2: Fecha futura rechazada ------------------------------------------


def test_ac2_future_birth_date_rejected_profile_unchanged(
    client: TestClient, db: Session
) -> None:
    """PUT birth_date 2030-01-01: 422 con detalle es-MX y el perfil no cambia."""
    headers, _user_id = consented_user(client, db)
    r_seed = put_profile(client, headers, {"birth_date": "1990-03-15"})
    assert r_seed.status_code == 200, r_seed.text

    r = put_profile(client, headers, {"birth_date": "2030-01-01"})

    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, str), detail
    # Texto exacto esperado (contrato: detalle es-MX para fecha fuera de rango).
    assert detail == "La fecha de nacimiento no puede estar en el futuro", detail

    r_get = get_profile(client, headers)
    assert r_get.status_code == 200, r_get.text
    assert r_get.json()["birth_date"] == "1990-03-15"


# --- Escenario 3: Perfil vacío válido ---------------------------------------------


def test_ac3_empty_profile_put_is_valid_with_null_fields(
    client: TestClient, db: Session
) -> None:
    """PUT {}: 200 con los campos del perfil en null."""
    headers, _user_id = consented_user(client, db)

    r = put_profile(client, headers, {})

    assert r.status_code == 200, r.text
    profile = r.json()
    assert profile["birth_date"] is None
    assert profile["sex"] is None
    assert profile["allergies"] is None
    assert profile["latest_weight"] is None
    assert profile["latest_height"] is None
    assert profile["onboarding"] == "pending"


# --- Escenario 4: Medición nueva no borra la anterior -----------------------------


def test_ac4_new_measurement_keeps_previous_and_updates_latest(
    client: TestClient, db: Session
) -> None:
    """POST 72 y 74 kg: quedan las dos (ciphertext en BD), orden por
    measured_on DESC con fechas DISTINTAS y latest_weight.value 74."""
    headers, user_id = consented_user(client, db)
    # Same zone the server stamps measured_on with (routes/profile.py): the
    # runner's local date (UTC in CI) is a day ahead from 18:00 México time.
    today = datetime.now(ZoneInfo("America/Mexico_City")).date().isoformat()

    r_first = post_measurement(client, headers, "weight", 72)
    assert r_first.status_code == 201, r_first.text
    first = r_first.json()
    assert first["id"]
    assert first["type"] == "weight"
    assert first["value"] == 72
    assert first["measured_on"] == today  # measured_on lo pone el servidor

    r_second = post_measurement(client, headers, "weight", 74)
    assert r_second.status_code == 201, r_second.text
    second = r_second.json()

    # Ciphertext determinista en BD (review G4/M2): el valor crudo es un token
    # Fernet y descifra al valor capturado.
    db.expire_all()
    raw_rows = (
        db.execute(
            text(
                "SELECT id, value FROM body_measurement "
                "WHERE user_id = CAST(:uid AS uuid)"
            ),
            {"uid": user_id},
        )
        .mappings()
        .all()
    )
    raw_values = {str(r["id"]): str(r["value"]) for r in raw_rows}
    assert set(raw_values) == {str(first["id"]), str(second["id"])}
    for measurement_id, expected_value in (
        (str(first["id"]), 72.0),
        (str(second["id"]), 74.0),
    ):
        raw = raw_values[measurement_id]
        assert raw.startswith("gAAAA"), raw
        decrypted = decrypt_str(raw)
        assert decrypted is not None, raw
        assert float(decrypted) == expected_value

    # Orden por fecha REAL (review G5/M3): retrodatar la primera captura por
    # SQL para que las fechas sean DISTINTAS y el DESC no dependa del empate
    # por created_at.
    db.execute(
        text(
            "UPDATE body_measurement SET measured_on = '2026-09-01' "
            "WHERE id = CAST(:id AS uuid)"
        ),
        {"id": str(first["id"])},
    )
    db.commit()

    r_list = list_measurements(client, headers, "weight")
    assert r_list.status_code == 200, r_list.text
    body = r_list.json()
    assert body["count"] == 2
    assert len(body["data"]) == 2
    assert body["data"][0]["value"] == 74  # measured_on DESC: la más reciente
    assert body["data"][0]["measured_on"] == today
    assert body["data"][1]["value"] == 72
    assert body["data"][1]["measured_on"] == "2026-09-01"

    r_profile = get_profile(client, headers)
    assert r_profile.status_code == 200, r_profile.text
    latest = r_profile.json()["latest_weight"]
    assert latest is not None
    assert latest["value"] == 74
    assert latest["measured_on"] == today


# --- Escenario 5: Valor implausible -----------------------------------------------


def test_ac5_implausible_measurement_values_rejected(
    client: TestClient, db: Session
) -> None:
    """weight 0 y height 500: 422 con detalle string es-MX; no se crean filas."""
    headers, user_id = consented_user(client, db)

    r_weight = post_measurement(client, headers, "weight", 0)
    assert r_weight.status_code == 422, r_weight.text
    weight_detail = r_weight.json()["detail"]
    # Texto exacto de models.py (review G14/M8), no solo "es un string".
    assert weight_detail == "El peso debe ser mayor que 0 y de hasta 400 kg", (
        weight_detail
    )

    r_height = post_measurement(client, headers, "height", 500)
    assert r_height.status_code == 422, r_height.text
    height_detail = r_height.json()["detail"]
    assert height_detail == "La estatura debe estar entre 30 y 250 cm", height_detail

    for type_ in ("weight", "height"):
        r_list = list_measurements(client, headers, type_)
        assert r_list.status_code == 200, r_list.text
        assert r_list.json()["count"] == 0
        assert r_list.json()["data"] == []

    db.expire_all()
    row_count = db.execute(
        text(
            "SELECT COUNT(*) FROM body_measurement WHERE user_id = CAST(:uid AS uuid)"
        ),
        {"uid": user_id},
    ).scalar_one()
    assert row_count == 0


# --- Escenario 6: AHF con línea y detalle -----------------------------------------


def test_ac6_family_history_with_relatives_and_note_encrypted_at_rest(
    client: TestClient, db: Session
) -> None:
    """POST AHF diabetes (2 parientes + nota + detalle): 201, GET igual, BD
    ciphertext en condition, other_text, relatives y note."""
    headers, user_id = consented_user(client, db)

    payload = family_history_payload(other_text="tipo 2, inicio a los 50")
    r = post_family_history(client, headers, payload)

    assert r.status_code == 201, r.text
    entry = r.json()
    assert entry["id"]
    assert entry["condition"] == "diabetes"
    assert entry["other_text"] == "tipo 2, inicio a los 50"
    assert entry["relatives"] == ["paternal_grandfather", "mother"]
    assert entry["note"] == "abuelo diagnosticado a los 50"

    r_list = list_family_history(client, headers)
    assert r_list.status_code == 200, r_list.text
    body = r_list.json()
    assert body["count"] == 1
    listed = body["data"][0]
    assert str(listed["id"]) == str(entry["id"])
    assert listed["condition"] == "diabetes"
    assert listed["other_text"] == "tipo 2, inicio a los 50"
    assert listed["relatives"] == ["paternal_grandfather", "mother"]
    assert listed["note"] == "abuelo diagnosticado a los 50"

    db.expire_all()
    row = (
        db.execute(
            text("SELECT * FROM family_history WHERE user_id = CAST(:uid AS uuid)"),
            {"uid": user_id},
        )
        .mappings()
        .one()
    )
    # condition y other_text entran al loop (reviews G2 y G13/M7); el
    # descifrado-y-comparación es determinista (G4/M13).
    expected_plaintext = {
        "condition": "diabetes",
        "other_text": "tipo 2, inicio a los 50",
        "relatives": '["paternal_grandfather", "mother"]',
        "note": "abuelo diagnosticado a los 50",
    }
    for column, plaintext in expected_plaintext.items():
        value = str(row[column])
        assert value.startswith("gAAAA"), (column, value)
        assert decrypt_str(value) == plaintext, column


# --- Escenario 7: Quitar condición elimina sus parentescos ------------------------


def test_ac7_delete_family_history_removes_entry_and_row(
    client: TestClient, db: Session
) -> None:
    """DELETE de la entrada AHF: 200 con message es-MX, GET count 0, 0 filas en BD."""
    headers, user_id = consented_user(client, db)
    r_create = post_family_history(client, headers, family_history_payload())
    assert r_create.status_code == 201, r_create.text
    entry_id = r_create.json()["id"]

    r_delete = client.delete(family_history_url(entry_id), headers=headers)

    assert r_delete.status_code == 200, r_delete.text
    message = r_delete.json()["message"]
    # Texto exacto es-MX de la ruta (review G14/M8).
    assert message == "Antecedente eliminado", message

    r_list = list_family_history(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 0
    assert r_list.json()["data"] == []

    db.expire_all()
    row_count = db.execute(
        text("SELECT COUNT(*) FROM family_history WHERE user_id = CAST(:uid AS uuid)"),
        {"uid": user_id},
    ).scalar_one()
    assert row_count == 0


# --- Escenario 9: Onboarding una sola vez -----------------------------------------


def test_ac9_onboarding_closes_once_then_409(client: TestClient, db: Session) -> None:
    """Cuenta recién consentida: pending -> completed con POST; segundo POST: 409."""
    headers, _user_id = consented_user(client, db)

    r_initial = get_profile(client, headers)
    assert r_initial.status_code == 200, r_initial.text
    assert r_initial.json()["onboarding"] == "pending"

    r_close = client.post(
        f"{PROFILE_URL}/onboarding", headers=headers, json={"outcome": "completed"}
    )
    assert r_close.status_code == 200, r_close.text
    assert r_close.json()["onboarding"] == "completed"

    r_after = get_profile(client, headers)
    assert r_after.status_code == 200, r_after.text
    assert r_after.json()["onboarding"] == "completed"

    r_again = client.post(
        f"{PROFILE_URL}/onboarding", headers=headers, json={"outcome": "skipped"}
    )
    assert r_again.status_code == 409, r_again.text
    # El segundo intento no cambia el resultado registrado.
    r_final = get_profile(client, headers)
    assert r_final.status_code == 200, r_final.text
    assert r_final.json()["onboarding"] == "completed"


# --- Escenario 12: Perfil ajeno indistinguible ------------------------------------


def test_ac12_foreign_resources_indistinguishable_from_missing(
    client: TestClient, db: Session
) -> None:
    """B contra ids de A y contra ids inexistentes: misma respuesta, sin fugas."""
    headers_a, _user_a = consented_user(client, db)
    headers_b, _user_b = consented_user(client, db)

    r_measure = post_measurement(client, headers_a, "weight", 72)
    assert r_measure.status_code == 201, r_measure.text
    r_ahf = post_family_history(client, headers_a, family_history_payload())
    assert r_ahf.status_code == 201, r_ahf.text
    foreign_ahf_id = r_ahf.json()["id"]
    missing_ahf_id = str(uuid.uuid4())

    # Las listas de B no contienen nada de A.
    r_b_measurements = list_measurements(client, headers_b, "weight")
    assert r_b_measurements.status_code == 200, r_b_measurements.text
    assert r_b_measurements.json()["count"] == 0
    r_b_ahf = list_family_history(client, headers_b)
    assert r_b_ahf.status_code == 200, r_b_ahf.text
    assert r_b_ahf.json()["count"] == 0
    assert str(foreign_ahf_id) not in r_b_ahf.text
    assert "abuelo" not in r_b_ahf.text

    put_body = family_history_payload(note="intento de edición ajena")
    probes = (
        ("PUT", {"json": put_body}),
        ("DELETE", {}),
    )
    for method, kwargs in probes:
        r_foreign = client.request(
            method, family_history_url(foreign_ahf_id), headers=headers_b, **kwargs
        )
        r_missing = client.request(
            method, family_history_url(missing_ahf_id), headers=headers_b, **kwargs
        )
        # Indistinguibles: mismo status (404) y mismo cuerpo con el detail
        # exacto es-MX (review G14/M8), y nunca un éxito.
        assert r_foreign.status_code == 404, (method, r_foreign.text)
        assert r_missing.status_code == 404, (method, r_missing.text)
        assert r_foreign.json() == {"detail": "Antecedente no encontrado"}, (
            method,
            r_foreign.text,
        )
        assert r_foreign.json() == r_missing.json(), (method, r_foreign.text)
        assert "abuelo" not in r_foreign.text, method
        assert "intento de edición ajena" not in r_foreign.text, method

    # Los datos de A siguen intactos tras los intentos de B.
    r_a_ahf = list_family_history(client, headers_a)
    assert r_a_ahf.status_code == 200, r_a_ahf.text
    assert r_a_ahf.json()["count"] == 1
    assert r_a_ahf.json()["data"][0]["note"] == "abuelo diagnosticado a los 50"
    r_a_measurements = list_measurements(client, headers_a, "weight")
    assert r_a_measurements.status_code == 200, r_a_measurements.text
    assert r_a_measurements.json()["count"] == 1


# --- Review G3: condición duplicada -> 409; "other" admite varias ------------------


def test_family_history_duplicate_condition_rejected_other_allowed(
    client: TestClient, db: Session
) -> None:
    """2º POST de la misma condición: 409 es-MX sin crear fila; "other" sí
    admite dos entradas (se distinguen por other_text)."""
    headers, _user_id = consented_user(client, db)

    r_first = post_family_history(client, headers, family_history_payload())
    assert r_first.status_code == 201, r_first.text

    r_dup = post_family_history(
        client, headers, family_history_payload(relatives=["father"], note=None)
    )
    assert r_dup.status_code == 409, r_dup.text
    assert r_dup.json()["detail"] == (
        "Ya tienes un antecedente de esa condición; edítalo en lugar de crearlo"
    )

    r_list = list_family_history(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 1  # el duplicado no dejó fila

    for other_text in ("lupus eritematoso", "asma infantil"):
        r_other = post_family_history(
            client,
            headers,
            {"condition": "other", "other_text": other_text, "relatives": ["mother"]},
        )
        assert r_other.status_code == 201, r_other.text

    r_final = list_family_history(client, headers)
    assert r_final.status_code == 200, r_final.text
    assert r_final.json()["count"] == 3  # diabetes + 2 "other"

    # La misma regla por la otra puerta (review G3): renombrar vía PUT hacia
    # una condición ya usada también es 409; renombrar hacia una libre pasa.
    r_cancer = post_family_history(
        client,
        headers,
        {"condition": "cancer", "relatives": ["mother"]},
    )
    assert r_cancer.status_code == 201, r_cancer.text
    cancer_id = r_cancer.json()["id"]
    r_rename_dup = client.put(
        f"{PROFILE_URL}/family-history/{cancer_id}",
        headers=headers,
        json={"condition": "diabetes", "relatives": ["mother"]},
    )
    assert r_rename_dup.status_code == 409, r_rename_dup.text
    assert r_rename_dup.json()["detail"] == (
        "Ya tienes un antecedente de esa condición; edítalo en lugar de crearlo"
    )
    r_rename_free = client.put(
        f"{PROFILE_URL}/family-history/{cancer_id}",
        headers=headers,
        json={"condition": "hypertension", "relatives": ["mother"]},
    )
    assert r_rename_free.status_code == 200, r_rename_free.text
    assert r_rename_free.json()["condition"] == "hypertension"


def test_family_history_two_distinct_conditions_coexist(
    client: TestClient, db: Session
) -> None:
    """Varios antecedentes SHALL: dos condiciones distintas conviven."""
    headers, _user_id = consented_user(client, db)

    r_diabetes = post_family_history(client, headers, family_history_payload())
    assert r_diabetes.status_code == 201, r_diabetes.text
    r_hypertension = post_family_history(
        client,
        headers,
        family_history_payload(condition="hypertension", relatives=["father"]),
    )
    assert r_hypertension.status_code == 201, r_hypertension.text

    r_list = list_family_history(client, headers)
    assert r_list.status_code == 200, r_list.text
    body = r_list.json()
    assert body["count"] == 2
    assert [entry["condition"] for entry in body["data"]] == [
        "diabetes",
        "hypertension",
    ]


# --- Review G13/M7: condición "other" con texto libre ------------------------------


def test_family_history_other_condition_echoes_other_text(
    client: TestClient, db: Session
) -> None:
    """POST condition="other" con other_text: 201 y eco correcto."""
    headers, _user_id = consented_user(client, db)

    r = post_family_history(
        client,
        headers,
        {
            "condition": "other",
            "other_text": "lupus eritematoso",
            "relatives": ["mother"],
        },
    )

    assert r.status_code == 201, r.text
    entry = r.json()
    assert entry["condition"] == "other"
    assert entry["other_text"] == "lupus eritematoso"
    assert entry["relatives"] == ["mother"]
    assert entry["note"] is None


# --- Review G11/M5: relatives acotado y deduplicado --------------------------------


def test_family_history_relatives_deduped_and_bounded(
    client: TestClient, db: Session
) -> None:
    """Duplicados en relatives se consolidan preservando orden; más de 8
    elementos: 422 es-MX sin crear fila."""
    headers, _user_id = consented_user(client, db)

    r = post_family_history(
        client,
        headers,
        family_history_payload(relatives=["mother", "mother", "father", "mother"]),
    )
    assert r.status_code == 201, r.text
    assert r.json()["relatives"] == ["mother", "father"]

    r_over = post_family_history(
        client,
        headers,
        {"condition": "cancer", "relatives": ["mother"] * 9},
    )
    assert r_over.status_code == 422, r_over.text
    assert r_over.json()["detail"] == (
        "La lista de parentescos admite como máximo 8 elementos"
    )

    r_list = list_family_history(client, headers)
    assert r_list.status_code == 200, r_list.text
    assert r_list.json()["count"] == 1  # solo la entrada válida


# --- Extra: sin consentimiento no entra ni un dato (review G23/M10: 9/9 rutas) -----

_AHF_ID = "00000000-0000-0000-0000-000000000000"
_AHF_PAYLOAD = {"condition": "diabetes", "relatives": ["mother"]}
CONSENT_GATED_ROUTES: list[
    tuple[str, str, dict[str, Any] | None, dict[str, str] | None]
] = [
    ("GET", "", None, None),
    ("PUT", "", {"birth_date": "1990-03-15"}, None),
    ("POST", "/onboarding", {"outcome": "completed"}, None),
    ("POST", "/measurements", {"type": "weight", "value": 70}, None),
    ("GET", "/measurements", None, {"type": "weight"}),
    ("POST", "/family-history", _AHF_PAYLOAD, None),
    ("GET", "/family-history", None, None),
    ("PUT", f"/family-history/{_AHF_ID}", _AHF_PAYLOAD, None),
    ("DELETE", f"/family-history/{_AHF_ID}", None, None),
]


@pytest.mark.parametrize(
    "method,path,json_body,params",
    CONSENT_GATED_ROUTES,
    ids=[f"{method} /profile{path}" for method, path, _, _ in CONSENT_GATED_ROUTES],
)
def test_profile_routes_require_consent(
    client: TestClient,
    db: Session,
    method: str,
    path: str,
    json_body: dict[str, Any] | None,
    params: dict[str, str] | None,
) -> None:
    """Sin consentimiento, las 9 rutas del perfil responden 403 CONSENT_REQUIRED."""
    headers = user_without_consent_headers(client, db)

    r = client.request(
        method, f"{PROFILE_URL}{path}", headers=headers, json=json_body, params=params
    )

    assert r.status_code == 403, (method, path, r.text)
    assert r.json()["detail"] == "CONSENT_REQUIRED"
