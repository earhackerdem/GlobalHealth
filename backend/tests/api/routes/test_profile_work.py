"""Tests for the work block of the medical profile (perfil-trabajo, C-9,
scenarios T-1...T-6 of the spec delta).

Interface contract (openspec/changes/perfil-trabajo/design.md, "## Interface
contract"; base /api/v1, behind ConsentedUser):
- GET /profile/work -> 200 Work. No profile or no work saved: all null /
  empty; reading never creates the profile.
- PUT /profile/work body Work -> 200 Work (normalized and stored); replaces the
  whole block. Schema errors -> 422 with loc ["body", <field>] (plus the index
  inside exposures).
- Work (closed: an extra property is 422):
  status: employed|looking|retired|homemaker|student|unable_health|null
  occupation: str max 200|null (only with employed)
  longest_job: str max 200|null (with any status, also with none)
  exposures: list[dust|chemicals|loud_noise], max 3 items, default []
             (only with employed)
  no_exposures: bool, default false ("Nada de esto"; only with employed)
  shift: day|night|rotating|null (only with employed)
- Server normalization, in this order: trim spaces (empty text -> null; the
  200 max measured after trimming); drop repeated exposures; no_exposures true
  -> exposures []; status != employed -> occupation, exposures, no_exposures
  and shift cleared (null / [] / false). Everything empty -> the stored column
  is null.
- Stored in the new encrypted column patient_profile.work (Fernet, "gAAAA").
"""

from typing import Any

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session

from tests.api.routes.test_profile import (
    PROFILE_URL,
    consented_user,
    put_profile,
    user_without_consent_headers,
)
from tests.api.routes.test_profile_history import BIRTH_DATE, raw_rows

WORK_URL = f"{PROFILE_URL}/work"

WORK_KEYS = {
    "status",
    "occupation",
    "longest_job",
    "exposures",
    "no_exposures",
    "shift",
}

EMPTY_WORK: dict[str, Any] = {
    "status": None,
    "occupation": None,
    "longest_job": None,
    "exposures": [],
    "no_exposures": False,
    "shift": None,
}

DRIVER: dict[str, Any] = {
    "status": "employed",
    "occupation": "Chofer de transporte",
    "exposures": ["loud_noise"],
    "shift": "rotating",
}


# --- helpers ----------------------------------------------------------------------


def work(**fields: Any) -> dict[str, Any]:
    """A full (normalized) Work: the given fields, the rest empty."""
    return {**EMPTY_WORK, **fields}


def get_work(client: TestClient, headers: dict[str, str]) -> Any:
    return client.get(WORK_URL, headers=headers)


def put_work(client: TestClient, headers: dict[str, str], body: dict[str, Any]) -> Any:
    return client.put(WORK_URL, headers=headers, json=body)


def stored_work(client: TestClient, headers: dict[str, str]) -> dict[str, Any]:
    r = get_work(client, headers)
    assert r.status_code == 200, r.text
    body: dict[str, Any] = r.json()
    return body


def save(
    client: TestClient, headers: dict[str, str], body: dict[str, Any]
) -> dict[str, Any]:
    r = put_work(client, headers, body)
    assert r.status_code == 200, r.text
    saved: dict[str, Any] = r.json()
    return saved


def profile_rows(user_id: str) -> list[Any]:
    return raw_rows(
        "SELECT id FROM patient_profile WHERE user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )


def raw_work_rows(user_id: str) -> list[Any]:
    return raw_rows(
        "SELECT work FROM patient_profile WHERE user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )


def raw_profile_row_text(user_id: str) -> str:
    """The whole patient_profile row as stored, as text."""
    rows = raw_rows(
        "SELECT CAST(p AS text) AS row_text FROM patient_profile p "
        "WHERE p.user_id = CAST(:uid AS uuid)",
        {"uid": user_id},
    )
    assert len(rows) == 1, rows
    return str(rows[0]["row_text"])


def error_locs(r: Any) -> list[list[Any]]:
    assert r.status_code == 422, r.text
    detail = r.json()["detail"]
    assert isinstance(detail, list), detail
    return [list(error["loc"]) for error in detail]


# --- T-1: guardar el trabajo y verlo ---------------------------------------------


def test_t1_employed_driver_round_trip(client: TestClient, db: Session) -> None:
    """employed, «Chofer de transporte», ["loud_noise"], rotating -> PUT 200 con
    ese cuerpo y GET igual."""
    headers, _ = consented_user(client, db)
    expected = work(**DRIVER)

    saved = save(client, headers, DRIVER)

    assert saved == expected
    assert stored_work(client, headers) == expected


# --- T-2: todo es opcional --------------------------------------------------------


def test_t2_empty_put_returns_empty_and_stores_null(
    client: TestClient, db: Session
) -> None:
    """Con perfil y sin trabajo: PUT {} -> 200 todo vacío; GET igual; la columna
    work de la fila queda null."""
    headers, user_id = consented_user(client, db)
    r_profile = put_profile(client, headers, {"birth_date": BIRTH_DATE})
    assert r_profile.status_code == 200, r_profile.text

    saved = save(client, headers, {})

    assert saved == EMPTY_WORK
    assert stored_work(client, headers) == EMPTY_WORK
    rows = raw_work_rows(user_id)
    assert len(rows) == 1, rows
    assert rows[0]["work"] is None, rows


def test_t2_empty_put_after_saved_work_stores_null(
    client: TestClient, db: Session
) -> None:
    """Con el trabajo guardado, PUT {} reemplaza el bloque: 200 todo vacío y la
    columna work queda null."""
    headers, user_id = consented_user(client, db)
    save(client, headers, DRIVER)

    saved = save(client, headers, {})

    assert saved == EMPTY_WORK
    assert stored_work(client, headers) == EMPTY_WORK
    rows = raw_work_rows(user_id)
    assert len(rows) == 1, rows
    assert rows[0]["work"] is None, rows


def test_t2_get_without_profile_is_empty_and_does_not_create_it(
    client: TestClient, db: Session
) -> None:
    """Usuario sin perfil: GET /profile/work -> 200 el cuerpo vacío completo y no
    aparece fila en patient_profile."""
    headers, user_id = consented_user(client, db)

    assert stored_work(client, headers) == EMPTY_WORK

    assert profile_rows(user_id) == []


# --- T-3: «Nada de esto» y una exposición se excluyen -----------------------------


def test_t3_no_exposures_drops_exposures(client: TestClient, db: Session) -> None:
    """employed con no_exposures true y ["dust"] -> se guarda sin exposiciones
    (exposures [], no_exposures true)."""
    headers, _ = consented_user(client, db)
    expected = work(status="employed", exposures=[], no_exposures=True)

    saved = save(
        client,
        headers,
        {"status": "employed", "exposures": ["dust"], "no_exposures": True},
    )

    assert saved == expected
    assert stored_work(client, headers) == expected


# --- T-4: jubilado con el trabajo de más años -------------------------------------


def test_t4_retired_keeps_longest_job_drops_occupation_and_shift(
    client: TestClient, db: Session
) -> None:
    """retired con «Minero» y además occupation y shift -> occupation y shift se
    descartan, «Minero» queda."""
    headers, _ = consented_user(client, db)
    expected = work(status="retired", longest_job="Minero")

    saved = save(
        client,
        headers,
        {
            "status": "retired",
            "longest_job": "Minero",
            "occupation": "Chofer de transporte",
            "shift": "day",
        },
    )

    assert saved == expected
    assert stored_work(client, headers) == expected


# --- T-6: cambiar de situación borra lo del trabajo -------------------------------


def test_t6_switch_to_looking_clears_job_fields_keeps_longest_job(
    client: TestClient, db: Session
) -> None:
    """Guardado employed completo con «Taxista» como trabajo de más años; el
    mismo cuerpo con status looking -> GET sin occupation, exposiciones ni
    shift; «Taxista» queda."""
    headers, _ = consented_user(client, db)
    full = {**DRIVER, "longest_job": "Taxista"}
    assert save(client, headers, full) == work(**full)

    save(client, headers, {**full, "status": "looking"})

    assert stored_work(client, headers) == work(
        status="looking", longest_job="Taxista"
    )


# --- Fuera de opciones o de largo -------------------------------------------------

SEED: dict[str, Any] = {**DRIVER, "longest_job": "Taxista"}

OUT_OF_OPTIONS_CASES = [
    pytest.param({**SEED, "status": "unemployed"}, ["body", "status"], id="status"),
    pytest.param(
        {**SEED, "exposures": ["dust", "asbestos"]},
        ["body", "exposures", 1],
        id="exposure-item",
    ),
    pytest.param({**SEED, "shift": "evening"}, ["body", "shift"], id="shift"),
    pytest.param(
        {**SEED, "occupation": "  " + "a" * 201 + "  "},
        ["body", "occupation"],
        id="occupation-201-after-trim",
    ),
    pytest.param(
        {**SEED, "longest_job": "  " + "b" * 201 + "  "},
        ["body", "longest_job"],
        id="longest_job-201-after-trim",
    ),
    pytest.param({**SEED, "risk": "high"}, ["body", "risk"], id="extra-property"),
    pytest.param(
        {**SEED, "exposures": ["dust", "chemicals", "loud_noise", "dust"]},
        ["body", "exposures"],
        id="exposures-4-items",
    ),
]


@pytest.mark.parametrize(("body", "loc"), OUT_OF_OPTIONS_CASES)
def test_out_of_options_or_length_is_422_and_leaves_work_unchanged(
    client: TestClient, db: Session, body: dict[str, Any], loc: list[Any]
) -> None:
    """Status, exposición o turno desconocidos, texto de 201 tras recortar, una
    propiedad extra o exposures de 4 -> 422 con su loc; GET sin cambios."""
    headers, _ = consented_user(client, db)
    before = save(client, headers, SEED)

    r = put_work(client, headers, body)

    assert loc in error_locs(r), r.text
    assert stored_work(client, headers) == before


def test_text_of_200_after_trim_is_accepted(client: TestClient, db: Session) -> None:
    """200 caracteres con espacios alrededor -> 200 y se guardan los 200 sin
    los espacios (el máximo se mide después de recortar)."""
    headers, _ = consented_user(client, db)
    occupation = "a" * 200
    longest_job = "b" * 200
    expected = work(status="employed", occupation=occupation, longest_job=longest_job)

    saved = save(
        client,
        headers,
        {
            "status": "employed",
            "occupation": f"   {occupation}   ",
            "longest_job": f"  {longest_job}  ",
        },
    )

    assert saved == expected
    assert stored_work(client, headers) == expected


def test_texts_are_trimmed_and_blank_becomes_null(
    client: TestClient, db: Session
) -> None:
    """«  Albañil  » se guarda recortado y «   » queda null."""
    headers, _ = consented_user(client, db)
    expected = work(status="employed", occupation="Albañil", longest_job=None)

    saved = save(
        client,
        headers,
        {"status": "employed", "occupation": "  Albañil  ", "longest_job": "   "},
    )

    assert saved == expected
    assert stored_work(client, headers) == expected


def test_blank_occupation_becomes_null(client: TestClient, db: Session) -> None:
    """occupation «   » con employed -> null; «  Albañil  » como trabajo de más
    años -> «Albañil»."""
    headers, _ = consented_user(client, db)
    expected = work(status="employed", occupation=None, longest_job="Albañil")

    saved = save(
        client,
        headers,
        {"status": "employed", "occupation": "   ", "longest_job": "  Albañil  "},
    )

    assert saved == expected
    assert stored_work(client, headers) == expected


def test_repeated_exposures_are_stored_once(client: TestClient, db: Session) -> None:
    """employed con ["dust", "dust"] -> se guarda ["dust"]."""
    headers, _ = consented_user(client, db)
    expected = work(status="employed", exposures=["dust"])

    saved = save(client, headers, {"status": "employed", "exposures": ["dust", "dust"]})

    assert saved == expected
    assert stored_work(client, headers) == expected


# --- T-5: solo del paciente y cifrado ---------------------------------------------


def test_t5_other_user_gets_own_empty_work(client: TestClient, db: Session) -> None:
    """A guarda «Chofer de transporte»; B (con consentimiento, sin trabajo) lee su
    propio trabajo vacío, no el de A."""
    headers_a, _ = consented_user(client, db)
    save(client, headers_a, DRIVER)
    headers_b, _ = consented_user(client, db)

    r = get_work(client, headers_b)

    assert r.status_code == 200, r.text
    assert r.json() == EMPTY_WORK
    assert "Chofer de transporte" not in r.text
    assert stored_work(client, headers_a) == work(**DRIVER)


def test_t5_work_is_encrypted_at_rest(client: TestClient, db: Session) -> None:
    """Guardado «Chofer de transporte»: la columna work es un cifrado Fernet
    ("gAAAA") y el texto no aparece en claro en la fila de patient_profile."""
    headers, user_id = consented_user(client, db)
    save(client, headers, DRIVER)

    rows = raw_work_rows(user_id)
    assert len(rows) == 1, rows
    assert str(rows[0]["work"]).startswith("gAAAA"), rows
    row_text = raw_profile_row_text(user_id)
    for plain in ("Chofer de transporte", "loud_noise", "rotating"):
        assert plain not in row_text, plain


@pytest.mark.parametrize(
    ("method", "json_body"),
    [("GET", None), ("PUT", DRIVER)],
    ids=["GET /profile/work", "PUT /profile/work"],
)
def test_t5_work_requires_consent(
    client: TestClient,
    db: Session,
    method: str,
    json_body: dict[str, Any] | None,
) -> None:
    """Sin consentimiento: GET y PUT /profile/work -> 403 CONSENT_REQUIRED."""
    headers = user_without_consent_headers(client, db)

    r = client.request(method, WORK_URL, headers=headers, json=json_body)

    assert r.status_code == 403, (method, r.text)
    assert r.json()["detail"] == "CONSENT_REQUIRED"


# --- Sin veredicto ------------------------------------------------------------------


def test_response_has_exactly_the_six_keys_no_verdict(
    client: TestClient, db: Session
) -> None:
    """La respuesta de PUT y de GET trae exactamente las seis claves de Work:
    ningún riesgo, puntaje ni veredicto."""
    headers, _ = consented_user(client, db)

    saved = save(client, headers, DRIVER)
    stored = stored_work(client, headers)

    assert set(saved) == WORK_KEYS, saved
    assert set(stored) == WORK_KEYS, stored
