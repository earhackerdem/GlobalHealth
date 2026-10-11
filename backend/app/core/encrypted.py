"""Application-level encrypted column type (NFR-001) and PKCE-cookie helpers.

``EncryptedString`` is a SQLAlchemy TypeDecorator that transparently encrypts
on write and decrypts on read using Fernet (symmetric, authenticated).

Key management (one material, two purposes):
- **Data key**: ``settings.ENCRYPTION_KEY`` (urlsafe base64, 32 bytes). When
  unset, a deterministic key is derived from ``SECRET_KEY`` (sha256) so local
  development works out of the box; outside development the settings refuse to
  start without a dedicated ``ENCRYPTION_KEY`` (app/core/config.py).
- **Cookie key**: derived from the data key material with a purpose tag
  (``sha256(key material + b"pkce")``), so a leaked short-lived cookie key
  never exposes data at rest and vice versa.
- **Rotation**: ``settings.ENCRYPTION_KEY_PREVIOUS``, when set, is added as a
  decrypt-only key (MultiFernet): new writes use the current key while old
  ciphertext still decrypts until it is re-encrypted.

Note: Fernet is non-deterministic (random IV per encryption), so encrypted
columns cannot be filtered by value in SQL; compare after decryption.
"""

import base64
import hashlib
from functools import lru_cache
from typing import Any

from cryptography.fernet import Fernet, InvalidToken, MultiFernet
from sqlalchemy import String
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator


def _data_key() -> bytes:
    """Current data-key material (urlsafe base64, 32 bytes).

    Derivation kept EXACTLY as the original single-key scheme so ciphertext
    written before the purpose split still decrypts.
    """
    from app.core.config import settings

    key = settings.ENCRYPTION_KEY
    if not key:
        # Dev fallback: deterministic derivation from SECRET_KEY.
        key = base64.urlsafe_b64encode(
            hashlib.sha256(settings.SECRET_KEY.encode()).digest()[:32]
        ).decode()
    return key.encode()


def _purpose_key(material: bytes, purpose: bytes) -> bytes:
    """Derive a purpose-scoped Fernet key from base key material."""
    return base64.urlsafe_b64encode(hashlib.sha256(material + purpose).digest())


@lru_cache(maxsize=1)
def _data_fernet() -> MultiFernet:
    """Fernet for data at rest; encrypts with the current key, decrypts with
    the current and (while rotating) the previous one."""
    from app.core.config import settings

    keys = [Fernet(_data_key())]
    if settings.ENCRYPTION_KEY_PREVIOUS:
        keys.append(Fernet(settings.ENCRYPTION_KEY_PREVIOUS.encode()))
    return MultiFernet(keys)


@lru_cache(maxsize=1)
def _cookie_fernet() -> Fernet:
    """Fernet for the short-lived PKCE cookie (purpose-separated key)."""
    return Fernet(_purpose_key(_data_key(), b"pkce"))


def encrypt_str(value: str) -> str:
    """Encrypt a string for the PKCE cookie (cookie-purpose key)."""
    return _cookie_fernet().encrypt(value.encode()).decode()


def decrypt_str(token: str) -> str | None:
    """Decrypt a Fernet token (cookie-purpose first, then the data keys);
    returns None if invalid or tampered."""
    for fernet in (_cookie_fernet(), _data_fernet()):
        try:
            return fernet.decrypt(token.encode()).decode()
        except InvalidToken:
            continue
    return None


class EncryptedString(TypeDecorator[str]):
    """String column stored encrypted at rest (Fernet token in the DB)."""

    impl = String
    cache_ok = True

    def process_bind_param(self, value: Any, dialect: Dialect) -> str | None:
        if value is None:
            return None
        return _data_fernet().encrypt(str(value).encode()).decode()

    def process_result_value(self, value: Any, dialect: Dialect) -> str | None:
        if value is None:
            return None
        return _data_fernet().decrypt(str(value).encode()).decode()
