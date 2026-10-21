# Design

Status: APPROVED
Approved by: Saúl Pérez (author) on 2026-10-20, sobre el prototipo v4 ya navegado (bloques de hábitos C-1…C-4, C-6)

**En una frase:** la tarjeta "Hábitos" abre un cuestionario de cuatro bloques (alcohol con el AUDIT-C, tabaco y
vapeador, humo de otras personas, humo de leña) que se guarda con un solo "Guardar" en un dato cifrado del perfil,
sin puntajes, descartando lo que no aplica y rechazando edades imposibles junto a su campo.

## Context

- Las secciones de lista (Story A y B) viven en `medical_history_entry`, una fila cifrada por registro. Los
  hábitos son otra forma: un cuestionario 1→0..1 por paciente, sin "ninguna" (`product/dominio.md` § Hábitos).
- El perfil ya guarda datos 1:1 cifrados en columnas propias: `blood_type` y `sections_none`
  (`backend/app/models.py:431-439`, perfil-eventos Decision 3).
- La Story C se partió en dos (Saúl Pérez, 2026-10-20, exploration.md §8). Este cambio es la C1. La C2 agregará
  ejercicio, movimiento del día y sueño **al mismo dato de hábitos y a la misma pantalla**, y el trabajo al Perfil
  básico.
- Lecciones de la review de B que este diseño atiende de entrada: errores junto a su campo (R5), nombres accesibles
  distintos (R7), "hoy" de México (R11), y no enrutar errores comparando el texto del mensaje (R20).

## Goals / Non-Goals

**Goals:** C-1…C-4 y C-6, la tarjeta enlazada con su estado, la variante de chips de selección múltiple, cifrado y
aislamiento.

**Non-Goals:** ejercicio, movimiento del día, sueño y trabajo (C2); vacunación; otras sustancias; puntajes o
avisos de riesgo (C-6, NFR-008); la mascota y la experiencia "casi como Duolingo" (inbox); convertir los antecedentes
familiares de checkboxes a chips.

## Qué se toca / qué NO

| Se toca | NO se toca |
|---|---|
| `backend/app/models.py` (esquemas de hábitos y su normalización), `backend/app/api/routes/profile.py` (GET/PUT `/profile/habits`), una migración Alembic | `medical_history_entry`, las rutas de historial, `sections_none` |
| `frontend/src/routes/_layout/perfil_.habitos.tsx` (nueva), `frontend/src/components/Profile/HabitsForm.tsx` (nuevo), `ChipGroup.tsx` (variante múltiple), `history.ts` (exportar `ageToday` si hace falta), `perfil.tsx` (tarjeta), `queries.ts`, `frontend/src/locales/es-MX/profile.json`, el cliente regenerado | `HistoryEntryForm`, `HistorySection`, `WhenField`, el expediente, los antecedentes familiares |
| Tests: `backend/tests/api/routes/test_profile_habits.py` (nuevo), `frontend/tests/profile-habits.spec.ts` (nuevo), los citadores de "hábitos sin captura" | Las suites de A y B, salvo esos citadores |

**Ampliación aprobada en la revisión** (Saúl Pérez, 2026-10-20): `frontend/src/hooks/useAuth.ts`, para que cerrar e
iniciar sesión vacíen la caché de consultas (R1: sin eso, otra cuenta en el mismo navegador veía y podía guardar los
hábitos de la anterior). En la ronda 2 (Saúl Pérez, 2026-10-21), `frontend/src/main.tsx`: cuando otra pestaña del
mismo navegador cambia la sesión, esta también vacía la caché y se recarga (N1: la otra pestaña seguía mostrando y
guardando los datos de la cuenta anterior con el token de la nueva; pasaba también, desde antes, en "Editar datos
básicos"). También `frontend/playwright.config.ts`: el `testMatch` de s26-ultra incluye
`profile-habits`, y entró en el commit verde c2b3d32 sin estar listado aquí (R24).

**Decisión afectada:** ninguna ADR cambia. D13 (cifrado) y D18 (chips) se aplican; D18 se extiende a la selección
múltiple dentro de su propia regla ("chips cuando se tienen opciones").

**Citadores de "hábitos sin captura"** (vencen en este cambio): la spec canónica
`openspec/specs/records/patient-profile/spec.md:90,97,103` (vía la delta), `frontend/src/routes/_layout/perfil.tsx:150-166`
(comentario y rama sin enlace), `frontend/src/components/Profile/history.ts:25` (comentario),
`frontend/src/locales/es-MX/profile.json:79` ("Los hábitos llegan pronto."), y los tests que afirman que hábitos
no tiene enlace (`frontend/tests/profile.spec.ts`, `profile-history.spec.ts`; se ubican con `grep -n habits`).

## Interface contract

Base `/api/v1`, detrás de `ConsentedUser`. Los nombres de campo y valores son en inglés; las etiquetas es-MX van en
la UI.

**Tipos** (`Habits`, el mismo objeto en el cuerpo del PUT y en la respuesta; todo opcional, `extra="forbid"`):
- `alcohol: AlcoholHabit | null`
  - `status: "never" | "quit" | "current"` (requerido dentro del objeto)
  - `quit_age: int 0..130 | null`
  - `frequency: "monthly_or_less" | "two_to_four_monthly" | "two_to_three_weekly" | "four_plus_weekly" | null`
  - `typical_drinks: "one_two" | "three_four" | "five_six" | "seven_nine" | "ten_plus" | null`
  - `six_or_more: "never" | "less_than_monthly" | "monthly" | "weekly" | "daily" | null`
  - `mostly_weekends: bool | null`
- `tobacco: TobaccoHabit | null`
  - `status: "never" | "former" | "current"` (requerido dentro del objeto)
  - `cigarettes_per_day: int 1..100 | null`
  - `start_age: int 0..130 | null`
  - `quit_age: int 0..130 | null`
- `vaping: "never" | "former" | "current" | null`
- `secondhand_smoke: SecondhandSmoke | null`
  - `exposed: bool` (requerido dentro del objeto)
  - `places: list["home" | "work_school" | "other"]` (sin repetidos, se ordena así)
  - `days_per_week: int 1..7 | null`
- `wood_smoke: WoodSmokeHabit | null`
  - `status: "never" | "former" | "current"` (requerido dentro del objeto)
  - `years: int 0..130 | null`

**Normalización (servidor, antes de cifrar): se descarta lo que no aplica**
- alcohol ≠ `current` → `frequency`, `typical_drinks`, `six_or_more`, `mostly_weekends` a null;
  alcohol ≠ `quit` → `quit_age` a null.
- tabaco `never` → `cigarettes_per_day`, `start_age`, `quit_age` a null; tabaco ≠ `former` → `quit_age` a null.
- leña `never` → `years` a null.
- `exposed: false` → `places: []` y `days_per_week` a null.

**Validación (servidor, después de normalizar)**, con "hoy" de México y la fecha de nacimiento del perfil. "Hoy"
es `datetime.now(MEXICO_CITY).date()` dentro de `app.api.routes.profile`, como en el historial, así que los tests lo
congelan con `freeze_routes_clock` (`backend/tests/api/routes/test_profile_history.py:81`):
- `alcohol.quit_age`, `tobacco.start_age`, `tobacco.quit_age` mayores que la edad actual → "La edad no puede ser
  mayor que tu edad actual" (el mismo texto de la Story A). Sin fecha de nacimiento no se compara.
- `tobacco.start_age` > `tobacco.quit_age` → "No puede ser mayor que la edad en que lo dejaste", en `start_age`.
- `exposed: true` sin `places` → "Elige dónde, o «No me expongo»", en `places`.
- **Forma del error:** estos rechazos responden 422 con la misma forma que los de rango de FastAPI:
  `detail: [{"loc": ["body", "<bloque>", "<campo>"], "msg": "<es-MX>", "type": "value_error"}]`. El frontend
  ubica cualquier 422 por su `loc`, no por el texto (R20).

**Operaciones**
- `GET /profile/habits` → 200 `Habits`. Sin hábitos guardados (o sin perfil): todos los campos en null. No crea el
  perfil.
- `PUT /profile/habits` (cuerpo `Habits`) → 200 `Habits` ya normalizado. Reemplaza el cuestionario completo. Si
  todo queda en null se guarda null (la tarjeta vuelve a "Sin llenar"). Toma `_lock_profile`
  (`profile.py:140`), que crea el perfil si falta.
- Sin consentimiento: 403, como el resto del perfil.

**Tablas:** `patient_profile.habits`: `EncryptedString`, nullable, con el JSON del objeto normalizado. Migración
Alembic que solo agrega la columna.

**Frontend**
- **Tarjeta:** `history-card-habits` pasa a ser un enlace a `/perfil/habitos`, con chevron, y su insignia dice
  "Sin llenar" o "Con datos" (algún campo de primer nivel no nulo). La consulta es `["habits"]`.
- **Pantalla** `/perfil/habitos`: "‹ Mi perfil médico", título "Hábitos", y la línea "Contesta solo lo que quieras.
  «Nunca» también le sirve a tu médico. La app no califica tus respuestas." Cuatro bloques con su título:
  - **Alcohol:** chips "Nunca" · "Lo dejé" · "Actual". Con "Lo dejé": número "¿A qué edad dejaste de tomar?". Con
    "Actual": chips "¿Con qué frecuencia tomas?" (Una vez al mes o menos · 2 a 4 veces al mes · 2 a 3 veces por
    semana · 4 o más veces por semana), chips «Sí» / «No» para "Sobre todo fines de semana" (tocar el elegido lo
    deja sin contestar; era una casilla hasta la revisión, R14), chips "En un día que tomas, ¿cuántas
    bebidas?" (1 o 2 · 3 o 4 · 5 o 6 · 7 a 9 · 10 o más) con la ayuda "Una bebida: una cerveza, una copa de vino o
    un trago de tequila, ron u otro destilado.", chips "¿Cada cuándo tomas 6 o más bebidas en una sola ocasión?"
    (Nunca · Menos de una vez al mes · Cada mes · Cada semana · A diario o casi).
  - **Tabaco:** chips "Nunca" · "Antes" · "Actual". Si no es "Nunca": "Cigarros al día" y "¿A qué edad empezaste a
    fumar?"; con "Antes", además, "¿A qué edad dejaste de fumar?". Debajo, chips "Vapeador o cigarro electrónico"
    (Nunca · Antes · Actual).
  - **Humo de tabaco de otras personas:** ayuda "Estar cerca de quien fuma, aunque tú no fumes."; chips múltiples
    "¿Dónde?" (Casa · Trabajo o escuela · Otro lugar) más "No me expongo", excluyente. Con algún lugar: "Días por
    semana".
  - **Humo de leña:** ayuda "Cocinar o calentar la casa con leña o carbón."; chips "Nunca" · "Antes" · "Actual"; si
    no es "Nunca": "Años con humo de leña, aprox.".
  - "Guardar" hace el PUT, invalida `["habits"]`, avisa "Hábitos guardados" y vuelve a `/perfil`. "Cancelar" vuelve
    sin guardar.
- **Nombres accesibles:** cada grupo y cada número tiene un nombre distinto (los de arriba). Ningún par de
  controles comparte nombre (R7).
- **Validación en el cliente**, antes de enviar y con las mismas reglas que el servidor: edad mayor que la actual
  (con `mexicoCityTodayIso`), inicio > dejó, lugar faltante. El error va junto a su campo, con `aria-invalid` y
  `aria-describedby`, y el foco al primer campo con error. Un 422 del servidor se ubica por `loc` igual.
- **`ChipMultiGroup`** (en `ChipGroup.tsx`): `label`, `options`, `values: V[]`, `onChange(V[])`, y
  `exclusive?: {value, label}`. Cada chip es un toggle con `aria-pressed`; elegir el excluyente vacía los demás, y
  elegir otro apaga el excluyente. Va en un `fieldset` con el mismo estilo que `ChipGroup`.

## Decisions

1. **Una columna cifrada en el perfil, no filas en `medical_history_entry`.** Los hábitos son 1→0..1 y sin
   "ninguna"; la tabla de historial es de listas. Es el patrón de `blood_type`. Descartado: una sección más del
   historial con "solo un registro" (regla que esa tabla no tiene).
2. **Un PUT del cuestionario completo.** La pantalla tiene un solo "Guardar" (prototipo). Descartado: un endpoint
   por bloque (más rutas, guardados parciales que el prototipo no tiene).
3. **El servidor normaliza y valida; el cliente adelanta la validación.** El servidor es la fuente de verdad (Story
   B, "hasta" descartado); el cliente evita que el paciente vea un error lejos de su campo.
4. **Errores de este endpoint con `loc`.** Las rutas de historial responden `detail` como texto y la UI lo enruta
   comparando el texto, que fue el hallazgo R20 de la Story B. Aquí se usa la forma estándar de FastAPI con `loc`.
   Descartado: seguir el texto (frágil) o inventar una forma propia.
5. **La C2 extiende este mismo objeto.** `extra="forbid"` hoy; la C2 agrega `exercise`, `daily_movement` y `sleep`
   al esquema y a la pantalla. El trabajo irá en su propia columna del perfil.
6. **Edad como número, no "cuándo".** El dominio pide edad en estos campos (ronda 8); `WhenField` sobra.

## Test plan (one row per scenario, mandatory)

| # | Spec · scenario | Test | Dónde |
|---|---|---|---|
| 1 | Hábitos · Alcohol actual con el AUDIT-C (C-1) | pytest: PUT con las cinco respuestas → GET igual. e2e: elegirlas, guardar → tarjeta "Con datos" → reabrir y verlas elegidas (`aria-pressed`) | pytest + Playwright |
| 2 | Hábitos · Lo dejó, con la edad (C-1) | pytest: `quit` + 30 → GET igual. e2e: reabrir muestra 30 y ninguna pregunta del AUDIT-C | pytest + Playwright |
| 3 | Hábitos · Una edad mayor que la actual (C-1, C-2) | pytest: nacido 1990-03-15, `quit_age` 40 → 422 con `loc` `["body","alcohol","quit_age"]` y el texto; nada guardado; sin fecha de nacimiento, 40 se acepta; lo mismo para `tobacco.start_age` y `quit_age`. e2e: el error junto al campo, el foco ahí, nada guardado | pytest + Playwright |
| 4 | Hábitos · Lo que no aplica se descarta (C-1) | pytest: cada regla de normalización (alcohol, tabaco `never`/`current`, leña, `exposed: false`). e2e: "Actual" + AUDIT-C → "Nunca" → reabrir sin preguntas | pytest + Playwright |
| 5 | Hábitos · Tabaco que dejó, y vapeador actual (C-2) | pytest roundtrip. e2e: llenarlo y verlo al reabrir | pytest + Playwright |
| 6 | Hábitos · Empezó después de dejarlo (C-2) | pytest: 30/18 → 422 en `start_age`. e2e: error junto a la edad de inicio | pytest + Playwright |
| 7 | Hábitos · Humo ajeno en varios lugares, y después "No me expongo" (C-3) | pytest: `exposed` sin `places` → 422 en `places`; `exposed: false` vacía lugares y días. e2e: dos lugares + 2 días → "No me expongo" apaga los lugares y oculta los días | pytest + Playwright |
| 8 | Hábitos · Humo de leña de antes (C-4) | pytest roundtrip. e2e: verlo al reabrir | pytest + Playwright |
| 9 | Hábitos · Contesta solo una cosa | pytest: solo `vaping` → el resto null. e2e: tarjeta "Con datos" | pytest + Playwright |
| 10 | Hábitos · Respuestas fuera de su escala | pytest: 0 y 101 cigarros, 8 días, edad 131, opción fuera del enum, campo desconocido → 422 y GET sin cambios | pytest |
| 11 | No interpreta · Sin puntaje ni riesgo (C-6) | pytest: las llaves de la respuesta son exactamente las del contrato. e2e: tras guardar el caso extremo, el texto de la pantalla y de "Mi perfil médico" no contiene "riesgo", "puntaje" ni "AUDIT" | pytest + Playwright |
| 12 | Pantalla · Estado de cada sección en su tarjeta (A-1) | e2e existente con hábitos "Sin llenar" (citador actualizado) | Playwright |
| 13 | Pantalla · Secciones listadas sin captura | e2e: las seis tarjetas "Sin llenar", cada una enlace (citador actualizado) | Playwright |
| 14 | Pantalla · La tarjeta abre la pantalla de su sección | e2e: clic en "Hábitos" → `/perfil/habitos` con "Guardar" | Playwright |
| 15 | Aislados y cifrados · A-8, A-9, B-6 | sin cambios: suites de A y B en verde | pytest |
| 16 | Aislados y cifrados · Hábitos solo del paciente y cifrados | pytest: B pide sus hábitos → todo null; SQL directo sobre `patient_profile.habits`: ni `current`, ni `home`, ni `alcohol`, ni `monthly_or_less` en claro (era `quit_age`, que A no guarda y por eso no podía fallar; R26); GET y PUT sin consentimiento → 403 | pytest |

## Non-functional constraints addressed

- **NFR-001 / D13:** el cuestionario completo va cifrado (fila 16).
- **NFR-008 / C-6:** fila 11; el contrato no tiene ningún campo calculado.
- **D18:** chips para todas las opciones, incluida la selección múltiple.
- **Accesibilidad:** nombres distintos (R7), errores junto al campo con foco (R5), `aria-pressed` en los chips.
- **Móvil 384 px:** la pantalla es larga; la exploración en Chrome la recorre a ese ancho.
- **es-MX:** todos los textos en `profile.json`.

## Risks / Trade-offs

- **Pantalla larga.** Cuatro bloques ahora y siete con la C2. Mitigación: todo opcional, preguntas que solo aparecen
  cuando aplican. La experiencia por pasos ("casi como Duolingo") sigue en el inbox.
- **Guardar todo de una vez.** Si el paciente navega fuera sin guardar, pierde lo contestado (igual que en los
  formularios de A y B). No se agrega aviso de cambios sin guardar en este cambio.
- **Dos formas de error en el perfil.** El historial usa texto y los hábitos `loc`. Mitigación: la forma `loc` es la
  estándar de FastAPI y el frontend ya recibe 422 de rango con esa forma. Unificar el historial queda como deuda.

## Migration Plan

Una migración Alembic que agrega `patient_profile.habits` (nullable). Sin datos que mover; el downgrade quita la
columna.

## Gate that closes the work

1. La suite completa de pytest del backend, truly green (0 fallos, 0 errores, 0 skips), con cobertura ≥ 90 % y mypy
   limpio.
2. La suite completa de Playwright en chromium y s26-ultra, truly green.
3. `make tdd-check` verde.
4. `openspec validate perfil-habitos --strict` limpio.
5. La exploración en Chrome hecha por el agente, sin defectos, y el archivo como último commit del PR. Después, la
   validación de Saúl Pérez con `validation.md`. El merge es humano.

## Open Questions

Ninguna bloqueante: las tres preguntas de la exploración están respondidas (exploration.md §8).
