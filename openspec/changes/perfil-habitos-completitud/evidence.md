# Evidence — perfil-habitos-completitud (C-15…C-17)

## Suites

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Línea base (main tras el PR #32): `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | 345 passed | 0 | 0 | ✅ |
| Grupo 1, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **444 passed, 0 failed** (hábitos 194) · cobertura **96 %** | 0 (los UserWarning de configuración dev de siempre) | 0 | ✅ |
| `uv run mypy app` · `ruff check app` · `ruff format --check app` | limpios (25 archivos) | 0 | — | ✅ |
| Grupo 2, re-corrido por el orquestador (Vite :5173 + API del contenedor con el contrato nuevo): `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) | **181 passed, 0 failed** | 0 | 0 | ✅ |
| `-g "C-17" --repeat-each=5` | 21 passed | 0 | 0 | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/ tests/` | 0 errores · 104 archivos sin cambios | 0 | — | ✅ |
| Límites escritos a mano: `grep -nE "\b(130\|100\|30\|24\|7)\b" frontend/src/components/Profile/HabitsForm.tsx` | solo `className="w-24"` (ancho); las escalas salen de `zod.gen.ts` (la rama entera de la unión) | — | — | ✅ |
| Suite Playwright COMPLETA como CI tras el grupo 2 (`PLAYWRIGHT_BASE_URL=http://localhost:8000`, imagen reconstruida), 2 corridas | 280 passed + 3 failed · 281 passed + 2 failed: la C-17 nueva (línea 2394) en las dos plataformas, más el heredado `login.spec.ts:87` en la primera | 0 | 0 | ❌ → defecto, ver abajo |
| Suite Playwright COMPLETA tras el arreglo 4ba7717 (imagen reconstruida), 2 corridas | **283 passed, 0 failed** en la segunda; en la primera 282 passed + 1 failed: `reset-password.spec.ts:90`, timeout esperando el correo en Mailpit (heredado, `memory/inbox/2026-10-20-fix-aparte-e2e-intermitentes-heredados-admin.md`), que solo pasa 19/19 con `--repeat-each=3` | 0 | 0 | ✅ (🟡 intermitencia heredada ajena a hábitos) |

## Red before green

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1 · backend | `uv run pytest tests/api/routes/test_profile_habits.py -q` → **73 failed, 121 passed, 0 errors**: las obligatorias devuelven 200 en vez de 422 (51), el esquema rechaza `"unknown"` con `int_parsing` (22, incluidos C-6 y el cifrado, que ahora guardan `"unknown"`) | 11f7b56 | 194/194 del archivo; suite completa 444 passed (verde 4d81f31) | ✓ red 11f7b56, tests sin cambios hasta el verde |
| 2 · frontend | `bunx playwright test tests/profile-habits.spec.ts` → **29 failed, 74 passed** (14 por proyecto + 1 intermitente, 0 errores de setup): falta el chip "No recuerdo", las obligatorias no se revisan al guardar (el `PUT` sale), falta la intro, y los mensajes de escala desaparecieron porque el cliente regenerado volvió unión los números | 8dac137 | 103/103 del archivo (verde ccd7820) | ✓ red 8dac137, tests sin cambios hasta el verde y el arreglo 4ba7717 |

Nota del grupo 2: el primer rojo del tester corrió contra un contenedor con la imagen vieja (creada antes del verde del
backend). La imagen no se podía reconstruir porque compila el frontend y `tsc` estaba rojo hasta el grupo 2; se copió
`backend/app/models.py` al contenedor (`fastapi dev` recarga, igual que el `sync` de `docker compose watch`) y el rojo
se volvió a correr. Al verde, la imagen se reconstruyó.

## Defecto de la suite completa: el error que aparecía mientras se escribe (C-17)

- **Síntoma:** solo en la suite completa (carga alta), en las dos plataformas, la C-17 (línea 2394) fallaba en la línea
  2422: la edad de fin con `aria-invalid="true"` mientras se escribía "1a". Sola pasaba.
- **Causa** (confirmada por el implementer con una reproducción determinista en el scratchpad, que retrasa 400 ms el
  temporizador de `pointerup`: 4/4 fallan sin el arreglo, 8/8 pasan con él): con carga, Chrome atiende el teclado antes
  que los temporizadores; la salida de la edad de inicio quedaba diferida (`afterPress`) y, al correr tarde, revisaba la
  pareja con el borrador de ese momento ("1a") y marcaba un error nuevo en el campo que se estaba escribiendo.
- **Arreglo** (4ba7717, solo `leave()` en `HabitsForm.tsx`): la pareja con el foco no recibe un error nuevo; sí se le
  quita o actualiza el que ya tenía. Sin cambios en tests.

Nota del grupo 1: `places` faltante conserva su mensaje de antes ("Elige dónde, o «No me expongo»"), más específico que
"Contesta esta pregunta."; el tester lo dejó así y el implementer lo mantuvo (`HABITS_MISSING_MESSAGE` en
`backend/app/models.py`). El caso de normalización `vaping-no-frequency-drops-days` se retiró: ese cuerpo ahora es 422 y lo
cubren los casos C-15 del vapeador "Actual" sin frecuencia.

El cliente regenerado (0a4d90d) deja `tsc` rojo en `HabitsForm.tsx` hasta el grupo 2 (los números ahora admiten
`"unknown"`).

## Criterio → prueba

| Escenario (spec delta) | Prueba | Estado |
|---|---|---|
| Escenarios de la C1 y de perfil-habitos-ajustes con datos completos (fila 1) | pytest existentes completados; e2e filas 1, 3–7, 9, 15, 23, 24, 26–28, 30, 31a–c, R1, N1, R9, R12, R14, N3, R18 | ✅ |
| Falta una pregunta de lo que eligió (C-15) | `test_c15_missing_required_answer_rejected_habits_unchanged` (48 casos: cada campo de la tabla, omitido y `null`), `test_c15_complete_answers_saved`, `test_c15_quit_alcohol_with_only_quit_age_rejected`; e2e "C-15 (completitud fila 2)" | ✅ |
| Alcohol actual sin las preguntas de frecuencia (C-15) | `test_c15_current_alcohol_without_frequency_questions_four_errors`; e2e "C-15 (completitud fila 3)", R14 | ✅ |
| No recuerda cuándo empezó (C-16) | `test_c16_unknown_start_age_with_quit_age_18_saved_and_read_back`, `test_c16_unknown_admitted_saved_and_never_compared`, `test_c16_number_beside_unknown_still_checked_against_current_age`; e2e "C-16 (completitud fila 4)" | ✅ |
| "No recuerdo" solo en lo que pasó (C-16) | `test_c16_unknown_in_current_amount_rejected`, `test_c16_unknown_where_never_admitted_is_schema_error`, `OUT_OF_SCALE_CASES` nuevos; e2e "C-16 (completitud fila 5)" | ✅ |
| Escribir un número quita "No recuerdo" (C-16) | e2e "C-16 (completitud fila 6)" | ✅ |
| Lo guardado a medias pide completar al guardar (C-15) | `test_c15_partial_row_saved_before_read_with_null`, `test_c15_partial_row_saved_before_resaved_as_is_rejected`; e2e "C-15 (completitud fila 7)" (GET simulado: el `PUT` ya no deja sembrarlo) | ✅ |
| Respuestas fuera de su escala / lo guardado antes se lee (filas 8, 9) | `OUT_OF_SCALE_CASES`, `test_legacy_stored_habits_still_read` (ningún campo vuelve `"unknown"`) | ✅ |
| No interpreta (C-6, fila 10) | `test_c6_no_score_or_risk_in_the_response` con `start_age: "unknown"`; e2e fila 15 | ✅ |
| El error se va al corregirlo (C-17) | e2e "C-17 (completitud fila 11)" (dos pruebas) | ✅ |
| Accesibilidad de "No recuerdo" (R7, D20) | e2e "C-16 (completitud fila 12)" y "marcar 'No recuerdo' es un cambio sin guardar" | ✅ |
| Aislados y cifrados (fila 13) | `test_c_habits_isolated_and_encrypted_at_rest` guarda `"unknown"`: no aparece en el texto guardado, sí al descifrar | ✅ |

## Exploración en Chrome (agente, antes de la validación humana)

Vite `localhost:5173` + API del contenedor, ventana de 500 px (más angosta que los 580 px del plan), cuenta de prueba
con 36 años y la sesión inyectada en la pestaña.

| Intento | Qué pasó |
|---|---|
| Intro | El texto nuevo, completo, arriba de las preguntas |
| Alcohol "Lo dejé" con solo 30 → "Guardar" | Sin guardar; "Contesta esta pregunta o marca «No recuerdo»." junto a la edad de inicio, foco ahí con `aria-invalid="true"` |
| "No recuerdo" en esa edad | Se va el error, el chip queda marcado |
| Escribir 16 con "No recuerdo" marcado | Se desmarca (`aria-pressed="false"`) |
| Marcar otra vez, "Guardar", reabrir | Guardado; "No recuerdo" marcado, el número vacío y 30 en la de fin; "Mi perfil médico" dice "Con datos" sin mostrar `unknown` |
| Alcohol "Actual" + tabaco "Actual" → "Guardar" | "Contesta esta pregunta." bajo frecuencia, fines de semana, bebidas y 6 o más, y en cigarros; "…o marca «No recuerdo»." en la edad de inicio del tabaco; foco en el primer chip de frecuencia; solo dos "No recuerdo" (las edades de inicio) |
| Elegir una frecuencia | Su mensaje se va; quedan los otros tres |
| "12a" en cigarros | Mientras escribe, nada; al salir, "Escribe solo el número." con `aria-invalid` |
| Volver y borrar la "a" | 12, sin mensaje ni `aria-invalid`, foco en el campo (C-17) |
| Tabaco "Antes" | "No recuerdo" en cigarros, inicio y fin, con nombres distintos |
| Completar todo y doble clic en "Guardar" | Vuelve a "Mi perfil médico" con lo guardado: `start_age: "unknown"` en alcohol y tabaco, 12 cigarros, fin 30 (GET de la API) |
| Ancho | `scrollWidth` 500 = ventana: sin desplazamiento lateral |
| Consola | Sin errores de la app (solo uno de una extensión de Chrome, ajeno) |
| Prototipo de producto (`perfil-secciones.html`, servido local) | Intro nueva, chips "No recuerdo" en las edades y en cigarros solo con "Antes"; marcar vacía el número y escribir desmarca; sin errores en consola |

## Entorno

macOS, Docker Desktop (API, BD y BD de prueba de `make up`), Vite `localhost:5173`, Playwright chromium + s26-ultra.

## Deuda

- La tabla de obligatoriedad vive en el servidor y en la pantalla (`HABITS_REQUIRED` en los dos); el servidor manda.
- Una salida de campo diferida por un toque sigue corriendo con el temporizador de `pointerup`: el arreglo impide errores
  nuevos en el campo con el foco, pero con mucha carga los mensajes de otros campos aún se pueden reacomodar tarde.
  Correrla en `click`/`focusin` quitaría la carrera de raíz (anotado por el implementer).
- El estrés de la C-17 en Vite no detecta esta clase de carrera; solo la suite completa contra `:8000` la mostró.
- `login.spec.ts:87` sigue intermitente (heredado, en el inbox de deudas).
