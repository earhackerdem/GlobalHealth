---
id: D18
date: 2026-10-20
status: accepted
---

## D18 — Opciones en la UI: chips como estándar de la casa

- **Date:** 2026-10-20 · **Status:** accepted
- **Decision:** Saúl Pérez, al decidir R25 en la review de perfil-cronicas: cuando el usuario elige entre opciones
  fijas, la UI usa **chips** (`frontend/src/components/Profile/ChipGroup.tsx`), no radios, ni selects, ni
  componentes escritos a mano. Cita: "hay que tener un estándar, guarda como regla usar chips cuando se tienen
  opciones".
- **Why:** consistencia en toda la app. Las secciones de la Story A, el grupo sanguíneo y los prototipos ya usan
  chips, y había dos implementaciones del mismo patrón: chips y radios a mano en las crónicas.
- **Exception:** objeción del agente, anotada en la misma conversación y sujeta a que Saúl Pérez la retire. Las
  listas **dinámicas o largas** van en un desplegable o un buscador, no en chips. Son las que crecen con los datos
  del paciente, como el selector de diagnósticos del expediente (hasta 1000), o las que superan unas 15 opciones.
  Una pared de chips con datos del usuario no escala en el teléfono.
- **Discarded:** radios nativos por sección. Rompían el estándar y obligaban a duplicar la lógica de error y foco.
- **Applies to:** formularios nuevos y los que se reabran. "¿Cuál?" de las crónicas se migra en el apply de la
  review del PR #26.
