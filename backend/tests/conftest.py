"""Session bootstrap: the suite ONLY runs against the dedicated test database.

Before any app.* import, resolve TEST_DATABASE_URL (process env first — an
empty value counts as unset — then the repo-root .env), refuse to start when
it is missing or when the database name does not end in _test, and export it
as DATABASE_URL so every app module (settings, engine, in-process alembic)
targets the ephemeral db-test container instead of the development database.
"""

import os
import urllib.parse
from collections.abc import Generator
from pathlib import Path

import pytest
from dotenv import dotenv_values

_BACKEND_DIR = Path(__file__).resolve().parents[1]
_REPO_ROOT = _BACKEND_DIR.parent


def _db_name_from_url(url: str) -> str:
    return url.rsplit("/", 1)[-1].split("?", 1)[0]


def _resolve_test_database_url() -> str:
    # Explicitly-empty means "disabled": no fallback, the guard aborts.
    # Only a truly UNSET variable falls back to the repo-root .env.
    if "TEST_DATABASE_URL" in os.environ:
        return os.environ["TEST_DATABASE_URL"]
    return dotenv_values(_REPO_ROOT / ".env").get("TEST_DATABASE_URL") or ""


_test_db_url = _resolve_test_database_url()
if not _test_db_url:
    pytest.exit(
        "TEST_DATABASE_URL no está definida (ni en el entorno ni en el .env raíz). "
        "Defínela (ver .env.example) y levanta la BD de prueba: "
        "docker compose up -d --wait db-test",
        returncode=3,
    )
_db_name = _db_name_from_url(_test_db_url)
if not _db_name.endswith("_test"):
    pytest.exit(
        f"La base configurada en TEST_DATABASE_URL ('{_db_name}') no es una base "
        "de prueba (el nombre debe terminar en _test); me niego a correr la "
        "suite contra ella.",
        returncode=3,
    )
# Shape check BEFORE the export: a malformed URL must never reach pydantic's
# ValidationError, which echoes the raw value (password included). Name only
# the problem, never the value.
try:
    _split = urllib.parse.urlsplit(_test_db_url)
    _url_shape_ok = _split.scheme.startswith("postgres") and bool(_split.hostname)
except ValueError:
    _url_shape_ok = False
if not _url_shape_ok:
    pytest.exit(
        "TEST_DATABASE_URL está malformada: no es una URL postgres con hostname. "
        "No imprimo su valor (puede incluir credenciales); revísala contra "
        ".env.example.",
        returncode=3,
    )
os.environ["DATABASE_URL"] = _test_db_url

from fastapi.testclient import TestClient  # noqa: E402
from sqlmodel import Session, delete  # noqa: E402

from app.core.config import settings  # noqa: E402
from app.core.db import engine, init_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models import Item, User  # noqa: E402
from tests.utils.user import authentication_token_from_email  # noqa: E402
from tests.utils.utils import get_superuser_token_headers  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _migrated_test_db() -> None:
    """The test database is ephemeral (tmpfs): bring its schema to head."""
    from alembic import command
    from alembic.config import Config
    from sqlalchemy.exc import OperationalError

    from app.core.config import settings as _settings

    # Belt and braces: if any module imported app.* before the guard above ran,
    # settings froze on the development URL and migrating would hit the dev DB.
    _effective_db = _db_name_from_url(str(_settings.DATABASE_URL))
    assert _effective_db.endswith("_test"), (
        "settings.DATABASE_URL does not point at a *_test database; "
        "app was imported before the conftest guard"
    )

    cfg = Config(str(_BACKEND_DIR / "alembic.ini"))
    cfg.set_main_option("script_location", str(_BACKEND_DIR / "app" / "alembic"))
    try:
        command.upgrade(cfg, "head")
    except OperationalError:
        pytest.exit(
            "No se pudo conectar a la BD de prueba. Levántala con: "
            "docker compose up -d --wait db-test",
            returncode=3,
        )


@pytest.fixture(scope="session", autouse=True)
def db(_migrated_test_db: None) -> Generator[Session]:
    with Session(engine) as session:
        init_db(session)
        yield session
        statement = delete(Item)
        session.execute(statement)
        statement = delete(User)
        session.execute(statement)
        session.commit()


@pytest.fixture(scope="module")
def client() -> Generator[TestClient]:
    with TestClient(app) as c:
        yield c


@pytest.fixture(scope="module")
def superuser_token_headers(client: TestClient) -> dict[str, str]:
    return get_superuser_token_headers(client)


@pytest.fixture(scope="module")
def normal_user_token_headers(client: TestClient, db: Session) -> dict[str, str]:
    return authentication_token_from_email(
        client=client, email=settings.EMAIL_TEST_USER, db=db
    )
