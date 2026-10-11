from collections.abc import Generator
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jwt.exceptions import InvalidTokenError
from pydantic import ValidationError
from sqlmodel import Session, select

from app.core import security
from app.core.config import settings
from app.core.consent_text import CONSENT_TEXTS
from app.core.db import engine
from app.models import ConsentGrant, TokenPayload, User

reusable_oauth2 = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/login/access-token"
)


def get_db() -> Generator[Session]:
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_db)]
TokenDep = Annotated[str, Depends(reusable_oauth2)]


def get_token_payload(token: TokenDep) -> TokenPayload:
    """Decode and validate the session JWT (sub + amr claims)."""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[security.ALGORITHM]
        )
        return TokenPayload(**payload)
    except InvalidTokenError, ValidationError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials",
        )


TokenPayloadDep = Annotated[TokenPayload, Depends(get_token_payload)]


def get_current_user(session: SessionDep, token_data: TokenPayloadDep) -> User:
    user = session.get(User, token_data.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_active_superuser(current_user: CurrentUser) -> User:
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user


def require_consent(session: SessionDep, current_user: CurrentUser) -> User:
    """Require an express consent grant of the CURRENT version (NFR-004).

    Every health-data router (E2+) must declare this dependency. An
    authenticated user without a ConsentGrant row for the current consent
    version (max of CONSENT_TEXTS) gets 403 CONSENT_REQUIRED: when the text
    is revised, older grants stop opening health-data capture.
    """
    current_version = max(CONSENT_TEXTS)
    grant = session.exec(
        select(ConsentGrant)
        .where(ConsentGrant.user_id == current_user.id)
        .where(ConsentGrant.version == current_version)
    ).first()
    if not grant:
        raise HTTPException(status_code=403, detail="CONSENT_REQUIRED")
    return current_user


ConsentedUser = Annotated[User, Depends(require_consent)]
