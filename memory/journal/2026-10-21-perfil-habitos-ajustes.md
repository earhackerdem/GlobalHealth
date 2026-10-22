# 2026-10-21 · perfil-habitos-ajustes (C-10…C-14)

**Quién:** Saúl Pérez (author) con el agente (orquestador), con tester e implementer por grupo.

## Intención
Al validar la C1, Saúl Pérez pidió: edad de inicio en alcohol, una medida para el vapeador, la leña como rango de
edades, validar en el front con las reglas del contrato, y guardar al momento para no perder lo contestado. Pidió
investigar primero cómo se recaba cada dato.

## Decisiones de Saúl Pérez
- Un solo cambio con lo técnico (A); horas al día en la leña además del rango (B); vapeador "todos los días / algunos
  días" con días de los últimos 30, más edades (C); orden #30 → este cambio → C2 → deudas → investigación de UX (D).
- "Guardar" y "Cancelar" se quedan, desactivados mientras se guarda: "evitar el happy click en todos los lados
  posibles" → D20, aplicada aquí y como fila de la tarea de deudas para el resto de la app. "Cancelar" restaura lo
  que había al abrir (si no, con el guardado automático no desharía nada).
- "plan approved" sobre el prototipo navegable.

## Qué se hizo
- Investigación en `memory/research/`: horas-año de la leña (Pérez-Padilla 1996, >200 horas-año OR 75), vapeador
  por días de los últimos 30 (PATH; sin medida validada en pods), edad del primer consumo de alcohol (LOINC 63634-0).
- Backend: alcohol con `start_age`, vapeador como objeto, leña con inicio, fin y horas; lo guardado en la forma
  anterior se convierte al leer (sin migración, solo hay cuentas de prueba).
- Frontend: cliente con esquemas Zod del OpenAPI (los límites salen de ahí), validación al salir de cada campo,
  guardado automático de a un `PUT`, estado accesible, D20.

## Verificación
Backend 342 passed (96 %); e2e del cambio 137 passed (chromium + s26-ultra); suite completa 239 passed en una corrida y
238 + el heredado `login.spec.ts:87` en otra. Exploración en Chrome (8 intentos, sin defectos; *corrección: 10 filas en evidence.md, a 580 px y con cierre de sesión
en otra pestaña, no a 384 px ni con cambio de cuenta*). Números en
`openspec/changes/perfil-habitos-ajustes/evidence.md`.

## Sorpresas
- La validación estricta de OpenSpec rechazó renombrar escenarios existentes en un MODIFIED (el archivo los
  perdería): se conservaron los nombres.
- La imagen de Docker no se puede construir entre el rojo y el verde del frontend (corre `tsc`); se copiaron los dos
  archivos del backend al contenedor para el rojo.
- Un `socket hang up` intermitente en R1 (s26-ultra): conexión keep-alive ociosa justo en los 5 s del servidor; los
  e2e mandan `Connection: close`.
- El puerto 8765 está ocupado por un proceso ajeno; el prototipo se sirvió en 8799 solo para recorrerlo.

## Deuda
Ver evidence.md § Deuda.

## Revisión ronda 1 y cambio de diseño (2026-10-21)
- La revisión adversarial confirmó 22 hallazgos (comentarios finder y validator en el PR #32). El más grave, A5 (alto,
  privacidad): con otra pestaña que entra a otra cuenta, un guardado automático pendiente mandaba los hábitos de una
  cuenta con la sesión de la otra. Siete más salían del mismo mecanismo.
- El agente recomendó arreglar el guardado automático y mencionó como alternativa volver a "Guardar" con aviso de cambios
  sin guardar. Saúl Pérez propuso quitarlo ("podemos retirar el guardado automático si de principio pedimos, da click
  en el botón guardar"); el agente objetó que el texto solo no evita perder datos y propuso sumarle los avisos de
  salida (`useBlocker` y `beforeunload`); Saúl Pérez eligió quitarlo con eso. design.md Decision 8.
- Costo aceptado: en el celular, si el navegador cierra la pestaña en segundo plano, lo no guardado se pierde.
- Plan revisado a DRAFT: spec (C-13 nuevo), design (contrato, decisiones 5, 7 y 8, filas 16–24), tasks (grupos 4–6) y
  el prototipo, recorrido por el agente en Chrome antes de pedir la aprobación. Cerrados: A2, A4–A9, T2, T4 (sin
  objeto) y D11 (falso positivo).

## Aplicación de la ronda 1 (2026-10-21)
- Saúl Pérez escribió "plan approved" sobre el prototipo revisado.
- Grupo 4 (tester → implementer): "Guardar" por `useMutation`, "Cancelar" sin `PUT`, `aria-disabled` (D20 revisada),
  aviso al salir con `useBlocker` y `beforeunload`, sin aviso si la sesión cambió (A5), errores que solo se van con su
  pregunta (A3). Se borró `useAutosave.ts`. Grupo 5: `pydantic_core.from_json` para las filas ilegibles (B1).
- La exploración en Chrome encontró un defecto dentro del plan: el foco caía a `<body>` tras "Seguir editando"; rojo
  (fila 17b) y arreglo, vuelto a probar en Chrome.
- Documentos: D20, investigación (D4, D5), prototipo del producto (D3), evidence (D1), afirmaciones del recorrido (D6).
- Verificación: backend 345 passed (96 %); e2e de hábitos 65 passed; suite completa como CI 245 passed.
- Sorpresa: `ui/loading-button.tsx` pone `disabled` nativo; hábitos arma su botón y el modo `aria-disabled` queda en
  la fila de D20 de la tarea de deudas. La ventana de Chrome no baja de 580 px aquí: 384 px lo cubre s26-ultra.

## Ronda 2 de la revisión (2026-10-21)
- 2 finders y 2 validadores sobre 05579b7..27c7b16: 7 confirmados, 1 parcial, 1 sin violar el contrato. El alto (R2-1):
  un "Guardar" en camino sobrevivía a cerrar sesión y entrar con otra cuenta en la misma pestaña, y su respuesta
  llegaba a la caché de la otra cuenta. La reescritura había perdido la guarda que tenía la versión anterior.
- Saúl Pérez aprobó la recomendación ("procede con tu recomendación"): R2-1…R2-4, R2-7, "Guardando…" (R2-5) y los
  documentos. Contrato y test plan ampliados (filas 26–29), rojo 97ab624, verde 8de47e1, exploración en Chrome por el
  menú lateral sin defectos.
- Deuda nueva: los chips no tienen una propiedad para quedar no disponibles; un error del `PUT` con la pantalla
  cerrada aún muestra el aviso genérico.

## Ronda 3 de la revisión (2026-10-21)
- 2 finders y 1 validador sobre 27c7b16..247f6ec: 4 confirmados (uno en parte). El medio R3-1 lo introdujo el arreglo de
  R2-2: salir mientras guarda y reabrir abría un formulario con lo de antes, y el siguiente "Guardar" borraba lo
  guardado.
- El agente objetó que el guardado en camino ya iba por la tercera ronda de bordes y propuso una regla simple: salir
  mientras guarda espera a que termine. Saúl Pérez aprobó ("procede con tu recomendación"). Rojo 45b73b3, verde
  b09397f; la fila 27 endurecida (R3-2); chips atenuados (R3-4).
