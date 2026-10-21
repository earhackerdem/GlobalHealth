---
date: 2026-10-20
state: frozen
anchor: journal: 2026-10-20 · perfil-cronicas (review)
---

R3 de perfil-cronicas: "un PUT sin `sensitive` recalcula el valor por defecto y desmarca una crónica que el paciente marcó"

**Verdict and why:** Falso positivo reproducido: el PUT reemplaza el registro completo (omitir cualquier campo lo borra, por contrato `design.md:65-66`) y la UI siempre manda la marca

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-cronicas (review)
