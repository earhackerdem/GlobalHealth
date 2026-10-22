# Design

Status: APPROVED
Approved by: Saúl Pérez (author) on 2026-10-21, sobre el prototipo navegable (`prototipo.html`, C-10…C-14). Revisión
aprobada por Saúl Pérez (author) el 2026-10-21, sobre el prototipo revisado: sin guardado automático (C-13 nuevo: se
guarda con "Guardar" y la pantalla avisa antes de perder cambios). Decision 8.

**En una frase:** los hábitos ganan la edad de inicio del alcohol, un vapeador con frecuencia y edades, y la leña
como rango de edades con horas al día; la pantalla valida al salir de cada campo con los límites del contrato, guarda
al tocar "Guardar" (desactivado mientras guarda) y avisa antes de salir con cambios sin guardar.

## Context

- La C1 (PR #30) guarda los hábitos como un JSON cifrado en `patient_profile.habits`, con un solo `PUT` que reemplaza
  el cuestionario (`backend/app/api/routes/profile.py`, perfil-habitos Decisions 1 y 2). Sumar campos no pide
  migración.
- `_stored_habits` lee con el esquema cerrado (`extra="forbid"`, `backend/app/models.py:855`; `profile.py:616-626`):
  sin conversión, una fila con la forma anterior se leería entera como vacía (exploration.md §2).
- No hay datos reales: no hay flujo de despliegue (`.github/workflows/`), solo cuentas de prueba locales.
- Saúl Pérez decidió (2026-10-21): un solo cambio con lo técnico (A), horas al día en la leña (B), el vapeador con
  "todos los días / algunos días" y días de los últimos 30, más edades (C), y que "Guardar" y "Cancelar" se queden,
  desactivados mientras se guardan los datos, "para evitar el happy click en todos los lados posibles".

## Goals / Non-Goals

**Goals:** C-10…C-14; leer lo guardado en la forma anterior; los límites de los números tomados del contrato; D20
(botones desactivados mientras hay un envío) registrada y aplicada en la pantalla de hábitos.

**Non-Goals:** guardado automático (Decision 8); el aviso de cambios sin guardar y el doble clic en el resto de la app
(van a la tarea de deudas, con D20 como regla); calcular horas-año o cualquier índice (C-6); la Story C2; pasar el
formulario a React Hook Form; cambiar el listener de sesión de `main.tsx` (N1, M1 ⏸️).

## Qué se toca / qué NO

| Se toca | NO se toca |
|---|---|
| `backend/app/models.py` (esquemas de hábitos, normalización, `habits_errors`, la conversión de lo guardado), `backend/app/api/routes/profile.py` (`_stored_habits` llama a la conversión) | La columna, sus migraciones, las rutas de historial |
| `frontend/openapi-ts.config.ts` (plugin `zod`), el cliente regenerado (`src/client/zod.gen.ts` nuevo, `types.gen.ts`), `frontend/src/components/Profile/HabitsForm.tsx`, `frontend/src/locales/es-MX/profile.json`; se borra `frontend/src/components/Profile/useAutosave.ts` | `ChipGroup.tsx`, `perfil.tsx`, `ui/dialog.tsx` (se usa, no se cambia), `main.tsx`, `useAuth.ts`, las demás pantallas del perfil |
| Tests: `backend/tests/api/routes/test_profile_habits.py`, `frontend/tests/profile-habits.spec.ts` | Las suites de A y B |
| `memory/decisions/D20-…md` (nueva; revisada: `aria-disabled`), la tarea de deudas en el inbox (fila del doble clic), `product/dominio.md` § Hábitos, `product/prototipos/perfil-secciones.html` (pantalla de hábitos) | Las demás decisiones |

**Decisiones afectadas:** D18 (chips) se aplica a "Todos los días / Algunos días". **D20 nueva:** un botón que envía
datos, o que sale de la pantalla mientras ese envío sigue en curso, queda no disponible hasta que termine. Revisada en
este cambio: "no disponible" es `aria-disabled` (sigue en el recorrido del teclado y no pierde el foco) y el botón
ignora el clic, no `disabled` (hallazgo A1 de la revisión).

**Citadores que vencen en este cambio:**
- La spec canónica `records/patient-profile` (vía la delta).
- `product/dominio.md` § Hábitos: vapeador y leña ("años aprox.").
- `profile.json`: "Años con humo de leña, aprox.", los textos de "Guardar" y las llaves `habits.autosave.*` (se van).
- `product/prototipos/perfil-secciones.html`: la pantalla de hábitos con alcohol sin edad de inicio, el vapeador como
  chip suelto y la leña con "años aproximados".
- Los e2e que eligen el vapeador como chip suelto o escriben los años de leña (`frontend/tests/profile-habits.spec.ts`;
  se ubican con `grep -n "vaping\|Años con humo"`).
- Los pytest de leña con `years` y de vapeador como texto (`grep -n "years\|\"vaping\"" backend/tests/api/routes/test_profile_habits.py`).

## Interface contract

Base `/api/v1`, detrás de `ConsentedUser`. Mismos `GET` y `PUT /profile/habits`; cambian estos tipos (lo demás de
`Habits` queda como en la C1):

- `alcohol: AlcoholHabit | null`: se agrega `start_age: int 0..130 | null`.
- `vaping: VapingHabit | null` (antes era el texto `"never" | "former" | "current"`):
  - `status: "never" | "former" | "current"` (requerido dentro del objeto)
  - `frequency: "daily" | "some_days" | null`
  - `days_last_30: int 1..30 | null`
  - `start_age: int 0..130 | null`
  - `quit_age: int 0..130 | null`
- `wood_smoke: WoodSmokeHabit | null`: se quita `years`; se agregan `start_age: int 0..130 | null`,
  `quit_age: int 0..130 | null` y `hours_per_day: int 1..24 | null`.

**Normalización (servidor, antes de cifrar)**, además de la de la C1:
- alcohol `never` → `start_age` a null (y `quit_age` como hoy).
- vapeador `never` → todo a null salvo `status`; ≠ `current` → `frequency` y `days_last_30` a null;
  `frequency` ≠ `some_days` → `days_last_30` a null; ≠ `former` → `quit_age` a null.
- leña `never` → `start_age`, `quit_age`, `hours_per_day` a null; ≠ `former` → `quit_age` a null.

**Validación (servidor, después de normalizar; mismo "hoy" de México y forma 422 con `loc` de la C1):**
- Cada `start_age` y `quit_age` de alcohol, tabaco, vapeador y leña mayor que la edad actual → "La edad no puede ser
  mayor que tu edad actual", en ese campo.
- `start_age` > `quit_age` → en `start_age`: alcohol "No puede ser mayor que la edad en que lo dejaste"; tabaco y
  vapeador, el mismo texto; leña "No puede ser mayor que la edad en que terminó".

**Lo guardado en la forma anterior** (`upgrade_stored_habits(raw: dict) -> dict` en `models.py`, que `_stored_habits`
aplica al JSON descifrado antes de validarlo; NO se aplica al cuerpo del `PUT`, que sigue cerrado):
- `vaping` como texto → `{"status": <texto>}`.
- `wood_smoke.years` → se descarta.
- Una fila ilegible (JSON inválido, que no es un objeto, o anidado tan hondo que el lector se rinde) se lee como
  vacía con el aviso de fila ilegible en el log, nunca como un 500 (hallazgo B1: se lee con `pydantic_core.from_json`).

**Frontend**
- **Generación:** `frontend/openapi-ts.config.ts` agrega el plugin `{ name: "zod" }`. `src/client/zod.gen.ts` exporta
  `zHabits`, `zAlcoholHabit`, `zTobaccoHabit`, `zVapingHabit`, `zSecondhandSmoke`, `zWoodSmokeHabit`. El formulario
  toma de ahí la escala de cada número: en `HabitsForm.tsx` no queda ningún límite escrito a mano (ni 130, ni 100, ni
  7, ni 30, ni 24).
- **Preguntas nuevas** (los nombres accesibles son estos textos, distintos entre sí):
  - Alcohol, con "Lo dejé" o "Actual": "¿A qué edad empezaste a tomar?", ayuda "Sin contar probaditas.".
  - Vapeador (dentro del bloque de tabaco): con "Antes" o "Actual", "¿A qué edad empezaste a vapear?"; con "Antes",
    "¿A qué edad dejaste de vapear?"; con "Actual", chips "¿Con qué frecuencia vapeas?" (Todos los días · Algunos
    días); con "Algunos días", "¿Cuántos días de los últimos 30?".
  - Leña, con "Antes" o "Actual": "¿A qué edad empezaste a exponerte?" y "¿Cuántas horas al día, en promedio?"; con
    "Antes", "¿A qué edad dejaste de exponerte?". Sale "Años con humo de leña, aprox.".
- **Validación al momento:** al salir de un campo numérico se valida ese campo (entero, escala del esquema generado,
  edad ≤ actual) y la regla de inicio ≤ fin de su bloque; el error va junto al campo con `aria-invalid` y
  `aria-describedby` (sin mover el foco). Al tocar "Guardar" se valida todo y el foco va al primer error (como hoy).
  Los mensajes de escala: "Debe estar entre {min} y {max}" con los límites del esquema.
- **Al abrir:** debajo de la introducción, el texto "Tus respuestas se guardan cuando tocas «Guardar»."
- **"Guardar":** valida todo; si hay errores, foco al primero y no manda nada. Si no, manda un `PUT` con el
  cuestionario completo por la mutación de TanStack Query (con el manejo de 401/403 de `main.tsx`), avisa "Hábitos
  guardados" y vuelve a `/perfil`. Un 422 se ubica por `loc` como en la C1. Al terminar el `PUT`, todo eso ocurre solo
  si la pantalla sigue abierta y el token es el de cuando se abrió; si no, la respuesta no se escribe en la caché: solo
  se invalida `["habits"]` (se vuelve a pedir con la sesión de ese momento), sin aviso ni navegación (hallazgos R2-1 y
  R2-2 de la ronda 2).
- **"Cancelar":** no manda nada. Si hay cambios sin guardar, vuelve con el aviso "Se descartaron los cambios"; si no,
  solo vuelve. Nunca abre el diálogo de salida.
- **No disponibles mientras guarda (D20):** "Guardar" y "Cancelar" con `aria-disabled="true"` mientras el `PUT` está en
  curso; un clic o Enter en ellos no hace nada, y el foco se queda donde estaba. Mientras tanto "Guardar" dice
  "Guardando…" con el indicador de carga de los demás formularios (como el prototipo aprobado; R2-5), armado en
  `HabitsForm.tsx`: `ui/loading-button.tsx` pone `disabled` nativo y no se toca aquí (su modo `aria-disabled` va a la
  fila de D20 de la tarea de deudas). Las preguntas tampoco aceptan cambios mientras guarda: los chips con
  `aria-disabled="true"` ignoran el clic y se ven atenuados como "Guardar" (R3-4), y los números quedan de solo lectura
  (R2-3).
- **Cambios sin guardar:** hay cambios si lo que está en pantalla (incluido un número escrito sin salir del campo)
  difiere de lo que había al abrir. Elegir una opción y volver a la de antes no cuenta como cambio.
- **Aviso al salir dentro de la app** (menú, "‹ Mi perfil médico", atrás del navegador), con `useBlocker` de TanStack
  Router: un diálogo (`ui/dialog.tsx`) "¿Salir sin guardar?" con el texto "Los cambios que hiciste en Hábitos se van a
  perder." y los botones "Seguir editando" (con el foco al abrir) y "Salir sin guardar". "Seguir editando" deja la
  pantalla como estaba, con el foco donde estaba; si ese elemento ya no existe (el menú lateral del celular o el menú de
  usuario se cerraron), el foco va al título "Hábitos" (R2-4). "Salir sin guardar" sigue a donde iba. No aparece
  después de "Guardar" o "Cancelar", ni mientras el `PUT` de "Guardar" está en curso (R2-2). **Salir mientras guarda
  espera a que termine** (ronda 3, R3-1 y R3-3): la navegación queda retenida sin diálogo; si el guardado sale bien,
  avisa "Hábitos guardados" y sigue a donde iba (no a `/perfil`); si falla, la navegación se cancela y la pantalla se
  queda con el error a la vista (un 422 junto a su campo, otro error con el aviso genérico). Así no se puede reabrir la
  pantalla con datos de antes del guardado. No retiene la salida si la sesión terminó o cambió. Recargar o cerrar la
  pestaña mientras guarda no pregunta.
- **Aviso al recargar o cerrar la pestaña:** el evento `beforeunload` pide el aviso del navegador (su texto no se puede
  cambiar).
- **Sin aviso cuando la sesión terminó o cambió:** si el token de `localStorage` ya no es el de cuando se abrió la
  pantalla (cerrar sesión aquí o en otra pestaña, o una petición que encontró la sesión vencida y la cerró), ni el
  diálogo ni el aviso del navegador aparecen: la
  salida es obligatoria y quedarse permitiría guardar lo de una cuenta con la sesión de otra (hallazgo A5).
- **Errores y opciones (hallazgo A3):** al elegir una opción, se borran solo los errores de las preguntas que se
  ocultan; un campo que sigue a la vista conserva su marca.

## Decisions

1. **Conversión al leer, no migración.** No hay datos reales; una función pura sobre el JSON descifrado se prueba
   sola, y el `PUT` sigue cerrado (`extra="forbid"`). Descartado: migración Alembic que descifra y vuelve a cifrar
   (más riesgo, cero beneficio sin datos reales) y aceptar el texto viejo en el `PUT` (abre el contrato).
2. **Vapeador como objeto propio, no dentro de `tobacco`.** Tiene su propia frecuencia (días de los últimos 30) que el
   tabaco no tiene. Descartado: reutilizar `TobaccoHabit` (cigarros al día no aplica).
3. **Los años de leña se descartan.** No se pueden convertir a una edad de inicio sin inventar el dato. La pantalla
   pide la edad de inicio en su lugar.
4. **Guardar solo cuando todo es válido.** Guardar un campo inválido como null borraría lo guardado antes; guardar por
   bloque exige un endpoint por bloque (descartado en la C1, Decision 2).
5. **Cancelar descarta sin mandar nada.** Sin guardado automático no hay nada que restaurar (reemplaza a la Decision 5
   aprobada, "Cancelar restaura con un `PUT`").
6. **Límites desde `zod.gen.ts`; reglas entre campos a mano en una función.** El OpenAPI no expresa "≤ edad actual" ni
   "inicio ≤ fin". Descartado: React Hook Form + `zodResolver` para toda la pantalla (rehace el estado por bloque).
7. **Nada en el navegador.** Ni borradores en `localStorage` (datos de salud en equipos compartidos) ni en
   `sessionStorage`. Lo no guardado se pierde al salir, y la pantalla avisa antes.
8. **Guardar con el botón, con aviso al salir, en vez de guardado automático.** Decidido por Saúl Pérez el 2026-10-21,
   tras la revisión ronda 1 del PR #32. El guardado automático con un `PUT` que reemplaza todo el cuestionario trajo
   un hallazgo alto (con otra pestaña que entra a otra cuenta, un guardado pendiente mandaba los hábitos de una cuenta
   con la sesión de otra, A5) y siete más (A2, A4, A6–A9, T2) que salen del mismo mecanismo. Descartado: arreglar el
   guardado automático (token por pestaña en `main.tsx` y `useAuth.ts`, fuera del alcance, más una cola con foto de lo
   confirmado). Costo: en el celular, si el navegador cierra la pestaña en segundo plano, lo no guardado se pierde.

## Test plan (one row per scenario, mandatory)

| # | Spec · scenario | Test | Dónde |
|---|---|---|---|
| 1 | Hábitos · Alcohol actual con el AUDIT-C (C-1) | e2e existente (fila 1), con "Guardar" | Playwright |
| 2 | Hábitos · Lo dejó, con la edad (C-1, C-10) | pytest: `quit` + 17/30 → GET igual. e2e: reabrir muestra 17 y 30 | pytest + Playwright |
| 3 | Hábitos · Alcohol: empezó después de dejarlo (C-10) | pytest: 30/18 → 422 en `["body","alcohol","start_age"]`. e2e: error junto a la edad de inicio al salir del campo, nada guardado | pytest + Playwright |
| 4 | Hábitos · Una edad mayor que la actual (C-1, C-2) | pytest: las ocho edades (inicio y fin de los cuatro bloques) con 40 → 422 en su `loc`. e2e existente (fila 3) | pytest + Playwright |
| 5 | Hábitos · Lo que no aplica se descarta (C-1) | pytest: cada regla nueva de normalización (alcohol `never`, vapeador, leña). e2e existente (fila 4) | pytest + Playwright |
| 6 | Hábitos · Tabaco que dejó, y vapeador actual (C-2) | pytest y e2e existentes, con el vapeador como objeto ("Actual", "Todos los días") | pytest + Playwright |
| 7 | Hábitos · Empezó después de dejarlo (C-2) | existentes | pytest + Playwright |
| 8 | Hábitos · Vapeador actual algunos días (C-11) | pytest roundtrip. e2e: llenarlo y verlo al reabrir | pytest + Playwright |
| 9 | Hábitos · Vapeador de antes, y luego todos los días (C-11) | pytest: normalización (`daily` vacía días; `former` vacía frecuencia y días). e2e: la pregunta de días se oculta con "Todos los días"; al final "Antes" con 25/28 | pytest + Playwright |
| 10 | Hábitos · Humo ajeno… (C-3) | existentes | pytest + Playwright |
| 11 | Hábitos · Humo de leña de antes (C-4, C-12) | pytest roundtrip y `start_age` > `quit_age` → 422. e2e: verlo al reabrir | pytest + Playwright |
| 12 | Hábitos · Contesta solo una cosa | e2e existente (fila 9), con el vapeador como objeto | Playwright |
| 13 | Hábitos · Respuestas fuera de su escala | pytest: los casos nuevos (días 0/31, horas 0/25, `vaping` como texto en el `PUT`, `years` en el `PUT`) → 422 y GET sin cambios | pytest |
| 14 | Hábitos · Lo guardado antes se sigue leyendo | pytest: fila cifrada con la forma anterior en la BD de prueba → GET con vapeador `{status}` y leña sin años, el tabaco intacto; sin aviso de fila ilegible en el log. Unitario de `upgrade_stored_habits`. Filas ilegibles: JSON inválido, una lista y un JSON anidado 100 000 niveles (con `json.loads` es `RecursionError`, verificado hoy) → GET 200 con hábitos vacíos y el aviso en el log | pytest |
| 15 | No interpreta · Sin puntaje ni riesgo (C-6) | pytest: llaves exactas del contrato nuevo. e2e: la pantalla no contiene "horas-año", "riesgo", "puntaje", "AUDIT" | pytest + Playwright |
| 16 | Guardar · Se guarda al tocar "Guardar" (C-13) | e2e: el texto "Tus respuestas se guardan cuando tocas «Guardar»."; elegir tabaco "Nunca" sin tocar nada más → ningún `PUT` (contador de `page.on('request')`); "Guardar" → un `PUT`, aviso "Hábitos guardados", tarjeta "Con datos"; reabrir | Playwright |
| 17 | Guardar · Aviso al salir con cambios sin guardar (C-13) | e2e: tabaco "Nunca" sembrado → "Actual", 12 sin salir del campo, "‹ Mi perfil médico" → diálogo con el foco en "Seguir editando"; "Seguir editando" → misma pantalla con "Actual" y 12; atrás del navegador → diálogo; "Salir sin guardar" → `/perfil`, ningún `PUT`, GET con "Nunca" | Playwright |
| 18 | Guardar · Sin cambios no hay aviso (C-13) | e2e: abrir y volver sin tocar → sin diálogo; elegir "Actual" y volver a "Nunca" → sin diálogo | Playwright |
| 19 | Guardar · Aviso del navegador al recargar (C-13) | e2e: con un cambio, `page.reload()` → `page.on('dialog')` recibe uno de tipo `beforeunload`; sin cambios, ninguno | Playwright |
| 20 | Guardar · Sin aviso cuando la sesión cambió (C-13, N1) | e2e: con un cambio, otra pestaña del mismo contexto cierra sesión → esta llega a `/login` sin diálogo de la app ni `beforeunload`, ningún `PUT` | Playwright |
| 21 | Guardar · No disponibles mientras guarda (C-13, D20) | e2e: con el `PUT` retenido por `page.route`, "Guardar" (con el texto "Guardando…") y "Cancelar" con `aria-disabled="true"`, el foco sigue en "Guardar"; Enter y un clic más → un solo `PUT`; al soltarlo, `/perfil` | Playwright |
| 22 | Guardar · Cancelar descarta (C-13) | e2e: tabaco "Nunca" sembrado → "Actual" + 5 → "Cancelar" → `/perfil` con "Se descartaron los cambios", sin diálogo, ningún `PUT`; abrir y "Cancelar" sin cambios → sin ese aviso | Playwright |
| 23 | Errores al momento · Fuera de escala al salir del campo (C-14) | e2e: leña "Actual", 25 horas, Tab → "Debe estar entre 1 y 24", `aria-invalid`, ningún `PUT`. Lo mismo, sin `PUT`, para 40 en una edad (mayor que la actual), inicio 30 y fin 18 en vapeador y en leña, y "12a" ("Escribe solo el número."). Revisión estática: `HabitsForm.tsx` sin límites literales (grep en la verificación) | Playwright + grep |
| 24 | Errores al momento · La marca sigue mientras el campo está a la vista (C-14) | e2e: tabaco "Actual", 101 cigarros, Tab → error; elegir "Antes" → el error y `aria-invalid` siguen junto a los cigarros | Playwright |
| 26 | Guardar · Solo un número cambia (C-13; R2-7) | e2e: tabaco "Actual" con 12 sembrado; escribir 20 sin salir del campo ni tocar chips → "‹ Mi perfil médico" pregunta; "Cancelar" avisa "Se descartaron los cambios"; recargar pide `beforeunload` | Playwright |
| 27 | Guardar · Un guardado en camino no cruza de cuenta en la misma pestaña (C-13; R2-1, R3-2) | e2e: A elige tabaco "Actual" 20 y "Guardar" (`PUT` retenido); "Cerrar sesión" real; B entra por el formulario real, con su GET de hábitos demorado; al soltar el `PUT` de A: B no es llevado a `/perfil` ni ve "Hábitos guardados"; con el GET de B todavía demorado, la tarjeta de B no dice "Con datos" y su formulario no muestra "Actual" ni 20; el GET de B sigue vacío | Playwright |
| 28 | Guardar · Mientras guarda no se cambia nada, y salir espera sin preguntar (C-13; R2-2, R2-3, R3-1, R3-4) | e2e: `PUT` retenido; un chip con `aria-disabled="true"`, atenuado (opacidad < 1) y su clic no cambia nada; un número de solo lectura; el menú → "Expediente": sin diálogo, la URL sigue en `/perfil/habitos` mientras el `PUT` está retenido; al soltarlo, `/expediente` con "Hábitos guardados" y el GET trae lo guardado; reabrir "Hábitos" muestra lo guardado | Playwright |
| 30 | Guardar · Un rechazo al salir se queda a la vista (C-13; R3-3) | e2e: fecha de nacimiento cambiada por la API después de abrir (como R9); alcohol "Lo dejé" con 40 → "Guardar" (`PUT` retenido) → "‹ Mi perfil médico" → al soltar, 422: sigue en `/perfil/habitos` con "La edad no puede ser mayor que tu edad actual" junto al campo; nada guardado | Playwright |
| 29 | Guardar · El foco vuelve al título si su elemento ya no existe (C-13; R2-4) | e2e en s26-ultra: con un cambio, menú lateral → "Mi perfil médico" → diálogo → "Seguir editando" → foco en el título "Hábitos" | Playwright |
| 25 | Aislados y cifrados (C1) | existentes: SQL directo sin texto en claro, ahora también `some_days`; 403 sin consentimiento | pytest |

## Non-functional constraints addressed

- **NFR-001 / D13:** el mismo JSON cifrado; nada en el navegador (Decision 7, fila 25).
- **NFR-008 / C-6:** sin horas-año ni índices (fila 15).
- **D18 / D20:** chips para la frecuencia; botones no disponibles mientras se guarda, sin perder el foco (fila 21).
- **Accesibilidad:** errores junto al campo (R5); nombres distintos (R7); el diálogo de salida con el foco en "Seguir
  editando" y Escape como "Seguir editando"; `aria-disabled` en vez de `disabled` (fila 21).
- **Red:** un `PUT` por "Guardar".
- **Móvil 384 px:** s26-ultra recorre la pantalla con las preguntas nuevas; la exploración en Chrome, a 580 px (el mínimo de la ventana en este equipo).
- **es-MX (D15):** todos los textos en `profile.json`.

## Risks / Trade-offs

- **Lo no guardado se pierde** si el navegador cierra la pestaña sin avisar (en el celular, en segundo plano) o si la
  sesión termina. Mitigación: el texto al abrir y los dos avisos de salida (Decision 8).
- **El aviso del navegador** (`beforeunload`) tiene el texto del navegador, y algunos navegadores de celular no lo
  muestran.
- **El cliente generado crece** con `zod.gen.ts` (todos los esquemas). Es código generado, no se edita a mano.

## Migration Plan

Sin migración de base de datos. Las filas en la forma anterior se convierten al leer (Decision 1); la siguiente
escritura las guarda en la forma nueva.

## Gate that closes the work

1. La suite completa de pytest del backend, truly green, cobertura ≥ 90 % y mypy limpio.
2. La suite completa de Playwright en chromium y s26-ultra, truly green.
3. `make tdd-check` verde.
4. `openspec validate perfil-habitos-ajustes --strict` limpio.
5. La exploración en Chrome hecha por el agente (doble clic, salir a media escritura por el menú y por atrás, recargar,
   cerrar sesión en otra pestaña), sin defectos; la ronda 2 de la revisión adversarial sobre lo que cambió; el archivo
   como último commit del PR. Después, la validación de Saúl Pérez con
   `validation.md`. El merge es humano.

## Open Questions

Ninguna bloqueante: las preguntas de la exploración están respondidas (exploration.md §6 y las respuestas de Saúl
Pérez: "Guardar" y "Cancelar" se quedan, desactivados mientras se guarda; sin guardado automático, Decision 8).
