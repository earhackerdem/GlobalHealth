---
date: 2026-10-31
state: deferred
anchor: journal: 2026-10-31 · bd-candados-indices-y-log: la base de datos con candados, índices y sin valores en el registro (M1, H1, R2, índices)
---
Ronda 1 de bd-candados-indices-y-log (PR #48): F2 queda como deuda; F4a y L-6 se congelan; los demás se corrigieron en el PR

**Verdict and why:** gate por delegación de Saúl Pérez (author), 2026-10-31.
- **F2 (deuda, baja):** `hide_parameters` quita el volcado de parámetros de SQLAlchemy, pero Postgres repite el valor en
  el `DETAIL` de una violación de unicidad, y psycopg lo mete en `str(exc)`.
  - 12 altas en paralelo con el mismo correo dan 1×200 y 11×500, y `docker compose logs backend` muestra
    `Key (email)=(…) already exists`. Con Sentry encendido, iría en el evento.
  - La carrera del alta ya existía antes del cambio, y el valor es el correo de quien lo intenta.
  - Para pagarla, atrapar `IntegrityError` en el alta y responder 400 «Ya existe una cuenta con ese correo».
- **F4a (congelado):** la rama de NUL de `authenticate` no fijaba `DUMMY_HASH` en una prueba. Se quitó en la revisión:
  `get_user_by_email` devuelve `None` con un NUL, y `authenticate` ya verifica contra `DUMMY_HASH` en ese caso.
- **L-6 (congelado):** el commit `f217b5f` repite el asunto del anterior. Ya está subido; no se reescribe historia con
  `--force` (AGENTS.md).

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-31 · bd-candados-indices-y-log: la base de datos con candados, índices y sin valores en el registro (M1, H1, R2, índices)
