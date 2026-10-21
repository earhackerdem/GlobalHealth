---
id: D20
date: 2026-10-21
status: accepted
---

## D20 — Botones desactivados mientras se envía
- **Status:** Accepted · 2026-10-21 · decided by: Saúl Pérez (author/owner)
- **Decision:** un botón que envía datos ("Guardar", "Eliminar", "Sí, eliminar"…), o que sale de la pantalla mientras
  ese envío sigue en curso ("Cancelar"), queda no disponible hasta que el envío termine, y la pantalla muestra que está
  enviando. "No disponible" es `aria-disabled="true"` con el clic y Enter ignorados, no `disabled` nativo: el botón
  sigue en el recorrido del teclado y no pierde el foco. Un doble clic nunca manda dos veces lo mismo.
- **Revised:** 2026-10-21, en la revisión ronda 1 de perfil-habitos-ajustes (hallazgo A1): con `disabled` nativo, el
  foco caía a la página y Enter ya no hacía nada. Aprobado por Saúl Pérez con el plan revisado.
- **Why:** Saúl Pérez, al decidir cómo se guardan los hábitos: "quiero evitar el happy click en todos los lados
  posibles".
- **Consequence:** aplicada primero en la pantalla de hábitos (perfil-habitos-ajustes, fila 21 del test plan). Revisar
  los demás formularios de la app es una fila de la tarea de deudas
  (`memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`). Los cambios nuevos la
  cumplen desde su plan.
