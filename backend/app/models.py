import uuid
from collections.abc import Sequence
from datetime import UTC, date, datetime
from typing import Annotated, Any, Literal

from pydantic import ConfigDict, Discriminator, EmailStr, StringConstraints
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
    # perfil-habitos Decision 1: the habits questionnaire is 1:1, so the JSON
    # of the normalized Habits lives INSIDE this encrypted field (null = not
    # answered), like blood_type.
    habits: str | None = Field(
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

# perfil-cronicas Decision 1: chronic diseases are one more section, first in
# the canonical order; its link to a diagnosis lives inside the encrypted JSON.
HistorySection = Literal["chronic", "past", "surgeries", "fractures", "transfusions"]
HISTORY_SECTIONS: tuple[HistorySection, ...] = (
    "chronic",
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
HISTORY_MIN_YEAR = PROFILE_MIN_BIRTH_DATE.year


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

# Typical ages per school stage in Mexico, [first, last] inclusive; the same
# ranges as frontend/src/components/Profile/history.ts (STAGE_AGE_RANGES),
# which shows the approximate year. Here they decide a 422 (chronic "hasta"
# before "desde"): change both together.
STAGE_AGE_RANGES: dict[str, tuple[int, int]] = {
    "before_primary": (0, 5),
    "primary": (6, 11),
    "secondary": (12, 14),
    "high_school": (15, 17),
}


# Content per section. Every field is optional AT THE SCHEMA LEVEL (also the
# section's required one) so that a missing required field reaches
# validate_history_content and gets a STRING es-MX 422, and so stored entries
# tolerate absent fields on read (Risks: defaults None). Enums and lengths
# are still enforced by pydantic.
ChronicCondition = Literal[
    "type2_diabetes",
    "hypertension",
    "asthma",
    "hypothyroidism",
    "high_cholesterol",
    "copd",
    "arthritis",
    "epilepsy",
    "depression",
    "anxiety",
    "bipolar_disorder",
    "substance_use",
    "other",
]
# perfil-cronicas Decision 2: `sensitive` defaults to true for these when the
# client does not send it.
CHRONIC_SENSITIVE_BY_DEFAULT: frozenset[str] = frozenset(
    {"depression", "anxiety", "bipolar_disorder", "substance_use"}
)


class ChronicHistoryContent(SQLModel):
    section: Literal["chronic"]
    condition: ChronicCondition | None = None
    other_text: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    sensitive: bool | None = None
    status: Literal["active", "resolved"] | None = None
    since: When | None = None
    until: When | None = None
    treatment: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    note: str | None = Field(default=None, max_length=HISTORY_TEXT_MAX)
    # A diagnosis HealthRecord of the same patient (checked in the route).
    diagnosis_id: uuid.UUID | None = None


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
    ChronicHistoryContent
    | PastHistoryContent
    | SurgeryHistoryContent
    | FractureHistoryContent
    | TransfusionHistoryContent
)
# Request body of POST/PUT /profile/history: discriminated by `section`.
HistoryContent = Annotated[HistoryContentModel, Discriminator("section")]


class ChronicHistoryEntry(ChronicHistoryContent):
    id: uuid.UUID
    created_at: datetime


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
    ChronicHistoryEntry
    | PastHistoryEntry
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
    "chronic": ("condition", "Elige la condición o escribe cuál es"),
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
            raise ValueError(f"La edad debe estar entre 0 y {HISTORY_MAX_AGE} años")
    elif isinstance(when, WhenYear):
        if birth_date is not None and when.value < birth_date.year:
            raise ValueError("El año no puede ser anterior a tu nacimiento")
        if when.value < HISTORY_MIN_YEAR:
            raise ValueError(f"El año no puede ser anterior a {HISTORY_MIN_YEAR}")
        if when.value > today.year:
            raise ValueError("El año no puede ser futuro")


def _when_age_range(
    when: WhenAge | WhenStage | WhenYear | WhenUnknown | None,
    birth_date: date | None,
) -> tuple[int, int] | None:
    """`when` as an inclusive age range, or None when it cannot be compared
    (unknown, absent, or a year without a birth date). A year is two ages:
    before and after that year's birthday (review R11)."""
    if isinstance(when, WhenAge):
        return (when.value, when.value)
    if isinstance(when, WhenStage):
        return STAGE_AGE_RANGES[when.value]
    if isinstance(when, WhenYear) and birth_date is not None:
        age = when.value - birth_date.year
        return (max(age - 1, 0), max(age, 0))
    return None


def _validate_chronic_dates(
    content: ChronicHistoryContent, birth_date: date | None, today: date
) -> None:
    """since/until with Story A's rules; until only counts when resolved
    (Decision 5) and is rejected only when it surely precedes since
    (Decision 6: max(until) < min(since)). Year against year compares the
    years themselves, with or without a birth date (review R13)."""
    until = content.until if content.status == "resolved" else None
    validate_when(content.since, birth_date, today)
    validate_when(until, birth_date, today)
    if isinstance(content.since, WhenYear) and isinstance(until, WhenYear):
        if until.value < content.since.value:
            raise ValueError("No puede ser antes de «desde cuándo»")
        return
    since_range = _when_age_range(content.since, birth_date)
    until_range = _when_age_range(until, birth_date)
    if since_range and until_range and until_range[1] < since_range[0]:
        raise ValueError("No puede ser antes de «desde cuándo»")


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
        if (
            isinstance(content, PastHistoryContent | ChronicHistoryContent)
            and content.condition == "other"
        ):
            if not _is_filled(content.other_text):
                raise ValueError(message)
    if isinstance(content, ChronicHistoryContent):
        _validate_chronic_dates(content, birth_date, today)
    else:
        validate_when(content.when, birth_date, today)


def normalize_history_content(content: HistoryContentModel) -> HistoryContentModel:
    """What gets stored, after validation: a chronic entry always carries an
    explicit `sensitive` (Decision 2) and no `until` unless resolved
    (Decision 5). Other sections pass through untouched."""
    if not isinstance(content, ChronicHistoryContent):
        return content
    updates: dict[str, Any] = {}
    if content.sensitive is None:
        updates["sensitive"] = content.condition in CHRONIC_SENSITIVE_BY_DEFAULT
    if content.status != "resolved":
        updates["until"] = None
    return content.model_copy(update=updates)


# --- Habits questionnaire (perfil-habitos design.md §Interface contract) ----
# Every field optional in the schema; what the chosen answer requires is checked
# after normalizing (HABITS_REQUIRED, perfil-habitos-completitud). extra="forbid"
# so an unknown field is a 422 (Decision 5: the C2 extends this same object on
# purpose, never by accident).
HabitStatus = Literal["never", "former", "current"]
SecondhandPlace = Literal["home", "work_school", "other"]
# Contract order of `places`: stored deduped and sorted this way.
SECONDHAND_PLACES: tuple[SecondhandPlace, ...] = ("home", "work_school", "other")
# perfil-habitos-completitud Decision 1: "No recuerdo" (FHIR asked-unknown) goes
# in the same field as the number, as this exact string; any other string stays
# a schema 422. Only where it is admitted (Decision 2: what already happened).
HABIT_UNKNOWN = "unknown"
HabitUnknown = Literal["unknown"]
# Decision 6: ages are plain numbers, with the history's bounds.
HabitAge = Annotated[int, Field(ge=0, le=HISTORY_MAX_AGE)]
CigarettesPerDay = Annotated[int, Field(ge=1, le=100)]
HoursPerDay = Annotated[int, Field(ge=1, le=24)]


class _ClosedSchema(SQLModel):
    # sqlmodel types model_config as its private SQLModelConfig (not exported);
    # a ConfigDict merges into it the same way at runtime. hide_input_in_errors:
    # a ValidationError of a stored row never carries decrypted answers (R2).
    model_config = ConfigDict(extra="forbid", hide_input_in_errors=True)  # type: ignore[assignment]  # ty: ignore[invalid-assignment]


class AlcoholHabit(_ClosedSchema):
    status: Literal["never", "quit", "current"]
    start_age: HabitAge | HabitUnknown | None = None
    quit_age: HabitAge | HabitUnknown | None = None
    frequency: (
        Literal[
            "monthly_or_less",
            "two_to_four_monthly",
            "two_to_three_weekly",
            "four_plus_weekly",
        ]
        | None
    ) = None
    typical_drinks: (
        Literal["one_two", "three_four", "five_six", "seven_nine", "ten_plus"] | None
    ) = None
    six_or_more: (
        Literal["never", "less_than_monthly", "monthly", "weekly", "daily"] | None
    ) = None
    mostly_weekends: bool | None = None


class TobaccoHabit(_ClosedSchema):
    status: HabitStatus
    cigarettes_per_day: CigarettesPerDay | HabitUnknown | None = None
    start_age: HabitAge | HabitUnknown | None = None
    quit_age: HabitAge | HabitUnknown | None = None


class SecondhandSmoke(_ClosedSchema):
    exposed: bool
    # Bounded like relatives (review G11): more than three entries can only be
    # repeats, which normalize_habits would drop anyway.
    places: list[SecondhandPlace] = Field(
        default_factory=list, max_length=len(SECONDHAND_PLACES)
    )
    days_per_week: int | None = Field(default=None, ge=1, le=7)


# perfil-habitos-ajustes Decision 2: its own object, not a TobaccoHabit (it has
# days of the last 30, not cigarettes per day).
class VapingHabit(_ClosedSchema):
    status: HabitStatus
    frequency: Literal["daily", "some_days"] | None = None
    days_last_30: int | None = Field(default=None, ge=1, le=30)
    start_age: HabitAge | HabitUnknown | None = None
    quit_age: HabitAge | HabitUnknown | None = None


class WoodSmokeHabit(_ClosedSchema):
    status: HabitStatus
    start_age: HabitAge | HabitUnknown | None = None
    quit_age: HabitAge | HabitUnknown | None = None
    hours_per_day: HoursPerDay | HabitUnknown | None = None


# perfil-habitos-actividad-sueno design.md §Interface contract. Decision 6: no
# "unknown" anywhere in these blocks (they describe the present).
DaysPerWeek = Annotated[int, Field(ge=1, le=7)]
MinutesPerSession = Annotated[int, Field(ge=1, le=600)]
# Trimmed before its bound; an empty name is not a schema error but a missing
# one ("Escribe cuál."), so the 1 of 1..60 is checked after normalizing.
ActivityName = Annotated[str, StringConstraints(strip_whitespace=True, max_length=60)]
SleepTrouble = Literal["never", "some_days", "most_days", "every_day"]


class ExerciseActivity(_ClosedSchema):
    days_per_week: DaysPerWeek | None = None
    minutes_per_session: MinutesPerSession | None = None


class OtherExerciseActivity(ExerciseActivity):
    name: ActivityName | None = None


# Decision 2: one property per type (catalog order), null when not chosen; a
# closed object, not a list or a free dict, so an unknown type is a 422.
class ExerciseActivities(_ClosedSchema):
    walking: ExerciseActivity | None = None
    running: ExerciseActivity | None = None
    cycling: ExerciseActivity | None = None
    swimming: ExerciseActivity | None = None
    weights_gym: ExerciseActivity | None = None
    football_other_sport: ExerciseActivity | None = None
    yoga_pilates: ExerciseActivity | None = None
    dance: ExerciseActivity | None = None
    other: OtherExerciseActivity | None = None


class ExerciseHabit(_ClosedSchema):
    # Decision 3: false is "No hago ejercicio", not "unanswered".
    does_exercise: bool
    activities: ExerciseActivities = Field(default_factory=ExerciseActivities)


class DailyMovement(_ClosedSchema):
    # Decision 5: the 4 levels of NHANES PAQ180; travel and sitting from GPAQ.
    main_activity: (
        Literal["sitting", "standing_walking", "light_loads", "heavy_work"] | None
    ) = None
    active_travel: bool | None = None
    active_travel_days: DaysPerWeek | None = None
    sitting_hours: int | None = Field(default=None, ge=0, le=24)


class SleepHabit(_ClosedSchema):
    # Whole hours in 24 (naps included); the two NHIS insomnia items.
    hours: HoursPerDay | None = None
    trouble_falling_asleep: SleepTrouble | None = None
    trouble_staying_asleep: SleepTrouble | None = None


class Habits(_ClosedSchema):
    alcohol: AlcoholHabit | None = None
    tobacco: TobaccoHabit | None = None
    vaping: VapingHabit | None = None
    secondhand_smoke: SecondhandSmoke | None = None
    wood_smoke: WoodSmokeHabit | None = None
    exercise: ExerciseHabit | None = None
    daily_movement: DailyMovement | None = None
    sleep: SleepHabit | None = None


def upgrade_stored_habits(raw: dict[str, Any]) -> dict[str, Any]:
    """The decrypted JSON stored before perfil-habitos-ajustes, in the current
    shape (Decision 1: converted on read, no migration). Only for stored rows:
    the PUT body stays closed. Vaping as text becomes {"status": text}; the
    wood smoke `years` is dropped (Decision 3: it cannot become an age). Pure:
    `raw` is not modified."""
    upgraded = dict(raw)
    if isinstance(upgraded.get("vaping"), str):
        upgraded["vaping"] = {"status": upgraded["vaping"]}
    wood = upgraded.get("wood_smoke")
    if isinstance(wood, dict) and "years" in wood:
        upgraded["wood_smoke"] = {k: v for k, v in wood.items() if k != "years"}
    return upgraded


def _normalize_alcohol(alcohol: AlcoholHabit) -> AlcoholHabit:
    updates: dict[str, Any] = {}
    if alcohol.status != "current":
        updates.update(
            frequency=None, typical_drinks=None, six_or_more=None, mostly_weekends=None
        )
    if alcohol.status == "never":
        updates["start_age"] = None
    if alcohol.status != "quit":
        updates["quit_age"] = None
    return alcohol.model_copy(update=updates)


def _normalize_tobacco(tobacco: TobaccoHabit) -> TobaccoHabit:
    updates: dict[str, Any] = {}
    if tobacco.status == "never":
        updates.update(cigarettes_per_day=None, start_age=None)
    if tobacco.status != "former":
        updates["quit_age"] = None
    return tobacco.model_copy(update=updates)


def _normalize_secondhand(smoke: SecondhandSmoke) -> SecondhandSmoke:
    if not smoke.exposed:
        return smoke.model_copy(update={"places": [], "days_per_week": None})
    places = [place for place in SECONDHAND_PLACES if place in smoke.places]
    return smoke.model_copy(update={"places": places})


def _normalize_vaping(vaping: VapingHabit) -> VapingHabit:
    updates: dict[str, Any] = {}
    if vaping.status == "never":
        updates["start_age"] = None
    if vaping.status != "current":
        updates.update(frequency=None, days_last_30=None)
    elif vaping.frequency != "some_days":
        updates["days_last_30"] = None
    if vaping.status != "former":
        updates["quit_age"] = None
    return vaping.model_copy(update=updates)


def _normalize_wood(wood: WoodSmokeHabit) -> WoodSmokeHabit:
    updates: dict[str, Any] = {}
    if wood.status == "never":
        updates.update(start_age=None, hours_per_day=None)
    if wood.status != "former":
        updates["quit_age"] = None
    return wood.model_copy(update=updates)


def _normalize_exercise(exercise: ExerciseHabit) -> ExerciseHabit:
    if not exercise.does_exercise:
        return exercise.model_copy(update={"activities": ExerciseActivities()})
    other = exercise.activities.other
    if other is None or other.name != "":
        return exercise
    # Already trimmed by the schema (ActivityName): empty is unanswered.
    activities = exercise.activities.model_copy(
        update={"other": other.model_copy(update={"name": None})}
    )
    return exercise.model_copy(update={"activities": activities})


def _normalize_movement(movement: DailyMovement) -> DailyMovement:
    if movement.active_travel is not True:
        return movement.model_copy(update={"active_travel_days": None})
    return movement


def normalize_habits(habits: Habits) -> Habits:
    """What gets stored: whatever does not apply to the chosen answer is
    dropped (perfil-habitos Decision 3, like chronic `until`), and `places`
    deduped in contract order. Runs BEFORE habits_errors."""
    updates: dict[str, Any] = {}
    if habits.alcohol is not None:
        updates["alcohol"] = _normalize_alcohol(habits.alcohol)
    if habits.tobacco is not None:
        updates["tobacco"] = _normalize_tobacco(habits.tobacco)
    if habits.vaping is not None:
        updates["vaping"] = _normalize_vaping(habits.vaping)
    if habits.secondhand_smoke is not None:
        updates["secondhand_smoke"] = _normalize_secondhand(habits.secondhand_smoke)
    if habits.wood_smoke is not None:
        updates["wood_smoke"] = _normalize_wood(habits.wood_smoke)
    if habits.exercise is not None:
        updates["exercise"] = _normalize_exercise(habits.exercise)
    if habits.daily_movement is not None:
        updates["daily_movement"] = _normalize_movement(habits.daily_movement)
    return habits.model_copy(update=updates)


# perfil-habitos-completitud design.md §Interface contract: what each answer
# requires once normalized. block -> answer -> (required, "unknown" NOT
# admitted; required, "unknown" admitted). An answer not listed requires nothing.
HabitAnswer = (
    AlcoholHabit
    | TobaccoHabit
    | VapingHabit
    | SecondhandSmoke
    | WoodSmokeHabit
    | ExerciseHabit
    | DailyMovement
)
HABITS_REQUIRED: dict[str, dict[str, tuple[tuple[str, ...], tuple[str, ...]]]] = {
    "alcohol": {
        "quit": ((), ("start_age", "quit_age")),
        "current": (
            ("frequency", "typical_drinks", "six_or_more", "mostly_weekends"),
            ("start_age",),
        ),
    },
    "tobacco": {
        "former": ((), ("cigarettes_per_day", "start_age", "quit_age")),
        "current": (("cigarettes_per_day",), ("start_age",)),
    },
    "vaping": {
        "former": ((), ("start_age", "quit_age")),
        "current": (("frequency",), ("start_age",)),
        "current_some_days": (("frequency", "days_last_30"), ("start_age",)),
    },
    "secondhand_smoke": {"exposed": (("places", "days_per_week"), ())},
    "wood_smoke": {
        "former": ((), ("start_age", "quit_age", "hours_per_day")),
        "current": (("hours_per_day",), ("start_age",)),
    },
    # perfil-habitos-actividad-sueno; the sleep requires nothing.
    "exercise": {"does_exercise": (("activities",), ())},
    "daily_movement": {"active_travel": (("active_travel_days",), ())},
}
# A missing answer whose message is not the generic one keeps its own.
HABITS_MISSING_MESSAGE = {
    ("secondhand_smoke", "places"): "Elige dónde, o «No me expongo»",
    ("exercise", "activities"): "Elige al menos una actividad, o «No hago ejercicio»",
}
# What each chosen activity requires, and the message of the one that differs.
ACTIVITY_REQUIRED = ("days_per_week", "minutes_per_session")
OTHER_ACTIVITY_REQUIRED = ("name", *ACTIVITY_REQUIRED)
ACTIVITY_MISSING_MESSAGE = {"name": "Escribe cuál."}


def _habit_answer_key(answer: HabitAnswer) -> str:
    """The HABITS_REQUIRED row of an answer: its status, except those that
    depend on another field (the exposure, the vaping frequency, exercising,
    the active travel)."""
    if isinstance(answer, ExerciseHabit):
        return "does_exercise" if answer.does_exercise else "no_exercise"
    if isinstance(answer, DailyMovement):
        return "active_travel" if answer.active_travel else "no_active_travel"
    if isinstance(answer, SecondhandSmoke):
        return "exposed" if answer.exposed else "not_exposed"
    if isinstance(answer, VapingHabit) and answer.frequency == "some_days":
        return f"{answer.status}_some_days"
    return answer.status


def habits_errors(
    habits: Habits, birth_date: date | None, today: date
) -> list[tuple[str, str, str]]:
    """(block, field, es-MX message) per missing or impossible answer of a
    NORMALIZED Habits (a dropped field is never checked). Ages are compared to
    the current one only with a birth date, and only between numbers ("unknown"
    is never compared); at most one error per field. A field nested deeper
    than its block is a dotted path (an activity's: "activities.walking.
    days_per_week"), one `loc` level per segment."""
    age_now = _age_on(birth_date, today) if birth_date is not None else None
    errors: dict[tuple[str, str], str] = {}

    def above_now(age: int | str | None) -> bool:
        return isinstance(age, int) and age_now is not None and age > age_now

    above = "La edad no puede ser mayor que tu edad actual"
    after_quit = "No puede ser mayor que la edad en que lo dejaste"
    after_end = "No puede ser mayor que la edad en que terminó"
    # Same start/quit rules in every block; only the wood's wording differs.
    aged = AlcoholHabit | TobaccoHabit | VapingHabit | WoodSmokeHabit
    age_blocks: list[tuple[str, aged | None, str]] = [
        ("alcohol", habits.alcohol, after_quit),
        ("tobacco", habits.tobacco, after_quit),
        ("vaping", habits.vaping, after_quit),
        ("wood_smoke", habits.wood_smoke, after_end),
    ]
    for block, answer, start_after_quit in age_blocks:
        if answer is None:
            continue
        start, quit = answer.start_age, answer.quit_age
        if above_now(start):
            errors[(block, "start_age")] = above
        elif isinstance(start, int) and isinstance(quit, int) and start > quit:
            errors[(block, "start_age")] = start_after_quit
        if above_now(quit):
            errors[(block, "quit_age")] = above

    missing = "Contesta esta pregunta."
    missing_or_unknown = "Contesta esta pregunta o marca «No recuerdo»."
    unknown_not_admitted = "Esta pregunta no admite «No recuerdo»."
    answers: dict[str, HabitAnswer | None] = {
        "alcohol": habits.alcohol,
        "tobacco": habits.tobacco,
        "vaping": habits.vaping,
        "secondhand_smoke": habits.secondhand_smoke,
        "wood_smoke": habits.wood_smoke,
        "exercise": habits.exercise,
        "daily_movement": habits.daily_movement,
    }
    for block, given in answers.items():
        if given is None:
            continue
        no_unknown, with_unknown = HABITS_REQUIRED[block].get(
            _habit_answer_key(given), ((), ())
        )
        for field in no_unknown:
            value = getattr(given, field)
            if _unanswered(value):
                message = HABITS_MISSING_MESSAGE.get((block, field), missing)
                errors.setdefault((block, field), message)
            elif value == HABIT_UNKNOWN:
                errors.setdefault((block, field), unknown_not_admitted)
        for field in with_unknown:
            if getattr(given, field) is None:
                errors.setdefault((block, field), missing_or_unknown)
    # Each chosen activity, one level deeper: its field is the dotted path
    # under the block ("activities.<type>.<field>").
    if habits.exercise is not None:
        for kind, chosen in _chosen_activities(habits.exercise.activities):
            required = (
                OTHER_ACTIVITY_REQUIRED
                if isinstance(chosen, OtherExerciseActivity)
                else ACTIVITY_REQUIRED
            )
            for field in required:
                if getattr(chosen, field) is None:
                    message = ACTIVITY_MISSING_MESSAGE.get(field, missing)
                    path = f"activities.{kind}.{field}"
                    errors.setdefault(("exercise", path), message)
    return [(block, field, message) for (block, field), message in errors.items()]


def _chosen_activities(
    activities: ExerciseActivities,
) -> list[tuple[str, ExerciseActivity]]:
    """(type, answers) of every chosen activity, in catalog order."""
    kinds = ExerciseActivities.model_fields
    chosen = ((kind, getattr(activities, kind)) for kind in kinds)
    return [(kind, answers) for kind, answers in chosen if answers is not None]


def _unanswered(value: Any) -> bool:
    if isinstance(value, ExerciseActivities):
        return not _chosen_activities(value)
    return value is None or value == []


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
