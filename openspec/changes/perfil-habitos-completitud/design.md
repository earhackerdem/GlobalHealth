# Design

Status: DRAFT

**En una frase:** cuando una respuesta de hábitos abre más preguntas, esas preguntas se contestan antes de guardar,
con "No recuerdo" solo en las que tratan del pasado (guardado como `"unknown"`, distinto de "sin respuesta"), y un error
ya marcado se quita en cuanto el número es válido.

## Context

- Hoy cada respuesta es opcional (`openspec/specs/records/patient-profile/spec.md:341-342`); todos los campos de
  hábitos son `| None` (`backend/app/models.py:858-911`), y la pantalla dice "Contesta solo lo que quieras"
  (`frontend/src/locales/es-MX/profile.json:338`).
- Saúl Pérez decidió (2026-10-22): obligatorias, con "No recuerdo".
- Investigación (`memory/research/habitos.md#no-recuerdo`): "no sabe" se guarda aparte de "sin respuesta" (NHIS,
  NSDUH, FHIR `asked-unknown`); el AUDIT no tiene "no sé"; ofrecerlo en todo invita a contestar sin pensar.
- El `PUT` reemplaza el cuestionario completo, valida con `habits_errors` después de normalizar y devuelve 422 por
  `loc` (`models.py:988-1040`; `profile.py`), y la pantalla ubica esos errores por `loc` (R20).

## Goals / Non-Goals

**Goals:** C-15…C-17; lo guardado a medias sigue legible y se completa al guardar.

**Non-Goals:** "Prefiero no responder" (`asked-declined`); "mejor estimación" por rangos tras "No recuerdo"; una vista
para el médico; exportar a FHIR; la Story C2; las demás secciones del perfil.

## Qué se toca / qué NO

| Se toca | NO se toca |
|---|---|
| `backend/app/models.py` (tipos con `"unknown"`, obligatoriedad y comparaciones en `habits_errors`) | `routes/profile.py`, la columna, migraciones, `upgrade_stored_habits` |
| Cliente regenerado (`frontend/src/client/types.gen.ts`, `zod.gen.ts`), `frontend/src/components/Profile/HabitsForm.tsx`, `frontend/src/locales/es-MX/profile.json` | `ChipGroup.tsx`, `ui/*`, `main.tsx`, `useAuth.ts`, las demás pantallas |
| Tests: `backend/tests/api/routes/test_profile_habits.py`, `frontend/tests/profile-habits.spec.ts` | Las suites de las demás secciones |
| `product/dominio.md` § Hábitos, `product/prototipos/perfil-secciones.html` (la pantalla de hábitos) | Las decisiones |

**Decisiones afectadas:** D18 (chips) se aplica a "No recuerdo"; D20 (no disponibles mientras guarda) también lo
cubre. Ninguna decisión cambia.

**Citadores que vencen:** la spec canónica (vía la delta); `habits.intro` en `profile.json`; las semillas y escenarios
de pytest y e2e con bloques a medias (alcohol o tabaco "Actual" sin edad de inicio, vapeador "Actual" sin edad), que se
ubican con `grep -n "seedHabits\|SEED\|status" frontend/tests/profile-habits.spec.ts backend/tests/api/routes/test_profile_habits.py`;
`product/dominio.md` § Hábitos y el prototipo del producto.

## Interface contract

Base `/api/v1`, detrás de `ConsentedUser`. Mismos `GET` y `PUT /profile/habits`. Cambian estos tipos (lo demás de
`Habits` queda igual):

- `start_age` y `quit_age` de `AlcoholHabit`, `TobaccoHabit`, `VapingHabit` y `WoodSmokeHabit`:
  `int 0..130 | "unknown" | null`.
- `TobaccoHabit.cigarettes_per_day`: `int 1..100 | "unknown" | null`.
- `WoodSmokeHabit.hours_per_day`: `int 1..24 | "unknown" | null`.

`"unknown"` = "No recuerdo" (FHIR `asked-unknown`). `null` = no aplica o, en lo guardado antes, sin respuesta.

**Normalización:** la misma de hoy; un `"unknown"` que no aplica se descarta igual que un número.

**Validación (servidor, después de normalizar; forma 422 con `loc` de la C1; un error por campo):**

| Respuesta | Obligatorio (sin `"unknown"`) | Obligatorio (admite `"unknown"`) |
|---|---|---|
| alcohol `quit` | — | `start_age`, `quit_age` |
| alcohol `current` | `frequency`, `typical_drinks`, `six_or_more`, `mostly_weekends` | `start_age` |
| tabaco `former` | — | `cigarettes_per_day`, `start_age`, `quit_age` |
| tabaco `current` | `cigarettes_per_day` | `start_age` |
| vapeador `former` | — | `start_age`, `quit_age` |
| vapeador `current` | `frequency`; `days_last_30` con `some_days` | `start_age` |
| humo ajeno `exposed: true` | `places` (al menos uno), `days_per_week` | — |
| leña `former` | — | `start_age`, `quit_age`, `hours_per_day` |
| leña `current` | `hours_per_day` | `start_age` |

- Falta uno sin `"unknown"` → "Contesta esta pregunta."; falta uno que lo admite → "Contesta esta pregunta o marca
  «No recuerdo».".
- `"unknown"` en `cigarettes_per_day` con `current` o en `hours_per_day` con `current` → "Esta pregunta no admite «No
  recuerdo».".
- Las reglas de hoy ("≤ edad actual", "inicio ≤ fin") se aplican solo entre números; un `"unknown"` no se compara.

**Frontend**
- **Introducción:** "Contesta los hábitos que quieras. Si eliges una respuesta, completa sus preguntas; si no recuerdas
  un dato del pasado, marca «No recuerdo». «Nunca» también le sirve a tu médico. La app no califica tus respuestas."
- **"No recuerdo":** un chip con `aria-pressed` debajo de cada número que lo admite según la tabla (las edades siempre;
  cigarros y horas solo con "Antes"). Nombre accesible distinto por pregunta: "No recuerdo: <pregunta>" (R7). Al
  marcarlo, se vacía el número y se quita su error; al escribir en el número, se desmarca. Cuenta para "cambios sin
  guardar" y queda no disponible mientras guarda (D20).
- **Obligatorias:** se revisan al tocar "Guardar" junto con lo demás (no al salir de cada campo): el error va junto a
  su pregunta (número o grupo de chips) y el foco al primero, como hoy. Al ocultarse una pregunta se va su error (A3).
- **El error se va al corregirlo (C-17):** con un error ya marcado en un número, cada cambio revisa ese campo y quita el
  error si el valor es válido o el campo queda vacío; mientras se escribe no aparece un error nuevo.
- Lo guardado a medias abre sin errores; "Guardar" marca lo que falta.

## Decisions

1. **`"unknown"` en el mismo campo, no `null` ni un número especial ni un booleano aparte.** `null` se confundiría con
   "sin respuesta" de lo guardado antes; un 99 contamina promedios; un booleano permite "número y no recuerda" a la vez.
   El JSON cifrado no cambia de forma y el esquema cerrado sigue rechazando lo demás.
2. **"No recuerdo" solo en lo que pasó** (edades; cigarros y horas de "Antes"). El AUDIT no tiene "no sé" y lo actual
   se puede estimar (`memory/research/habitos.md#no-recuerdo`).
3. **El servidor también obliga.** El contrato es del servidor; la pantalla solo adelanta los mismos mensajes. Así una
   llamada directa al `PUT` no guarda un rango a medias.
4. **Obligatorias al guardar, no al salir de cada campo.** Marcar "Contesta esta pregunta" al pasar con Tab regañaría
   antes de tiempo; los errores de formato siguen al salir del campo (C-14).
5. **Lo guardado a medias no se convierte.** Un `null` de antes sigue siendo "sin respuesta"; nunca se vuelve
   `"unknown"` sin que el paciente lo diga.

## Test plan (one row per scenario, mandatory)

| # | Spec · scenario | Test | Dónde |
|---|---|---|---|
| 1 | Hábitos · escenarios de la C1 y de perfil-habitos-ajustes que hoy guardan a medias (alcohol "Actual", tabaco "Actual" y "Antes", vapeador "Actual", leña, C-6) | pytest y e2e existentes, con los datos completos que pide la spec delta | pytest + Playwright |
| 2 | Hábitos · Falta una pregunta de lo que eligió (C-15) | pytest: por cada fila de la tabla de obligatoriedad, el `PUT` sin ese campo → 422 en su `loc` con su mensaje, y el GET sin cambios. e2e: alcohol "Lo dejé" con solo 30 → "Guardar" → mensaje junto a la edad de inicio, foco ahí, ningún `PUT` | pytest + Playwright |
| 3 | Hábitos · Alcohol actual sin las preguntas de frecuencia (C-15) | e2e: "Actual" + 18 → "Guardar" → "Contesta esta pregunta." bajo las cuatro, sin chip "No recuerdo" en ellas, ningún `PUT` | Playwright |
| 4 | Hábitos · No recuerda cuándo empezó (C-16) | pytest: `start_age: "unknown"` con `quit_age: 18` → 200 y GET igual; `"unknown"` no dispara "≤ edad actual" ni "inicio ≤ fin". e2e: marcar, guardar, reabrir con "No recuerdo" marcado y 18 | pytest + Playwright |
| 5 | Hábitos · "No recuerdo" solo en lo que pasó (C-16) | pytest: `"unknown"` en cigarros o en horas con `current` → 422 "Esta pregunta no admite «No recuerdo»."; en cualquier campo de AUDIT-C o en días → 422 de esquema. e2e: con tabaco "Actual", sin chip en cigarros y con chip en la edad; con "Antes", con chip en los tres | pytest + Playwright |
| 6 | Hábitos · Escribir un número quita "No recuerdo" (C-16) | e2e: marcar en la edad de inicio, escribir 16 → `aria-pressed="false"`; guardar y reabrir → 16 | Playwright |
| 7 | Hábitos · Lo guardado a medias pide completar al guardar (C-15) | e2e: fila sembrada (alcohol `quit` con solo `quit_age`) → abrir sin errores; "Guardar" → mensaje junto a la edad de inicio, ningún `PUT`; GET sin cambios. pytest: GET de esa fila → 200 con `start_age: null` | pytest + Playwright |
| 8 | Hábitos · Respuestas fuera de su escala | pytest: los casos nuevos de `"unknown"` (fila 5) y que `"unknown"` en un campo no permitido no cambia lo guardado | pytest |
| 9 | Hábitos · Lo guardado antes se sigue leyendo | pytest existente + ningún campo vuelve como `"unknown"` | pytest |
| 10 | No interpreta · Sin puntaje ni riesgo (C-6) | pytest y e2e existentes con los datos completos, incluido `start_age: "unknown"` | pytest + Playwright |
| 11 | Errores al momento · El error se va al corregirlo (C-17) | e2e: "12a" + Tab → error; volver, dejar 12 sin salir → sin mensaje ni `aria-invalid`; con 101 en cigarros y borrar todo → sin mensaje; al escribir "1a" mientras está limpio no aparece error hasta salir | Playwright |
| 12 | Accesibilidad de "No recuerdo" (R7, D20) | e2e: dos chips "No recuerdo" visibles tienen nombres accesibles distintos; con el `PUT` retenido, el chip tiene `aria-disabled="true"` | Playwright |
| 13 | Aislados y cifrados (C1) | pytest existente: SQL directo sin `"unknown"` en claro | pytest |

## Non-functional constraints addressed

- **NFR-001 / D13:** el mismo JSON cifrado (fila 13).
- **NFR-008 / C-6:** "No recuerdo" no se interpreta (fila 10).
- **Accesibilidad:** nombres distintos (fila 12), errores junto a su campo (R5), foco al primero al guardar.
- **es-MX (D15):** textos nuevos en `profile.json`.

## Risks / Trade-offs

- **"No recuerdo" como salida rápida.** Si en uso real pasa claramente del ~1 % de NHIS en algún ítem, revisar
  (`memory/research/habitos.md#no-recuerdo`, "Re-check if").
- **Quien guardó a medias** tendrá que completar antes de poder guardar otro cambio en hábitos. Solo hay cuentas de
  prueba.
- **Más preguntas obligatorias** pueden hacer que alguien deje un hábito sin contestar en vez de completarlo; sigue
  siendo válido.

## Migration Plan

Sin migración. Lo guardado conserva sus `null`; el siguiente "Guardar" pide completarlo.

## Gate that closes the work

1. La suite completa de pytest del backend, truly green, cobertura ≥ 90 % y mypy limpio.
2. La suite completa de Playwright en chromium y s26-ultra, truly green.
3. `make tdd-check` verde.
4. `openspec validate perfil-habitos-completitud --strict` limpio.
5. La exploración en Chrome hecha por el agente, sin defectos; la revisión adversarial; el archivo como último commit
   del PR. Después, la validación de Saúl Pérez con `validation.md`. El merge es humano.

## Open Questions

Ninguna bloqueante. Se aprueban con el prototipo: dónde va "No recuerdo" (Decision 2) y el texto de la introducción.
