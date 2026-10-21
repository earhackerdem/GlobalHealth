---
date: 2026-10-20
state: deferred
anchor: journal: 2026-10-20 · perfil-cronicas (review)
---

Ronda 3 de perfil-cronicas: (H1) un usuario SIN perfil cuyo primer POST de crónica enlazada corre a la vez que el DELETE del diagnóstico deja un enlace colgante (`crud.lock_profile` no bloquea cero filas) · (H2) el candado de POST /profile/history y de "ninguna" no tiene prueba de que se toma

**Verdict and why:** H1 solo por API (la UI crea el perfil con GET /profile antes de cualquier POST); arreglo de fondo: serializar sobre la fila del diagnóstico (FOR UPDATE / FOR SHARE). H2: esos candados vienen de la Story A, sin cambio de semántica. Convergencia: ronda 1 → 24, ronda 2 → 12, ronda 3 → 2 bajos

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-cronicas (review)
