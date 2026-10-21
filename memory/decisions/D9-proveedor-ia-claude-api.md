---
id: D9
date: 2026-10-11
status: accepted
---

## D9 — Proveedor IA: Claude API
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** la capa IA usa Claude API (claude-sonnet-5-5 para Q&A y preparación de consulta; claude-haiku-5-5
  para tareas baratas), detrás de AiGateway.
- **Why:** no entrena con contenido de clientes API por defecto [fuentes secundarias coincidentes, 2026-10-11];
  calidad en cita/grounding requerida por NFR-011.
- **Consequence:** NFR-005 obliga a verificar retención (7 vs 30 días en fuentes) y ZDR en Commercial Terms/DPA
  oficiales, con captura fechada en memory/research.md, ANTES del primer dato real en el sistema.
