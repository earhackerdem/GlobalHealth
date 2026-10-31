---
date: 2026-10-26
state: deferred
anchor: journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)
---
Ronda 2 de perfil-habitos-actividad-sueno (PR #34, diff a95570c..d3f114b), once hallazgos bajos validados por reproducción:
- **C1:** un nombre de "Otra" hecho solo de marcas invisibles (U+034F, U+FE00–FE0F, U+E0100–E01EF, U+17B4/17B5, U+180B–180D) todavía cuenta como escrito (`_is_blank` en `models.py`, `BLANK` en `HabitsForm.tsx`). Arreglo propuesto: tratar como blanco cualquier `Default_Ignorable_Code_Point`, más el espacio y U+2800.
- **C2:** ningún pytest fija que `{"sitting_hours": 0}` o `{"active_travel": false}` solos siguen siendo una respuesta (el mutante `_all_null` con `not value` deja 310/310; la fila 6 e2e cubre el *No*).
- **C3:** "meta" se busca como palabra entera (`\bmeta\b`) y deja pasar "metas"; en la spec es una raíz, como "recomend".
- **C4:** `changeOtherName` (escribir solo texto invisible después de "Escribe cuál." no quita el error) no tiene prueba.
- **M1:** la evidencia de la ronda 1 no registraba que 3 de 6 corridas conocidas de las suites de perfil tuvieron un fallo intermitente. Es la fila 4 con "socket hang up" dentro de `createUser` (`frontend/tests/utils/privateApi.ts`, el cliente axios compartido, que no tiene la mitigación `Connection: close` de `profile-habits.spec.ts:192-197`). Ocurre antes de cualquier código de hábitos, así que no es regresión del producto; el validador lo bajó de medio a bajo. Se registró al cerrar en `evidence.md` y en el inbox.
- **M2:** los anclajes `file:line` criterio→prueba de `evidence.md` quedaron viejos tras 2c99c8f, y las pruebas nuevas no tienen anclaje.
- **M4:** `design.md` § Normalización y la spec no dicen que un nombre invisible es `null` ni que un bloque de movimiento o sueño sin respuestas se guarda `null`.
- **M5:** "así que no se cuenta dos veces" (Decision 5) exagera: el total no suma el desplazamiento, pero nada en pantalla impide anotar el trayecto también en "Caminar".
- **M6:** `prototipo.html:86` sigue diciendo "lista de actividades".
- **M8:** `memory/closed/2026-10-26-b2-texto-invisible-en-otra-del-historial.md` escribe un criterio distinto del de `_is_blank` y no nombra los otros usos de `_is_filled` (`name` de cirugías, `what` de fracturas).
- **M10 (cosmético):** jerga en `validation.md` ("commit 641e976", "fila 12"); el journal dice que la Decision 5 "ya no dice 'sin convertir'", pero lo dice acotado a NHIS, BRFSS y NHANES.

**Verdict and why:** Encontrados por dos finders de la ronda 2 (código y documentos) y validados por otros dos agentes, por reproducción: API en :8000, mutantes en copias, Playwright sobre la pila estable. Ninguno hace perder datos al paciente ni le muestra un veredicto. Se aplica la regla de cierre de la Decision 7 de `design.md`, aprobada con el plan por Saúl Pérez el 2026-10-26: si una ronda después de la primera trae solo hallazgos bajos, quedan como deuda registrada y se archiva. Lo único que se tocó al cerrar fue el registro de M1 (evidencia e inbox), porque la evidencia debe decir los números reales (AGENTS.md). Se pagan en la tarea de deudas (`memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`): C1 con B2 del historial (una sola regla de blanco compartida), M1 con los e2e intermitentes heredados.

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)

**C1 pagado (2026-10-31):** validaciones-hoy-y-texto-invisible, PR #47, junto con B2 como preveía este veredicto: una sola regla de blanco (espacio, Cc, Cf, `Default_Ignorable_Code_Point`, U+2800) en `_is_blank` (`BLANK_RANGES`, Unicode 16) e `isBlank` (`\p{Default_Ignorable_Code_Point}`). Los demás hallazgos de esta ronda siguen diferidos.
