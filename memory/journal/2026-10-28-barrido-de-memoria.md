# 2026-10-28 · Barrido de memoria tras perfil-habitos-actividad-sueno

**Quién:** Saúl Pérez (author) pidió `/epe-memory` al cerrar la sesión de la C2a (PR #34, abierto, CI en verde),
que acumulaba 8 compactaciones sin barrido.

**Qué se hizo:**
- `make memory-check`: sin pistas mecánicas en el repo ni en la memoria privada.
- Inbox: cerrado el del daemon de Docker que no bajaba imágenes base (hoy baja de ghcr.io y Docker Hub). En el
  inventario de deudas (`memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`) se
  agregó la deuda de la C2a (B1, B2 del historial, ronda 2, `<main>` anidado, fila 4), y se dejó escrito que la
  propuesta de `lint.py` se decide antes de la C2b.
- Se revisaron otra vez `validate_birth_date` (sigue con `date.today()`), `formatDateMx` (sigue duplicado) y el
  `SidebarTrigger` (sigue derivando de `open`): siguen abiertos.
- Memoria privada del agente: dos memorias corregidas y dos nuevas sobre cómo trabajar aquí (typos, pase
  exploratorio en Chrome, brief de los fixers).

**Deuda:** el inbox tiene 17 abiertos. Toca hacer el `/triage` del inventario de deudas con Saúl Pérez después de
la C2b.
