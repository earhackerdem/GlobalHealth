---
date: 2026-10-11
state: deferred
anchor: journal: 2026-10-11 · bd-pruebas-docker (review)
---

"Healthcheck de db-test por socket: ventana del server temporal"

**Verdict and why:** Riesgo teórico medido (ventana ≈160 ms, cierra ~4.4 s antes del primer probe; 0/5 reproducciones); fix opcional `pg_isready -h 127.0.0.1` si algún día flakea

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-11 · bd-pruebas-docker (review)
