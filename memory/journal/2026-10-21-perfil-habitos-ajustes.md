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
238 + el heredado `login.spec.ts:87` en otra. Exploración en Chrome (8 intentos, sin defectos). Números en
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
