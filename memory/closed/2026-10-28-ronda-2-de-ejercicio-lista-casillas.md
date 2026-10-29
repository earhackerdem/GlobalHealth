---
date: 2026-10-28
state: deferred
anchor: journal: 2026-10-28 · ejercicio-lista-casillas (E-1…E-4)
---
Ronda 2 de ejercicio-lista-casillas (PR #35, diff fc51300..1203df9). Quedan como deuda tres de los cinco hallazgos bajos:
- **R2-1:** comentarios de `HabitsForm.tsx` que todavía no son fieles:
  - `:1161` dice «the first chip of an invalid group», y el foco cae en la casilla «Caminar»;
  - `:1647` dice «the chips look like Guardar», y esa clase también atenúa el cuadro de las casillas;
  - el docblock de `activityBox` no dice que el cuadro se atenúa con la regla del `form`, porque `Checkbox` no tiene estilo `aria-disabled:`.
- **R2-2:** el atenuado del nombre de la actividad mientras guarda (B2, `peer-aria-disabled:opacity-50`) no tiene aserción. La única medida de opacidad del archivo es la de un chip (`profile-habits.spec.ts:1594-1598`).
- **R2-4 (juicio de diseño):** el nombre de la actividad en negritas (600) pesa más que la pregunta del grupo (`legend` «¿Qué ejercicio haces?», 500), y «No hago ejercicio» también va en negritas aunque no abre campos.

**Verdict and why:** Los encontró el finder de la ronda 2, que midió con una sonda headless a 384 px (los pesos, el atenuado al guardar y el clic en la etiqueta). No pasaron por validador, por la regla de cierre que Saúl Pérez (author) aprobó con la ronda 1 («Todo lo recomendado… Después, ronda 2: si solo trae bajos, quedan como deuda y se archiva», 2026-10-28). Ninguno pierde datos ni deja de cumplir E-1 a E-4. Se pagan así:
- R2-1 y R2-2 cuando se reabra `HabitsForm.tsx`;
- R2-4 al decidir el estilo de las casillas para toda la app, junto con el tamaño de 16 px que ya está declarado en `validation.md`.

R2-3 (el guion de E-3 partía de cero aunque E-2 ya había guardado Caminar) y R2-5 (los conteos de la ronda 1 no cuadraban con los comentarios del PR) se corrigieron al cerrar, porque el guion debe poder recorrerse y la evidencia debe decir los números reales (AGENTS.md).
