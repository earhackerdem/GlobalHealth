"""Review C6 (PR #13): the receta-mexicana data migration, on ephemeral DBs.

Each test creates its own throwaway database on the already-running test
Postgres (CREATE DATABASE via an admin connection), migrates it to the
revision BEFORE c91f3b7a52e8, seeds old-format rows, and then:

(a) correct key — ``upgrade head`` folds each old prescription into ONE
    medicine (name = decrypted title, re-encrypted), appends the validity
    window to ``notes`` ("Vigencia migrada: X a Y" / "desde X" / "hasta Y",
    review K1), nulls the title and marks diagnoses ``unconfirmed``;
(b) wrong key — ciphertext sealed with ANOTHER key makes the upgrade RAISE
    (InvalidToken) and roll back whole: nothing is silently destroyed
    (review S2; before the fix the migration swallowed InvalidToken and
    overwrote the data with None, exiting 0).

The ephemeral database is dropped in teardown (DROP DATABASE WITH (FORCE)).
"""

import uuid
from collections.abc import Callable, Iterator
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
import sqlalchemy as sa
from alembic import command
from alembic.config import Config
from cryptography.fernet import Fernet, InvalidToken

from app.core.config import settings
from app.core.encrypted import EncryptedString, decrypt_str

_BACKEND_DIR = Path(__file__).resolve().parents[1]

PREVIOUS_REVISION = "0b7c5e1d94aa"
TARGET_REVISION = "c91f3b7a52e8"

OWNER = uuid.UUID("00000000-0000-0000-0000-00000000aaaa")
RX_FULL = uuid.UUID("00000000-0000-0000-0000-000000000001")  # notes+dose+ambas
RX_FROM_ONLY = uuid.UUID("00000000-0000-0000-0000-000000000002")  # solo inicio
RX_TO_ONLY = uuid.UUID("00000000-0000-0000-0000-000000000003")  # solo fin
RX_BARE = uuid.UUID("00000000-0000-0000-0000-000000000004")  # sin dosis/vigencia
DX = uuid.UUID("00000000-0000-0000-0000-000000000005")


def _alembic_config() -> Config:
    cfg = Config(str(_BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_DIR / "app" / "alembic"))
    return cfg


def _upgrade(url: str, revision: str) -> None:
    """Run alembic against the ephemeral DB: env.py reads settings.DATABASE_URL,
    so swap it for the duration of the command and always restore it."""
    original = settings.DATABASE_URL
    settings.DATABASE_URL = url  # type: ignore[assignment]
    try:
        command.upgrade(_alembic_config(), revision)
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


def _seed_old_format(url: str, encrypt: Callable[[str], str]) -> None:
    """Old-model rows (pre c91f3b7a52e8): title NOT NULL, record-level
    dose/valid_from/valid_to, no medicines table."""
    engine = sa.create_engine(url, poolclass=sa.pool.NullPool)
    now = datetime.now(UTC)
    try:
        with engine.begin() as conn:
            conn.execute(
                sa.text(
                    'INSERT INTO "user" (id, email, hashed_password, is_active, '
                    "is_superuser, created_at) VALUES (:id, 'migra@example.com', "
                    "'x', true, false, :now)"
                ),
                {"id": OWNER, "now": now},
            )

            def rec(
                rid: uuid.UUID,
                rtype: str,
                title: str,
                notes: str | None,
                dose: str | None,
                vfrom: date | None,
                vto: date | None,
            ) -> None:
                conn.execute(
                    sa.text(
                        "INSERT INTO healthrecord (id, owner_id, record_type, "
                        "occurred_on, title, professional, notes, dose, "
                        "valid_from, valid_to, created_at, updated_at) VALUES "
                        "(:id, :owner, :rt, :on, :title, NULL, :notes, :dose, "
                        ":vf, :vt, :now, :now)"
                    ),
                    {
                        "id": rid,
                        "owner": OWNER,
                        "rt": rtype,
                        "on": date(2026, 1, 1),
                        "title": encrypt(title),
                        "notes": encrypt(notes) if notes else None,
                        "dose": encrypt(dose) if dose else None,
                        "vf": vfrom,
                        "vt": vto,
                        "now": now,
                    },
                )

            rec(
                RX_FULL,
                "prescription",
                "Amoxicilina 500",
                "Nota previa importante",
                "500 mg cada 8 h",
                date(2026, 1, 1),
                date(2026, 2, 1),
            )
            rec(
                RX_FROM_ONLY,
                "prescription",
                "Paracetamol",
                None,
                None,
                date(2026, 3, 1),
                None,
            )
            rec(
                RX_TO_ONLY,
                "prescription",
                "Ibuprofeno",
                None,
                None,
                None,
                date(2026, 12, 30),
            )
            rec(RX_BARE, "prescription", "Loratadina", None, None, None, None)
            rec(DX, "diagnosis", "Diagnóstico X", "dx note", None, None, None)
    finally:
        engine.dispose()


def _app_encrypt(value: str) -> str:
    """Ciphertext with the app's OWN data key (EncryptedString)."""
    token = EncryptedString().process_bind_param(value, None)  # type: ignore[arg-type]
    assert token is not None
    return token


def test_migration_folds_old_prescriptions_with_app_key(
    ephemeral_db_url: str,
) -> None:
    """Correct key: 1 medicina por receta vieja, vigencia a notes, dx unconfirmed."""
    _upgrade(ephemeral_db_url, PREVIOUS_REVISION)
    _seed_old_format(ephemeral_db_url, _app_encrypt)

    _upgrade(ephemeral_db_url, TARGET_REVISION)

    engine = sa.create_engine(ephemeral_db_url, poolclass=sa.pool.NullPool)
    try:
        with engine.connect() as conn:
            records = {
                row.id: row
                for row in conn.execute(
                    sa.text(
                        "SELECT id, record_type, title, notes, "
                        "confirmation_status FROM healthrecord"
                    )
                )
            }
            medicines = {
                row.record_id: row
                for row in conn.execute(
                    sa.text(
                        "SELECT record_id, position, name, dose, frequency, "
                        "route FROM healthrecordmedicine"
                    )
                )
            }
            version = conn.execute(
                sa.text("SELECT version_num FROM alembic_version")
            ).scalar_one()
    finally:
        engine.dispose()

    assert version == TARGET_REVISION
    # One medicine per old prescription, none for the diagnosis.
    assert set(medicines) == {RX_FULL, RX_FROM_ONLY, RX_TO_ONLY, RX_BARE}

    # Every prescription: title NULL, medicine name = old title (re-encrypted
    # Fernet token, never plaintext), position 0.
    expected_names = {
        RX_FULL: "Amoxicilina 500",
        RX_FROM_ONLY: "Paracetamol",
        RX_TO_ONLY: "Ibuprofeno",
        RX_BARE: "Loratadina",
    }
    for rid, expected_name in expected_names.items():
        assert records[rid].title is None, rid
        med = medicines[rid]
        assert med.position == 0
        assert str(med.name).startswith("gAAAA"), med.name
        assert decrypt_str(str(med.name)) == expected_name
        assert med.frequency is None and med.route is None

    # Record-level dose folded into the medicine (re-encrypted) or absent.
    assert decrypt_str(str(medicines[RX_FULL].dose)) == "500 mg cada 8 h"
    assert medicines[RX_FROM_ONLY].dose is None

    # Validity window folded into notes, K1 wording per case.
    assert decrypt_str(str(records[RX_FULL].notes)) == (
        "Nota previa importante\nVigencia migrada: 2026-01-01 a 2026-02-01"
    )
    assert decrypt_str(str(records[RX_FROM_ONLY].notes)) == (
        "Vigencia migrada: desde 2026-03-01"
    )
    assert decrypt_str(str(records[RX_TO_ONLY].notes)) == (
        "Vigencia migrada: hasta 2026-12-30"
    )
    assert records[RX_BARE].notes is None

    # Diagnosis: untouched title, confirmation_status backfilled.
    assert decrypt_str(str(records[DX].title)) == "Diagnóstico X"
    assert records[DX].confirmation_status == "unconfirmed"
    for rid in expected_names:
        assert records[rid].confirmation_status is None, rid


def test_migration_wrong_key_aborts_and_rolls_back(ephemeral_db_url: str) -> None:
    """Wrong key: el upgrade LANZA (InvalidToken) y los datos quedan intactos."""
    _upgrade(ephemeral_db_url, PREVIOUS_REVISION)
    other_fernet = Fernet(Fernet.generate_key())
    _seed_old_format(
        ephemeral_db_url, lambda v: other_fernet.encrypt(v.encode()).decode()
    )

    engine = sa.create_engine(ephemeral_db_url, poolclass=sa.pool.NullPool)
    try:
        with engine.connect() as conn:
            before = {
                row.id: row
                for row in conn.execute(
                    sa.text(
                        "SELECT id, title, notes, dose, valid_from, valid_to "
                        "FROM healthrecord"
                    )
                )
            }

        with pytest.raises(InvalidToken):
            _upgrade(ephemeral_db_url, TARGET_REVISION)

        with engine.connect() as conn:
            version = conn.execute(
                sa.text("SELECT version_num FROM alembic_version")
            ).scalar_one()
            after = {
                row.id: row
                for row in conn.execute(
                    sa.text(
                        "SELECT id, title, notes, dose, valid_from, valid_to "
                        "FROM healthrecord"
                    )
                )
            }
            medicines_table = conn.execute(
                sa.text(
                    "SELECT COUNT(*) FROM information_schema.tables "
                    "WHERE table_name = 'healthrecordmedicine'"
                )
            ).scalar_one()
    finally:
        engine.dispose()

    # Whole-transaction rollback: still on the previous revision, the new
    # table never materialized, and every row (ciphertext, dose, validity)
    # is byte-for-byte what was seeded.
    assert version == PREVIOUS_REVISION
    assert medicines_table == 0
    assert after == before
    assert all(row.title is not None for row in after.values())
