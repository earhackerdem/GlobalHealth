# 2026-10-19 · discovery: perfil médico por secciones (FR-028)

**Quién:** Saúl Pérez (author) preguntó qué seguía después de archivar onboarding-perfil, porque al ampliar el
alcance quedaron 6 secciones del historial visibles pero vacías. El harness recomendó FR-028 con discovery
primero: el dominio solo tenía una línea por sección, y "crónicas" se cruza con los diagnósticos (FR-005).
Saúl respondió "procede con 028".

**Qué:** se partió de un borrador 0 sacado de research.md § anamnesis y se corrigió en 5 rondas. La ronda 5 no
añadió nada. Decisiones de Saúl:
- crónicas aparte del diagnóstico, con enlace opcional;
- "cuándo" como año aproximado, "En la infancia" o "No recuerdo";
- estado "ninguna" por sección;
- crónica activa o "ya no la tengo";
- tratamiento como texto libre;
- en cirugías, hospital, médico y reacción a la anestesia;
- material implantado en fracturas y en cirugías;
- lado en fracturas;
- en transfusiones, componente y hospital;
- grupo sanguíneo como un solo valor;
- salud mental marcada como sensible para FR-014;
- tabaco con cantidad, más vapeador y humo de leña;
- alcohol y ejercicio con frecuencia y cantidad;
- fuera: vacunación, otras sustancias y alimentación/sueño;
- cruces entre secciones como un sí/no, sin enlaces.

Partición: **Story A (eventos)** y después **Story B (crónicas + hábitos)**.

**Artefactos:** product/dominio.md (rebanada nueva, draft), roles-permisos.md (3 filas del perfil médico, que
faltaban desde el onboarding), prd.md (nota de partición en US-18), research.md § humo de leña (riesgo
[VERIFIED] con el INER; forma de captura [ASSUMPTION]), prototipo product/prototipos/perfil-secciones.html,
publicado en https://claude.ai/artifact/TRBywm3SEhDA5ey2duMV8n.

**Gate pendiente:** Saúl navega el prototipo. Queda abierto qué pasa con la crónica al borrar el diagnóstico
enlazado.
