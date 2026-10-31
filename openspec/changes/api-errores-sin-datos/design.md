# Design

Status: APPROVED
Approved: 2026-10-31, by delegation of Saúl Pérez (author): «toma las tareas que correspondan a fast api y
resuélvelas de manera autónoma… quiero ver hasta dónde llegas» (`/epe-autopilot`)

## Context
`backend/app/main.py` es el del template: sin handlers propios y con `sentry_sdk.init(dsn=…, enable_tracing=True)`
cuando hay DSN fuera de `development`. Las rutas lanzan `RequestValidationError` propias con `loc`/`msg`/`type`
(`routes/profile.py:649`) que la UI coloca por `loc`.

## Goals / Non-Goals
**Goals:** ningún 422 devuelve `input` ni falla al serializar; ningún evento de Sentry lleva cuerpo, variables o token.
**Non-Goals:** traducir los `msg` de pydantic (🔒); cambiar los 500 que no vienen de validación; activar Sentry o
elegir un DSN; tocar el esquema OpenAPI o el cliente generado.

## Interface contract
- `app.main.validation_error_content(errors: Sequence[Any]) -> dict[str, Any]`: devuelve `{"detail": [...]}`, cada
  error sin la clave `input` y pasado por `jsonable_encoder`; toda cadena (también las de `loc`) queda como UTF-8
  válido: un surrogate suelto se cambia por `"?"`.
- Handler registrado en `app` para `RequestValidationError`: `JSONResponse(422, validation_error_content(exc.errors()))`.
- `app.main.SENTRY_OPTIONS: dict[str, Any]` con, al menos, `traces_sample_rate=1.0` (lo que hacía el `enable_tracing=True` obsoleto en 2.70.0), `max_request_body_size="never"`,
  `include_local_variables=False`, `send_default_pii=False`; `sentry_sdk.init(dsn=…, **SENTRY_OPTIONS)` con la
  misma condición de hoy.

## Decisions
1. **Quitar `input` de todo 422, no solo del que falla.** El cliente ya tiene lo que envió; el eco no le sirve a
   ninguna pantalla (nadie lo lee) y es el dato de salud de vuelta en la respuesta. Perdió: escapar el surrogate
   (sigue haciendo eco, ver exploration §3).
2. **Sanear cadenas con `encode("utf-8", "replace")`** después del `jsonable_encoder`, para la clave desconocida con
   surrogate (`loc`). Perdió: rechazar el cuerpo antes de parsear (un middleware que lea el cuerpo crudo, más caro y
   duplica lo que pydantic ya hace).
3. **Opciones de Sentry y no un `before_send`.** Medido: las dos opciones bastan. Perdió: `before_send` que borre
   `request.data` (red sobre un campo que ya no se captura).
4. **Por delegación:** `send_default_pii=False` explícito, aunque es el valor por defecto, para que un cambio de
   default de la librería no lo prenda en silencio.

## Test plan (one row per scenario, mandatory)
| Spec · scenario | Test |
|---|---|
| error-reports · Texto con un surrogate suelto en el alta | `backend/tests/api/routes/test_error_reports.py::test_signup_lone_surrogate_is_422_without_echo_or_log` |
| error-reports · Un 422 ordinario conserva su forma y pierde el eco | `…::test_ordinary_422_keeps_shape_without_input` |
| error-reports · Una clave desconocida con un surrogate suelto | `…::test_unknown_key_with_lone_surrogate_is_valid_utf8_422` |
| error-reports · Falla inesperada al guardar un antecedente | `…::test_sentry_event_has_no_body_locals_or_token` |

## Non-functional constraints addressed
NFR-001 y privacidad (arriba); NFR-014 conservado (el evento trae tipo, stack y ruta); NFR-009 (una prueba por
escenario, suite verde).

## Risks / Trade-offs
- [Un desarrollador pierde el `input` al depurar un 422] → el `loc` y el `msg` bastan para saber qué campo; el
  desarrollador tiene su propia petición.
- [La integración de Sentry parcha clases de Starlette de forma global en la prueba] → la prueba cierra el cliente
  de Sentry al terminar (`sentry_sdk.init()` sin DSN) para no afectar a las demás.

## Gate that closes the work
`cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` con 0 fallas, 0 errores y 0
saltadas, cobertura ≥ 90; `uv run ruff check app tests`, `uv run mypy app`; `openspec validate api-errores-sin-datos
--strict`; el `curl` de la exploración responde 422 y `docker logs` no contiene el texto.
