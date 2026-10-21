---
id: D6
date: 2026-10-11
status: revised
---

## D6 — Stack v1: monolito Laravel + Postgres(pgvector) + Claude API tras AiGateway
- **Status:** Revised · 2026-10-11 → ver D11 · decided by: Saúl Pérez (author/owner), recomendación del technical brief
- **Decision:** v1 es un monolito Laravel 12 con PostgreSQL (pgvector para recuperación) y la capa IA como
  llamadas directas a Claude API encapsuladas en una interfaz interna propia (`AiGateway`).
- **Why:** el equipo es una persona fluida en Laravel; el código más delicado (consentimiento, revocación,
  cifrado) se escribe en el framework que domina. Tecnología aburrida gana.
- **Discarded:** (B) template full-stack FastAPI — apila dos aprendizajes (Python reciente + React) sobre el núcleo
  de privacidad; (C) sidecar FastAPI desde v1 — dos deploys para una persona. C queda como evolución: si el
  procesado de documentos/OCR lo exige, el sidecar se añade detrás de AiGateway sin rediseño.
