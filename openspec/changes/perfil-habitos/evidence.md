# Evidence — perfil-habitos (Story C1: sustancias y humo)

## Suites

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Línea base antes del cambio: `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | 250 passed | 0 | 0 | ✅ |
| Grupo 1, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **289 passed, 0 failed** · cobertura total **96 %** | 0 (los UserWarning de configuración dev de siempre) | 0 | ✅ |
| `uv run mypy app` · `uv run ruff check app` | limpios (25 archivos) | 0 | — | ✅ |
| Grupo 2, re-corrido por el orquestador (Vite :5173 + backend del árbol): `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) | **101 passed, 0 failed** | 0 | 0 | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/ tests/` | 0 errores · 104 archivos, sin cambios | 0 | — | ✅ |
| Suite Playwright COMPLETA como CI (`PLAYWRIGHT_BASE_URL=http://localhost:8000`, imagen reconstruida con este frontend), 3 corridas | 2 × **203 passed**; 1 × 202 passed + 1 failed: `login.spec.ts:87` ("¡Qué gusto verte de nuevo!" vs el redirect de la home), que este cambio no toca; aislada con `--repeat-each=5`: 5/5 | 1 corrida con un fallo | 0 | 🟡 inestabilidad heredada, ver deuda |

### Tras el apply de la revisión (ronda 1)

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **303 passed, 0 failed** (hábitos 53, antes 39) · cobertura **96 %** | 0 | 0 | ✅ |
| Mutantes con un plugin fuera del repo (`MUT=nosort`, `ge`, `utc`) sobre `test_profile_habits.py` | 1, 5 y 1 fallos: los tres mueren (antes sobrevivían) | — | 0 | ✅ |
| `uv run mypy app` · `ruff check` · `ruff format --check` | limpios | 0 | — | ✅ |
| `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) | **115 passed, 0 failed** | 0 | 0 | ✅ |
| R1 sin el fix (`useAuth.ts` de `43f08be`) → con el fix, `-g "R1 otro paciente" --project=chromium` | 1 failed (B ve "Actual" marcado) → 2 passed | — | 0 | ✅ |
| Fila 7 (R4) `--repeat-each=5` en chromium; fila 7 y R14 en s26-ultra | 6 passed · 11 passed | 0 | 0 | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/ tests/` | 0 errores · 104 archivos, sin cambios | 0 | — | ✅ |
| Suite Playwright COMPLETA como CI, imagen reconstruida, 3 corridas | 217 passed · 216 + 1 failed (`reset-password.spec.ts:90`) · 215 + 2 failed (ese y `login.spec.ts:87`); los dos specs solos `--repeat-each=10`: 151 passed | 2 corridas con fallos heredados | 0 | 🟡 inestabilidad heredada (misma tasa que antes del apply), ver deuda |

### Tras el apply de la revisión (ronda 2)

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **304 passed, 0 failed** (hábitos 54: + "No" guarda `False`, N3) · cobertura **96 %** | 0 | 0 | ✅ |
| `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra), corrida del fixer | **119 passed, 0 failed** | 0 | 0 | ✅ |
| N1 sin el fix (`main.tsx` de `7872cdf`) → con el fix, `-g "R2 \(N1\)" --project=chromium` | 1 failed (la pestaña 1 sigue en `/perfil/habitos` con los datos de A) → 2 passed | — | 0 | ✅ |
| N2: R1 con un fix estrecho (`removeQueries(["habits"])`) | 2 failed (el menú de B muestra el correo de A) → con `clear()`, verde | — | 0 | ✅ |
| Sondas del validador de la ronda 2, después del fix | ya no pueden guardar: la pestaña 1 sale de la pantalla de hábitos (y del diálogo "Editar datos básicos") en cuanto la otra cambia la sesión | — | — | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/ tests/` | 0 errores · 104 archivos, sin cambios | 0 | — | ✅ |
| Suite Playwright COMPLETA como CI, imagen reconstruida, 3 corridas | 221 passed · 221 passed · 220 + 1 failed (`reset-password.spec.ts:90`, heredado) | 1 corrida con el fallo heredado | 0 | 🟡 inestabilidad heredada, ver deuda |

## Red before green

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1 · backend | `uv run pytest tests/api/routes/test_profile_habits.py -q` → **39 failed, 0 passed, 0 errors**: todas por 404 en `/api/v1/profile/habits` (la ruta no existía) | d15b2ba | 39/39 del grupo; suite completa 289 passed | ✓ red commit d15b2ba, test paths sin cambios desde entonces |
| 2 · frontend | `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts --project=chromium` → **13 failed, 38 passed, 0 errores de setup**: 11 sin enlace a `/perfil/habitos` (timeout de `waitForURL`), 2 citadores ("la tarjeta habits es un enlace") | ca29b35 | 101 passed (chromium + s26-ultra) | ✓ red commit ca29b35, test paths sin cambios desde entonces |

## Criterio → prueba

| AC / escenario | Prueba | Estado |
|---|---|---|
| C-1 Alcohol actual con AUDIT-C | `test_c1_current_alcohol_with_audit_c_round_trip` · e2e fila 1 | ✅ |
| C-1 Lo dejó, con la edad | `test_c1_quit_alcohol_with_age_round_trip` · e2e fila 2 | ✅ |
| C-1/C-2 Edad mayor que la actual | `test_c1_c2_age_above_current_rejected_nothing_saved` (3 campos), `test_c1_c2_age_without_birth_date_accepted` · e2e fila 3 | ✅ |
| C-1 Lo que no aplica se descarta | `test_c1_what_does_not_apply_is_dropped` (7 reglas), `test_c1_switch_current_to_never_drops_stored_audit_c`, `test_c1_dropped_age_is_not_validated` · e2e fila 4 | ✅ |
| C-2 Tabaco que dejó y vapeador actual | `test_c2_former_tobacco_and_current_vaping_round_trip` · e2e fila 5 | ✅ |
| C-2 Empezó después de dejarlo | `test_c2_start_age_after_quit_age_rejected` · e2e fila 6 | ✅ |
| C-3 Humo ajeno y "No me expongo" | `test_c3_secondhand_places_then_not_exposed`, `test_c3_exposed_without_places_rejected` · e2e fila 7 | ✅ |
| C-4 Humo de leña | `test_c4_former_wood_smoke_round_trip` · e2e fila 8 | ✅ |
| Contesta solo una cosa | `test_c_only_vaping_answered_rest_stays_null` · e2e fila 9 | ✅ |
| Fuera de escala | `test_c_out_of_scale_answers_rejected_habits_unchanged` (17 casos: 12 del grupo 1 y 5 cotas inferiores de la revisión, R7) | ✅ |
| C-6 Sin puntaje ni riesgo | `test_c6_no_score_or_risk_in_the_response` · e2e fila 11 | ✅ |
| A-1 / sin captura / la tarjeta abre su pantalla | `profile-history.spec.ts` S01, `profile.spec.ts` escenario 11, e2e fila 14 | ✅ |
| Hábitos solo del paciente y cifrados | `test_c_habits_isolated_and_encrypted_at_rest`, `test_c_habits_require_consent` | ✅ |

## Exploración en Chrome (agente, antes de la validación humana)

Vite :5173 contra el backend del árbol, cuenta de prueba local nueva (nacida el 15/03/1990, 36 años), ventana de
814 px y después de 500 px (el mínimo de Chrome; 384 px lo cubre el proyecto s26-ultra de Playwright).

| Intento | Qué pasó |
|---|---|
| Abrir "Mi perfil médico" | Tarjeta "Hábitos · Sin llenar", con enlace; ya no dice "Los hábitos llegan pronto" |
| Alcohol "Actual" | Aparecen las tres preguntas del AUDIT-C, "Sobre todo fines de semana" y la ayuda de qué es una bebida |
| "Lo dejé" con 40 años y Guardar | "La edad no puede ser mayor que tu edad actual" junto al campo, `aria-invalid`, foco ahí; no se guarda |
| La misma edad con "3.5", "-5", "abc", "🍺" | "Escribe solo el número." junto al campo cada vez; no se guarda |
| " 30 " con espacios | Se acepta, guarda 30 y vuelve a `/perfil` con "Con datos"; el GET ya no trae las respuestas del AUDIT-C (descartadas por "Lo dejé") |
| Reabrir | "Lo dejé" y 30 precargados |
| Tabaco "Antes", empezó 30, dejó 18 | "No puede ser mayor que la edad en que lo dejaste" junto a la edad de inicio, con foco |
| Corregido (18/30), vapeador "Actual", humo en "Casa" + "Trabajo o escuela" 2 días, leña "Antes" 12 años | Guardado tal cual (GET) |
| Doble clic real en "Guardar" | 1 PUT (el botón se deshabilita al guardar). Tres clics sintéticos en el mismo milisegundo mandaron 2 PUT idénticos: inofensivo, el PUT reemplaza el cuestionario |
| "No me expongo" | Apaga los lugares y oculta los días; elegir otro lugar los vuelve a mostrar; desmarcar todo deja el bloque sin contestar |
| "No me expongo" y "Cancelar" | Vuelve a `/perfil` sin guardar: el GET sigue con casa y trabajo |
| Caso extremo (4+ por semana, 10 o más, a diario, fines de semana) | Guardado; la edad de "Lo dejé" se descarta; ni la pantalla de hábitos ni "Mi perfil médico" dicen "riesgo", "puntaje" ni "AUDIT" |
| "Actual" → "Nunca" y Guardar | Las preguntas del AUDIT-C se ocultan y el GET las trae en null |
| 500 px | Sin scroll horizontal ni elementos fuera del ancho; "Guardar" y "Cancelar" al final, alcanzables |
| 384 px (medido en la revisión, R11) | design.md prometía este ancho y la pasada en Chrome no llegó (mínimo 500), y s26-ultra no mide el desborde. El validador lo midió con Playwright a 384 px, con todos los bloques desplegados: `scrollWidth` igual al ancho de la ventana y ningún elemento fuera |
| Consola | Solo un error de una extensión de Chrome ajena a la app (`chrome-extension://…`, 401 de "Flags") |

Sin defectos dentro del plan.

## Entorno

- 2026-10-21, ronda 2: Saúl Pérez sospechó que el paso de datos entre cuentas (N1) venía de tener dos instancias y
  pidió apagar la que no era de la sesión. Se detuvo el `fastapi dev` PID 1076 (y su worker) con TERM; desde entonces
  `:8000` es solo el contenedor. N1 se reprodujo igual con un solo backend: el fallo está en el navegador (token
  compartido entre pestañas y datos en memoria), no en el servidor.

- Dos backends en `:8000`: el `fastapi dev` de larga duración (PID 1076, que recarga este árbol) en `127.0.0.1` y el
  contenedor en `*:8000`. `localhost` resuelve a `::1`, así que el navegador hablaba con el contenedor viejo y la BD
  de desarrollo no tenía la migración (`make migrate` corre dentro de ese contenedor). Se reconstruyó la imagen
  (`docker compose build backend` + `make up`, que migró a `7d3e9a1c5b42`) antes del rojo del grupo 2 y otra vez
  antes de la suite completa.

## Deuda

- **Flake heredado** `login.spec.ts:87`: la misma familia que `admin.spec.ts:204` (el saludo contra el redirect de la
  home), agregado en la revisión (R25) al pendiente del inbox de los e2e inestables heredados
  (`memory/inbox/2026-10-20-fix-aparte-e2e-intermitentes-heredados-admin.md`).
- **Sin aviso de cambios sin guardar:** salir de la pantalla pierde lo contestado (declarado en design.md § Risks).
- **Dos formas de error en el perfil:** el historial responde `detail` como texto; los hábitos, con `loc` (design.md
  Decision 4). Unificar el historial queda fuera.
- **`lint.py` con el Python del sistema** marca como error de sintaxis el `except A, B:` (PEP 758) de
  `profile.py:220`; lo reportó el implementer. Ya está en el inbox del template (2026-10-20).
