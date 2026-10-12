"""Tests for the test-database guard at the top of backend/tests/conftest.py.

The CHILD pytest processes spawned here touch zero real services: each case
runs in ``--collect-only`` mode, so the import-time guard fires but no
fixture, HTTP call or database connection ever runs in the child. This file
itself, running inside the suite, uses the session fixtures from conftest
like every other backend test (they migrate and connect to db-test). The
guard must resolve ``TEST_DATABASE_URL`` (empty string counts as explicitly
disabled: no fallback), abort the whole session via ``pytest.exit`` with a
nonzero returncode when the value is missing or when the database name does
not end in ``_test``, and otherwise export ``DATABASE_URL`` so the suite
targets the test database.
"""

import os
import subprocess
import sys
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[2]


def run_child_pytest(test_db_url: str | None) -> subprocess.CompletedProcess:
    """Run a child pytest in collect-only mode with the given TEST_DATABASE_URL.

    ``None`` means the variable is NOT defined in the child's environment
    (the guard then falls back to the repo-root .env).
    """
    env = os.environ.copy()
    # The parent's pytest knobs must not leak into the child run.
    env.pop("PYTEST_ADDOPTS", None)
    env.pop("PYTEST_PLUGINS", None)
    if test_db_url is None:
        env.pop("TEST_DATABASE_URL", None)
    else:
        env["TEST_DATABASE_URL"] = test_db_url
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "--collect-only",
            "-q",
            "-p",
            "no:cacheprovider",
            "tests/core/test_encrypted.py",
        ],
        cwd=BACKEND_DIR,
        env=env,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )


def test_ac1_missing_test_database_url_aborts_before_any_test() -> None:
    """AC1: no test-DB configuration -> abort naming the variable and the fix."""
    result = run_child_pytest("")

    output = result.stdout + result.stderr
    assert result.returncode != 0, output
    assert "TEST_DATABASE_URL no está definida" in output
    assert "docker compose up -d --wait db-test" in output
    # No test was collected/executed: the abort happens before collection
    # (the abort prints no collection line at all; a successful run prints
    # "N tests collected").
    assert "collected" not in output


def test_ac2_non_test_database_name_aborts() -> None:
    """AC2: URL pointing at the dev database 'app' -> abort, not a test DB."""
    result = run_child_pytest("postgresql://postgres:changethis@localhost:5432/app")

    output = result.stdout + result.stderr
    assert result.returncode != 0, output
    assert "no es una base de prueba" in output


def test_ac3_valid_test_database_url_lets_the_session_proceed() -> None:
    """AC3: database name ends in '_test' -> the session proceeds normally."""
    result = run_child_pytest(
        "postgresql://postgres:changethis@localhost:5433/app_test"
    )

    assert result.returncode == 0, result.stdout + result.stderr


def test_fallback_to_root_dotenv_when_unset() -> None:
    """TEST_DATABASE_URL not defined at all -> the guard falls back to the
    repo-root .env, which defines a valid URL; the session proceeds. This is
    exactly the CI path. Depends on the repo-root .env being present (dev and
    CI both have it)."""
    result = run_child_pytest(None)

    assert result.returncode == 0, result.stdout + result.stderr
