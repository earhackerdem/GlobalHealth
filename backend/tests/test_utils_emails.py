from app.core.config import settings
from app.utils import generate_new_account_email, generate_reset_password_email


def test_generate_new_account_email_es_mx() -> None:
    email_data = generate_new_account_email(
        email_to="x@example.com", username="x@example.com", password="secret"
    )

    assert (
        email_data.subject
        == f"{settings.PROJECT_NAME} - Nueva cuenta para x@example.com"
    )
    assert "Entrar a mi cuenta" in email_data.html_content


def test_generate_reset_password_email_es_mx() -> None:
    email_data = generate_reset_password_email(
        email_to="x@example.com", email="x@example.com", token="sometoken"
    )

    assert "Recuperación de contraseña para" in email_data.subject
    assert "Restablecer contraseña" in email_data.html_content
