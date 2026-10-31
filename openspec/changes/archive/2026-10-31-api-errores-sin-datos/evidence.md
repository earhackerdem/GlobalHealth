# Evidence — api-errores-sin-datos

## Escenario → prueba → estado
| Escenario (`specs/privacy/error-reports/spec.md`) | Prueba (`backend/tests/api/routes/test_error_reports.py`) | Estado |
|---|---|---|
| Texto con un surrogate suelto en el alta | `test_signup_lone_surrogate_is_422_without_echo_or_log` | ✅ |
| Un 422 ordinario conserva su forma y pierde el eco | `test_ordinary_422_keeps_shape_without_input` | ✅ |
| Una clave desconocida con un surrogate suelto | `test_unknown_key_with_lone_surrogate_is_valid_utf8_422` | ✅ |
| Falla inesperada al guardar un antecedente | `test_sentry_event_has_no_body_locals_or_token` · `test_production_sentry_init_uses_the_privacy_options` (el init real) | ✅ |

## Rojo antes del verde
| Grupo | Corrida | Commit |
|---|---|---|
| 1 y 2 (un solo `test:`; los dos grupos son `single` y comparten archivo) | `uv run pytest tests/api/routes/test_error_reports.py` → **4 failed**: `500 == 422` (alta y hábitos), `'input' not in {…'input': 'sin-arroba'…}`, y el texto de prueba dentro del evento de Sentry (`body_bytes`, `json_body`) | `ec3968e` |

## Verde
| Corrida | Resultado | Commit |
|---|---|---|
| `FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **592 passed, 0 failed, 0 errors, 0 skipped** (línea base en `main`: 588); cobertura **96 %**; `app/main.py` 97 % (la línea sin cubrir es el `sentry_sdk.init` de producción) | `74908ed`, `traces_sample_rate` en el commit siguiente |
| `uv run ruff check app tests` · `ruff format --check` · `uv run mypy app` | limpios | ídem |
| `make tdd-check` | ✓ rojo `ec3968e`, pruebas sin tocar desde entonces | ídem |
| `openspec validate api-errores-sin-datos --strict` | válido | ídem |

Advertencias: 1047, todas previas al cambio (claves `changethis`, JWT de 10 bytes, `httpx` en `TestClient`). La única
que el cambio agregaba (`enable_tracing` obsoleto) se quitó con `traces_sample_rate=1.0`.

## Pase real (API reconstruida, `docker compose up -d --build --force-recreate --no-deps --wait backend` + `prestart.sh`)
| Intento | Antes (2026-10-31, `main`) | Después |
|---|---|---|
| `POST /users/signup` con `full_name` `"Dato-Sensible-Prueba…\ud800"` | **500**; el texto en `docker compose logs backend` | **422** `string_unicode` en `["body","full_name"]`, sin `input`; 0 apariciones en el log |
| alta con `email` `sin-arroba`, `password` `x` | 422 con `"input":"sin-arroba"` y `"input":"x"` | 422 con `loc`, `msg`, `type`, `ctx`; sin `input` |
| Sentry (sonda con `Transport` en memoria, `sentry_sdk` 2.70.0) | el texto en `request.data` y en `frames[].vars` | ausente; el evento conserva `RuntimeError` y su stack |

**Pase exploratorio en el navegador:** no aplica; el cambio no tiene superficie visible. Ninguna pantalla lee `input`
y los `msg` no cambian.

## Revisión, ronda 1 (una ronda: diff de código < 200 líneas)
Tres buscadores (seguridad y privacidad; criterios y pruebas; casa y restricciones) y un validador distinto que
reprodujo cada hallazgo. Gate y arreglos por delegación de Saúl Pérez (author).

| Id | Hallazgo (validado) | Decisión |
|---|---|---|
| M2 | `_valid_utf8` era código muerto: ningún surrogate llega al 422 fuera de `input` (18 tipos de petición, pydantic-core ya cambia a U+FFFD) | corregido: se quitó; exploración y diseño corregidos |
| M3 | el `sentry_sdk.init` de producción no tenía prueba | corregido: `init_sentry()` + `test_production_sentry_init_uses_the_privacy_options` (también cubre `send_default_pii`, L10) |
| L2 | la spec prometía 422 para «texto que no es Unicode válido»; un byte inválido da 400 | corregido: la spec dice surrogate (escape JSON) y el 400 |
| L3 | la propuesta decía que el 422 trae `url` | corregido |
| L4 | la aserción de `caplog` no puede fallar; el log lo cubre el pase real | corregido en el plan de pruebas |
| L5 | el «antes» citaba otra petición | corregido |
| L6 | `validation.md` tenía un paso que no comprobaba nada y jerga | reescrito |
| L7 | `tasks.md` sin palomear journal y PR | corregido |
| M1 | un NUL en un texto da 500 y el log trae los parámetros SQL (correo, nombre, hash) | deuda: `memory/closed/2026-10-31-nul-500-y-parametros-sql-en-el-log.md` |
| L1 | el discriminador (`section`, `when.kind`) repite el valor en `msg` y `ctx.tag` | deuda: `memory/closed/2026-10-31-ronda-1-de-api-errores-sin-datos.md` |
| L8 | cada transacción de Sentry lleva el `query_string` (el `code` de Google) | deuda: ídem |
| L9 | el teardown de la prueba lee `SENTRY_DSN` del entorno | falso positivo como defecto (ninguna parte lo define): ídem |

Rojo de la revisión: `4e41a4e`, 1 failed (`AttributeError: … no attribute 'init_sentry'`). Verde: **593 passed, 0
failed, 0 errors, 0 skipped**; cobertura 96 %, `app/main.py` 100 %; ruff y mypy limpios; `make tdd-check` ✓.
