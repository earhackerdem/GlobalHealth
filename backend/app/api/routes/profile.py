"""Patient profile, body measurements, family history and onboarding state.

Contract in openspec/changes/onboarding-perfil/design.md §Interface contract:
everything behind ``ConsentedUser``; the profile is created pending on first
read/write (Decision 1: the onboarding state lives on the server); range
validations run BEFORE encrypting and surface as a 422 with a STRING detail
in es-MX (Decision 4); per-owner isolation with the SAME 404 for a
nonexistent family-history id and a foreign one; sensitive values encrypted
at rest by the models (EncryptedString, NFR-001); lists use the template
envelope ``{"data": [...], "count": N}``.

The medical-history event sections (``/profile/history``) follow
openspec/changes/perfil-eventos/design.md §Interface contract with the same
rules: one encrypted JSON per entry, its section included (Decisions 1-2).
"""

import json
import logging
import uuid
from datetime import date, datetime
from typing import Any, Literal, cast
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Query
from pydantic import ConfigDict, TypeAdapter, ValidationError
from sqlmodel import col, func, select

from app.api.deps import ConsentedUser, SessionDep
from app.models import (
    HISTORY_SECTIONS,
    BloodType,
    BodyMeasurement,
    BodyMeasurementCreate,
    BodyMeasurementLatest,
    BodyMeasurementPublic,
    BodyMeasurementsPublic,
    FamilyHistoriesPublic,
    FamilyHistory,
    FamilyHistoryCreate,
    FamilyHistoryPublic,
    HistoryContent,
    HistoryContentModel,
    HistoryEntriesPublic,
    HistoryEntry,
    HistorySection,
    HistorySectionNone,
    MedicalHistoryEntry,
    Message,
    OnboardingClose,
    PatientProfile,
    PatientProfilePublic,
    PatientProfileUpdate,
    get_datetime_utc,
    normalize_relatives,
    validate_birth_date,
    validate_history_content,
    validate_measurement_value,
)

router = APIRouter(prefix="/profile", tags=["profile"])

logger = logging.getLogger(__name__)

MEXICO_CITY = ZoneInfo("America/Mexico_City")
# hide_input_in_errors: a ValidationError must never carry decrypted content
# (it lives on the adapter: the outermost validator's config is the one that
# applies, a model_config on the HistoryEntry schemas does not).
_HISTORY_ENTRY: TypeAdapter[HistoryEntry] = TypeAdapter(
    HistoryEntry, config=ConfigDict(hide_input_in_errors=True)
)


def _get_or_create_profile(
    session: SessionDep, current_user: ConsentedUser
) -> PatientProfile:
    """The 1:1 profile row, created ``pending`` on first access (design.md
    Migration Plan: existing accounts see the onboarding on their next visit)."""
    profile = session.exec(
        select(PatientProfile).where(PatientProfile.user_id == current_user.id)
    ).first()
    if profile is None:
        profile = PatientProfile(user_id=current_user.id)
        session.add(profile)
        session.commit()
        session.refresh(profile)
    return profile


def _latest_measurement(
    session: SessionDep, user_id: uuid.UUID, type_: str
) -> BodyMeasurementLatest | None:
    row = session.exec(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == user_id)
        .where(BodyMeasurement.type == type_)
        .order_by(
            col(BodyMeasurement.measured_on).desc(),
            col(BodyMeasurement.created_at).desc(),
        )
        .limit(1)
    ).first()
    if row is None:
        return None
    return BodyMeasurementLatest(value=float(row.value), measured_on=row.measured_on)


def _profile_public(
    session: SessionDep, current_user: ConsentedUser, profile: PatientProfile
) -> PatientProfilePublic:
    return PatientProfilePublic(
        birth_date=(
            date.fromisoformat(profile.birth_date) if profile.birth_date else None
        ),
        sex=profile.sex,
        allergies=profile.allergies,
        onboarding=profile.onboarding_outcome,
        latest_weight=_latest_measurement(session, current_user.id, "weight"),
        latest_height=_latest_measurement(session, current_user.id, "height"),
        # Only values of the enum get written (PatientProfileUpdate).
        blood_type=cast(BloodType | None, profile.blood_type),
        sections_none=_sections_none(profile),
    )


def _sections_none(profile: PatientProfile) -> list[HistorySection]:
    """The decrypted "ninguna" marks, in the canonical section order."""
    marks = set(json.loads(profile.sections_none)) if profile.sections_none else set()
    return [section for section in HISTORY_SECTIONS if section in marks]


def _store_sections_none(profile: PatientProfile, marks: list[HistorySection]) -> None:
    ordered = [section for section in HISTORY_SECTIONS if section in marks]
    profile.sections_none = json.dumps(ordered) if ordered else None


def _lock_profile(session: SessionDep, current_user: ConsentedUser) -> PatientProfile:
    """The profile re-read FOR UPDATE: "mark ninguna" and "create an entry"
    serialize on it, so neither acts on a stale view of the other (design.md
    Risks: two tabs)."""
    _get_or_create_profile(session, current_user)
    return session.exec(
        select(PatientProfile)
        .where(PatientProfile.user_id == current_user.id)
        .with_for_update()
        .execution_options(populate_existing=True)
    ).one()


def _profile_birth_date(profile: PatientProfile) -> date | None:
    return date.fromisoformat(profile.birth_date) if profile.birth_date else None


def _validate_history(content_in: HistoryContentModel, profile: PatientProfile) -> None:
    """es-MX 422 BEFORE encrypting; "today" is Mexico City's today (G8)."""
    try:
        validate_history_content(
            content_in, _profile_birth_date(profile), datetime.now(MEXICO_CITY).date()
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e


def _history_public(entry: MedicalHistoryEntry) -> HistoryEntry:
    return _HISTORY_ENTRY.validate_python(
        {**json.loads(entry.content), "id": entry.id, "created_at": entry.created_at}
    )


def _owned_history(
    session: SessionDep, current_user: ConsentedUser
) -> list[HistoryEntry]:
    """ONLY the session user's entries, decrypted, by created_at ascending
    (Decision 2: grouping/filtering by section happens here, in memory)."""
    rows = session.exec(
        select(MedicalHistoryEntry)
        .where(MedicalHistoryEntry.user_id == current_user.id)
        .order_by(col(MedicalHistoryEntry.created_at).asc())
    ).all()
    entries: list[HistoryEntry] = []
    for row in rows:
        try:
            entries.append(_history_public(row))
        except json.JSONDecodeError, ValidationError:
            # Unreadable row (review S4): left out of the list, only its id logged.
            logger.warning("Skipped unreadable medical history entry %s", row.id)
    return entries


def _get_owned_history_entry(
    session: SessionDep, current_user: ConsentedUser, id: uuid.UUID
) -> MedicalHistoryEntry:
    """Same 404 (status and body) for a missing entry and a foreign one."""
    entry = session.get(MedicalHistoryEntry, id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Registro no encontrado")
    return entry


def _measurement_public(measurement: BodyMeasurement) -> BodyMeasurementPublic:
    return BodyMeasurementPublic(
        id=measurement.id,
        type=measurement.type,
        value=float(measurement.value),
        measured_on=measurement.measured_on,
    )


def _family_history_public(entry: FamilyHistory) -> FamilyHistoryPublic:
    return FamilyHistoryPublic(
        id=entry.id,
        condition=entry.condition,
        other_text=entry.other_text,
        relatives=json.loads(entry.relatives),
        note=entry.note,
    )


def _get_owned_family_history(
    session: SessionDep, current_user: ConsentedUser, id: uuid.UUID
) -> FamilyHistory:
    """Fetch an entry only if owned by the session user.

    A missing entry and a foreign entry raise the SAME 404 (status and body)
    so the endpoint never reveals whether someone else's entry exists.
    """
    entry = session.get(FamilyHistory, id)
    if not entry or entry.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Antecedente no encontrado")
    return entry


@router.get("", response_model=PatientProfilePublic)
def read_profile(session: SessionDep, current_user: ConsentedUser) -> Any:
    """The session user's profile, with the latest weight/height captures."""
    profile = _get_or_create_profile(session, current_user)
    return _profile_public(session, current_user, profile)


@router.put("", response_model=PatientProfilePublic)
def update_profile(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    profile_in: PatientProfileUpdate,
) -> Any:
    """Partial update: absent = untouched, explicit null clears the field.

    birth_date must fall in [1900-01-01, today]; the check runs HERE (not a
    pydantic validator) so the 422 carries a string es-MX detail, and BEFORE
    anything gets encrypted or persisted.
    """
    update_dict = profile_in.model_dump(exclude_unset=True)
    birth_date = update_dict.get("birth_date")
    if birth_date is not None:
        try:
            validate_birth_date(birth_date)
        except ValueError as e:
            raise HTTPException(status_code=422, detail=str(e)) from e
        update_dict["birth_date"] = birth_date.isoformat()
    profile = _get_or_create_profile(session, current_user)
    profile.sqlmodel_update(update_dict)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return _profile_public(session, current_user, profile)


@router.post("/onboarding", response_model=PatientProfilePublic)
def close_onboarding(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    close_in: OnboardingClose,
) -> Any:
    """Close the onboarding exactly once (completed|skipped); a second close
    is a 409 and the recorded outcome does not change (Decision 5)."""
    profile = _get_or_create_profile(session, current_user)
    if profile.onboarding_outcome != "pending":
        raise HTTPException(status_code=409, detail="El onboarding ya fue cerrado")
    profile.onboarding_outcome = close_in.outcome
    profile.onboarding_closed_at = get_datetime_utc()
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return _profile_public(session, current_user, profile)


@router.post("/measurements", response_model=BodyMeasurementPublic, status_code=201)
def create_measurement(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    measurement_in: BodyMeasurementCreate,
) -> Any:
    """Persist a new capture (never an UPDATE of a previous one); measured_on
    is set by the SERVER to today. Implausible values get an es-MX 422."""
    try:
        validate_measurement_value(measurement_in.type, measurement_in.value)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    measurement = BodyMeasurement(
        user_id=current_user.id,
        type=measurement_in.type,
        value=str(measurement_in.value),
        # Single-market es-MX product: "today" is Mexico City's today, not the
        # server's UTC date (review G8).
        measured_on=datetime.now(MEXICO_CITY).date(),
    )
    session.add(measurement)
    session.commit()
    session.refresh(measurement)
    return _measurement_public(measurement)


@router.get("/measurements", response_model=BodyMeasurementsPublic)
def read_measurements(
    session: SessionDep,
    current_user: ConsentedUser,
    type: Literal["weight", "height"],
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """ONLY the session user's captures of one type, newest first (same-day
    ties broken by capture time)."""
    count = session.exec(
        select(func.count())
        .select_from(BodyMeasurement)
        .where(BodyMeasurement.user_id == current_user.id)
        .where(BodyMeasurement.type == type)
    ).one()
    rows = session.exec(
        select(BodyMeasurement)
        .where(BodyMeasurement.user_id == current_user.id)
        .where(BodyMeasurement.type == type)
        .order_by(
            col(BodyMeasurement.measured_on).desc(),
            col(BodyMeasurement.created_at).desc(),
        )
        .offset(skip)
        .limit(limit)
    ).all()
    return BodyMeasurementsPublic(
        data=[_measurement_public(row) for row in rows], count=count
    )


@router.post("/family-history", response_model=FamilyHistoryPublic, status_code=201)
def create_family_history(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    entry_in: FamilyHistoryCreate,
) -> Any:
    """Persist one family antecedent; relatives travel as a JSON array
    serialized INSIDE the encrypted column (design.md trade-off), bounded and
    deduped (review G11/M5).

    condition is encrypted at rest (review G2), so per-user uniqueness cannot
    be a partial index (Fernet is non-deterministic): dedupe happens HERE by
    comparing the decrypted conditions the ORM already returns (review G3).
    "other" admits several entries, told apart by other_text.
    """
    try:
        relatives = normalize_relatives(entry_in.relatives)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    if entry_in.condition != "other":
        existing_conditions = session.exec(
            select(FamilyHistory.condition).where(
                FamilyHistory.user_id == current_user.id
            )
        ).all()
        if entry_in.condition in existing_conditions:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Ya tienes un antecedente de esa condición; edítalo en "
                    "lugar de crearlo"
                ),
            )
    entry = FamilyHistory(
        user_id=current_user.id,
        condition=entry_in.condition,
        other_text=entry_in.other_text,
        relatives=json.dumps(relatives),
        note=entry_in.note,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _family_history_public(entry)


@router.get("/family-history", response_model=FamilyHistoriesPublic)
def read_family_history(
    session: SessionDep,
    current_user: ConsentedUser,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
) -> Any:
    """ONLY the session user's antecedents, in capture order."""
    count = session.exec(
        select(func.count())
        .select_from(FamilyHistory)
        .where(FamilyHistory.user_id == current_user.id)
    ).one()
    rows = session.exec(
        select(FamilyHistory)
        .where(FamilyHistory.user_id == current_user.id)
        .order_by(col(FamilyHistory.created_at).asc())
        .offset(skip)
        .limit(limit)
    ).all()
    return FamilyHistoriesPublic(
        data=[_family_history_public(row) for row in rows], count=count
    )


@router.put("/family-history/{id}", response_model=FamilyHistoryPublic)
def update_family_history(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    entry_in: FamilyHistoryCreate,
) -> Any:
    """Full update of an owned antecedent (same fields as the create);
    relatives bounded and deduped like on create (review G11/M5)."""
    try:
        relatives = normalize_relatives(entry_in.relatives)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e
    entry = _get_owned_family_history(session, current_user, id)
    # Renaming into an already-used condition would create the duplicate the
    # POST dedupe forbids (review G3) — same rule, same door.
    if entry_in.condition != "other" and entry_in.condition != entry.condition:
        existing_conditions = session.exec(
            select(FamilyHistory.condition).where(
                FamilyHistory.user_id == current_user.id,
                col(FamilyHistory.id) != entry.id,
            )
        ).all()
        if entry_in.condition in existing_conditions:
            raise HTTPException(
                status_code=409,
                detail=(
                    "Ya tienes un antecedente de esa condición; edítalo en "
                    "lugar de crearlo"
                ),
            )
    entry.condition = entry_in.condition
    entry.other_text = entry_in.other_text
    entry.relatives = json.dumps(relatives)
    entry.note = entry_in.note
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _family_history_public(entry)


@router.delete("/family-history/{id}")
def delete_family_history(
    session: SessionDep, current_user: ConsentedUser, id: uuid.UUID
) -> Message:
    """Delete an owned antecedent (removing a condition removes its
    relatives line with it: they live in the same row)."""
    entry = _get_owned_family_history(session, current_user, id)
    session.delete(entry)
    session.commit()
    return Message(message="Antecedente eliminado")


# --- Medical history event sections (perfil-eventos design.md) --------------


@router.get("/history", response_model=HistoryEntriesPublic)
def read_history(session: SessionDep, current_user: ConsentedUser) -> Any:
    """ONLY the session user's entries of every section, oldest first."""
    entries = _owned_history(session, current_user)
    return HistoryEntriesPublic(data=entries, count=len(entries))


@router.post("/history", response_model=HistoryEntry, status_code=201)
def create_history_entry(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    entry_in: HistoryContent,
) -> Any:
    """Persist one entry (its section travels inside the encrypted JSON) and,
    in the SAME transaction, drop that section from the "ninguna" marks
    (Decision 3). No dedupe (Decision 6)."""
    profile = _lock_profile(session, current_user)
    _validate_history(entry_in, profile)
    _store_sections_none(
        profile,
        [s for s in _sections_none(profile) if s != entry_in.section],
    )
    entry = MedicalHistoryEntry(
        user_id=current_user.id, content=json.dumps(entry_in.model_dump(mode="json"))
    )
    session.add(profile)
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _history_public(entry)


@router.put("/history/{id}", response_model=HistoryEntry)
def update_history_entry(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    id: uuid.UUID,
    entry_in: HistoryContent,
) -> Any:
    """Full update of an owned entry; its section cannot change (422)."""
    profile = _get_or_create_profile(session, current_user)
    _validate_history(entry_in, profile)
    entry = _get_owned_history_entry(session, current_user, id)
    if json.loads(entry.content)["section"] != entry_in.section:
        raise HTTPException(
            status_code=422, detail="No se puede cambiar la sección de un registro"
        )
    entry.content = json.dumps(entry_in.model_dump(mode="json"))
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return _history_public(entry)


@router.delete("/history/{id}")
def delete_history_entry(
    session: SessionDep, current_user: ConsentedUser, id: uuid.UUID
) -> Message:
    """Delete an owned entry (same 404 for missing and foreign)."""
    entry = _get_owned_history_entry(session, current_user, id)
    session.delete(entry)
    session.commit()
    return Message(message="Registro eliminado")


@router.put("/history/sections/{section}/none", response_model=PatientProfilePublic)
def set_history_section_none(
    *,
    session: SessionDep,
    current_user: ConsentedUser,
    section: HistorySection,
    none_in: HistorySectionNone,
) -> Any:
    """Mark (or unmark) a section as "ninguna". Marking a section that has
    entries is a 409 and the marks do not change (Decision 3)."""
    profile = _lock_profile(session, current_user)
    marks = [s for s in _sections_none(profile) if s != section]
    if none_in.none:
        if any(e.section == section for e in _owned_history(session, current_user)):
            raise HTTPException(
                status_code=409,
                detail="No puedes marcar «ninguna» si la sección tiene registros",
            )
        marks.append(section)
    _store_sections_none(profile, marks)
    session.add(profile)
    session.commit()
    session.refresh(profile)
    return _profile_public(session, current_user, profile)
