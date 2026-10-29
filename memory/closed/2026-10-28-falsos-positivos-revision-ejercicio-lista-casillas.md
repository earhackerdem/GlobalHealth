---
date: 2026-10-28
state: frozen
anchor: journal: 2026-10-28 · ejercicio-lista-casillas (E-1…E-4)
---
Falsos positivos y descartes parciales de la revisión de ejercicio-lista-casillas (PR #35), ronda 1:
- **A5, comportamiento («Guardar sin nada en Ejercicio no queda probado»):** guardar sin marcar nada da `exercise: null`. Es lo que pide la spec (`openspec/specs/records/patient-profile/spec.md:612`, cada bloque es opcional) y lo prueba la fila 9 (`profile-habits.spec.ts:3319`).
- **A1, prototipo `ejercicio-variantes.html:138`, «casilla nativa»:** describe el prototipo, que sí usa `<input type="checkbox">`.
- **A1, el rol en la línea Revised de D18:** la casa pone solo el nombre en las líneas de decisión (D17, D18, D20).
- **A4, `design.md:34-35`:** es un permiso condicional de alcance, no un texto viejo.

**Verdict and why:** Los reprodujeron como falsos o los descartaron los validadores de la ronda 1, con el servidor real, las líneas exactas y los registros de decisiones. No se reportan otra vez sin evidencia nueva.
