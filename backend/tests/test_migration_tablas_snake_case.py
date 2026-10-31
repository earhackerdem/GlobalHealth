"""Change tablas-snake-case (D25): the rename migration, on an ephemeral DB.

Interface contract (openspec/changes/tablas-snake-case/design.md):
- A new migration with ``down_revision = "26de7399b12f"`` renames
  oauthidentity -> oauth_identity, consentgrant -> consent_grant,
  healthrecord -> health_record, healthrecordmedicine -> health_record_medicine
  and healthrecordattachment -> health_record_attachment (with their
  constraints and indexes); ``downgrade`` does the same in reverse.

Like test_migration_receta_mexicana.py, the test creates its own throwaway
database on the already-running test Postgres, so the shared test DB is never
touched, and drops it in teardown (DROP DATABASE WITH (FORCE)).
"""

import uuid
from collections.abc import Iterator
from datetime import UTC, date, datetime
from pathlib import Path
from typing import Any

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory

from app.core.config import settings

_BACKEND_DIR = Path(__file__).resolve().parents[1]

PREVIOUS_REVISION = "26de7399b12f"

USER_ID = uuid.UUID("00000000-0000-0000-0000-00000000bbbb")
RECORD_ID = uuid.UUID("00000000-0000-0000-0000-000000000011")
MEDICINE_ID = uuid.UUID("00000000-0000-0000-0000-000000000012")
ATTACHMENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000013")
CONSENT_ID = uuid.UUID("00000000-0000-0000-0000-000000000014")
IDENTITY_ID = uuid.UUID("00000000-0000-0000-0000-000000000015")
RECORD_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000021")
MEDICINE_2_ID = uuid.UUID("00000000-0000-0000-0000-000000000022")

NOW = datetime(2026, 10, 31, 12, 0, tzinfo=UTC)

RECORD = {
    "id": RECORD_ID,
    "owner_id": USER_ID,
    "record_type": "prescription",
    "occurred_on": date(2026, 10, 1),
    "title": None,
    "professional": "opaque-professional",
    "notes": "opaque-notes",
    "diagnosis": "opaque-diagnosis",
    "archived": False,
    "confirmation_status": None,
    "created_at": NOW,
    "updated_at": NOW,
}
MEDICINE = {
    "id": MEDICINE_ID,
    "record_id": RECORD_ID,
    "position": 0,
    "name": "opaque-name",
    "dose": "opaque-dose",
    "frequency": "opaque-frequency",
    "route": "opaque-route",
}
ATTACHMENT = {
    "id": ATTACHMENT_ID,
    "record_id": RECORD_ID,
    "filename": "opaque-filename",
    "media_type": "application/pdf",
    "size_bytes": 7,
    "content": b"opaque!",
    "created_at": NOW,
}
CONSENT = {
    "id": CONSENT_ID,
    "user_id": USER_ID,
    "version": "v1",
    "text_sha256": "a" * 64,
    "granted_at": NOW,
    "auth_method": "password",
}
IDENTITY = {
    "id": IDENTITY_ID,
    "user_id": USER_ID,
    "provider": "google",
    "subject": "google-subject-123",
    "email": "snake@example.com",
    "created_at": NOW,
}
RECORD_2 = {**RECORD, "id": RECORD_2_ID, "notes": "opaque-notes-2"}
MEDICINE_2 = {
    **MEDICINE,
    "id": MEDICINE_2_ID,
    "record_id": RECORD_2_ID,
    "name": "opaque-name-2",
}


def _alembic_config() -> Config:
    cfg = Config(str(_BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_DIR / "app" / "alembic"))
    return cfg


def _head_revision() -> str:
    head = ScriptDirectory.from_config(_alembic_config()).get_current_head()
    assert head is not None
    return head


def _with_url(url: str, action: str, revision: str) -> None:
    """Run alembic against the ephemeral DB: env.py reads settings.DATABASE_URL,
    so swap it for the duration of the command and always restore it."""
    original = settings.DATABASE_URL
    settings.DATABASE_URL = url  # type: ignore[assignment]
    try:
        if action == "upgrade":
            command.upgrade(_alembic_config(), revision)
        else:
            command.downgrade(_alembic_config(), revision)
    finally:
        settings.DATABASE_URL = original


@pytest.fixture()
def ephemeral_db_url() -> Iterator[str]:
    """CREATE DATABASE on the test server; DROP it (FORCE) on teardown."""
    base_url = str(settings.DATABASE_URL)
    db_name = f"migration_{uuid.uuid4().hex[:12]}_test"
    admin_engine = sa.create_engine(
        base_url, isolation_level="AUTOCOMMIT", poolclass=sa.pool.NullPool
    )
    with admin_engine.connect() as conn:
        conn.execute(sa.text(f'CREATE DATABASE "{db_name}"'))
    try:
        yield base_url.rsplit("/", 1)[0] + "/" + db_name
    finally:
        with admin_engine.connect() as conn:
            conn.execute(sa.text(f'DROP DATABASE "{db_name}" WITH (FORCE)'))
        admin_engine.dispose()


def _insert(conn: sa.Connection, table: str, row: dict[str, Any]) -> None:
    columns = ", ".join(row)
    params = ", ".join(f":{c}" for c in row)
    conn.execute(sa.text(f"INSERT INTO {table} ({columns}) VALUES ({params})"), row)


def _select(conn: sa.Connection, table: str, row: dict[str, Any]) -> list[dict]:
    columns = ", ".join(row)
    return [
        dict(r)
        for r in conn.execute(
            sa.text(f"SELECT {columns} FROM {table} WHERE id = :id"), {"id": row["id"]}
        ).mappings()
    ]


def _count(conn: sa.Connection, table: str, record_id: uuid.UUID) -> int:
    return int(
        conn.execute(
            sa.text(f"SELECT COUNT(*) FROM {table} WHERE record_id = :rid"),
            {"rid": record_id},
        ).scalar_one()
    )


def _public_tables(conn: sa.Connection) -> set[str]:
    return set(
        conn.execute(
            sa.text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'")
        ).scalars()
    )


def _version(conn: sa.Connection) -> str:
    return str(
        conn.execute(sa.text("SELECT version_num FROM alembic_version")).scalar_one()
    )


def test_rename_keeps_rows_and_cascade_both_ways(ephemeral_db_url: str) -> None:
    """Escenario «Los datos sobreviven a subir y bajar la migración»: un registro
    con medicina y adjunto, un consentimiento y una identidad de Google sembrados
    con los nombres viejos aparecen intactos en las tablas nuevas tras
    ``upgrade head``; borrar el registro arrastra medicina y adjunto; y tras
    ``downgrade`` a 26de7399b12f las filas vuelven bajo los nombres viejos."""
    head = _head_revision()
    assert head != PREVIOUS_REVISION, "no migration after 26de7399b12f yet"

    _with_url(ephemeral_db_url, "upgrade", PREVIOUS_REVISION)

    engine = sa.create_engine(ephemeral_db_url, poolclass=sa.pool.NullPool)
    try:
        # Seed with the OLD names, at the previous revision.
        with engine.begin() as conn:
            conn.execute(
                sa.text(
                    'INSERT INTO "user" (id, email, hashed_password, is_active, '
                    "is_superuser, created_at) VALUES (:id, 'snake@example.com', "
                    "'x', true, false, :now)"
                ),
                {"id": USER_ID, "now": NOW},
            )
            _insert(conn, "healthrecord", RECORD)
            _insert(conn, "healthrecordmedicine", MEDICINE)
            _insert(conn, "healthrecordattachment", ATTACHMENT)
            _insert(conn, "consentgrant", CONSENT)
            _insert(conn, "oauthidentity", IDENTITY)

        _with_url(ephemeral_db_url, "upgrade", "head")

        # Same rows, same values, under the NEW names; old tables gone.
        with engine.connect() as conn:
            assert _version(conn) == head
            tables = _public_tables(conn)
            assert _select(conn, "health_record", RECORD) == [RECORD]
            assert _select(conn, "health_record_medicine", MEDICINE) == [MEDICINE]
            assert _select(conn, "health_record_attachment", ATTACHMENT) == [ATTACHMENT]
            assert _select(conn, "consent_grant", CONSENT) == [CONSENT]
            assert _select(conn, "oauth_identity", IDENTITY) == [IDENTITY]
        old_tables = {
            "healthrecord",
            "healthrecordmedicine",
            "healthrecordattachment",
            "consentgrant",
            "oauthidentity",
        }
        assert tables & old_tables == set()

        # ON DELETE CASCADE still works under the new names.
        with engine.begin() as conn:
            conn.execute(
                sa.text("DELETE FROM health_record WHERE id = :id"), {"id": RECORD_ID}
            )
        with engine.connect() as conn:
            assert _count(conn, "health_record_medicine", RECORD_ID) == 0
            assert _count(conn, "health_record_attachment", RECORD_ID) == 0

        # New rows written under the new names survive the downgrade.
        with engine.begin() as conn:
            _insert(conn, "health_record", RECORD_2)
            _insert(conn, "health_record_medicine", MEDICINE_2)

        _with_url(ephemeral_db_url, "downgrade", PREVIOUS_REVISION)

        with engine.connect() as conn:
            assert _version(conn) == PREVIOUS_REVISION
            tables = _public_tables(conn)
            assert _select(conn, "healthrecord", RECORD_2) == [RECORD_2]
            assert _select(conn, "healthrecordmedicine", MEDICINE_2) == [MEDICINE_2]
            assert _select(conn, "consentgrant", CONSENT) == [CONSENT]
            assert _select(conn, "oauthidentity", IDENTITY) == [IDENTITY]
        new_tables = {
            "health_record",
            "health_record_medicine",
            "health_record_attachment",
            "consent_grant",
            "oauth_identity",
        }
        assert tables & new_tables == set()
        assert old_tables <= tables

        # And it goes up again.
        _with_url(ephemeral_db_url, "upgrade", "head")
        with engine.connect() as conn:
            assert _version(conn) == head
            assert _select(conn, "health_record", RECORD_2) == [RECORD_2]
    finally:
        engine.dispose()
