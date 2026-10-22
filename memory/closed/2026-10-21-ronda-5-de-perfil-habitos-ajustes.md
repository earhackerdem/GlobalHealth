---
date: 2026-10-21
state: deferred
anchor: journal: 2026-10-21 · perfil-habitos-ajustes (C-10…C-14)
---
Ronda 5 de perfil-habitos-ajustes (PR #32, diff fd6acf7..1c81af1), seis hallazgos bajos: R5-1 `focusTitleOnceGone` (`HabitsForm.tsx:395-398`) manda el foco al título aunque el usuario ya lo haya puesto en otro campo durante la espera (4/4 escritorio y 384 px); R5-2 el `takeBack` de 1 s deshace el primer movimiento del usuario fuera del formulario en el menú lateral del celular (3/4); R5-3 un 422 con el menú de usuario aún cerrándose deja el foco en el botón del menú, no en el campo (4/4, no es regresión); R5-4 las ramas `!placed` y "el elemento sigue en pantalla" de R4-3 no tienen prueba (los mutantes sobreviven 80/80); R5-5 `prototipo.html` no dice en su resumen C-13 que salir espera, `salidaPendiente` no se lee y no simula un fallo, y la fila de la ronda 2 en evidence.md no dice que fue superada; R5-6 la SHALL nueva de la spec no exceptúa la sesión que termina durante la espera (401/403 → `/login`) y limita la espera a "dentro de la app" aunque atrás también espera

**Verdict and why:** Reproducidos por los finders (R5-1…R5-4) o leídos (R5-5, R5-6); sin validador, por la regla de cierre que Saúl Pérez aprobó en la ronda 4: si la ronda 5 trae solo hallazgos bajos, quedan como deuda registrada y se archiva. Ninguno pierde datos ni cruza cuentas; R5-1/R5-2 son el costo del respaldo de foco de R4-3. Se pagan con la fila de foco y D20 de la tarea de deudas (`memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`)

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-21 · perfil-habitos-ajustes (C-10…C-14)
