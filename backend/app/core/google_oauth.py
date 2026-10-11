"""Google OIDC authorization-code exchange.

Contract (openspec/changes/cuenta-consentimiento/design.md): the routes call
``google_oauth.exchange_code(code)`` and the tests patch
``app.core.google_oauth.exchange_code``; Google is NEVER called in tests.
"""

from dataclasses import dataclass

import httpx
import jwt
from fastapi import HTTPException

from app.core.config import settings

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_JWKS_URL = "https://www.googleapis.com/oauth2/v3/certs"
GOOGLE_ISSUERS = ("https://accounts.google.com", "accounts.google.com")


@dataclass
class GoogleClaims:
    sub: str
    email: str
    email_verified: bool


async def exchange_code(code: str, code_verifier: str | None = None) -> GoogleClaims:
    """Exchange an authorization code for Google's verified identity claims.

    POSTs the code to Google's token endpoint (with the PKCE ``code_verifier``
    when the login flow provided one) and validates the returned ``id_token``
    (signature against Google's JWKS, audience, issuer).
    """
    if not (
        settings.GOOGLE_CLIENT_ID
        and settings.GOOGLE_CLIENT_SECRET
        and settings.GOOGLE_REDIRECT_URI
    ):
        raise HTTPException(status_code=500, detail="Google OAuth is not configured")

    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }
    if code_verifier:
        data["code_verifier"] = code_verifier
    async with httpx.AsyncClient() as client:
        response = await client.post(GOOGLE_TOKEN_URL, data=data)
    if response.status_code != 200:
        raise HTTPException(
            status_code=400, detail="Could not exchange the Google authorization code"
        )
    id_token = response.json().get("id_token")
    if not id_token:
        raise HTTPException(status_code=400, detail="Google returned no id_token")

    try:
        signing_key = jwt.PyJWKClient(GOOGLE_JWKS_URL).get_signing_key_from_jwt(
            id_token
        )
        claims = jwt.decode(
            id_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=settings.GOOGLE_CLIENT_ID,
        )
    except jwt.PyJWTError:
        raise HTTPException(status_code=400, detail="Invalid Google id_token")
    if claims.get("iss") not in GOOGLE_ISSUERS:
        raise HTTPException(status_code=400, detail="Invalid Google id_token issuer")

    return GoogleClaims(
        sub=claims["sub"],
        email=claims["email"],
        email_verified=bool(claims.get("email_verified", False)),
    )
