---
date: 2026-10-20
state: deferred
anchor: journal: 2026-10-20 · perfil-cronicas (review)
---

Ronda 2 de perfil-cronicas: el DELETE de diagnóstico bloquea `patient_profile` → `healthrecord` y el borrado de cuenta (cascada) va al revés: interbloqueo reproducido por SQL

**Verdict and why:** Exige borrar la cuenta y un diagnóstico del mismo usuario en el mismo instante; Postgres elige víctima y la otra operación termina. Entra si el borrado de cuenta se vuelve asíncrono o masivo

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-cronicas (review)

**Medido el 2026-10-31 (bd-candados-indices-y-log, PR #48):** con el DELETE de diagnóstico en pausa y un borrado de cuenta en paralelo, el código del PR da 200/200 (3 de 3). Sin `lock_diagnosis`, el DELETE moría con 500. La ventana que queda está entre `lock_profile` y `lock_diagnosis`. Sigue diferido, con su misma condición.
