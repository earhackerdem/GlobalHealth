# Evidence — perfil-habitos-actividad-sueno (C-5, C-7, C-8)

## Suites

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Línea base (main tras el PR #33, fd6a7da): `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | 442 passed (cierre del PR #33; la ronda 2 no tocó código) | 0 | 0 | ✅ |
| Grupo 1, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **551 passed, 0 failed** (hábitos 301) · cobertura **96 %** | 0 (los UserWarning de configuración dev de siempre) | 0 | ✅ |
| `uv run mypy app` · `ruff check app` · `ruff format --check app` | limpios (25 archivos) | 0 | — | ✅ |
| Grupo 2, re-corrido por el orquestador (Vite :5173 + API del contenedor con el contrato nuevo): `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) | **227 passed, 0 failed** | 0 | 0 | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/ tests/` · `grep -nE "\b(600\|60\|24\|7)\b" HabitsForm.tsx` | 0 errores · 104 archivos sin cambios · solo `className="w-24"` (ancho; ya estaba) | 0 | — | ✅ |
| Suite Playwright COMPLETA como CI (`PLAYWRIGHT_BASE_URL=http://localhost:8000`, imagen reconstruida con 0d49477), 2 corridas | **328 passed + 1 failed** en las dos: `reset-password.spec.ts:90` (chromium), timeout esperando el correo en Mailpit (`utils/mailpit.ts:45`), heredado (`memory/inbox/2026-10-20-fix-aparte-e2e-intermitentes-heredados-admin.md`); aislada con `--repeat-each=3` falla 1 de 3. El diff contra `main` no toca autenticación, correo ni recuperación (solo `models.py`, una línea de `routes/profile.py`, el cliente, `HabitsForm.tsx` y `profile.json`) | 0 | 0 | 🟡 intermitencia heredada ajena a hábitos; más frecuente que en el PR #33 (2/2 frente a 1/2) |
| Cliente regenerado (`scripts/generate-client.sh`) · `bunx tsc -p tsconfig.build.json --noEmit` | `zod.gen.ts` con días 1–7, minutos 1–600, horas sentado 0–24, nombre ≤ 60 · tsc 0 errores; imagen reconstruida, `Habits` del OpenAPI con `exercise`, `daily_movement`, `sleep` | 0 | — | ✅ |

## Red before green

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1 · backend | Re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` → **285 failed, 266 passed, 0 errors** (551). 117 por `extra_forbidden` en `["body","exercise"]`, `["body","daily_movement"]` o `["body","sleep"]` (los bloques no existen); el resto, comparaciones del cuerpo completo que ya esperan las tres claves nuevas en `null` (incluida la de "lo guardado no cambia" de los rechazos) | be8ae0f | 301/301 del archivo; suite completa 551 passed (verde 4556d92) | ✓ red be8ae0f, tests sin cambios hasta el verde |
| 2 · frontend | Re-corrido por el orquestador: `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` → **24 failed, 203 passed** (12 por proyecto, 0 errores de setup): la pantalla no tiene el grupo "¿Qué ejercicio haces?", ni el desplazamiento, ni el sueño; las 203 previas pasan | d630f04 · 7d5d76a (fila 10 corregida por el tester) | 227/227 de las tres suites de perfil (verde 0d49477) | ✓ red 7d5d76a, tests sin cambios hasta el verde |

Nota del grupo 1: el implementer se detuvo con 39 rojos porque `routes/profile.py:649` armaba siempre un `loc` de tres
elementos y el contrato pide cinco para los campos de cada actividad; el plan decía "NO se toca" la ruta. Era una
contradicción del plan: el orquestador corrigió `design.md` (una línea de la ruta, el campo partido por puntos) y el
implementer la aplicó; los errores de un solo nivel conservan su `loc`. El nombre de "Otra" quedó sin mínimo en el
esquema (vacío = sin contestar, "Escribe cuál."), así que `zod.gen.ts` lleva `max(60)` pero no `min(1)`.

Nota del grupo 2: el implementer devolvió la fila 10 (C-6) como prueba equivocada: `page.locator("main")` choca con el
modo estricto porque el layout anida dos `<main>` (`ui/sidebar.tsx:325` y `routes/_layout.tsx:31`, del esqueleto
`cb48c3a`). Volvió al tester, que la acotó a `main` interior (`.last()`) y agregó que ese contenedor tenga las
preguntas de hábitos antes de buscar palabras prohibidas; commit propio `test:` 7d5d76a. El `<main>` anidado quedó como
deuda (`memory/inbox/2026-10-26-main-anidado-en-el-layout.md`). El implementer también hizo que los chips del día
partan su texto (por `className` de `ChipGroup`, sin tocarlo): "Cargando cosas ligeras o subiendo escaleras seguido"
ensanchaba la página más allá de 384 px y rompía tres pruebas móviles previas que abren el menú lateral.
