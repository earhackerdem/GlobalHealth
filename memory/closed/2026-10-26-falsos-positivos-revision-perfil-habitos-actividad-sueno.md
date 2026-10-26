---
date: 2026-10-26
state: frozen
anchor: journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)
---
Falsos positivos de la revisión de perfil-habitos-actividad-sueno (PR #34), rondas 1 y 2:
- **Ronda 1, D2 `proposal.md:57` "sin migración ni cambio de ruta":** el endpoint no cambió; solo el `loc` del 422.
- **Ronda 1, D2 `product/dominio.md:435` "actividad física (1→0..N)":** sigue siendo cierto (de 0 a 9, una por tipo).
- **Ronda 1, D3 `validation.md:22`:** redacción ambigua, ya corregida a "se desmarcan".
- **Ronda 1, D4 (casi todo):** el plan enmendado sí estaba registrado en el commit 4556d92, en `evidence.md` y en el journal; solo faltaba la nota en el encabezado, que se agregó.
- **Ronda 2, M3:** la nota de enmienda de `design.md` sí cubre lo que Saúl Pérez aprobó en la compuerta (D4 la nota, D7 la reescritura de la Decision 5).
- **Ronda 2, M7:** "una sola cifra promedio" en `memory/research/habitos.md` describe la forma de la pregunta; `FA0400` de ENSANUT es un solo ítem promedio codificado en categorías.

**Verdict and why:** Reproducidos como falsos por los validadores (lectura de líneas exactas, `git log -p`, el mensaje de compuerta de Saúl Pérez del 2026-10-26). No se reportan otra vez sin evidencia nueva.

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)
