---
date: 2026-10-31
---

# tablas-snake-case: las cinco tablas del default de SQLModel en snake_case (D25)

**Quién:** Saúl Pérez (author) pidió «procede con el nombre de las tablas» después de mergear los PRs #45–#48. El
agente le había avisado que eran renombres con datos; él lo reafirmó, y eso quedó en D25. El resto del ciclo corrió por
delegación (`/epe-autopilot`).

**Qué se hizo (`test→impl`):**
- `__tablename__` en snake_case para `oauth_identity`, `consent_grant`, `health_record`, `health_record_medicine` y
  `health_record_attachment`.
- La migración `c4a9e1d7b2f5` renombra cada tabla y luego todo lo que el catálogo diga que tiene el prefijo viejo
  (restricciones, incluidas las `NOT NULL` con nombre de Postgres 18, e índices). El `downgrade` hace lo mismo al revés.
- El SQL crudo de las pruebas pasó a los nombres nuevos.
- D16 dice el nombre nuevo.
- Lo pendiente de la ronda anterior: M1 marcado pagado por el PR #48, el avance en la nota de deudas, y el inbox de las
  tablas cerrado.

**Verificación:**
- Rojo `7c34d94`.
- Verde de 643/0/0/0, cobertura 97 %; la migración sube y baja sin perder restricciones ni índices.
- Base de desarrollo migrada con las mismas filas; e2e 82/0; `tdd-check` ✓.

**Deuda:** ninguna nueva.

## Revisión y archivo

**Ronda 1:** un buscador con todas las lentes, que reprodujo todo en bases desechables.
- **F1 (medio), corregido:** la prueba de migración no miraba el catálogo. Ahora exige no dejar ningún prefijo viejo al
  subir y el mismo catálogo al bajar; el mutante «solo tablas» muere.
- **F2–F6, corregidos:** fidelidad de los documentos y el comentario del orden.
- **F7:** congelado.

**Verde:** 643/0/0/0. La base de desarrollo bajó y subió con las mismas filas.

**Lección:** dos veces seguidas la evidencia dijo que una prueba existente cubría algo que no recorre (la receta). Una
afirmación de cobertura «de paso» también se mide.
