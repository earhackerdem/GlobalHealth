import base64
import hashlib
import json
import secrets
from datetime import timedelta
from typing import Annotated, Any
from urllib.parse import urlencode

from fastapi import APIRouter, Cookie, Depends, HTTPException, Response
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select

from app import crud
from app.api.deps import CurrentUser, SessionDep, get_current_active_superuser
from app.core import google_oauth, security
from app.core.config import settings
from app.core.encrypted import decrypt_str, encrypt_str
from app.models import (
    Message,
    NewPassword,
    OAuthIdentity,
    Token,
    User,
    UserPublic,
    UserUpdate,
)
from app.utils import (
    generate_password_reset_token,
    generate_reset_password_email,
    send_email,
    verify_password_reset_token,
)

router = APIRouter(tags=["login"])


@router.post("/login/access-token")
def login_access_token(
    session: SessionDep, form_data: Annotated[OAuth2PasswordRequestForm, Depends()]
) -> Token:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = crud.authenticate(
        session=session, email=form_data.username, password=form_data.password
    )
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return Token(
        access_token=security.create_access_token(
            user.id, expires_delta=access_token_expires, amr="password"
        )
    )


PKCE_COOKIE = "g_pkce"
INVALID_AUTHORIZATION_DETAIL = "Solicitud de autorización inválida o expirada"


def _error_response(status_code: int, detail: str) -> JSONResponse:
    """Error response for the Google callback: always deletes the PKCE cookie
    so a failed attempt never leaves a stale verifier behind."""
    response = JSONResponse(status_code=status_code, content={"detail": detail})
    response.delete_cookie(PKCE_COOKIE)
    return response


@router.get("/login/google")
def login_google() -> RedirectResponse:
    """
    Redirect to Google's OAuth 2.0 / OIDC authorization endpoint
    (Authorization Code + PKCE + state; verifier and state travel sealed in an
    encrypted, HttpOnly cookie that the callback REQUIRES)
    """
    code_verifier = secrets.token_urlsafe(64)
    state = secrets.token_urlsafe(32)
    code_challenge = (
        base64.urlsafe_b64encode(hashlib.sha256(code_verifier.encode()).digest())
        .rstrip(b"=")
        .decode()
    )
    params = urlencode(
        {
            "client_id": settings.GOOGLE_CLIENT_ID or "",
            "redirect_uri": settings.GOOGLE_REDIRECT_URI or "",
            "response_type": "code",
            "scope": "openid email profile",
            "code_challenge": code_challenge,
            "code_challenge_method": "S256",
            "state": state,
        }
    )
    response = RedirectResponse(url=f"{google_oauth.GOOGLE_AUTH_URL}?{params}")
    response.set_cookie(
        PKCE_COOKIE,
        encrypt_str(json.dumps({"v": code_verifier, "s": state})),
        max_age=600,
        httponly=True,
        secure=True,
        samesite="lax",
    )
    return response


@router.get("/login/google/callback")
async def login_google_callback(
    session: SessionDep,
    code: str,
    state: str | None = None,
    g_pkce: Annotated[str | None, Cookie()] = None,
) -> Response:
    """
    Google OIDC callback: verify the sealed PKCE verifier + state, create or
    link the account by Google-verified email and hand the session token to
    the SPA via the redirect's URL fragment (never logged, never cached)
    """
    payload = decrypt_str(g_pkce) if g_pkce else None
    try:
        data = json.loads(payload) if payload else None
    except ValueError:
        data = None
    code_verifier = data.get("v") if isinstance(data, dict) else None
    sealed_state = data.get("s") if isinstance(data, dict) else None
    if not code_verifier or not sealed_state or not state or state != sealed_state:
        return _error_response(400, INVALID_AUTHORIZATION_DETAIL)

    claims = await google_oauth.exchange_code(code, code_verifier=code_verifier)
    if not claims.email_verified:
        return _error_response(
            400, "El correo de la cuenta de Google no está verificado"
        )

    user = crud.get_user_by_email(session=session, email=claims.email)
    if not user:
        user = User(email=claims.email, hashed_password=None, is_active=True)
        session.add(user)
        session.commit()
        session.refresh(user)
    elif not user.is_active:
        return _error_response(400, "Usuario inactivo")

    # Link the Google identity if not already linked (subject is encrypted at
    # rest, so compare decrypted values in Python instead of filtering in SQL)
    identities = session.exec(
        select(OAuthIdentity).where(
            OAuthIdentity.user_id == user.id, OAuthIdentity.provider == "google"
        )
    ).all()
    if not any(identity.subject == claims.sub for identity in identities):
        session.add(
            OAuthIdentity(
                user_id=user.id,
                provider="google",
                subject=claims.sub,
                email=claims.email,
            )
        )
        session.commit()

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = security.create_access_token(
        user.id, expires_delta=access_token_expires, amr="google"
    )
    # Handoff to the SPA via URL fragment: it never reaches a server log and
    # no-store keeps the token out of any cache.
    response: Response = RedirectResponse(
        url=(
            f"{settings.FRONTEND_HOST}/google-callback"
            f"#access_token={access_token}&token_type=bearer"
        ),
        status_code=307,
        headers={"Cache-Control": "no-store", "Pragma": "no-cache"},
    )
    response.delete_cookie(PKCE_COOKIE)
    return response


@router.post("/login/test-token", response_model=UserPublic)
def test_token(current_user: CurrentUser) -> Any:
    """
    Test access token
    """
    return current_user


@router.post("/password-recovery/{email}")
def recover_password(email: str, session: SessionDep) -> Message:
    """
    Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    # Always return the same response to prevent email enumeration attacks
    # Only send email if user actually exists
    if user:
        password_reset_token = generate_password_reset_token(email=email)
        email_data = generate_reset_password_email(
            email_to=user.email, email=email, token=password_reset_token
        )
        send_email(
            email_to=user.email,
            subject=email_data.subject,
            html_content=email_data.html_content,
        )
    return Message(
        message="If that email is registered, we sent a password recovery link"
    )


@router.post("/reset-password/")
def reset_password(session: SessionDep, body: NewPassword) -> Message:
    """
    Reset password
    """
    email = verify_password_reset_token(token=body.token)
    if not email:
        raise HTTPException(status_code=400, detail="Invalid token")
    user = crud.get_user_by_email(session=session, email=email)
    if not user:
        # Don't reveal that the user doesn't exist - use same error as invalid token
        raise HTTPException(status_code=400, detail="Invalid token")
    elif not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    user_in_update = UserUpdate(password=body.new_password)
    crud.update_user(
        session=session,
        db_user=user,
        user_in=user_in_update,
    )
    return Message(message="Password updated successfully")


@router.post(
    "/password-recovery-html-content/{email}",
    dependencies=[Depends(get_current_active_superuser)],
    response_class=HTMLResponse,
)
def recover_password_html_content(email: str, session: SessionDep) -> Any:
    """
    HTML Content for Password Recovery
    """
    user = crud.get_user_by_email(session=session, email=email)

    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this username does not exist in the system.",
        )
    password_reset_token = generate_password_reset_token(email=email)
    email_data = generate_reset_password_email(
        email_to=user.email, email=email, token=password_reset_token
    )

    return HTMLResponse(
        content=email_data.html_content, headers={"subject:": email_data.subject}
    )
