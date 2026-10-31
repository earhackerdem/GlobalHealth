"""Database-level guarantees (change bd-candados-indices-y-log).

Interface contract (design.md, "## Interface contract"):
- `app.core.db.engine` is created with `hide_parameters=True`: the `str()` of a
  `DBAPIError` raised by a query with a bound parameter does not carry the value.
- Every foreign key has an index whose first column is the key's column (new
  migration `<rev>_index_foreign_keys.py`, down_revision "3b8e5f2a9c61").
"""

from typing import Any

import pytest
from pydantic import ValidationError
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app import models
from app.core.db import engine
from tests.utils.utils import random_email

MARKER = "Valor-Prueba-M1"

# Foreign keys of the public schema whose first column does not lead any index
# of the same table.
UNINDEXED_FOREIGN_KEYS_SQL = """
SELECT c.conrelid::regclass::text AS table_name,
       a.attname AS column_name,
       c.conname AS constraint_name
FROM pg_constraint c
JOIN pg_attribute a
  ON a.attrelid = c.conrelid AND a.attnum = c.conkey[1]
WHERE c.contype = 'f'
  AND c.connamespace = 'public'::regnamespace
  AND NOT EXISTS (
    SELECT 1
    FROM pg_index i
    WHERE i.indrelid = c.conrelid
      AND i.indkey[0] = c.conkey[1]
  )
ORDER BY 1, 2
"""


def test_db_error_message_hides_parameters() -> None:
    """Escenario «Error de base de datos con un valor de prueba»: una consulta
    con el parámetro "Valor-Prueba-M1" que la base rechaza falla, y el mensaje
    de la excepción no contiene Valor-Prueba-M1.

    The query is rejected by Postgres (division by zero) without Postgres
    echoing the value itself, so the only place the marker can appear is the
    parameter dump SQLAlchemy appends to the message."""
    with pytest.raises(DBAPIError) as exc_info:
        with engine.connect() as conn:
            conn.execute(
                text("SELECT length(CAST(:p AS text)) / 0"),
                {"p": MARKER},
            )

    assert MARKER not in str(exc_info.value), str(exc_info.value)


def test_every_foreign_key_has_an_index() -> None:
    """Escenario «Catálogo de la base migrada»: con la base migrada a la última
    versión, buscar en pg_constraint y pg_index las llaves foráneas sin índice
    no devuelve ninguna."""
    with engine.connect() as conn:
        rows: list[Any] = list(
            conn.execute(text(UNINDEXED_FOREIGN_KEYS_SQL)).mappings().all()
        )

    unindexed = [
        f"{r['table_name']}.{r['column_name']} ({r['constraint_name']})" for r in rows
    ]
    assert unindexed == [], unindexed


# Change tablas-snake-case (D25): old SQLModel-default table name -> new name.
RENAMED_TABLES = {
    "oauthidentity": "oauth_identity",
    "consentgrant": "consent_grant",
    "healthrecord": "health_record",
    "healthrecordmedicine": "health_record_medicine",
    "healthrecordattachment": "health_record_attachment",
}

EXPECTED_SNAKE_CASE_INDEXES = {
    "ix_health_record_owner_id",
    "ix_health_record_medicine_record_id",
    "ix_health_record_attachment_record_id",
    "ix_consent_grant_user_id",
    "ix_oauth_identity_user_id",
}


def test_domain_tables_are_snake_case() -> None:
    """Escenario «Catálogo en snake_case»: con la base migrada a la última
    versión, existen las cinco tablas nuevas, no existe ninguna vieja, ningún
    nombre de restricción o índice del esquema public empieza con un prefijo
    viejo (``<viejo>_`` o ``ix_<viejo>_``) y existen los ``ix_`` esperados."""
    with engine.connect() as conn:
        tables = set(
            conn.execute(
                text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
            ).scalars()
        )
        constraints = set(
            conn.execute(
                text(
                    "SELECT conname FROM pg_constraint "
                    "WHERE connamespace = 'public'::regnamespace"
                )
            ).scalars()
        )
        indexes = set(
            conn.execute(
                text("SELECT indexname FROM pg_indexes WHERE schemaname = 'public'")
            ).scalars()
        )

    missing_new = sorted(set(RENAMED_TABLES.values()) - tables)
    assert missing_new == [], missing_new
    remaining_old = sorted(set(RENAMED_TABLES) & tables)
    assert remaining_old == [], remaining_old

    old_prefixes = tuple(
        prefix for old in RENAMED_TABLES for prefix in (f"{old}_", f"ix_{old}_")
    )
    old_constraints = sorted(n for n in constraints if n.startswith(old_prefixes))
    assert old_constraints == [], old_constraints
    old_indexes = sorted(n for n in indexes if n.startswith(old_prefixes))
    assert old_indexes == [], old_indexes

    missing_indexes = sorted(EXPECTED_SNAKE_CASE_INDEXES - indexes)
    assert missing_indexes == [], missing_indexes


@pytest.mark.parametrize(
    ("schema", "field"),
    [
        ("UserCreate", "full_name"),
        ("UserRegister", "full_name"),
        ("UserUpdate", "full_name"),
        ("UserUpdateMe", "full_name"),
        ("ItemCreate", "title"),
        ("ItemCreate", "description"),
        ("ItemUpdate", "title"),
        ("ItemUpdate", "description"),
    ],
)
def test_every_plain_text_input_rejects_nul(schema: str, field: str) -> None:
    """Review F4b: every input schema of the contract rejects a NUL in its
    clear-text fields (a validation error on that field)."""
    model = getattr(models, schema)
    base: dict[str, Any] = {"email": random_email(), "password": "contrasena-larga"}
    if schema.startswith("Item"):
        base = {"title": "Elemento"}
    with pytest.raises(ValidationError) as caught:
        model.model_validate({**base, field: "Texto\u0000"})
    assert [e["loc"] for e in caught.value.errors()] == [(field,)]
