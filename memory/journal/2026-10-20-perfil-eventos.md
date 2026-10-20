# 2026-10-20 · perfil-eventos (Story A de FR-028): apertura y exploración

**Quién:** Saúl Pérez (author) pidió "procede con la story a" sobre el prototipo v4. El gate del discovery se
cerró para la Story A y se abrió el PR #18.

**Qué:** se abrió `openspec/changes/perfil-eventos/` con los criterios A-1…A-9 del prototipo en el proposal. La
rama sale de la del discovery y se rebasa sobre `main` antes del PR. Exploración:
- **Clasificación:** extensión de `records/patient-profile`.
- **Ya existe:** el cifrado, el consentimiento, el aislamiento con 404 idéntico y el patrón catálogo + "otra".
- **Es nuevo:** el estado "ninguna", "cuándo" por edad/etapa/año y los cuatro formularios.
- **Se rompe a propósito:** `frontend/tests/profile.spec.ts:280-300`, que asierta las secciones sin captura.
- **Dependencia:** el archive necesita el PR #17.
- **Preguntas al gate:** modelo genérico o tipado, qué va en claro, pantalla o diálogo, y los dos tropiezos del
  inbox (Alembic y el reformateo de tests).
