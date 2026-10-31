---
date: 2026-10-20
state: frozen
anchor: journal: 2026-10-20 · perfil-eventos (review)
---

T3: `backend/tests/api/routes/test_profile.py:204-219` usa "2030-01-01" como fecha de nacimiento futura: desde 2030 falla siempre

**Verdict and why:** Preexistente (onboarding-perfil), fuera del diff; fix de una línea (hoy + 2 días) cuando el archivo se reabra

**State:** 🔒 frozen (pagado)

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-eventos (review)

**Pagado (2026-10-31):** validaciones-hoy-y-texto-invisible, PR #47: la prueba usa «pasado mañana en México» en lugar de `2030-01-01`.
