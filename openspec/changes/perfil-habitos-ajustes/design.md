# Design

Status: APPROVED
Approved by: Saúl Pérez (author) on 2026-10-21, sobre el prototipo navegable (`prototipo.html`, C-10…C-14)

**En una frase:** los hábitos ganan la edad de inicio del alcohol, un vapeador con frecuencia y edades, y la leña
como rango de edades con horas al día; la pantalla guarda sola, valida al salir de cada campo con los límites del
contrato, y conserva "Guardar" y "Cancelar", desactivados mientras guarda.

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

**Non-Goals:** guardado automático en las demás secciones (listas con diálogo); revisar el doble clic en el resto de
la app (va a la tarea de deudas, con D20 como regla); calcular horas-año o cualquier índice (C-6); la Story C2;
pasar el formulario a React Hook Form.

## Qué se toca / qué NO

| Se toca | NO se toca |
|---|---|
| `backend/app/models.py` (esquemas de hábitos, normalización, `habits_errors`, la conversión de lo guardado), `backend/app/api/routes/profile.py` (`_stored_habits` llama a la conversión) | La columna, sus migraciones, las rutas de historial |
| `frontend/openapi-ts.config.ts` (plugin `zod`), el cliente regenerado (`src/client/zod.gen.ts` nuevo, `types.gen.ts`), `frontend/src/components/Profile/HabitsForm.tsx`, `frontend/src/locales/es-MX/profile.json` | `ChipGroup.tsx`, `perfil.tsx`, las demás pantallas del perfil |
| Tests: `backend/tests/api/routes/test_profile_habits.py`, `frontend/tests/profile-habits.spec.ts` | Las suites de A y B |
| `memory/decisions/D20-…md` (nueva), la tarea de deudas en el inbox (fila del doble clic), `product/dominio.md` § Hábitos | Las demás decisiones |

**Decisiones afectadas:** D18 (chips) se aplica a "Todos los días / Algunos días". **D20 nueva:** un botón que envía
datos, o que vuelve después de enviarlos, se desactiva mientras hay un envío en curso.

**Citadores que vencen en este cambio:**
- La spec canónica `records/patient-profile` (vía la delta).
- `product/dominio.md` § Hábitos: vapeador y leña ("años aprox.").
- `profile.json`: "Años con humo de leña, aprox." y los textos de "Guardar".
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
- **Guardado automático:**
  - Un chip guarda al elegirlo; un número, al salir de su campo. Se espera 600 ms sin cambios antes de mandar.
  - Solo se manda si todo el cuestionario es válido (la misma función que arma el cuerpo). Con algún error no se
    manda nada.
  - Un `PUT` a la vez: si llega otro cambio mientras uno está en curso, al terminar se manda el estado más reciente.
  - La respuesta del `PUT` actualiza la caché `["habits"]` sin reescribir lo que el paciente está escribiendo.
  - Un 422 se ubica por `loc` como hoy; otro error deja el estado "No se pudo guardar" y se reintenta con el siguiente
    cambio o con "Guardar".
  - Si el paciente sale de la pantalla por otro camino (menú, atrás) con un guardado pendiente y válido, se manda al
    salir.
- **Estado** (`role="status"`, sin mover el foco), debajo del título y junto a los botones: "Guardando…", "Guardado",
  "Sin guardar: corrige el campo marcado" o "No se pudo guardar". Sin aviso emergente por cada guardado.
- **"Guardar":** valida todo; si hay errores, foco al primero. Si no, manda lo pendiente (si hay), avisa "Hábitos
  guardados" y vuelve a `/perfil`.
- **"Cancelar":** si lo guardado difiere de lo que había al abrir la pantalla, manda un `PUT` con lo de entonces, avisa
  "Se descartaron los cambios" y vuelve; si no, solo vuelve.
- **Desactivados (D20):** "Guardar" y "Cancelar" con `disabled` mientras hay un `PUT` en curso, incluido el suyo; el
  texto del estado dice por qué.

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
5. **Cancelar restaura lo de la apertura.** Con el guardado automático, "Cancelar" sin restaurar no haría nada; Saúl
   Pérez pidió conservarlo. Se restaura con el mismo `PUT`.
6. **Límites desde `zod.gen.ts`; reglas entre campos a mano en una función.** El OpenAPI no expresa "≤ edad actual" ni
   "inicio ≤ fin". Descartado: React Hook Form + `zodResolver` para toda la pantalla (rehace el estado por bloque).
7. **Nada en el navegador.** Ni borradores en `localStorage` (datos de salud en equipos compartidos) ni en
   `sessionStorage`. Lo que no es válido se pierde al salir, y la pantalla lo dice antes.

## Test plan (one row per scenario, mandatory)

| # | Spec · scenario | Test | Dónde |
|---|---|---|---|
| 1 | Hábitos · Alcohol actual con el AUDIT-C (C-1) | e2e existente (fila 1), ajustado al guardado automático | Playwright |
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
| 14 | Hábitos · Lo guardado antes se sigue leyendo | pytest: fila cifrada con la forma anterior en la BD de prueba → GET con vapeador `{status}` y leña sin años, el tabaco intacto; sin aviso de fila ilegible en el log. Unitario de `upgrade_stored_habits` | pytest |
| 15 | No interpreta · Sin puntaje ni riesgo (C-6) | pytest: llaves exactas del contrato nuevo. e2e: la pantalla no contiene "horas-año", "riesgo", "puntaje", "AUDIT" | pytest + Playwright |
| 16 | Se guardan solos · Una respuesta se guarda al elegirla (C-13) | e2e: elegir tabaco "Nunca", ir a `/perfil` por el menú → "Con datos"; reabrir | Playwright |
| 17 | Se guardan solos · Un número se guarda al salir de su campo (C-13) | e2e: 12 cigarros, Tab → estado "Guardado"; recargar → 12 | Playwright |
| 18 | Se guardan solos · Con un error no se guarda nada (C-13, C-14) | e2e: 101 cigarros + salir + elegir vapeador → error, estado "Sin guardar…", ningún `PUT` (contador de `page.on('request')`); recargar → vapeador "Nunca" | Playwright |
| 19 | Se guardan solos · Botones desactivados mientras guarda (C-13) | e2e: con el `PUT` retenido por `page.route`, "Guardar" y "Cancelar" `toBeDisabled()`; doble clic forzado sobre "Guardar" al soltar → un solo `PUT` más | Playwright |
| 20 | Se guardan solos · Cancelar deja todo como al abrir (C-13) | e2e: tabaco "Nunca" sembrado → "Actual" + 5 (guardado solo) → "Cancelar" → GET con "Nunca" | Playwright |
| 21 | Errores al momento · Fuera de escala al salir del campo (C-14) | e2e: leña "Actual", 25 horas, Tab → "Debe estar entre 1 y 24", `aria-invalid`, ningún `PUT`. Revisión estática: `HabitsForm.tsx` sin límites literales (grep en la verificación) | Playwright + grep |
| 22 | Aislados y cifrados (C1) | existentes: SQL directo sin texto en claro, ahora también `some_days`; 403 sin consentimiento | pytest |

## Non-functional constraints addressed

- **NFR-001 / D13:** el mismo JSON cifrado; nada en el navegador (Decision 7, fila 22).
- **NFR-008 / C-6:** sin horas-año ni índices (fila 15).
- **D18 / D20:** chips para la frecuencia; botones desactivados mientras se guarda (fila 19).
- **Accesibilidad:** estado con `role="status"` sin robar el foco; errores junto al campo (R5); nombres distintos (R7).
- **Red:** un `PUT` por pausa y uno a la vez.
- **Móvil 384 px:** la exploración en Chrome y s26-ultra recorren la pantalla con las preguntas nuevas.
- **es-MX (D15):** todos los textos en `profile.json`.

## Risks / Trade-offs

- **Lo inválido no se guarda.** Si el paciente sale con un campo marcado, lo de ese momento se pierde. Mitigación: el
  estado lo dice antes ("Sin guardar: corrige el campo marcado").
- **Cancelar después de guardados automáticos** hace un `PUT` más. Si ese `PUT` falla, se queda en la pantalla con
  "No se pudo guardar" y no vuelve.
- **Otra pestaña cambia de cuenta (N1)** recarga la pantalla: con el guardado automático se pierde, como mucho, la
  última pausa de 600 ms.
- **El cliente generado crece** con `zod.gen.ts` (todos los esquemas). Es código generado, no se edita a mano.

## Migration Plan

Sin migración de base de datos. Las filas en la forma anterior se convierten al leer (Decision 1); la siguiente
escritura las guarda en la forma nueva.

## Gate that closes the work

1. La suite completa de pytest del backend, truly green, cobertura ≥ 90 % y mypy limpio.
2. La suite completa de Playwright en chromium y s26-ultra, truly green.
3. `make tdd-check` verde.
4. `openspec validate perfil-habitos-ajustes --strict` limpio.
5. La exploración en Chrome hecha por el agente (incluido el doble clic y salir a media escritura), sin defectos; la
   revisión adversarial; el archivo como último commit del PR. Después, la validación de Saúl Pérez con
   `validation.md`. El merge es humano.

## Open Questions

Ninguna bloqueante: las preguntas de la exploración están respondidas (exploration.md §6 y la respuesta de Saúl Pérez:
"Guardar" y "Cancelar" se quedan, desactivados mientras se guarda).
