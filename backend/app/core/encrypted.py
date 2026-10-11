"""Application-level encrypted column type (NFR-001).

``EncryptedString`` is a SQLAlchemy TypeDecorator that transparently encrypts
on write and decrypts on read using Fernet (symmetric, authenticated).

Key management: the key comes from ``settings.ENCRYPTION_KEY`` (urlsafe
base64, 32 bytes). When unset, a deterministic key is derived from
``SECRET_KEY`` (sha256) so local development works out of the box. In
production, ALWAYS set a dedicated ``ENCRYPTION_KEY`` so the signing secret
and the data-encryption key can be rotated independently.

Note: Fernet is non-deterministic (random IV per encryption), so encrypted
columns cannot be filtered by value in SQL; compare after decryption.
"""

import base64
import hashlib
from functools import lru_cache
from typing import Any

from cryptography.fernet import Fernet, InvalidToken
from sqlalchemy import String
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator

from app.core.config import settings


@lru_cache(maxsize=1)
def _fernet() -> Fernet:
    key = settings.ENCRYPTION_KEY
    if not key:
        # Dev fallback: deterministic derivation from SECRET_KEY.
        key = base64.urlsafe_b64encode(
            hashlib.sha256(settings.SECRET_KEY.encode()).digest()[:32]
        ).decode()
    return Fernet(key)


def encrypt_str(value: str) -> str:
    """Encrypt a string with the application Fernet key (e.g. PKCE cookie)."""
    return _fernet().encrypt(value.encode()).decode()


def decrypt_str(token: str) -> str | None:
    """Decrypt a Fernet token; returns None if invalid or tampered."""
    try:
        return _fernet().decrypt(token.encode()).decode()
    except InvalidToken:
        return None


class EncryptedString(TypeDecorator[str]):
    """String column stored encrypted at rest (Fernet token in the DB)."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Dialect) -> str | None:
        if value is None:
            return None
        return _fernet().encrypt(str(value).encode()).decode()

    def process_result_value(self, value: Any, dialect: Dialect) -> str | None:
        if value is None:
            return None
        return _fernet().decrypt(str(value).encode()).decode()
