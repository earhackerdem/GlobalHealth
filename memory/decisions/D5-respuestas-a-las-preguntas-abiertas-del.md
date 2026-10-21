---
id: D5
date: 2026-10-11
status: accepted
---

## D5 — Respuestas a las preguntas abiertas del brief
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** (1) recordatorios de medicación mínimos entran en v1, citas/agenda no; (2) acceso del profesional
  solo por control de enlace: un enlace por profesional (tipo + nombre), revocable individualmente, sin verificación
  por teléfono/correo; (3) la IA también atiende al paciente de forma proactiva — pregunta para completar el
  expediente y sugiere estudios/especialista a partir de huecos (incl. historial familiar de cáncer y diabetes) —
  con encuadre "preparación de consulta": toda sugerencia lleva fuente y se formula para discutir con el
  profesional, nunca como prescripción; (4) freemium = gratis con límite de consultas de IA.
- **Why:** motivación directa de Saúl: historial familiar de cáncer y diabetes; quiere que el paciente llegue con
  los estudios conversados proactivamente y no espere a que el médico los pida. El encuadre no-prescriptivo fue la
  objeción del agente (riesgo de recomendación clínica / COFEPRIS y daño por alucinación); Saúl puede revertirlo y
  quedaría registrado aquí como Revised.
- **Consequence:** la evidencia de comorbilidades que alimenta las sugerencias vive en
  memory/research.md#comorbilidades con su nivel de confianza; cada regla de sugerencia exige verificar la guía
  clínica vigente antes de implementarse (nunca desde memoria del modelo).
