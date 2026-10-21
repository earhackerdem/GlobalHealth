---
id: D2
date: 2026-10-11
status: accepted
---

## D2 — Privacidad primero y diseño multi-usuario desde v1
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** la v1 del expediente personal de salud la usa solo Saúl, pero el modelo de datos, el aislamiento
  por usuario, el consentimiento y la revocación de accesos compartidos se diseñan multi-usuario y con los datos de
  salud tratados como sensibles desde el primer commit.
- **Why:** el objetivo declarado es una app pública freemium; añadir privacidad después de hacerla pública implica
  reescritura. Saúl lo pidió explícitamente: "demos prioridad a la privacidad para evitar reescrituras".
- **Consequence:** toda exploración de cambio hereda esta restricción; el technical brief la convierte en
  presupuesto NFR medible (cifrado, revocación, auditoría de accesos).
