# Exploration — api-errores-sin-datos

**Matriz aceptada por delegación de Saúl Pérez (author), 2026-10-31 (`/epe-autopilot`).**

## 1. Entrada
Cuatro escenarios GIVEN/WHEN/THEN con datos concretos y un THEN observable (código, cuerpo, log, evento). Ninguno
impone una tecnología, salvo Sentry, que ya está en el código (`backend/app/main.py:18-19`).

## 2. Cobertura por escenario
| Escenario | Estado | Evidencia (2026-10-31) |
|---|---|---|
| Surrogate en el alta → 422, sin `input`, sin log | ❌ nuevo | `curl` al alta con `full_name` `"Dato-Sensible-Prueba\ud800"` → **500**; `docker compose logs backend` contiene el texto (`UnicodeEncodeError: 'utf-8' codec can't encode character '\ud800'`). No hay handler de `RequestValidationError` (`grep` en `backend/app`: solo `routes/profile.py:649`, que la *lanza*) |
| 422 ordinario conserva la forma, sin `input` | 🟡 parcial | hoy responde 422 con `loc`, `msg`, `type`, `ctx` **y `input`** (`"input":"bad"` en el alta). Ningún cliente lee `input` (`grep` en `frontend/src` y `android/app/src/main`); en el cliente generado es opcional (`frontend/src/client/types.gen.ts:1586`) |
| Clave desconocida con surrogate (hábitos) | ❌ nuevo | `_ClosedSchema` usa `extra="forbid"` (`backend/app/models.py:870`): pydantic pone el nombre de la clave en `loc`, así que quitar `input` no basta si la clave trae el surrogate |
| Evento de Sentry sin cuerpo, variables ni token | ❌ nuevo | sonda con `sentry_sdk` 2.70.0, FastAPI 0.141.1 y un `Transport` en memoria: con las opciones de hoy, el texto de prueba está en `request.data.diagnosis` y en `frames[].vars`; con `max_request_body_size="never"` + `include_local_variables=False` ya no está (solo quedaba en el código fuente de la propia sonda). El token ya lo filtra Sentry por defecto (`Authorization`) |

## 3. Lo que parecía útil y no lo fue
- `hide_input_in_errors=True` (ya en `_ClosedSchema`, `models.py:870`) solo esconde `input` en el **mensaje** de un
  `ValidationError` de pydantic, no en el `exc.errors()` que FastAPI devuelve; y solo aplica a los modelos cerrados.
- `ensure_ascii=True` al serializar: evita el 500, pero sigue devolviendo el valor (con escapes) y deja un surrogate
  suelto en el JSON, que algunos parsers estrictos rechazan.
- El veredicto S2 proponía un `before_send` que borre `request.data`. Con `max_request_body_size="never"` el cuerpo
  no se captura; un `before_send` sería una segunda red sobre algo que ya no existe.

## 4. Restricciones no funcionales
- **NFR-001 / privacidad:** el arreglo saca el dato de salud de la respuesta, del log y del reporte.
- **NFR-014 (observabilidad):** el evento conserva el tipo de excepción, el stack y la ruta; solo pierde valores.
- 🔒 «422 de pydantic íntegros en inglés» (`memory/closed/2026-10-19-422-de-pydantic-integros-en-ingles.md`): no se
  traduce nada; los `msg` quedan iguales.

## 5. Clasificación
**Extensión** de `backend/app/main.py`: un handler y dos opciones de Sentry. Sin preguntas abiertas.
