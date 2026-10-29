# 2026-10-28 · ejercicio-lista-casillas (E-1…E-4)

**Quién:** Saúl Pérez (author). Al usar la pantalla de hábitos, tras mergear el PR #34, vio que los campos del ejercicio
se apilaban. Propuso primero pestañas y luego una lista con casillas, eligió la variante E del prototipo
(`product/prototipos/ejercicio-variantes.html`) y aprobó el plan («plan approved»).

**Intención:** que el paciente vea siempre las nueve actividades y conteste los días y minutos de cada una justo debajo
de su casilla. Es el primer resultado del hilo 1 de la investigación de UX
(`memory/inbox/2026-10-28-investigacion-ux-completa.md`).

**Qué se hizo:**
- **Investigación:** `memory/research/formularios-ux.md` (NN/g, GOV.UK, APG) y un prototipo con cinco variantes,
  recorrido headless a 400 px. D18 revisada: lista con casillas cuando cada opción abre sus propias preguntas.
- **Frontend (test→impl):** el tester escribió E-1 a E-4 y pasó las pruebas del ejercicio de chips a casillas (rojo
  `8e958fe`). El implementer cambió el bloque en `HabitsForm.tsx` usando como modelo antecedentes familiares (verde
  `f1cf272`). El servidor y lo guardado no cambian.
- **Enmienda tras el rojo:** el tester mostró que la cláusula de E-4 sobre el foco del error de grupo no se puede
  alcanzar, porque los bloques son opcionales. Se quitó de la spec y del plan. El error fue del agente al escribir la
  spec, no de Saúl Pérez.
- **Prototipo de producto:** `perfil-secciones.html` pasó a la lista con casillas.

**Verificación:** `profile-habits.spec.ts` 161 de 161; suite completa como en CI 339 passed y 2 failed de
`reset-password` (heredado; pasan al repetirlas); backend 560; `tdd-check`, `tsc` y `biome` limpios. Pase exploratorio
en Chrome sin defectos (`evidence.md`).

**Deuda:** la casilla mide 16 × 16 px, como en el resto de la app; si se agranda, se decide para toda la casa
(`validation.md`). Sigue el intermitente de `reset-password`. Fila 31a falló una vez en el rojo y pasó 4 de 4 sola.

## Revisión, ronda 1, y apply

Dos finders y dos validadores: 14 hallazgos confirmados (3 medios: D18 decía «casilla nativa», el texto exageraba a GOV.UK y el guion de E-2 no se podía recorrer) y 1 falso positivo. Saúl Pérez (author) aprobó «Todo lo recomendado», aprobó después la enmienda de E-4 («Sí, guardar vacío»), que el agente había hecho tras el «plan approved» sin preguntarle, y eligió «Línea y nombre en negritas» para distinguir cada actividad. El fixer aplicó todo sin rebotes:
- prueba nueva E-4b del error de grupo del servidor;
- el nombre de la actividad se atenúa al guardar;
- `aria-disabled` llega por un solo camino;
- línea a la izquierda y nombre en negritas;
- documentos corregidos.

Resultado: hábitos 163 de 163; el guion de E-2 se recorrió de punta a punta.
