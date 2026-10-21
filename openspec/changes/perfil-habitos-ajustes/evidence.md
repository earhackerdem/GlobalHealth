# Evidence — perfil-habitos-ajustes (C-10…C-14)

## Suites

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Línea base (main tras el PR #30): `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | 304 passed | 0 | 0 | ✅ |
| Grupo 1, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **342 passed, 0 failed** (hábitos 92) · cobertura **96 %** | 0 (los UserWarning de configuración dev de siempre) | 0 | ✅ |
| `uv run mypy app` · `ruff check app` · `ruff format --check app` | limpios (25 archivos) | 0 | — | ✅ |
| Grupo 2, re-corrido por el orquestador (Vite :5173 + backend del contenedor con el contrato nuevo): `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) | **137 passed, 0 failed** | 0 | 0 | ✅ |
| R1 en s26-ultra tras endurecer la conexión de los e2e: `-g "R1 otro paciente" --project=s26-ultra --repeat-each=10` | 11 passed (setup + 10) | 0 | 0 | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/ tests/` | 0 errores · 105 archivos, sin cambios | 0 | — | ✅ |
| Límites escritos a mano: `grep -nE "\b(130\|100\|30\|24\|7)\b" frontend/src/components/Profile/HabitsForm.tsx` | solo `className="w-24"` (ancho, no límite); las escalas salen de `zod.gen.ts` | — | — | ✅ |
| Suite Playwright COMPLETA como CI (`PLAYWRIGHT_BASE_URL=http://localhost:8000`, imagen reconstruida con esta rama), 2 corridas | **239 passed** · 238 passed + 1 failed: `login.spec.ts:87`, el heredado del saludo contra el redirect de la home (en el inbox de deudas) | 1 corrida con el heredado | 0 | 🟡 inestabilidad heredada |

## Red before green

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1 · backend | `uv run pytest tests/api/routes/test_profile_habits.py -q` → **77 failed, 15 passed, 0 errors**: el modelo viejo rechaza el vapeador como objeto y los campos nuevos (`extra_forbidden`), falta `upgrade_stored_habits` (ImportError dentro de 6 tests) y la fila con la forma anterior se lee vacía | 97074f1 | 92/92 del archivo; suite completa 342 passed | ✓ red 97074f1, tests sin cambios hasta el verde 7e9b05b |
| 2 · frontend | `bunx playwright test tests/profile-habits.spec.ts` → **32 failed, 27 passed** (16 + 13 por proyecto, 0 errores de setup): faltan las preguntas nuevas, el estado, el guardado automático y D20; el vapeador sembrado como objeto no se ve elegido | 1cfa5ce | 59/59 (verde 7b56610) | ✓ red 1cfa5ce, tests sin cambios hasta el verde 7b56610. Después, un `test:` propio (1facd80): formato de biome y `Connection: close` en la API de los e2e (un `socket hang up` de R1 en s26-ultra, sin aserción cambiada). Después hubo otro `test:` (a985310, formato de ruff en un caso fuera de escala), y `make tdd-check` ancló en a985310, no en 1facd80 (*corrección, revisión ronda 1, D1*; deuda T6 conocida: pasa en vacío para ese commit) |

## Criterio → prueba

| AC / escenario | Prueba | Estado |
|---|---|---|
| C-1/C-10 Lo dejó, con la edad de inicio y la de fin | `test_c1_c10_quit_alcohol_with_start_and_quit_age_round_trip` · e2e fila 2 | ✅ |
| C-10 Alcohol: empezó después de dejarlo | `test_c2_c10_c12_start_age_after_quit_age_rejected[alcohol]` · e2e fila 3 | ✅ |
| C-1/C-2 Una edad mayor que la actual (las 8 edades) | `test_c1_c2_age_above_current_rejected_nothing_saved`, `test_c1_c2_age_without_birth_date_accepted` · e2e fila 4 | ✅ |
| C-1 Lo que no aplica se descarta | `test_c1_c11_what_does_not_apply_is_dropped`, `test_c1_switch_current_to_never_drops_stored_age_and_audit_c` · e2e fila 5 | ✅ |
| C-2 Tabaco que dejó, y vapeador actual | `test_c2_former_tobacco_and_current_daily_vaping_round_trip` · e2e fila 6 | ✅ |
| C-2 Empezó después de dejarlo | `…start_age_after_quit_age_rejected[tobacco]` · e2e fila 7 | ✅ |
| C-11 Vapeador actual algunos días | `test_c11_current_vaping_some_days_round_trip` · e2e fila 8 | ✅ |
| C-11 Vapeador de antes, y luego todos los días | `test_c11_some_days_then_daily_then_former` · e2e fila 9 | ✅ |
| C-3 Humo ajeno | existentes · e2e fila 10 | ✅ |
| C-4/C-12 Humo de leña de antes, como rango | `test_c4_c12_former_wood_smoke_round_trip`, `…[wood_smoke]` · e2e fila 11 | ✅ |
| Contesta solo una cosa | e2e fila 12 | ✅ |
| Respuestas fuera de su escala | `test_c_out_of_scale_answers_rejected_habits_unchanged` (días 0/31, horas 0/25, vapeador como texto, `years` en el PUT) | ✅ |
| Lo guardado antes se sigue leyendo | `test_legacy_stored_habits_still_read`, `test_upgrade_stored_habits_unit` | ✅ |
| C-6 Sin puntaje ni índice | `test_c6_no_score_or_risk_in_the_response` · e2e fila 15 ("horas-año") | ✅ |
| C-13 Una respuesta se guarda al elegirla | e2e fila 16 | ✅ |
| C-13 Un número se guarda al salir de su campo | e2e fila 17 | ✅ |
| C-13/C-14 Con un error no se guarda nada | e2e fila 18 | ✅ |
| C-13/D20 Botones desactivados mientras guarda | e2e fila 19 | ✅ |
| C-13 Cancelar deja todo como al abrir | e2e fila 20 | ✅ |
| C-14 Fuera de escala al salir del campo | e2e fila 21 + grep de límites | ✅ |
| Aislados y cifrados | `test_c_habits_isolated_and_encrypted_at_rest` (también `some_days` y `days_last_30` en claro) | ✅ |

## Exploración en Chrome (agente, antes de la validación humana)

### Primera versión, con guardado automático (retirado por la Decision 8; queda como historia)

Imagen reconstruida con esta rama en `localhost:8000`, cuenta de prueba local nueva (nacida el 15/03/1990, 36 años, con
tabaco "Nunca" sembrado), ventana de 580 px. Los `PUT` se contaron con el lector de red del navegador.

| Intento | Qué pasó |
|---|---|
| Alcohol "Actual" | Aparece "¿A qué edad empezaste a tomar?" con "Sin contar probaditas."; el chip se guarda solo ("Guardado", 1 `PUT`) |
| Edad de inicio 40 y Tab | "La edad no puede ser mayor que tu edad actual" junto al campo (`aria-describedby` = ayuda + error), estado "Sin guardar: corrige el campo marcado", el foco sigue al siguiente control, 0 `PUT` |
| Corregido a 17 y Tab, luego recargar | "Guardado" con 1 `PUT`; tras recargar, 17 sigue ahí |
| Vapeador "Actual" → "Algunos días" → 31 días | "Debe estar entre 1 y 30" y 0 `PUT`; con 12, "Guardado". 3 `PUT` en total (dos chips y el número) |
| Leña "Antes" | Aparecen inicio, fin y horas al día; ya no "Años con humo de leña" |
| Escribir 3 horas y, sin salir del campo, tocar "‹ Mi perfil médico" | Al salir se manda lo pendiente (1 `PUT`); al reabrir, 3 horas y 12 días |
| Leña "Actual" y triple clic inmediato en "Guardar" | 1 solo `PUT`, un aviso "Hábitos guardados", vuelve a `/perfil` |
| Tabaco "Actual" (guardado solo) y doble clic en "Cancelar" | Vuelve con un aviso "Se descartaron los cambios"; el GET trae tabaco "Nunca" y la leña como estaba al abrir |
| Otra pestaña quita la sesión (lo que hace "Cerrar sesión") | La pestaña con los hábitos se va sola a `/login` |
| Ancho y consola | Sin scroll horizontal a 580 px (384 lo cubre s26-ultra); en consola solo el error de una extensión de Chrome ajena a la app |

Sin defectos dentro del plan.

## Entorno

- Durante el grupo 2 la imagen no se podía construir (su `bun run build` corre `tsc` y `HabitsForm.tsx` usaba la forma
  vieja hasta el verde). Para que los e2e del rojo hablaran con el contrato nuevo se copiaron `models.py` y
  `routes/profile.py` al contenedor en marcha (`docker compose cp`; `fastapi dev` recarga). Tras el verde se reconstruyó
  la imagen y la suite completa corrió contra ella.

## Deuda

- **Doble clic en el resto de la app (D20):** fila en la tarea de deudas; aquí solo se aplica a hábitos.
- **Un error que no es 422 al tocar "Guardar" o "Cancelar"** se avisa solo en la línea de estado ("No se pudo
  guardar"), sin aviso emergente (lo señaló el implementer; el contrato solo habla del estado).
- **Flake heredado** `login.spec.ts:87` (en el inbox de deudas).
- **`make tdd-check` ancla en el `test:` más nuevo** (T6, ya ⏸️): para el grupo 2 la medición real es 1cfa5ce → 7b56610.
- **`lint.py` del harness** compila con el Python 3.9 del sistema y marca el `except A, B:` (PEP 758) de
  `profile.py`; ya en el inbox del template.
