---
date: 2026-10-20
state: deferred
anchor: journal: 2026-10-20 · perfil-eventos (review)
---

S2: si se configura `SENTRY_DSN`, un 500 envía el body del request (datos de salud en claro) a Sentry (`backend/app/main.py:18-19`, defaults de sentry_sdk)

**Verdict and why:** Heredado del template, dormido hoy (`SENTRY_DSN` no definido en ningún lado); afecta a todas las rutas de salud, no solo a las nuevas. Antes de activar Sentry: `max_request_body_size="never"` + `before_send` que borre `request.data`. Sube a alto si llega a producción con DSN

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-eventos (review)
