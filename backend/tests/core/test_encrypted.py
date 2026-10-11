"""Unit tests for app.core.encrypted (finding H12).

Pins the Fernet helpers used by the PKCE cookie (encrypt_str/decrypt_str) and
the EncryptedString column type used for data encrypted at rest (NFR-001).
"""

from app.core.encrypted import EncryptedString, decrypt_str, encrypt_str


def test_encrypt_decrypt_roundtrip() -> None:
    plaintext = "secreto-de-prueba áéí"

    token = encrypt_str(plaintext)

    assert token != plaintext
    assert token.startswith("gAAAA")  # Fernet version byte 0x80 in urlsafe-b64
    assert decrypt_str(token) == plaintext


def test_encrypt_is_non_deterministic() -> None:
    """Fernet uses a random IV: same plaintext, different tokens."""
    assert encrypt_str("mismo-texto") != encrypt_str("mismo-texto")


def test_decrypt_invalid_token_returns_none() -> None:
    assert decrypt_str("not-a-fernet-token") is None


def test_decrypt_tampered_token_returns_none() -> None:
    token = encrypt_str("integridad")
    tampered = token[:-4] + ("AAAA" if not token.endswith("AAAA") else "BBBB")

    assert decrypt_str(tampered) is None


def test_encrypted_string_bind_and_result_roundtrip() -> None:
    column_type = EncryptedString()

    stored = column_type.process_bind_param("nota clínica", dialect=None)

    assert stored is not None
    assert stored != "nota clínica"
    assert stored.startswith("gAAAA")
    assert column_type.process_result_value(stored, dialect=None) == "nota clínica"


def test_encrypted_string_none_passthrough() -> None:
    column_type = EncryptedString()

    assert column_type.process_bind_param(None, dialect=None) is None
    assert column_type.process_result_value(None, dialect=None) is None


def test_encrypted_string_is_compatible_with_encrypt_str() -> None:
    """Both paths share the same application key: tokens interoperate."""
    column_type = EncryptedString()

    stored = column_type.process_bind_param("compartido", dialect=None)
    assert stored is not None
    assert decrypt_str(stored) == "compartido"
