# Evidence — perfil-habitos-actividad-sueno (C-5, C-7, C-8)

## Suites

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Línea base (main tras el PR #33, fd6a7da): `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | 442 passed (cierre del PR #33; la ronda 2 no tocó código) | 0 | 0 | ✅ |
| Grupo 1, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **551 passed, 0 failed** (hábitos 301) · cobertura **96 %** | 0 (los UserWarning de configuración dev de siempre) | 0 | ✅ |
| `uv run mypy app` · `ruff check app` · `ruff format --check app` | limpios (25 archivos) | 0 | — | ✅ |
| Cliente regenerado (`scripts/generate-client.sh`) · `bunx tsc -p tsconfig.build.json --noEmit` | `zod.gen.ts` con días 1–7, minutos 1–600, horas sentado 0–24, nombre ≤ 60 · tsc 0 errores; imagen reconstruida, `Habits` del OpenAPI con `exercise`, `daily_movement`, `sleep` | 0 | — | ✅ |

## Red before green

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1 · backend | Re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` → **285 failed, 266 passed, 0 errors** (551). 117 por `extra_forbidden` en `["body","exercise"]`, `["body","daily_movement"]` o `["body","sleep"]` (los bloques no existen); el resto, comparaciones del cuerpo completo que ya esperan las tres claves nuevas en `null` (incluida la de "lo guardado no cambia" de los rechazos) | be8ae0f | 301/301 del archivo; suite completa 551 passed (verde 4556d92) | ✓ red be8ae0f, tests sin cambios hasta el verde |

Nota del grupo 1: el implementer se detuvo con 39 rojos porque `routes/profile.py:649` armaba siempre un `loc` de tres
elementos y el contrato pide cinco para los campos de cada actividad; el plan decía "NO se toca" la ruta. Era una
contradicción del plan: el orquestador corrigió `design.md` (una línea de la ruta, el campo partido por puntos) y el
implementer la aplicó; los errores de un solo nivel conservan su `loc`. El nombre de "Otra" quedó sin mínimo en el
esquema (vacío = sin contestar, "Escribe cuál."), así que `zod.gen.ts` lleva `max(60)` pero no `min(1)`.
