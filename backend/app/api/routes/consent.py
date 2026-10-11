from typing import Any

from fastapi import APIRouter, HTTPException, Response
from sqlmodel import col, select

from app.api.deps import CurrentUser, SessionDep
from app.core.consent_text import CONSENT_TEXTS, consent_text_sha256
from app.models import (
    ConsentCreate,
    ConsentGrant,
    ConsentGrantPublic,
    ConsentStatusPublic,
)

router = APIRouter(prefix="/consent", tags=["consent"])


@router.post("", response_model=ConsentGrantPublic, status_code=201)
def grant_consent(
    *,
    session: SessionDep,
    current_user: CurrentUser,
    consent_in: ConsentCreate,
    response: Response,
) -> Any:
    """Record the express consent of the session user (NFR-004).

    Stores one row per grant with the version, the sha256 of the exact text
    accepted and the auth method of the session. Idempotent per version: a
    second POST for the same version returns the existing grant with 200 and
    the original granted_at.

    auth_method: the access token does not carry how the session was
    authenticated, so it is inferred from the account: a user without a local
    hashed_password can only have signed in via Google OIDC ("google");
    otherwise "password".
    """
    if consent_in.version not in CONSENT_TEXTS:
        raise HTTPException(status_code=400, detail="Unknown consent version")

    existing = session.exec(
        select(ConsentGrant)
        .where(ConsentGrant.user_id == current_user.id)
        .where(ConsentGrant.version == consent_in.version)
    ).first()
    if existing:
        response.status_code = 200
        return existing

    auth_method = "google" if current_user.hashed_password is None else "password"
    grant = ConsentGrant(
        user_id=current_user.id,
        version=consent_in.version,
        text_sha256=consent_text_sha256(consent_in.version),
        auth_method=auth_method,
    )
    session.add(grant)
    session.commit()
    session.refresh(grant)
    return grant


@router.get("/text")
def read_consent_text(_current_user: CurrentUser) -> dict[str, str]:
    """Return the current consent text so the frontend renders the exact
    version the grant will hash (single source: app/core/consent_text.py)."""
    version = max(CONSENT_TEXTS)
    return {"version": version, "text": CONSENT_TEXTS[version]}


@router.get("", response_model=ConsentStatusPublic)
def read_consent(session: SessionDep, current_user: CurrentUser) -> Any:
    """Return the current consent of the session user, or 404 if never granted."""
    grant = session.exec(
        select(ConsentGrant)
        .where(ConsentGrant.user_id == current_user.id)
        .order_by(col(ConsentGrant.granted_at).desc())
    ).first()
    if not grant:
        raise HTTPException(status_code=404, detail="Consent not granted")
    return grant
