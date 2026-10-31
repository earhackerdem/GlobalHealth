"""Database-level guarantees (change bd-candados-indices-y-log).

Interface contract (design.md, "## Interface contract"):
- `app.core.db.engine` is created with `hide_parameters=True`: the `str()` of a
  `DBAPIError` raised by a query with a bound parameter does not carry the value.
- Every foreign key has an index whose first column is the key's column (new
  migration `<rev>_index_foreign_keys.py`, down_revision "3b8e5f2a9c61").
"""

from typing import Any

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from app.core.db import engine

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
