---
date: 2026-10-29
---

# Captura híbrida: prototipo de variantes (hilo 3 de la investigación de UX)

**Quién e intención.** Saúl Pérez (autor) mergeó el PR #35 y fijó el orden de lo que queda de la investigación de
UX: primero el hilo 3 (captura), después los colores y al final la mascota.

**Qué se hizo.** El agente armó `product/prototipos/captura-hibrida.html` en la rama `docs/captura-hibrida`. Ya
estaba adoptado el híbrido (Saúl Pérez, 2026-10-20): texto obligatorio más un código opcional por dentro. El
prototipo no vuelve a abrir esa elección. Decide cómo se ve el híbrido, con tres variantes para el diagnóstico:
- **A**, sugiere mientras escribes;
- **B**, pregunta al guardar;
- **C**, solo texto, como hoy.

El prototipo también muestra tres cosas comunes a las variantes: «¿Para qué es?» por medicina (ronda 2 del
dominio), las sugerencias de medicinas tomadas de las recetas propias y la vista «Así lo ve el médico». Las
insignias van de CA-1 a CA-6.

**Supuestos declarados en el prototipo.**
- El vocabulario es propio: unos 16 conceptos en palabras de paciente, no la CIE-10 completa. La DGIS no publica
  licencia, y sus nombres oficiales dan 0 coincidencias con las palabras del paciente
  (`memory/research/captura-catalogos.md`).
- Cuatro códigos son [ASSUMPTION] y van marcados con `*`: J029, N390, K297 y G439.

**Verificación.**
- Chrome: el agente recorrió la variante A a mano: sugerencia «los» → Losartán con su dosis, «presión alta» →
  Hipertensión, y la vista del médico agrupada.
- Por script en la misma pestaña:
  - «ansiedad» queda sensible;
  - «artritis» ofrece dos opciones;
  - «dolor de rodilla por correr» no ofrece ninguna;
  - B pregunta después de guardar;
  - C deja «presión alta» sin reconocer.
- Headless a 400 px: sin desbordamiento, sin errores de página y la crónica muestra la medicina ligada. La consola
  de Chrome solo mostró un 401 de una extensión, no de la página.

**Pendiente.** Saúl Pérez elige la variante y contesta las preguntas abiertas. Después vienen, en el mismo PR:
- la sección de `product/dominio.md`;
- el ADR del híbrido;
- `product/prd.md`.

**Decisión (mismo día).** Saúl Pérez navegó el prototipo y eligió las cuatro respuestas recomendadas:
- A, sugerir mientras escribe;
- lista propia con código, no la CIE-10 completa (era la objeción del agente: licencia no publicada y nombres
  oficiales que dan 0 coincidencias);
- el «Tratamiento actual» convive con las medicinas ligadas;
- las medicinas se sugieren de las recetas propias.

Quedó registrado en:
- D21;
- `product/dominio.md` (rebanada captura híbrida);
- `product/prd.md` (FR-029..031, US-19);
- el inbox: ronda 2 cerrada y la investigación de UX con el hilo 3 hecho.

Construirlo es una story nueva, que no se ha abierto. Siguen la paleta y después la mascota.
