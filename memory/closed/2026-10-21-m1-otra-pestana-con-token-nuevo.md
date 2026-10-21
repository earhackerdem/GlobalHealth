---
date: 2026-10-21
state: deferred
anchor: journal: 2026-10-20 · perfil-habitos (Story C1: sustancias y humo)
---

M1 (ronda 3 de perfil-habitos): el listener de `storage` de `frontend/src/main.tsx` reacciona a cualquier cambio de `access_token`, no solo a un cambio de cuenta; si en otra pestaña la MISMA persona obtiene un token nuevo (p. ej. dos pestañas sin sesión, una entra con contraseña y la otra vuelve por `/google-callback`), esta pestaña se recarga y pierde lo que tenía sin guardar

**Verdict and why:** Reproducido por el finder (sonda T5) y por el orquestador. Costo aceptado del fix de N1: el camino es rebuscado (ningún flujo renueva el token solo; cerrar sesión ya debe sacar a las otras pestañas) y perder un borrador es preferible a dejar a la vista o guardable lo de otra cuenta. Arreglo si algún día importa: reaccionar solo cuando el token queda en null o cambia su `sub`. Deuda aceptada por Saúl Pérez

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-habitos (Story C1: sustancias y humo)
