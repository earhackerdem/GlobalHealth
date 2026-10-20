# Evidence — perfil-eventos

Date: 2026-10-20 · Branch: `feat/perfil-eventos` · PR: (pendiente, tarea 3.3)

## Automated tests

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` (grupo 1, re-corrido por el orquestador) | **190 passed, 0 failed** · cobertura total **96 %** | 0 | 0 | ✅ |
| `cd backend && uv run mypy app` | Success: no issues found in 25 source files | 0 | — | ✅ |
| Grupo 2: `bunx playwright test tests/profile-history.spec.ts tests/profile.spec.ts --project=chromium` (vs Vite :5173), `tsc --noEmit`, `biome check src/` | **23 passed, 0 failed**; tsc 0 errores; biome "No fixes applied" | 0 | 0 | ✅ |
| Estabilidad del cambio: `PLAYWRIGHT_BASE_URL=http://localhost:8000 bunx playwright test tests/profile-history.spec.ts tests/profile.spec.ts --repeat-each=5` (chromium + s26-ultra, imagen reconstruida) | **221 passed, 0 failed, 0 flaky** | 0 | 0 | ✅ |
| Suite Playwright COMPLETA como CI (ambos proyectos, build servido por el backend en :8000), 6 corridas | 4 × **141 passed**; 1 × 140 passed + 1 failed (`reset-password.spec.ts:32`, heredado, sola pasa 49/49 con `--repeat-each=8`); 1 × 139 passed + 2 failed ("toBeVisible"/"element(s) not found", no identificados en esa corrida). Ningún fallo en specs de este cambio | 0 | 0 | 🟡 ver deuda |
| Tarea 1.0: `TZ=<zona> uv run pytest tests/api/routes/test_profile.py -q` con Asia/Tokyo, UTC y America/Mexico_City | 22 passed en las tres (antes del arreglo: **1 failed** con Asia/Tokyo, el fallo del CI del PR #17) | 0 | 0 | ✅ |

## Red before green (tasks executed as test→impl)

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1.0 (single, solo test) | `TZ=Asia/Tokyo uv run pytest tests/api/routes/test_profile.py -q` → **1 failed, 21 passed** (`'2026-10-20' != '2026-10-21'`, mismo defecto que el CI del PR #17 a las 00:11 UTC) | 79a5cc9 | 22 passed en Tokio/UTC/México | n/a (single) |
| 2 · frontend | `bunx playwright test tests/profile-history.spec.ts tests/profile.spec.ts --project=chromium` → **17 failed, 6 passed, 0 errores de setup** (testids, URLs y textos inexistentes; el sembrado por API y el setup funcionaron) | 6c7dfca | 23 passed | ✓ red commit 6c7dfca, test paths sin cambios desde entonces |
| 1 · backend | `uv run pytest tests/api/routes/test_profile_history.py -q` → **22 failed, 0 errors** (404 de rutas inexistentes, `KeyError: blood_type`, 200 donde se espera 422); `test_profile.py` siguió en 22 passed | 90af786 | 44/44 del grupo; suite completa 190 passed | ✓ red commit 90af786, test paths sin cambios desde entonces |

## Traceability AC → test

| Scenario (design § Test plan) | Test(s) | File | Status |
|---|---|---|---|
| 3 Enfermedad pasada del catálogo | `test_s03_past_illness_from_catalog` | `backend/tests/api/routes/test_profile_history.py` | ✅ (+ e2e en grupo 2) |
| 4 Fuera del catálogo | `test_s04_past_illness_other_with_text`, `test_s04_past_illness_other_without_text_rejected` | ídem | ✅ |
| 5 Cirugía con todos sus datos | `test_s05_surgery_with_all_fields_round_trip` | ídem | ✅ (+ e2e) |
| 8 Falta el dato requerido | `test_s08_surgery_without_name_rejected`, `test_s08_past_without_condition_rejected`, `test_s08_fracture_without_what_rejected` | ídem | ✅ |
| 9 Registro vacío | `test_s09_empty_transfusion_rejected` | ídem | ✅ (+ e2e) |
| 10 Editar y eliminar | `test_s10_edit_fracture_side_then_delete` | ídem | ✅ (+ e2e) |
| 11 Edad con fecha de nacimiento | `test_s11_age_when_stored_as_answered` | ídem | ✅ (+ e2e) |
| 15 Imposibles | `test_s15_impossible_when_with_birth_date`, `test_s15_impossible_age_without_birth_date` | ídem | ✅ |
| 16 Marcar ninguna | `test_s16_mark_section_none` | ídem | ✅ (+ e2e) |
| 17 No con registros | `test_s17_cannot_mark_none_with_entries` | ídem | ✅ |
| 18 Agregar quita la marca | `test_s18_adding_entry_clears_none_mark` | ídem | ✅ (+ e2e) |
| 19 Deshacer | `test_s19_undo_none_mark`, `test_s19_none_on_section_outside_story_rejected` | ídem | ✅ (+ e2e) |
| 20 Grupo sanguíneo | `test_s20_blood_type_set_change_and_clear` | ídem | ✅ (+ e2e) |
| 21 Grupo fuera del catálogo | `test_s21_blood_type_outside_catalog_rejected` | ídem | ✅ |
| 22 Ajeno indistinguible | `test_s22_foreign_entry_indistinguishable_from_missing` | ídem | ✅ |
| 23 Cifrado en reposo | `test_s23_history_none_mark_and_blood_type_encrypted_at_rest` | ídem | ✅ |
| Humo de consentimiento | `test_consent_history_routes_require_consent` (las 5 rutas) | ídem | ✅ |
| 1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13, 14, 16, 18, 19, 20 (e2e) | `S01`…`S20` en `profile-history.spec.ts` | `frontend/tests/profile-history.spec.ts` | ✅ chromium + s26-ultra |
| 2b Secciones listadas sin captura | "Escenario 11 (Secciones listadas sin captura)…" | `frontend/tests/profile.spec.ts` | ✅ chromium + s26-ultra |

## Visible surface (if applicable)

Grupo 1: BD de desarrollo migrada a `2c7fa6505d5c (head)`; `GET /api/v1/profile/history` sin token → 401 (la ruta
existe y exige sesión). UI: grupo 2.

### Exploración real con Claude in Chrome (tarea 3.1, 2026-10-20)

Sobre el build servido por el backend (`http://localhost:8000`, imagen reconstruida), con un usuario de prueba
local creado para la exploración (consentimiento aceptado, onboarding omitido):

| Prueba | Visto |
|---|---|
| "Mi perfil médico" recién estrenado | "Tu historial", "Llénalas a tu ritmo; todo es opcional. Crónicas y hábitos llegan pronto." y las 6 tarjetas en "Sin llenar" ✅ |
| Fractura con edad **200** sin fecha de nacimiento | Rechazada: "La edad debe estar entre 0 y 130 años" ✅ (el mensaje sale al pie del formulario, no junto al campo: cosmético) |
| Edad **"diez"** | Rechazada en el campo: "Escribe solo el número." ✅ |
| **Doble clic** en "Guardar" | Un solo registro ("1 registro") ✅ |
| Sin fecha de nacimiento → registrar 1990-03-15 en "Editar datos básicos" | "izquierdo · a los 10 años" pasa a "a los 10 años (≈2000)" ✅ |
| "Nunca me han transfundido" | Sección y título en "Ninguna", "Deshacer" visible ✅ |
| Transfusión en el año **1985** (antes del nacimiento) | Rechazada: "El año no puede ser anterior a tu nacimiento"; la sección sigue en "Ninguna" ✅ |
| Corregida a 2015 | "Transfusión · Parto · en 2015", "1 registro", aviso "Guardado. La sección ya no dice «ninguna»." ✅ |
| URL a mano `/perfil/cronicas` y `/perfil/xyz` | 404 de la app en es-MX ✅ |
| 384 px | La ventana del navegador no bajó del ancho de escritorio; lo cubre el proyecto Playwright s26-ultra (384×832), verde |

Hallazgos para el review (no se tocaron: fuera del plan):
- El aviso al marcar "ninguna" repite "Listo": título "¡Listo!" y texto "Listo: sección respondida".
- "El médico verá que lo respondiste, no que falta." (texto del prototipo) promete algo que llega con E3/E4
  (compartir); hoy nadie más ve el perfil.

## Cross regression

- `tests/api/routes/test_profile.py` (perfil, mediciones, AHF, onboarding): 22 passed en todo momento, también
  bajo tres zonas horarias.
- Suite completa del backend (expediente, recetas, consentimiento, OAuth, migraciones): 190 passed.

## Declared debt

- **Inestabilidad de la suite completa de Playwright fuera de este cambio:** en 2 de 6 corridas completas cayó
  algo ajeno a los specs del perfil (una vez `reset-password.spec.ts:32`, que lee Mailpit y sola pasa 49/49; otra
  vez 2 fallos no identificados). El CI corre con `--fail-on-flaky-tests`: si el PR cae ahí, el diagnóstico
  empieza por esta línea. Los specs del cambio: 0 fallos en 6 corridas completas + 221/221 en `--repeat-each=5`.

- **Build de la imagen del backend bloqueado por la red del daemon de Docker:** `docker compose build backend` y
  `docker pull ghcr.io/astral-sh/uv:0.9.26` se quedan sin respuesta (`DeadlineExceeded`); Docker Desktop sale
  por el proxy `http.docker.internal:3128`, mientras el host sí llega a ghcr.io y Docker Hub. Para el grupo 1 se
  copió `backend/app` al contenedor (`docker compose cp`, lo que hace la acción `sync` de `docker compose watch`)
  y se migró con `make migrate`. Hay que reconstruir la imagen cuando el daemon tenga red.
- **`make migrate` solo basta si el contenedor ya tiene el código nuevo** (reconstruido o con `watch`); el
  comentario de `project.mk` (PR #19) lo dice a medias. Reportado por el implementer.
- **`validate_birth_date` usa `date.today()` del servidor** y no la fecha de México: el mismo tipo de defecto
  que la tarea 1.0 arregló solo en el test; entre las 18:00 y las 24:00 de México, el "hoy" del servidor (UTC en
  producción) ya es mañana. Fuera de alcance: va al inbox.
- Mensajes es-MX que el contract no fijaba y eligió el implementer: "Registro eliminado", "No se puede cambiar la
  sección de un registro", "El año no puede ser anterior a 1900" (sin fecha de nacimiento) y edad negativa con
  el mensaje del rango 0–130. Los valores fuera de un enum devuelven el 422 estándar de pydantic, como `sex` hoy
  (veredicto de closed.md 2026-10-19).
