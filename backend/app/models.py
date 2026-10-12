import uuid
from datetime import UTC, date, datetime
from typing import Literal

from pydantic import EmailStr, model_validator
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
class HealthRecord(SQLModel, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    owner_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    record_type: str = Field(max_length=32)  # "diagnosis" | "prescription"
    occurred_on: date
    title: str = Field(sa_column=Column(EncryptedString(), nullable=False))
    professional: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    notes: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    dose: str | None = Field(
        default=None, sa_column=Column(EncryptedString(), nullable=True)
    )
    valid_from: date | None = Field(default=None)
    valid_to: date | None = Field(default=None)
    created_at: datetime = Field(default_factory=get_datetime_utc)
    updated_at: datetime = Field(default_factory=get_datetime_utc)


# Properties to receive via API on creation, discriminated by record_type:
# a diagnosis carries no prescription fields; a prescription requires
# dose and validity window.
class HealthRecordCreate(SQLModel):
    record_type: Literal["diagnosis", "prescription"]
    title: str = Field(min_length=1, max_length=255)
    occurred_on: date
    professional: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=2000)
    dose: str | None = Field(default=None, max_length=255)
    valid_from: date | None = None
    valid_to: date | None = None

    @model_validator(mode="after")
    def _validate_fields_by_type(self) -> HealthRecordCreate:
        prescription_fields = ("dose", "valid_from", "valid_to")
        if self.record_type == "diagnosis":
            present = [f for f in prescription_fields if getattr(self, f) is not None]
            if present:
                raise ValueError(
                    "Un diagnóstico no admite dosis ni vigencia: " + ", ".join(present)
                )
        else:
            missing = [f for f in prescription_fields if getattr(self, f) is None]
            if missing:
                raise ValueError(
                    "Una receta requiere dosis y vigencia: falta " + ", ".join(missing)
                )
        return self


# Properties to receive via API on update, all optional; record_type is
# immutable and therefore absent here.
class HealthRecordUpdate(SQLModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    occurred_on: date | None = None
    professional: str | None = Field(default=None, max_length=255)
    notes: str | None = Field(default=None, max_length=2000)
    dose: str | None = Field(default=None, max_length=255)
    valid_from: date | None = None
    valid_to: date | None = None


class HealthRecordPublic(SQLModel):
    id: uuid.UUID
    record_type: str
    occurred_on: date
    title: str
    professional: str | None
    notes: str | None
    dose: str | None
    valid_from: date | None
    valid_to: date | None
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
