---
date: 2026-10-20
state: deferred
anchor: journal: 2026-10-20 · perfil-cronicas (review)
---

Ronda 2 de perfil-cronicas: el DELETE de diagnóstico bloquea `patient_profile` → `healthrecord` y el borrado de cuenta (cascada) va al revés: interbloqueo reproducido por SQL

**Verdict and why:** Exige borrar la cuenta y un diagnóstico del mismo usuario en el mismo instante; Postgres elige víctima y la otra operación termina. Entra si el borrado de cuenta se vuelve asíncrono o masivo

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-cronicas (review)
