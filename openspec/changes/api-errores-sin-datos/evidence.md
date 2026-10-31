# Evidence — api-errores-sin-datos

## Escenario → prueba → estado
| Escenario (`specs/privacy/error-reports/spec.md`) | Prueba (`backend/tests/api/routes/test_error_reports.py`) | Estado |
|---|---|---|
| Texto con un surrogate suelto en el alta | `test_signup_lone_surrogate_is_422_without_echo_or_log` | ✅ |
| Un 422 ordinario conserva su forma y pierde el eco | `test_ordinary_422_keeps_shape_without_input` | ✅ |
| Una clave desconocida con un surrogate suelto | `test_unknown_key_with_lone_surrogate_is_valid_utf8_422` | ✅ |
| Falla inesperada al guardar un antecedente | `test_sentry_event_has_no_body_locals_or_token` | ✅ |

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
| alta con `email` `sin-arroba`, `password` `x` | 422 con `"input":"bad"` | 422 con `loc`, `msg`, `type`, `ctx`; sin `input` |
| Sentry (sonda con `Transport` en memoria, `sentry_sdk` 2.70.0) | el texto en `request.data` y en `frames[].vars` | ausente; el evento conserva `RuntimeError` y su stack |

**Pase exploratorio en el navegador:** no aplica; el cambio no tiene superficie visible. Ninguna pantalla lee `input`
y los `msg` no cambian.
