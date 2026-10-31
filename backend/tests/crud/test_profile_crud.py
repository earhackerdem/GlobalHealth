"""crud helpers of the patient profile (change bd-candados-indices-y-log).

Interface contract (design.md, "## Interface contract"):
- `crud.unlink_diagnosis(*, session, owner_id, diagnosis_id)`: an unreadable
  row is logged with `logger.warning("Skipped unreadable medical history entry
  %s", row.id)` (the same text as the history list) and skipped.
"""

import logging
import uuid

import pytest
from sqlmodel import Session

from app import crud
from app.models import MedicalHistoryEntry
from tests.utils.user import create_random_user

UNREADABLE_CONTENT = "no-es-json"


def test_unlink_diagnosis_logs_unreadable_row(
    db: Session, caplog: pytest.LogCaptureFixture
) -> None:
    """(R2) Fila ilegible registrada: una entrada del historial cuyo contenido
    descifrado no es JSON; unlink_diagnosis la salta y deja un WARNING con su
    id (nunca el contenido)."""
    user = create_random_user(db)
    bad = MedicalHistoryEntry(user_id=user.id, content=UNREADABLE_CONTENT)
    db.add(bad)
    db.commit()
    db.refresh(bad)
    bad_id = str(bad.id)
    owner_id = user.id

    with caplog.at_level(logging.WARNING):
        crud.unlink_diagnosis(session=db, owner_id=owner_id, diagnosis_id=uuid.uuid4())
    db.rollback()

    warnings = [r for r in caplog.records if r.levelno == logging.WARNING]
    assert any(bad_id in r.getMessage() for r in warnings), caplog.text
    assert UNREADABLE_CONTENT not in caplog.text
