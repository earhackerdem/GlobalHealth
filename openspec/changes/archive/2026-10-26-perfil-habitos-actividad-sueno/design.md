# Design

Status: APPROVED
Approved by: Saúl Pérez (author) on 2026-10-26, después de navegar el prototipo
Enmendado tras la aprobación (2026-10-26, por el agente orquestador, durante el grupo 1): `routes/profile.py` pasa a «Se
toca» (una línea del `loc`) y el nombre de «Otra» queda sin mínimo en el esquema (vacío = sin contestar). Saúl Pérez lo
vio en la revisión del PR #34 y aprobó seguir.

**En una frase:** el cuestionario de hábitos suma ejercicio (actividades con días y minutos, o "No hago ejercicio", con
el total semanal a la vista), movimiento del día y sueño, con las formas de NHANES, GPAQ y NHIS, las mismas reglas de
guardado y obligatoriedad que la C1, y sin ningún veredicto.

## Context

- La C1 dejó el cuestionario como un esquema cerrado que la C2 extiende a propósito (`backend/app/models.py:843`,
  `Habits` en `:923`); la normalización (`:997`), la tabla de obligatoriedad (`HABITS_REQUIRED`, `:1021`) y
  `habits_errors` (`:1060`) corren en el `PUT` de reemplazo completo, que responde 422 por `loc`.
- La pantalla (`frontend/src/components/Profile/HabitsForm.tsx`) ya tiene chips (D18), chips múltiples con preguntas
  que dependen de lo elegido (humo ajeno, `:426`, `:1389`), números con límites leídos de `zod.gen.ts`, obligatorias al
  guardar (C-15), errores al salir y que se van al corregir (C-14, C-17), y "Guardar" con aviso de salida (C-13, D20).
- Saúl Pérez partió la C2 (2026-10-26) y eligió, con la investigación (`memory/research/habitos.md#actividad-sueno`):
  dos preguntas de insomnio de NHIS con 4 puntos, los 4 niveles de NHANES `PAQ180` para el día, el chip "No hago
  ejercicio" y las horas de sueño enteras en 24 horas.

## Goals / Non-Goals

**Goals:** C-5, C-7, C-8 con C-6 y C-13…C-17 vigentes en los bloques nuevos.

**Non-Goals:** "Trabajo" en el Perfil básico (C2b); confirmaciones suaves de valores raros (≤5 h de sueño, >240 min por
vez); separar el sueño de días laborales y libres; distinguir fuerza de aeróbico en el total; sumar el desplazamiento al
ejercicio; datos de wearables; una vista para el médico.

## Qué se toca / qué NO

| Se toca | NO se toca |
|---|---|
| `backend/app/models.py` (bloques `exercise`, `daily_movement`, `sleep`; normalización; filas de obligatoriedad; `loc` de cuatro niveles) y una línea de `routes/profile.py` (el `loc` del 422 parte el campo en sus niveles; corrección del plan durante el grupo 1: la ruta armaba siempre tres elementos y el contrato pide cinco) | El resto de `routes/profile.py`, la columna, migraciones, `upgrade_stored_habits` |
| Cliente regenerado (`types.gen.ts`, `zod.gen.ts`), `HabitsForm.tsx`, `frontend/src/locales/es-MX/profile.json` | `ChipGroup.tsx`, `ui/*`, `history.ts` (`hasHabits` ya cuenta los bloques nuevos), las demás pantallas |
| Tests: `backend/tests/api/routes/test_profile_habits.py`, `frontend/tests/profile-habits.spec.ts` | Las suites de las demás secciones |
| `product/dominio.md` § Hábitos, `product/prototipos/perfil-secciones.html` (C-5, C-7, C-8) | Las decisiones |

**Decisiones afectadas:** D18 (chips) y D20 (no disponibles mientras guarda) se aplican a los bloques nuevos; ninguna
cambia.

**Citadores que vencen:** la spec canónica (vía la delta); `product/dominio.md` § Hábitos (filas ejercicio, movimiento
del día y sueño, con la escala de 3, "horas por noche" y "sin actividades = no hago ejercicio"); el prototipo de producto
(C-5, C-7, C-8 y su leyenda, `perfil-secciones.html:134-137`, `:507-540`).

## Interface contract

Base `/api/v1`, detrás de `ConsentedUser`. Mismos `GET` y `PUT /profile/habits`. `Habits` suma tres propiedades
opcionales (cada bloque `null` si no se contesta; lo demás de `Habits` queda igual):

```
exercise: {
  does_exercise: bool,                       # false = "No hago ejercicio"
  activities: {                              # cerrado; una propiedad por tipo, null si no se eligió
    walking | running | cycling | swimming | weights_gym | football_other_sport | yoga_pilates | dance:
      { days_per_week: int 1..7 | null, minutes_per_session: int 1..600 | null } | null,
    other: { name: str ..60 (recortado; vacío = sin contestar, "Escribe cuál."; antes 1..60, enmienda tras la
                   aprobación) | null, days_per_week: int 1..7 | null,
             minutes_per_session: int 1..600 | null } | null
  }
} | null
daily_movement: {
  main_activity: "sitting" | "standing_walking" | "light_loads" | "heavy_work" | null,
  active_travel: bool | null,
  active_travel_days: int 1..7 | null,
  sitting_hours: int 0..24 | null
} | null
sleep: {
  hours: int 1..24 | null,
  trouble_falling_asleep: "never" | "some_days" | "most_days" | "every_day" | null,
  trouble_staying_asleep: "never" | "some_days" | "most_days" | "every_day" | null
} | null
```

Ningún campo nuevo acepta `"unknown"` ni otro texto que no sea su escala (422 de esquema, como hoy).

**Normalización:** `does_exercise: false` → todas las actividades `null`; `active_travel` distinto de `true` →
`active_travel_days: null`; el nombre de "Otra" recortado, y vacío → `null`.

**Validación (servidor, después de normalizar; un error por campo; forma 422 con `loc` de la C1):**

| Respuesta | Obligatorio | Mensaje |
|---|---|---|
| `exercise.does_exercise: true` sin ninguna actividad | `exercise.activities` | "Elige al menos una actividad, o «No hago ejercicio»" |
| una actividad elegida | sus `days_per_week` y `minutes_per_session` | "Contesta esta pregunta." |
| `other` elegida | su `name` | "Escribe cuál." |
| `daily_movement.active_travel: true` | `active_travel_days` | "Contesta esta pregunta." |

El `loc` de un campo de actividad es `["body", "exercise", "activities", "<tipo>", "<campo>"]`.

**Frontend**
- **Ejercicio:** "¿Qué ejercicio haces?" con un chip por actividad (varios) y "No hago ejercicio" (lo excluye, como "No
  me expongo"). Por cada actividad elegida, en el orden del catálogo: "Días por semana" y "Minutos cada vez" (nombres
  accesibles "Días por semana: <actividad>" y "Minutos cada vez: <actividad>", R7), y con "Otra", "¿Cuál?" antes.
  Debajo, "Total de lo anotado: N minutos por semana", que suma solo las actividades con días y minutos válidos y no se
  muestra si no hay ninguna.
- **Movimiento del día:** "En tu trabajo o actividad principal (casa, escuela…), ¿cómo pasas el día?" con los 4
  niveles; "¿Caminas o vas en bici al menos 10 minutos seguidos para ir a algún lado?" (No · Sí) y, con *Sí*,
  "¿Cuántos días por semana?"; "En un día normal, ¿cuántas horas pasas sentado o reclinado?" con la ayuda "Sin contar el
  tiempo que duermes.".
- **Sueño:** "En promedio, ¿cuántas horas duermes en un día?" con la ayuda "Cuenta las siestas. Si son 6 y media,
  escribe 7."; "En los últimos 30 días, ¿con qué frecuencia te costó dormirte?" y "En los últimos 30 días, ¿con qué
  frecuencia te costó seguir durmiendo o despertaste demasiado temprano?", con Nunca · Algunos días · Casi todos los
  días · Todos los días.
- Obligatorias al tocar "Guardar" (C-15) con el error junto a su pregunta y el foco al primero; errores de escala al
  salir del campo (C-14) y que se van al corregir (C-17); todo cuenta como cambio sin guardar y queda no disponible
  mientras guarda (D20). Los límites salen de `zod.gen.ts`.

## Decisions

1. **Un chip por tipo de actividad, no filas con "Agregar".** Evita repetidos, da un `loc` estable por tipo y reutiliza
   el patrón del humo ajeno (D18). Lo pierde: dos sesiones distintas de la misma actividad se anotan juntas.
2. **Actividades como objeto cerrado con una propiedad por tipo, no una lista ni un diccionario libre.** El cliente
   Zod se genera limpio y el esquema sigue rechazando lo desconocido.
3. **"No hago ejercicio" explícito (`does_exercise: false`).** Distingue "no hace" de "no contestó", como "Nunca" y la
   marca "ninguna" de las secciones (Saúl Pérez, 2026-10-26).
4. **El total semanal se calcula en la pantalla y no se guarda.** Es la suma de lo anotado (EVS), no un dato nuevo; se
   rotula "de lo anotado" porque mezcla fuerza y aeróbico (el CDC no suma pesas ni yoga) y nunca se compara (C-6).
5. **Formas estándar:** insomnio con los dos ítems de NHIS y su escala de 4; el día con los 4 niveles de NHANES
   `PAQ180`; horas de sueño enteras en 24 h (NHIS/BRFSS; ENSANUT 2022 pregunta "en un día" y usa 5 categorías, de ≤5
   a ≥9 h, en las que las horas enteras se agrupan, pero no al revés); desplazamiento y tiempo sentado del GPAQ
   panamericano (`habitos.md#actividad-sueno`). Así lo anotado se compara con NHIS, BRFSS y NHANES `PAQ180` sin
   convertir; con ENSANUT, agrupando; y con el GPAQ, de forma aproximada (horas sentado enteras frente a sus
   horas:minutos, y el desplazamiento, abajo).
   **El desplazamiento omite la introducción del GPAQ.** La guía de análisis pide no omitirla ("This statement should
   not be omitted", GPAQ Analysis Guide, OMS, p. 8 del PDF,
   https://www.who.int/docs/default-source/ncds/ncd-surveillance/gpaq-analysis-guide.pdf, consultada 2026-10-26).
   [OPINION] Se omite porque la pregunta ya lleva el propósito ("para ir a algún lado") y el caminar por gusto va en el
   chip "Caminar" del ejercicio, así que no se cuenta dos veces. Lo pierde: la comparación con el desplazamiento del
   GPAQ es aproximada, no exacta.
6. **Sin "No recuerdo" en estos bloques.** Todo describe el presente (Decision 2 de perfil-habitos-completitud).
7. **Regla de cierre de la revisión, decidida antes de la primera ronda** (lección de los PR #32 y #33): si una ronda
   después de la primera trae solo hallazgos bajos, quedan como deuda registrada y se archiva.

## Test plan (one row per scenario, mandatory)

| # | Spec · scenario | Test | Dónde |
|---|---|---|---|
| 1 | Dos actividades con su total (C-5) | pytest: `PUT` con caminar 5×30 y pesas 2×45 → 200, GET igual y sin total. e2e: elegir, ver "Total de lo anotado: 240 minutos por semana", guardar, reabrir | pytest + Playwright |
| 2 | Otra actividad con su nombre (C-5) | pytest: `other` sin `name` → 422 en `["body","exercise","activities","other","name"]` "Escribe cuál."; con "  Senderismo " → se guarda recortado. e2e: el mensaje junto a "¿Cuál?", foco ahí, ningún `PUT`; con nombre, se guarda y se ve al reabrir | pytest + Playwright |
| 3 | Falta un dato de una actividad (C-5, C-15) | pytest: por cada tipo y por cada campo (días, minutos), `null` u omitido → 422 en su `loc` de cuatro niveles con "Contesta esta pregunta.", GET sin cambios. e2e: correr 3 días sin minutos → mensaje, foco, ningún `PUT`, ningún "No recuerdo" en el bloque | pytest + Playwright |
| 4 | No hago ejercicio (C-5) | pytest: `does_exercise: false` con actividades → se guardan descartadas; `true` sin actividades → 422 "Elige al menos una actividad, o «No hago ejercicio»". e2e: con caminar guardado, "No hago ejercicio" → guardar → reabrir sin actividades ni total | pytest + Playwright |
| 5 | Movimiento del día aparte del ejercicio (C-7) | pytest: los 4 niveles, `active_travel` y 0/24 horas → 200 y GET igual. e2e: el total no cambia con el movimiento; reabrir | pytest + Playwright |
| 6 | Desplazamiento sin días (C-7, C-15) | pytest: `active_travel: true` sin días → 422 "Contesta esta pregunta."; `false` con días → se descartan. e2e: mensaje, *No* lo quita y guarda | pytest + Playwright |
| 7 | Sueño con las dos frecuencias (C-8) | pytest: 6 h y las dos escalas → 200, GET igual. e2e: contestar, guardar, reabrir con cada respuesta en su pregunta | pytest + Playwright |
| 8 | Fuera de escala en los bloques nuevos | pytest: días 0/8, minutos 0/601, horas sentado -1/25, sueño 0/25, nombre de 61, `"unknown"` en cada número nuevo, un tipo o nivel fuera de la escala y una propiedad extra → 422 de esquema en su `loc`, sin `value_error`, GET sin cambios. e2e: los cuatro mensajes de escala al salir del campo, ningún `PUT` | pytest + Playwright |
| 9 | Solo el sueño | pytest: solo `sleep.hours: 7` → 200, los demás bloques `null`. e2e: la tarjeta dice "Con datos" | pytest + Playwright |
| 10 | Sin puntaje ni riesgo (C-6) y Total semanal sin veredicto (C-5, C-6) | pytest: la respuesta no tiene total ni las palabras prohibidas. e2e: la pantalla dice "Total de lo anotado: 20 minutos por semana" y ninguna palabra prohibida | pytest + Playwright |
| 11 | Hábitos solo del paciente y cifrados (vigente) | pytest existente ampliado: los nombres y valores nuevos ("Senderismo", `trouble_falling_asleep`) no aparecen en claro | pytest |
| 12 | Accesibilidad y D20 en los bloques nuevos | e2e: los números de dos actividades tienen nombres distintos; con el `PUT` retenido, los chips nuevos tienen `aria-disabled="true"`; elegir una actividad cuenta como cambio sin guardar | Playwright |
| 13 | C-17 en los bloques nuevos | e2e: 601 minutos + Tab → error; corregir a 60 sin salir → se va | Playwright |

## Non-functional constraints addressed

- **NFR-001 / D13:** el mismo JSON cifrado (fila 11).
- **NFR-008 / C-6:** el total no se guarda ni se compara (filas 1, 10).
- **Accesibilidad:** nombres distintos y D20 (fila 12), errores junto a su campo, foco al primero.
- **es-MX (D15):** textos en `profile.json`, a partir del español oficial de NHIS y GPAQ.

## Risks / Trade-offs

- **La pantalla de hábitos se alarga.** Tres bloques más en el mismo formulario; si en la validación se siente larga,
  la división en pasos es un cambio aparte.
- **Días por semana subcuenta** a quien hace una actividad dos veces al día (EVS lo acepta).
- **El total mezcla fuerza y aeróbico.** Por eso dice "de lo anotado" y no se compara.

## Migration Plan

Sin migración: los bloques nuevos son opcionales y lo guardado antes los lee como `null`.

## Gate that closes the work

1. La suite completa de pytest del backend, truly green, cobertura ≥ 90 % y mypy limpio.
2. Las suites de perfil de Playwright en chromium y s26-ultra, truly green, y la suite completa como CI contra la
   imagen reconstruida.
3. `make tdd-check` verde.
4. `openspec validate perfil-habitos-actividad-sueno --strict` limpio.
5. La exploración en Chrome hecha por el agente, sin defectos; la revisión adversarial con la regla de cierre de la
   Decision 7; el archivo como último commit del PR. Después, la validación de Saúl Pérez con `validation.md`. El merge
   es humano.

## Open Questions

Ninguna bloqueante. Se aprueban con el prototipo: el catálogo de actividades con "¿Cuál?" en "Otra", los rangos (días
1–7, minutos 1–600, horas sentado 0–24, sueño 1–24) y los textos de las preguntas.
