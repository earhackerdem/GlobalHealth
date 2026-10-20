import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal

from pydantic import Discriminator, EmailStr
from sqlalchemy import Column
from sqlmodel import Field, Relationship, SQLModel

from app.core.encrypted import EncryptedBytes, EncryptedString


def get_datetime_utc() -> datetime:
    return datetime.now(UTC)


# Shared properties
class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True, max_length=255)
    is_active: bool = True
    is_superuser: bool = False
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation
class UserCreate(UserBase):
    password: str = Field(min_length=8, max_length=128)


class UserRegister(SQLModel):
    email: EmailStr = Field(max_length=255)
    password: str = Field(min_length=8, max_length=128)
    full_name: str | None = Field(default=None, max_length=255)


# Properties to receive via API on update, all are optional
class UserUpdate(SQLModel):
    email: EmailStr | None = Field(default=None, max_length=255)
    is_active: bool | None = None
    is_superuser: bool | None = None
    full_name: str | None = Field(default=None, max_length=255)
    password: str | None = Field(default=None, min_length=8, max_length=128)


class UserUpdateMe(SQLModel):
    full_name: str | None = Field(default=None, max_length=255)
    email: EmailStr | None = Field(default=None, max_length=255)


class UpdatePassword(SQLModel):
    current_password: str = Field(min_length=8, max_length=128)
    new_password: str = Field(min_length=8, max_length=128)


# Database model, database table inferred from class name
class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Nullable: accounts created via Google OIDC have no local password
    hashed_password: str | None = Field(default=None)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    items: list[Item] = Relationship(back_populates="owner", cascade_delete=True)


# OAuth identity linked to a user (e.g. Google); subject is encrypted at rest
class OAuthIdentity(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    provider: str = Field(max_length=32)
    subject: str = Field(sa_column=Column(EncryptedString(), nullable=False))
    email: EmailStr = Field(max_length=255)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)


# Express consent kept as data, not as a flag: one row per grant with the
# version and the sha256 of the exact text accepted (NFR-004, design.md)
class ConsentGrant(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    version: str = Field(max_length=32)
    text_sha256: str = Field(max_length=64)
    granted_at: datetime = Field(default_factory=get_datetime_utc)
    auth_method: str = Field(max_length=32)  # "password" | "google"


# Properties to receive via API when granting consent
class ConsentCreate(SQLModel):
    version: str = Field(max_length=32)


# Properties to return via API after granting consent
class ConsentGrantPublic(SQLModel):
    version: str
    granted_at: datetime
    auth_method: str


# Properties to return via API when the owner queries the current consent
class ConsentStatusPublic(SQLModel):
    version: str
    granted_at: datetime


# Clinical record (diagnosis or prescription). Encryption rule (NFR-001,
# expediente-registros design.md): all clinical text encrypted at rest;
# only type, dates and ids stay in the clear (ordering and FR-025 need them).
# receta-mexicana design.md: a prescription carries medicines[] 1..N (child
# table) and no title/dose/validity at record level; `archived` and
# `confirmation_status` are flow metadata and stay in the clear (Decision 3,
# same trade-off as record_type).
class HealthRecord(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    record_type: str = Field(max_length=32)  # "diagnosis" | "prescription"
    occurred_on: date
    # Nullable: only a diagnosis carries a title (prescriptions carry medicines)
    title: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    professional: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    diagnosis: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    notes: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    archived: bool = Field(default=False, sa_column_kwargs={"server_default": "false"})
    # "unconfirmed" for a diagnosis, None for a prescription; informational
    # only — no API operation flips it (receta-mexicana design.md).
    confirmation_status: str | None = Field(default=None, max_length=32)
    created_at: datetime = Field(default_factory=get_datetime_utc)
    updated_at: datetime = Field(default_factory=get_datetime_utc)
    medicines: list[HealthRecordMedicine] = Relationship(
        back_populates="record",
        cascade_delete=True,
        sa_relationship_kwargs={"order_by": "HealthRecordMedicine.position"},
    )


# One medicine of a prescription (receta-mexicana design.md, Decision 1):
# child table, not JSON — per-field encryption with EncryptedString and a
# clean CASCADE; `position` preserves the capture order.
class HealthRecordMedicine(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    # Optional in Python (the relationship assigns it on flush), NOT NULL
    # in the database.
    record_id: uuid.UUID | None = Field(
        default=None, foreign_key="healthrecord.id", nullable=False, ondelete="CASCADE"
    )
    position: int
    name: str = Field(sa_column=Column(EncryptedString(), nullable=False))
    dose: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    frequency: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    route: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    record: HealthRecord | None = Relationship(back_populates="medicines")


# Record-level fields of the RETIRED model (pre receta-mexicana). They stay
# on the input schemas only so a legacy payload gets a NAMED es-MX 422
# instead of being silently ignored.
LEGACY_HEALTH_RECORD_FIELDS = ("dose", "valid_from", "valid_to")


def reject_legacy_health_record_fields(
    dose: str | None, valid_from: date | None, valid_to: date | None
) -> None:
    """Raise es-MX ValueError when the retired record-level fields appear."""
    values = {"dose": dose, "valid_from": valid_from, "valid_to": valid_to}
    present = [f for f, v in values.items() if v is not None]
    if present:
        raise ValueError(
            "El registro ya no lleva dosis ni vigencia a nivel de receta "
            "(campos retirados: " + ", ".join(present) + "); captura cada "
            "medicina en la lista medicines"
        )


# Columns that are NOT NULL in the database but optional in the update
# schema (absent = "do not touch"). An EXPLICIT null must be rejected here
# with a 422: it would otherwise reach the database and surface as a 500
# (NotNullViolation) — review finding S3. The RETIRED fields with null stay
# as they are (documented leniency, Saúl's call on the same review).
NON_NULLABLE_UPDATE_FIELDS = ("occurred_on", "archived")


def reject_null_update_fields(update_dict: dict[str, Any]) -> None:
    """Raise es-MX ValueError when a non-nullable field arrives as explicit null."""
    present = [
        field
        for field in NON_NULLABLE_UPDATE_FIELDS
        if field in update_dict and update_dict[field] is None
    ]
    if present:
        raise ValueError(
            "No se admite null en " + ", ".join(present) + "; envía un "
            "valor o no incluyas el campo"
        )


# Upper bound of medicines per prescription (review finding S1: without a
# cap, a 20,000-medicine payload got a 201). Enforced in the shared
# validator, not with pydantic max_length, so the 422 detail stays a STRING
# in es-MX like every other message here.
MAX_MEDICINES_PER_PRESCRIPTION = 20


# Discriminated validation shared by the Create handler and the PATCH
# handler (which validates the RESULTANT state after a partial update):
# a diagnosis requires a title and admits neither medicines nor the
# `diagnosis` field; a prescription requires 1..N medicines (each with a
# non-empty name) and admits no title. Raises ValueError with the es-MX
# message; the routes surface it as an HTTP 422 with a string detail.
def validate_health_record_fields_by_type(
    record_type: str,
    title: str | None,
    diagnosis: str | None,
    medicine_names: list[str],
) -> None:
    if record_type == "diagnosis":
        if not title:
            raise ValueError("Un diagnóstico requiere un título")
        if medicine_names:
            raise ValueError("Un diagnóstico no admite medicinas")
        if diagnosis is not None:
            raise ValueError(
                "Un diagnóstico no admite el campo diagnosis; usa el título"
            )
    else:
        if title is not None:
            raise ValueError("Una receta no admite título; captura sus medicinas")
        if not medicine_names:
            raise ValueError("Una receta requiere al menos una medicina")
        if len(medicine_names) > MAX_MEDICINES_PER_PRESCRIPTION:
            raise ValueError(
                "Una receta admite como máximo "
                f"{MAX_MEDICINES_PER_PRESCRIPTION} medicinas"
            )
        if any(not name.strip() for name in medicine_names):
            raise ValueError("Cada medicina requiere un nombre")


# One medicine as received on create or on a PATCH replacement.
class HealthRecordMedicineCreate(SQLModel):
    name: str = Field(max_length=255)
    dose: str | None = Field(default=None, max_length=255)
    frequency: str | None = Field(default=None, max_length=255)
    route: str | None = Field(default=None, max_length=255)


# Properties to receive via API on creation, discriminated by record_type:
# a diagnosis carries title and no medicines; a prescription carries
# medicines 1..N and no title. The discriminated check lives in the route
# (not a model_validator) so the 422 detail is a STRING in es-MX.
class HealthRecordCreate(SQLModel):
    record_type: Literal["diagnosis", "prescription"]
    title: str | None = Field(default=None, max_length=255)
    occurred_on: date
    professional: str | None = Field(default=None, max_length=255)
    diagnosis: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)
    medicines: list[HealthRecordMedicineCreate] = []
    # Retired model, accepted only to be rejected by name (es-MX 422).
    dose: str | None = Field(default=None, max_length=255)
    valid_from: date | None = None
    valid_to: date | None = None


# Properties to receive via API on update, all optional; record_type is
# immutable and therefore absent here. `medicines` present = FULL
# replacement of the list; `archived` archives/unarchives.
class HealthRecordUpdate(SQLModel):
    title: str | None = Field(default=None, max_length=255)
    occurred_on: date | None = None
    professional: str | None = Field(default=None, max_length=255)
    diagnosis: str | None = Field(default=None, max_length=2000)
    notes: str | None = Field(default=None, max_length=2000)
    archived: bool | None = None
    medicines: list[HealthRecordMedicineCreate] | None = None
    # Retired model, accepted only to be rejected by name (es-MX 422).
    dose: str | None = Field(default=None, max_length=255)
    valid_from: date | None = None
    valid_to: date | None = None


class HealthRecordMedicinePublic(SQLModel):
    id: uuid.UUID
    name: str
    dose: str | None
    frequency: str | None
    route: str | None


class HealthRecordPublic(SQLModel):
    id: uuid.UUID
    record_type: str
    occurred_on: date
    title: str | None
    professional: str | None
    diagnosis: str | None
    notes: str | None
    archived: bool
    confirmation_status: str | None
    medicines: list[HealthRecordMedicinePublic]
    owner_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class HealthRecordsPublic(SQLModel):
    data: list[HealthRecordPublic]
    count: int


# Attachment of a clinical record (expediente-registros design.md §Interface
# contract, ADR D16): filename and content encrypted at rest; media_type and
# size_bytes (of the original, pre-encryption) stay in the clear.
class HealthRecordAttachment(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    record_id: uuid.UUID = Field(
        foreign_key="healthrecord.id", nullable=False, ondelete="CASCADE"
    )
    filename: str = Field(sa_column=Column(EncryptedString(), nullable=False))
    media_type: str = Field(max_length=64)
    size_bytes: int
    content: bytes = Field(sa_column=Column(EncryptedBytes(), nullable=False))
    created_at: datetime = Field(default_factory=get_datetime_utc)


# Properties to return via API: metadata only, never the content itself.
class HealthRecordAttachmentPublic(SQLModel):
    id: uuid.UUID
    record_id: uuid.UUID
    filename: str
    media_type: str
    size_bytes: int
    created_at: datetime


class HealthRecordAttachmentsPublic(SQLModel):
    data: list[HealthRecordAttachmentPublic]
    count: int


# --- Patient profile & onboarding (onboarding-perfil design.md) -------------
#
# Decision 2: three tables. Sensitive values encrypted at rest with the same
# EncryptedString as health records (D13/D16); the onboarding state and the
# measurement type discriminator stay in the clear (ordering/filtering need
# them, same trade-off as HealthRecord.record_type). family_history.condition
# is encrypted too (review G2, Saúl's call: the spec mandates it); its catalog
# is still enforced by the Literal on the Create/Update schema.

PROFILE_MIN_BIRTH_DATE = date(1900, 1, 1)


# Range validations run BEFORE encrypting (Decision 4) and live outside
# pydantic validators so the 422 detail stays a STRING in es-MX, like
# health_records.
def validate_birth_date(birth_date: date) -> None:
    """es-MX ValueError when birth_date falls outside [1900-01-01, today]."""
    if birth_date > date.today():
        raise ValueError("La fecha de nacimiento no puede estar en el futuro")
    if birth_date < PROFILE_MIN_BIRTH_DATE:
        raise ValueError(
            "La fecha de nacimiento no puede ser anterior al 1 de enero de 1900"
        )


def validate_measurement_value(type_: str, value: float) -> None:
    """es-MX ValueError when a measurement is implausible (Decision 4):
    weight in (0, 400] kg, height in [30, 250] cm."""
    if type_ == "weight" and not (0 < value <= 400):
        raise ValueError("El peso debe ser mayor que 0 y de hasta 400 kg")
    if type_ == "height" and not (30 <= value <= 250):
        raise ValueError("La estatura debe estar entre 30 y 250 cm")


# Upper bound of relatives per family-history entry: the cardinality of the
# relative enum (review G11/M5). Enforced in the shared helper, not with
# pydantic max_length, so the 422 detail stays a STRING in es-MX.
MAX_FAMILY_HISTORY_RELATIVES = 8


def normalize_relatives(relatives: Sequence[str]) -> list[str]:
    """Bound (es-MX ValueError over the enum cardinality) and dedupe
    preserving order before persisting (review G11/M5)."""
    if len(relatives) > MAX_FAMILY_HISTORY_RELATIVES:
        raise ValueError(
            "La lista de parentescos admite como máximo "
            f"{MAX_FAMILY_HISTORY_RELATIVES} elementos"
        )
    return list(dict.fromkeys(relatives))


# 1:1 with user; birth_date/sex/allergies are Fernet tokens at rest. The
# onboarding state lives HERE, on the server (Decision 1): pending ->
# completed|skipped exactly once (a second close is a 409 in the route).
class PatientProfile(SQLModel, table=True):
    __tablename__ = "patient_profile"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, unique=True, ondelete="CASCADE"
    )
    # ISO date string before encryption; the API parses it back to a date.
    birth_date: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    sex: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    allergies: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    onboarding_outcome: str = Field(default="pending", max_length=16)
    onboarding_closed_at: datetime | None = Field(default=None)
    # perfil-eventos Decision 3: both 1:1 with the profile and encrypted.
    blood_type: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    # JSON list of the sections marked "ninguna", serialized INSIDE the
    # encrypted field (null = no marks).
    sections_none: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )


# One row per capture, never UPDATE of the value (Decision 2: history is
# kept); value encrypted at rest, type/measured_on in the clear (the DESC
# listing orders by them).
class BodyMeasurement(SQLModel, table=True):
    __tablename__ = "body_measurement"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    type: str = Field(max_length=16)  # "weight" | "height"
    value: str = Field(sa_column=Column(EncryptedString(), nullable=False))
    measured_on: date
    # Tie-breaker for same-day measurements: the latest capture wins.
    created_at: datetime = Field(default_factory=get_datetime_utc)


# One row per condition; relatives is a JSON array serialized INSIDE the
# encrypted field (accepted trade-off: not SQL-filterable, read by owner only).
# condition is a Fernet token at rest (review G2), so uniqueness per user
# cannot be a partial index: the route dedupes by decrypt-and-compare (G3).
class FamilyHistory(SQLModel, table=True):
    __tablename__ = "family_history"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    condition: str = Field(sa_column=Column(EncryptedString(), nullable=False))
    other_text: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    relatives: str = Field(sa_column=Column(EncryptedString(), nullable=False))
    note: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    created_at: datetime = Field(default_factory=get_datetime_utc)


# --- Medical history event sections (perfil-eventos design.md) --------------
#
# Decision 1: ONE generic table; the whole entry (its section included) is a
# JSON document inside a single encrypted column, validated by one pydantic
# schema per section. Decision 2: nothing in the clear but id, user_id and
# created_at; the server groups/filters in memory after decrypting the
# owner's rows (tens per patient).

HistorySection = Literal["past", "surgeries", "fractures", "transfusions"]
HISTORY_SECTIONS: tuple[HistorySection, ...] = (
    "past",
    "surgeries",
    "fractures",
    "transfusions",
)
BloodType = Literal["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-", "unknown"]
YesNoUnknown = Literal["yes", "no", "unknown"]

HISTORY_TEXT_MAX = 2000
HISTORY_NAME_MAX = 200
HISTORY_MAX_AGE = 130
HISTORY_MIN_YEAR = 1900


class MedicalHistoryEntry(SQLModel, table=True):
    __tablename__ = "medical_history_entry"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    # JSON of the entry WITH its section, encrypted (Decision 2).
    content: str = Field(sa_column=Column(EncryptedString(), nullable=False))
    created_at: datetime = Field(default_factory=get_datetime_utc)


# "Cuándo", stored as answered (Decision 4); the approximate year is the
# frontend's job.
class WhenAge(SQLModel):
    kind: Literal["age"]
    value: int


class WhenStage(SQLModel):
    kind: Literal["stage"]
    value: Literal["before_primary", "primary", "secondary", "high_school"]


class WhenYear(SQLModel):
    kind: Literal["year"]
    value: int


class WhenUnknown(SQLModel):
    kind: Literal["unknown"]


When = Annotated[WhenAge | WhenStage | WhenYear | WhenUnknown, Discriminator("kind")]


# Content per section. Every field is optional AT THE SCHEMA LEVEL (also the
# section's required one) so that a missing required field reaches
# validate_history_content and gets a STRING es-MX 422, and so stored entries
# tolerate absent fields on read (Risks: defaults None). Enums and lengths
# are still enforced by pydantic.
class PastHistoryContent(SQLModel):
    section: Literal["past"]
    condition: (
        Literal[
            "varicella",
            "measles",
            "mumps",
            "rubella",
            "hepatitis_a",
            "hepatitis_b",
            "hepatitis_c",
            "severe_covid19",
            "dengue",
            "tuberculosis",
            "other",
        ]
        | None
    ) = None
    other_text: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    when: When | None = None
    hospitalized: YesNoUnknown | None = None
    sequelae: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    note: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)


class SurgeryHistoryContent(SQLModel):
    section: Literal["surgeries"]
    kind: Literal["surgery", "hospitalization"] | None = None
    name: str | None = Field(default=None, max_length=HISTORY_NAME_MAX)
    when: When | None = None
    reason: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    place: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    physician: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    complications: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    anesthesia_reaction: YesNoUnknown | None = None
    anesthesia_reaction_detail: str | None = Field(
        default=None, max_length=HISTORY_TEXT_MAX
    )
    implant: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)


class FractureHistoryContent(SQLModel):
    section: Literal["fractures"]
    what: str | None = Field(default=None, max_length=HISTORY_NAME_MAX)
    side: Literal["left", "right", "both", "not_applicable"] | None = None
    when: When | None = None
    required_surgery: YesNoUnknown | None = None
    implant: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    sequelae: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)


class TransfusionHistoryContent(SQLModel):
    section: Literal["transfusions"]
    when: When | None = None
    reason: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    component: Literal["blood", "platelets", "plasma", "unknown"] | None = None
    place: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    reaction: YesNoUnknown | None = None
    reaction_detail: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)


HistoryContentModel = (
    PastHistoryContent
    | SurgeryHistoryContent
    | FractureHistoryContent
    | TransfusionHistoryContent
)
# Request body of POST/PUT /profile/history: discriminated by `section`.
HistoryContent = Annotated[HistoryContentModel, Discriminator("section")]


class PastHistoryEntry(PastHistoryContent):
    id: uuid.UUID
    created_at: datetime


class SurgeryHistoryEntry(SurgeryHistoryContent):
    id: uuid.UUID
    created_at: datetime


class FractureHistoryEntry(FractureHistoryContent):
    id: uuid.UUID
    created_at: datetime


class TransfusionHistoryEntry(TransfusionHistoryContent):
    id: uuid.UUID
    created_at: datetime


# HistoryEntry = {id, section, created_at, ...fields of its section}.
HistoryEntry = Annotated[
    PastHistoryEntry
    | SurgeryHistoryEntry
    | FractureHistoryEntry
    | TransfusionHistoryEntry,
    Discriminator("section"),
]


class HistoryEntriesPublic(SQLModel):
    data: list[HistoryEntry]
    count: int


class HistorySectionNone(SQLModel):
    none: bool


# Required field per section and its es-MX message (Interface contract).
HISTORY_REQUIRED: dict[str, tuple[str, str]] = {
    "past": ("condition", "Elige la condición o escribe cuál fue"),
    "surgeries": ("name", "Escribe qué cirugía u hospitalización fue"),
    "fractures": ("what", "Escribe qué hueso o lesión fue"),
}


def _is_filled(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _age_on(birth_date: date, today: date) -> int:
    return (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )


def validate_when(
    when: WhenAge | WhenStage | WhenYear | WhenUnknown | None,
    birth_date: date | None,
    today: date,
) -> None:
    """es-MX ValueError when `when` is impossible (Decision 4: the server only
    rejects impossibles). `today` is Mexico City's today."""
    if isinstance(when, WhenAge):
        if birth_date is not None and when.value > _age_on(birth_date, today):
            raise ValueError("La edad no puede ser mayor que tu edad actual")
        if not (0 <= when.value <= HISTORY_MAX_AGE):
            raise ValueError("La edad debe estar entre 0 y 130 años")
    elif isinstance(when, WhenYear):
        if birth_date is not None and when.value < birth_date.year:
            raise ValueError("El año no puede ser anterior a tu nacimiento")
        if when.value < HISTORY_MIN_YEAR:
            raise ValueError("El año no puede ser anterior a 1900")
        if when.value > today.year:
            raise ValueError("El año no puede ser futuro")


def validate_history_content(
    content: HistoryContentModel, birth_date: date | None, today: date
) -> None:
    """es-MX ValueError for an empty entry, a missing required field or an
    impossible `when`; runs BEFORE anything is encrypted or persisted."""
    values = content.model_dump(exclude={"section"})
    if not any(_is_filled(value) for value in values.values()):
        raise ValueError("Llena al menos un dato")
    required = HISTORY_REQUIRED.get(content.section)
    if required is not None:
        field, message = required
        if not _is_filled(values.get(field)):
            raise ValueError(message)
        if isinstance(content, PastHistoryContent) and content.condition == "other":
            if not _is_filled(content.other_text):
                raise ValueError(message)
    validate_when(content.when, birth_date, today)


# Partial update: absent = "do not touch", explicit null clears the field.
class PatientProfileUpdate(SQLModel):
    birth_date: date | None = None
    sex: Literal["female", "male", "unspecified"] | None = None
    allergies: str | None = Field(default=None, max_length=2000)
    blood_type: BloodType | None = None


class BodyMeasurementLatest(SQLModel):
    value: float
    measured_on: date


# The profile as the API returns it (Interface contract, GET /profile).
class PatientProfilePublic(SQLModel):
    birth_date: date | None
    sex: str | None
    allergies: str | None
    onboarding: str
    latest_weight: BodyMeasurementLatest | None
    latest_height: BodyMeasurementLatest | None
    blood_type: BloodType | None
    sections_none: list[HistorySection]


class OnboardingClose(SQLModel):
    outcome: Literal["completed", "skipped"]


class BodyMeasurementCreate(SQLModel):
    type: Literal["weight", "height"]
    value: float


class BodyMeasurementPublic(SQLModel):
    id: uuid.UUID
    type: str
    value: float
    measured_on: date


class BodyMeasurementsPublic(SQLModel):
    data: list[BodyMeasurementPublic]
    count: int


class FamilyHistoryCreate(SQLModel):
    condition: Literal["diabetes", "cancer", "hypertension", "heart_disease", "other"]
    other_text: str | None = Field(default=None, max_length=2000)
    relatives: list[
        Literal[
            "mother",
            "father",
            "maternal_grandmother",
            "maternal_grandfather",
            "paternal_grandmother",
            "paternal_grandfather",
            "sibling",
            "other",
        ]
    ]
    note: str | None = Field(default=None, max_length=2000)


class FamilyHistoryPublic(SQLModel):
    id: uuid.UUID
    condition: str
    other_text: str | None
    relatives: list[str]
    note: str | None


class FamilyHistoriesPublic(SQLModel):
    data: list[FamilyHistoryPublic]
    count: int


# Properties to return via API, id is always required
class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime | None = None


class UsersPublic(SQLModel):
    data: list[UserPublic]
    count: int


# Shared properties
class ItemBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Properties to receive on item creation
class ItemCreate(ItemBase):
    pass


# Properties to receive on item update
class ItemUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=255)


# Database model, database table inferred from class name
class Item(ItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime | None = Field(default_factory=get_datetime_utc)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    owner: User | None = Relationship(back_populates="items")


# Properties to return via API, id is always required
class ItemPublic(ItemBase):
    id: uuid.UUID
    owner_id: uuid.UUID
    created_at: datetime | None = None


class ItemsPublic(SQLModel):
    data: list[ItemPublic]
    count: int


# Generic message
class Message(SQLModel):
    message: str


# JSON payload containing access token
class Token(SQLModel):
    access_token: str
    token_type: str = "bearer"


# Contents of JWT token
class TokenPayload(SQLModel):
    sub: str | None = None
    # Authentication method reference: "password" | "google" (None in tokens
    # issued before this claim existed)
    amr: str | None = None


class NewPassword(SQLModel):
    token: str
    new_password: str = Field(min_length=8, max_length=128)
