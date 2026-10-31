# Design

Status: APPROVED
Approved: 2026-10-31, by delegation of Saúl Pérez (author): «toma las tareas que correspondan a fast api y
resuélvelas de manera autónoma… quiero ver hasta dónde llegas» (`/epe-autopilot`)

## Context
Los validadores del perfil reciben «hoy» como parámetro (`routes/profile.py:169`, `:646`), salvo
`validate_birth_date`. Hábitos ya tiene el criterio de «nada visible» en la API y en la pantalla.

## Goals / Non-Goals
**Goals:** la fecha de nacimiento se mide con el «hoy» de México; un texto invisible cuenta como vacío en el historial,
en la API y en la pantalla; la prueba de la fecha futura no caduca.
**Non-Goals:** la edad que calcula la web con la fecha del aparato (deuda de la web); otros campos de texto fuera del
historial (alergias, trabajo); cambiar mensajes.

## Interface contract
- `app.models.validate_birth_date(birth_date: date, today: date) -> None`: mismos `ValueError` es-MX; futuro =
  `birth_date > today`. `update_profile` (`routes/profile.py`) le pasa `datetime.now(MEXICO_CITY).date()`, a través
  del `datetime` del módulo (lo que `freeze_routes_clock` congela).
- `app.models._is_filled(value)`: una cadena cuenta solo si `not _is_blank(value)`.
- `frontend/src/components/Profile/text.ts` (nuevo): `export const isBlank = (text: string) => boolean`, la misma
  expresión de `HabitsForm.tsx:146`; `HabitsForm.tsx` la importa de ahí.
- `HistoryEntryForm.tsx` `handleSubmit`: un valor que `isBlank` no entra en `body` (y por eso dispara el mensaje de
  requerido de la pantalla, en la caja de «¿Cuál fue?»).

## Decisions
1. **`today` como parámetro** (patrón de la casa). Perdió: `today_mx()` en `app/core` (exploración §3).
2. **Rechazar, no vaciar,** el texto invisible del historial: el campo es requerido y el mensaje ya existe.
3. **Un `isBlank` compartido** en la pantalla, para que historial y hábitos no diverjan (era la recomendación del
   veredicto B2). Perdió: copiar la expresión.
4. **Por delegación:** la prueba de la fecha futura usa «pasado mañana en México» (dos días cubren cualquier zona del
   runner).

## Test plan (one row per scenario, mandatory)
| Spec · scenario | Test |
|---|---|
| patient-profile · Fecha de nacimiento futura rechazada | `backend/tests/api/routes/test_profile.py::test_ac2_future_birth_date_rejected_profile_unchanged` (fecha relativa) |
| patient-profile · «Hoy» es el de Ciudad de México | `backend/tests/api/routes/test_profile.py::test_birth_date_today_is_mexico_city` |
| patient-profile · «¿Cuál fue?» con un texto invisible | API: `backend/tests/api/routes/test_profile_history.py::test_past_other_invisible_text_is_required` · pantalla: `frontend/tests/profile-history.spec.ts` «S04b …» (chromium y s26-ultra) |
| patient-profile · Un texto visible con un invisible dentro sí cuenta | `backend/tests/api/routes/test_profile_history.py::test_past_other_visible_text_with_zero_width_is_saved` |

## Non-functional constraints addressed
NFR-012 sin cambios de texto; NFR-009 una prueba por escenario.

## Risks / Trade-offs
- [Una fila guardada antes con texto invisible] → se sigue leyendo igual; solo un nuevo guardado la rechaza.
- [Los e2e corren contra la imagen del backend, que lleva el build del frontend] → reconstruir antes (AGENTS.md).

## Gate that closes the work
Backend: `FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` con 0/0/0 y cobertura ≥ 90, ruff y mypy.
Frontend: `bunx tsc -p tsconfig.json --noEmit`, `bun run lint` (biome, sin cambios ajenos), y
`PLAYWRIGHT_BASE_URL=http://localhost:8000 bunx playwright test profile-history.spec.ts profile-habits.spec.ts`
verdes en chromium y s26-ultra. `openspec validate validaciones-hoy-y-texto-invisible --strict`. `make tdd-check`.
