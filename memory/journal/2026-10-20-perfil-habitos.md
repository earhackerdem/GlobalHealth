# 2026-10-20 · perfil-habitos (Story C1: sustancias y humo)

**Quién:** Saúl Pérez (author) con el agente (orquestador), con tester e implementer por grupo.

## Intención
Llenar la tarjeta "Hábitos" (FR-028). En la exploración Saúl Pérez partió la Story C en dos ("1. Dos") y aceptó
las recomendaciones: el servidor descarta lo que no aplica y las edades imposibles se rechazan junto a su campo.
Esta es la C1: alcohol con el AUDIT-C, tabaco y vapeador, humo ajeno y humo de leña, sin puntajes (C-6).

## Qué se hizo
- `patient_profile.habits` cifrado (migración `7d3e9a1c5b42`), `GET/PUT /profile/habits` con normalización y
  errores 422 con `loc` (para no enrutar por el texto, hallazgo R20 de la Story B).
- Pantalla `/perfil/habitos`, `ChipMultiGroup` (chips de selección múltiple con opción excluyente, D18) y la
  tarjeta enlazada con "Sin llenar" / "Con datos".
- El gate pidió la frase literal: Saúl Pérez escribió "procece" y después "plan approved".

## Verificación
Backend 289 passed (cobertura 96 %), grupo 2 101 passed (chromium + s26-ultra), suite Playwright completa 203
passed en 2 de 3 corridas (la otra, el flake heredado de `login.spec.ts:87`). Exploración en Chrome sin defectos.
Números en `openspec/changes/perfil-habitos/evidence.md`.

## Sorpresas
- `localhost:8000` resuelve a `::1`, donde contesta el contenedor; el `fastapi dev` ajeno (PID 1076) solo escucha en
  `127.0.0.1`. Con la imagen vieja, el navegador no veía las rutas nuevas y `make migrate` no migraba. Se reconstruyó
  la imagen.
- La ventana de Chrome de la sesión anterior quedó en 114 px y no aceptaba cambios de tamaño; una pestaña nueva sí.

## Deuda
Ver evidence.md § Deuda.

## Revisión (ronda 1) y apply
- `/epe-4-review` con 5 lentes: 26 hallazgos tras deduplicar, todos reproducidos por validadores distintos. 23
  confirmados (3 medios: R1, R4, R5), R15 dudoso, R16 falso positivo, R3 descartado. Comentarios FINDER y VALIDATOR
  en el PR #30.
- **Gate:** Saúl Pérez aprobó "según tu recomendación": bloques 1 y 2 aplicados, R1 dentro de este PR aunque toca
  `useAuth.ts` (fuera del plan; ampliación registrada en design.md § Qué se toca), R14 como chips «Sí» / «No»
  (D18), y a deuda R15, R19, R20, R21 y R23. R16 y R3 se cierran (🔒). Tres veredictos en `memory/closed/`.
- **R1 (privacidad):** cerrar sesión no vaciaba la caché de consultas. Otro paciente que entraba sin recargar veía
  los hábitos del anterior y podía guardarlos en su perfil, y veía también el correo anterior en el menú. La causa
  es anterior a este cambio y la pantalla de hábitos la convirtió en una escritura. Ahora `queryClient.clear()`
  corre al cerrar y al iniciar sesión. El e2e de regresión falla sin el fix (B ve "Actual" marcado) y pasa con él;
  lo comprobó también el orquestador.
- Dos fixers con archivos disjuntos, sin autoridad para descartar; aplicaron los 16 hallazgos y no rebotaron
  ninguno. Los mutantes `nosort`, `ge` y `utc` ahora mueren.
- Efecto de R2, avisado por el fixer back: una fila ilegible se lee vacía, y si el paciente guarda la reemplaza.
  El PUT ya reemplazaba sin leer, así que no es un camino nuevo; es el mismo criterio que el historial (S4).
- Verificación tras el apply: backend 303 passed (cobertura 96 %); e2e del cambio 115 passed; suite completa en 3
  corridas: 217, 216 + 1 (`reset-password.spec.ts:90`) y 215 + 2 (ese y `login.spec.ts:87`). El de login falla al
  esperar el saludo, antes del cierre de sesión, con la misma tasa que antes del fix (1 de 3), y pasa 10/10 solo.
- **Ronda 2** (sobre lo que cambió el apply, 2026-10-21): 3 finders y un validador distinto. Sin regresiones; 7
  hallazgos confirmados. N1 (medio): el fix de R1 solo vaciaba la pestaña que cerraba o iniciaba sesión, y otra
  pestaña abierta guardaba los datos de A con el token de B; también pasaba antes, en `main`, con "Editar datos
  básicos". Saúl Pérez pensó que podía venir de las dos instancias en `:8000` y pidió apagar la ajena (PID 1076):
  se apagó y N1 se reprodujo igual. Saúl eligió arreglarlo en este PR (opción a), aunque toca `main.tsx`: ahora un
  listener de `storage` vacía la caché y lleva a `/login` cuando otra pestaña cambia el token. N2 (la prueba de R1
  ahora también vigila el correo del menú), N3 («No» guarda `false`, e2e y backend) y D1–D4 (textos que el apply dejó
  viejos, incluido `product/dominio.md`). Verificación: backend 304 passed, e2e del cambio 119 passed, suite completa
  221 · 221 · 220 + el heredado `reset-password.spec.ts:90`.
- **Ronda 3** (sobre el apply de la ronda 2, 2026-10-21): 2 finders, sin defectos de código. Ni bucles de recarga ni
  caminos de sesión sin cubrir (expirada, `localStorage.clear()`, Google, bfcache). 4 bajos: M1 (otra pestaña con
  un token nuevo de la MISMA cuenta también recarga y pierde el borrador) a deuda ⏸️, aceptado por Saúl Pérez; M2
  pruebas renombradas a "N1"/"N3 (ronda 2)" porque "R2" chocaba con el R2 de la ronda 1; M3 bloque "Cambiar de
  cuenta" en validation.md; M4 la casilla "truly green" del PR se desmarca (una corrida tuvo el heredado). Saúl
  Pérez pidió además una tarea para atender TODAS las deudas antes de la investigación de UX:
  `memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`, y el orden quedó también en el
  pendiente de la ronda 2 del dominio.
- El hook `lint.py` volvió a marcar el `except A, B:` (PEP 758) de `profile.py:220` con el Python 3.9 del sistema;
  ya está en el inbox del template.
