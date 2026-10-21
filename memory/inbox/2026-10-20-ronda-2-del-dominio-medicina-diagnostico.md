---
date: 2026-10-20
status: open
---

**Ronda 2 del dominio: medicina ↔ diagnóstico/crónica.** Saúl Pérez, al validar perfil-cronicas: una receta trae medicinas de varias enfermedades, así que el enlace va **por medicina** (no por receta) hacia un diagnóstico o una crónica propios; elegir/crear la crónica desde la receta ("¿para qué es?"). Respuestas del mismo día: (1) para ligar NO hace falta catálogo (se liga por id, como `diagnosis_id`); (2) crónicas **fuera** del onboarding; (3) enlace por medicina. Preocupación: fatiga por capturar dos veces el tratamiento → la crónica debería mostrar las medicinas ligadas sin recapturarlas

**Why it matters:** Toca receta (FR-005/FR-006), crónicas (FR-028) y el futuro de la IA; texto libre vs catálogo vs híbrido se decide con la investigación de `docs/investigacion-captura-ux` antes de `/product-discovery` ronda 2

**Status:** abierto · investigación hecha (research.md#captura-catalogos). Saúl Pérez (2026-10-20) adoptó como dirección el **híbrido**: texto obligatorio + código opcional (CIE-10 interno), sin catálogo cerrado ni CRUD de admin; se vuelve ADR al cerrar la ronda 2. Orden: cerrar PR #26 → hábitos (Story C) → deudas (`memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`, pedido de Saúl Pérez 2026-10-21) → ronda 2
