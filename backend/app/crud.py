import json
import logging
import uuid
from typing import Any

from sqlmodel import Session, select

from app.core.security import get_password_hash, verify_password
from app.models import (
    HealthRecord,
    Item,
    ItemCreate,
    MedicalHistoryEntry,
    PatientProfile,
    User,
    UserCreate,
    UserUpdate,
)

logger = logging.getLogger(__name__)


def create_user(*, session: Session, user_create: UserCreate) -> User:
    db_obj = User.model_validate(
        user_create, update={"hashed_password": get_password_hash(user_create.password)}
    )
    session.add(db_obj)
    session.commit()
    session.refresh(db_obj)
    return db_obj


def update_user(*, session: Session, db_user: User, user_in: UserUpdate) -> Any:
    user_data = user_in.model_dump(exclude_unset=True)
    extra_data = {}
    if "password" in user_data:
        password = user_data["password"]
        hashed_password = get_password_hash(password)
        extra_data["hashed_password"] = hashed_password
    db_user.sqlmodel_update(user_data, update=extra_data)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user


def get_user_by_email(*, session: Session, email: str) -> User | None:
    if "\x00" in email:
        # Postgres rejects a NUL in varchar (a 500): no such user, without
        # querying, for every caller (login, password recovery; review M-1)
        return None
    statement = select(User).where(User.email == email)
    session_user = session.exec(statement).first()
    return session_user


# Dummy hash to use for timing attack prevention when user is not found
# This is an Argon2 hash of a random password, used to ensure constant-time comparison
DUMMY_HASH = "$argon2id$v=19$m=65536,t=3,p=4$MjQyZWE1MzBjYjJlZTI0Yw$YTU4NGM5ZTZmYjE2NzZlZjY0ZWY3ZGRkY2U2OWFjNjk"


def authenticate(*, session: Session, email: str, password: str) -> User | None:
    db_user = get_user_by_email(session=session, email=email)
    if not db_user or not db_user.hashed_password:
        # Prevent timing attacks by running password verification even when the
        # user doesn't exist or has no local password (e.g. Google-only account)
        verify_password(password, DUMMY_HASH)
        return None
    verified, updated_password_hash = verify_password(password, db_user.hashed_password)
    if not verified:
        return None
    if updated_password_hash:
        db_user.hashed_password = updated_password_hash
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
    return db_user


def create_item(*, session: Session, item_in: ItemCreate, owner_id: uuid.UUID) -> Item:
    db_item = Item.model_validate(item_in, update={"owner_id": owner_id})
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


def lock_profile(*, session: Session, owner_id: uuid.UUID) -> PatientProfile | None:
    """The owner's profile re-read FOR UPDATE, or None if there is none (it is
    NOT created here). Every write that reads or changes the history or the
    "ninguna" marks takes it first, so they serialize per owner (perfil-cronicas
    review R1). Held until the caller's commit or rollback."""
    return session.exec(
        select(PatientProfile)
        .where(PatientProfile.user_id == owner_id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).first()


def lock_diagnosis(
    *, session: Session, owner_id: uuid.UUID, diagnosis_id: uuid.UUID
) -> HealthRecord | None:
    """The owner's diagnosis re-read FOR UPDATE, or None. The DELETE of a
    diagnosis takes it after lock_profile, and a chronic save reads it FOR SHARE
    (same order), so a link is never written to a diagnosis being deleted
    (bd-candados Decision 3). Held until the caller's commit or rollback."""
    return session.exec(
        select(HealthRecord)
        .where(
            HealthRecord.id == diagnosis_id,
            HealthRecord.owner_id == owner_id,
            HealthRecord.record_type == "diagnosis",
        )
        .with_for_update()
        .execution_options(populate_existing=True)
    ).first()


def unlink_diagnosis(
    *, session: Session, owner_id: uuid.UUID, diagnosis_id: uuid.UUID
) -> int:
    """Drop `diagnosis_id` from the owner's chronic entries that point to it and
    return how many changed (perfil-cronicas Decision 3). The link lives in the
    encrypted JSON, so the owner's rows are decrypted here, in memory. Does NOT
    commit: the caller deletes the diagnosis in the same transaction."""
    rows = session.exec(
        select(MedicalHistoryEntry).where(MedicalHistoryEntry.user_id == owner_id)
    ).all()
    changed = 0
    for row in rows:
        try:
            content = json.loads(row.content)
        except json.JSONDecodeError:
            # Unreadable row: left as is and only its id logged; the history
            # list leaves it out with the same warning.
            logger.warning("Skipped unreadable medical history entry %s", row.id)
            continue
        if (
            isinstance(content, dict)
            and content.get("section") == "chronic"
            and content.get("diagnosis_id") == str(diagnosis_id)
        ):
            content["diagnosis_id"] = None
            row.content = json.dumps(content)
            session.add(row)
            changed += 1
    return changed
