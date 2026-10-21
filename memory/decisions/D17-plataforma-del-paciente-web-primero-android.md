---
id: D17
date: 2026-10-18
status: accepted
---

## D17 — Plataforma del paciente: web primero; Android entra por spike con evidencia, no en paralelo

- **Date:** 2026-10-18 · **Status:** accepted
- **Decision:** Saúl Pérez decidió ("procedamos sin android por el momento") mantener la web app como única
  superficie del paciente mientras el modelo de dominio se asienta (el discovery de receta-mexicana acaba de
  corregir el modelo v1). Android nativo NO se abandona: entra como **spike acotado** tras el gate del discovery —
  leer recetas del corpus real de 74 fotos con ML Kit GenAI (Gemini Nano on-device) en su S26 Ultra — que a la vez
  evalúa el proveedor de Q4/NFR-005 (cero retención por construcción; ver memory/research.md 2026-10-18). Si el
  spike gana, la app Android se decide con evidencia en el tech-brief.
- **Why:** un solo desarrollador a tiempo parcial sin experiencia Android; dos frontends congelarían un modelo aún
  en validación y duplicarían cada corrección.
- **Discarded:** app Android en paralelo desde ya (riesgo de doble mantenimiento sobre modelo no validado);
  abandonar Android (perdería el único camino a IA on-device, que la web no puede tocar).
- **Revises:** matiza la propuesta original de "Android nativo para el paciente" del technical-brief (la intención
  sigue; cambia el cuándo y el cómo se decide).
