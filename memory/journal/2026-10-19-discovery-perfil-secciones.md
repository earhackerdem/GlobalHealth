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

**Ronda 6 (prototipo v1 → v2):** al clickear, Saúl Pérez vio que hábitos se quedaba corto. Señaló el alcohol de
fin de semana, la exposición a humo ajeno en un lugar fijo dos veces por semana y varios ejercicios cada uno con
su frecuencia, y pidió investigar cómo se maneja. La evidencia (research.md § hábitos) coincide con sus tres
puntos: son justo los huecos documentados de la captura estructurada en los expedientes. Decidió:
- alcohol con la forma del AUDIT-C y estado "lo dejé";
- humo ajeno como hábito propio (dónde y días por semana);
- ejercicio como lista de actividades con días y minutos;
- hábitos como **Story C** propia.

Objeción del harness, aceptada: la app no calcula puntajes ni riesgos (C-6, NFR-008).

**Ronda 7 (prototipo v2 → v3):** Saúl Pérez sumó la ocupación ("también te preguntan por tu profesión") y el
movimiento que implican algunos oficios. La investigación (research.md § ocupación) llevó a tres decisiones:
- la ocupación va en el Perfil básico, con situación laboral, trabajo de más años, exposiciones y turno;
- el movimiento del día se captura con la forma del GPAQ (trabajo, desplazamiento, horas sentado), separado del
  ejercicio y sin sumarse, por la paradoja de la actividad física;
- el sueño entra en versión mínima (antes estaba fuera).

Los datos de salud personales que Saúl mencionó como ejemplo no se registran en el repo.

**Ronda 8 (prototipo v3 → v4):** el único feedback de Saúl Pérez al v3 fue sobre "cuándo": recuerda mejor la
edad que el año, y el médico no pregunta el año sino "¿cuántos años tenías?" o "¿ibas en la primaria o en la
secundaria?" para calcularlo. Cambió en todo el perfil: crónicas (desde/hasta), tabaco y alcohol (a qué edad).
Ahora se contesta con edad, etapa escolar o año. Se guarda lo dicho y el año se calcula al mostrarlo con la fecha
de nacimiento; sin ella, solo se muestra la edad. Corrige la decisión de la ronda 1 ("año aproximado").
