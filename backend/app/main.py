from collections.abc import Sequence
from pathlib import Path
from typing import Any

import sentry_sdk
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute
from starlette.middleware.cors import CORSMiddleware

from app.api.main import api_router
from app.core.config import settings

FRONTEND_DIR = Path(__file__).parent / "frontend"

# api-errores-sin-datos Decisions 3-4: an event keeps the exception type, the
# stack and the route, never the request body, frame variables or PII.
SENTRY_OPTIONS: dict[str, Any] = {
    "traces_sample_rate": 1.0,  # what the deprecated enable_tracing=True set
    "max_request_body_size": "never",
    "include_local_variables": False,
    "send_default_pii": False,
}


def custom_generate_unique_id(route: APIRoute) -> str:
    return f"{route.tags[0]}-{route.name}"


def validation_error_content(errors: Sequence[Any]) -> dict[str, Any]:
    """FastAPI's 422 shape without the received value (`input`): the client
    already has it, and it is health data echoed back (Decision 1). Outside
    `input`, pydantic-core already turns a lone surrogate into U+FFFD, so the
    rest always encodes (review M2)."""
    detail = [{k: v for k, v in e.items() if k != "input"} for e in errors]
    return {"detail": jsonable_encoder(detail)}


def init_sentry() -> None:
    if settings.SENTRY_DSN and settings.FASTAPI_ENV != "development":
        sentry_sdk.init(dsn=str(settings.SENTRY_DSN), **SENTRY_OPTIONS)


init_sentry()

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    generate_unique_id_function=custom_generate_unique_id,
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(
    _request: Request, exc: RequestValidationError
) -> JSONResponse:
    return JSONResponse(status_code=422, content=validation_error_content(exc.errors()))


app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_HOST],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.API_V1_STR)
app.frontend("/", directory=FRONTEND_DIR)
