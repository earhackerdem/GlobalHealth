# Design

Status: DRAFT   <!-- the harness gate: "plan approved" from the person you work with → `Status: APPROVED` -->
Approved by: <name (role)> on YYYY-MM-DD

**En una frase:** las cuatro secciones de eventos del perfil médico se vuelven llenables (registros cifrados en
una tabla genérica, estado "ninguna", "cuándo" por edad/etapa/año y grupo sanguíneo), con una pantalla por
sección calcada del prototipo v4.

## Context

Motivación en proposal.md § Why; requisitos en specs/records/patient-profile/spec.md (1 MODIFIED + 5 ADDED, 23
escenarios); diagnóstico y decisiones del gate en exploration.md (§2 matriz, §8 respuestas de Saúl Pérez).
Infraestructura existente que se reutiliza, verificada el 2026-10-20:
- Perfil 1:1 cifrado `PatientProfile` (`backend/app/models.py:411`), su PUT parcial "ausente = no tocar, null
  borra" (`PatientProfileUpdate`, `models.py:472`; ruta `backend/app/api/routes/profile.py:136-162`) y su vista
  pública `PatientProfilePublic` (`models.py:484`).
- Cifrado `EncryptedString` (`backend/app/core/encrypted.py:89`, D13); consentimiento `ConsentedUser`
  (`backend/app/api/deps.py:87`); 404 idéntico ajeno/inexistente `_get_owned_family_history`
  (`profile.py:115-125`).
- Frontend: `frontend/src/routes/_layout/perfil.tsx` (tarjetas estáticas en `:141-161`, claves `:16-23`),
  componentes `frontend/src/components/Profile/`, namespace `frontend/src/locales/es-MX/profile.json`
  (`pending.*` en `:76-88`).
- Prototipo validado (fuente de la UX): `product/prototipos/perfil-secciones.html` v4.

**Precondición de ejecución:** los PRs #17 (archivo onboarding-perfil → spec base en `openspec/specs/`), #18
(discovery) y #19 (fix: `make migrate` y codegen sin lint) mergeados, y esta rama rebasada sobre `main`.

## Goals / Non-Goals

**Goals:** Story A de US-18 (FR-028): A-1…A-9 de proposal.md, verificados por los 23 escenarios.

**Non-Goals:** crónicas (Story B) y hábitos + trabajo (Story C), que siguen sin captura; compartir el historial
con el médico (E3/E4) y cómo se le muestra "ninguna"; avisos de IA (E5); fechas exactas en los registros;
enlaces entre registros de secciones distintas; paginación (decenas de registros por paciente).

## Qué se toca / qué NO

- **Se toca:** `backend/app/models.py` (tabla nueva + 2 columnas en `patient_profile` + esquemas),
  migración Alembic nueva (solo aditiva), `backend/app/api/routes/profile.py` (rutas nuevas + `blood_type` y
  `sections_none` en GET/PUT `/profile`), `backend/tests/api/routes/test_profile_history.py` (nuevo), `backend/tests/api/routes/test_profile.py:251`
  (tarea 1.0: `today` en la zona de México, defecto visto en el CI del PR #17); frontend:
  `routes/_layout/perfil.tsx` (tarjetas con estado y navegables), ruta nueva `routes/_layout/perfil_.$seccion.tsx`
  (el `_` final la saca del anidamiento bajo `perfil.tsx`), componentes nuevos en `components/Profile/`
  (`HistorySection`, `HistoryEntryForm`, `WhenField`, `BloodTypePicker`), `locales/es-MX/profile.json`,
  `frontend/tests/profile-history.spec.ts` (nuevo), `frontend/tests/profile.spec.ts` (citer, ver abajo),
  `frontend/playwright.config.ts:54` (spec nuevo al proyecto s26-ultra), cliente generado.
- **NO se toca:** onboarding, perfil básico salvo sus dos campos nuevos, mediciones, AHF, expediente
  (`health_records`), consentimiento, ninguna ADR.
- **Citers que expiran en este cambio:**
  - `frontend/tests/profile.spec.ts:14,52,280-300`: hoy asierta 6 secciones "Sin registros" sin inputs ni
    "Agregar". Queda así: crónicas y hábitos siguen sin captura y con "Sin llenar"; las 4 de eventos se
    asiertan en el spec nuevo.
  - `perfil.tsx:148` (comentario "Read-only by design (FR-027)").
  - `profile.json:79` (`pending.description`: "Estas secciones se podrán capturar próximamente.") → texto nuevo:
    "Llénalas a tu ritmo; todo es opcional. Crónicas y hábitos llegan pronto.". También `noEntries` "Sin
    registros" pasa a "Sin llenar" para las tarjetas.
  - Spec `records/patient-profile` requirement "Pantalla 'Mi perfil médico' con secciones visibles" (MODIFIED
    en el delta).
  - `product/dominio.md` y el prototipo no cambian: ya describen esto.
- **Decisiones de `memory/decisions.md` afectadas:** ninguna (D13 se reutiliza; se aplica el veredicto de
  `memory/closed.md` 2026-10-11: todo campo de salud cifrado desde su primera migración).

## Interface contract

Base `/api/v1/profile`, todo detrás de `ConsentedUser`; errores 422/409/404 con `detail` string es-MX; listas con
envelope `{data, count}`. Identificadores en inglés, UI en es-MX (veredicto de closed.md).

**Tipos compartidos**
- `section`: `"past" | "surgeries" | "fractures" | "transfusions"` (las claves ya usadas en `perfil.tsx:16-23`).
- `When`: `{ kind: "age", value: int }` · `{ kind: "stage", value: "before_primary" | "primary" | "secondary" |
  "high_school" }` · `{ kind: "year", value: int }` · `{ kind: "unknown" }`.
- `YesNoUnknown`: `"yes" | "no" | "unknown"`.
- `blood_type`: `"A+" | "A-" | "B+" | "B-" | "AB+" | "AB-" | "O+" | "O-" | "unknown"`.

**Contenido por sección** (unión discriminada por `section`; todos opcionales salvo los marcados; textos ≤ 2000,
nombres ≤ 200):
- `past`: `condition` (**req**) `"varicella" | "measles" | "mumps" | "rubella" | "hepatitis_a" | "hepatitis_b"
  | "hepatitis_c" | "severe_covid19" | "dengue" | "tuberculosis" | "other"`, `other_text` (req si `other`),
  `when`, `hospitalized: YesNoUnknown`, `sequelae`, `note`.
- `surgeries`: `kind: "surgery" | "hospitalization"`, `name` (**req**), `when`, `reason`, `place`, `physician`,
  `complications`, `anesthesia_reaction: YesNoUnknown`, `anesthesia_reaction_detail`, `implant`.
- `fractures`: `what` (**req**), `side: "left" | "right" | "both" | "not_applicable"`, `when`,
  `required_surgery: YesNoUnknown`, `implant`, `sequelae`.
- `transfusions`: `when`, `reason`, `component: "blood" | "platelets" | "plasma" | "unknown"`, `place`,
  `reaction: YesNoUnknown`, `reaction_detail`.

| Operación | Request | Response |
|---|---|---|
| GET `/profile` | — | lo de hoy + `blood_type: enum\|null` + `sections_none: section[]` |
| PUT `/profile` | lo de hoy + `blood_type?` (null borra) | el perfil como GET; 422 si `blood_type` fuera del enum |
| GET `/profile/history` | — | `{ data: [HistoryEntry], count }`, todas las secciones, por `created_at` ascendente |
| POST `/profile/history` | contenido de una sección (con `section`) | 201 `HistoryEntry`; quita `section` de `sections_none` en la misma transacción. 422 "Llena al menos un dato" si no trae ningún campo además de `section`; 422 es-MX por requerido faltante o `when` imposible |
| PUT `/profile/history/{id}` | contenido completo (mismo `section`) | 200 `HistoryEntry`; 422 si cambia `section`; 404 "Registro no encontrado" idéntico ajeno/inexistente |
| DELETE `/profile/history/{id}` | — | 200 `{ message }` es-MX; 404 idéntico |
| PUT `/profile/history/sections/{section}/none` | `{ none: bool }` | 200 el perfil; **409** "No puedes marcar «ninguna» si la sección tiene registros" si `none: true` con registros; 422 si `section` no es de esta story |

`HistoryEntry` = `{ id: uuid, section, created_at: datetime, ...campos de su sección }`.

**Validación de `when` (servidor, antes de cifrar):** con fecha de nacimiento: edad ∈ [0, edad actual] ("La edad
no puede ser mayor que tu edad actual"), año ∈ [año de nacimiento, año actual] ("El año no puede ser anterior a
tu nacimiento" / "El año no puede ser futuro"). Sin fecha de nacimiento: edad ∈ [0, 130] ("La edad debe estar
entre 0 y 130 años") y año ∈ [1900, año actual].

**Mensajes es-MX de requeridos:** past: "Elige la condición o escribe cuál fue"; surgeries: "Escribe qué cirugía
u hospitalización fue"; fractures: "Escribe qué hueso o lesión fue".

**Tablas** (para aserciones de ciphertext por SQL sin importar modelos): `medical_history_entry` (`id`, `user_id`
FK cascade, `content` = JSON del registro **con su `section`** cifrado, `created_at` en claro); `patient_profile`
gana `blood_type` y `sections_none` (lista JSON), ambos cifrados. Los campos cifrados empiezan con `gAAAA` como el
resto.

**Frontend**
- URLs: `/perfil/pasadas`, `/perfil/cirugias`, `/perfil/fracturas`, `/perfil/transfusiones`.
- Tarjetas en "Mi perfil médico": `data-testid="history-card-<section>"` (incluye `chronic` y `habits`) con el
  texto de estado "Sin llenar" · "Ninguna" · "1 registro" · "N registros". Solo las 4 de eventos son enlaces.
- Pantalla de sección: `data-testid="history-entries"` con un `data-testid="history-entry"` por registro; botones
  "Agregar", "Editar", "Eliminar" → confirmación en la misma pantalla con "Sí, eliminar" y "Cancelar"; "No he
  tenido ninguna" ("Nunca me han transfundido" en transfusiones), "Deshacer"; aviso al quitar la marca: "Guardado.
  La sección ya no dice «ninguna»."; en transfusiones, grupo de chips "Grupo sanguíneo" con A+ A- B+ B- AB+ AB- O+
  O- y "No lo sé".
- `WhenField`: campo "Edad que tenías" (alterna con "Año" vía el botón "o el año, si lo sabes" / "o la edad que
  tenías"), chips "Antes de la primaria", "En la primaria", "En la secundaria", "En la prepa", "No recuerdo".
- Resumen de "cuándo": "a los 7 años (≈1997)", "en la primaria (≈1996–2001)", "en 2015", "no recuerda cuándo";
  sin fecha de nacimiento, sin el paréntesis.

## Decisions

1. **Una tabla genérica `medical_history_entry`** con todo el contenido en un JSON cifrado, validado por esquemas
   pydantic por sección (Saúl Pérez, gate de la exploración). Las stories B y C agregan secciones al enum sin
   migración de tabla. Descartada: cuatro tablas tipadas (cuatro veces el CRUD y las migraciones).
2. **Nada en claro salvo `id`, `user_id` y `created_at`** (Saúl Pérez, gate): la sección viaja dentro del
   cifrado y el servidor agrupa/filtra en memoria tras descifrar los registros del dueño (decenas por paciente).
   Descartada: sección en claro como el `type` de las mediciones (G19), porque revelaría "tuvo una transfusión".
3. **"Ninguna" y grupo sanguíneo viven en `patient_profile`** (1:1), cifrados. La marca se quita al crear un
   registro de esa sección en la misma transacción, y no se puede poner con registros (409).
4. **"Cuándo" se guarda como se contestó** (`When`) y el año aproximado lo calcula el frontend al pintar, con la
   fecha de nacimiento del GET `/profile`; corregir la fecha recalcula sin migrar nada. Los rangos por etapa son
   [ASSUMPTION] del dominio y viven en una sola constante del frontend. El servidor solo valida imposibles.
5. **Una pantalla por sección** (Saúl Pérez, gate), con el formulario en la misma pantalla y confirmación de
   borrado en línea, como el prototipo. Descartada: diálogos sobre `/perfil` como los de AHF.
6. **Sin dedupe**: dos cirugías iguales son legítimas, a diferencia de las condiciones de AHF.

## Test plan (one row per scenario, mandatory)

| # | Spec · scenario | Test | Dónde |
|---|---|---|---|
| 1 | Pantalla · Estado de cada sección en su tarjeta (A-1) | 2 pasadas + "ninguna" en transfusiones → las 6 tarjetas con su texto; crónicas/hábitos sin enlace ni inputs | Playwright |
| 2 | Pantalla · La tarjeta abre la pantalla de su sección | clic en cirugías → `/perfil/cirugias` con "Agregar" | Playwright |
| 3 | Registros · Enfermedad pasada del catálogo (A-4) | POST past varicella/primary/no → GET la trae; e2e muestra "en la primaria" | pytest + Playwright |
| 4 | Registros · Enfermedad pasada fuera del catálogo (A-4) | POST `other` + "Chikungunya" → GET; sin `other_text` → 422 | pytest |
| 5 | Registros · Cirugía con todos sus datos (A-5) | e2e llena el formulario completo y al editar ve los mismos valores; pytest round-trip de los 10 campos | Playwright + pytest |
| 6 | Registros · Fractura con lado e implante (A-6) | e2e registra y ve "izquierdo" y el implante en el resumen | Playwright |
| 7 | Registros · Transfusión (A-7) | e2e registra y ve "en 2015" y "Parto" | Playwright |
| 8 | Registros · Falta el dato requerido | POST surgeries sin `name` → 422 con el mensaje exacto; nada persiste | pytest |
| 9 | Registros · Registro vacío no se guarda (A-8) | POST `{section: "transfusions"}` → 422 "Llena al menos un dato"; e2e ve el mensaje | pytest + Playwright |
| 10 | Registros · Editar y eliminar con confirmación (A-8) | e2e: editar lado → "derecho"; "Eliminar" → "Cancelar" lo conserva → "Sí, eliminar" lo quita; pytest PUT/DELETE + fila ausente en BD | Playwright + pytest |
| 11 | Cuándo · Edad con fecha de nacimiento (A-3) | pytest guarda `{age, 7}`; e2e (nacido 1990-03-15) ve "a los 7 años (≈1997)" | pytest + Playwright |
| 12 | Cuándo · Etapa escolar (A-3) | e2e ve "en la primaria (≈1996–2001)" | Playwright |
| 13 | Cuándo · Sin fecha de nacimiento (A-3) | e2e sin fecha ve "a los 10 años" sin paréntesis | Playwright |
| 14 | Cuándo · El año se recalcula (A-3) | e2e corrige nacimiento a 1992-01-01 → "(≈1999)" | Playwright |
| 15 | Cuándo · Edad o año imposibles (A-3) | 3 POST (edad 40, año 1985, año 2030) con nacimiento 1990-03-15 → 422 con mensaje exacto; y edad 131 sin nacimiento → 422 | pytest |
| 16 | Ninguna · Marcar (A-2) | PUT none:true → `sections_none` la trae; e2e ve "Ninguna" en sección y tarjeta | pytest + Playwright |
| 17 | Ninguna · No se marca con registros (A-2) | PUT none:true con 1 fractura → 409 mensaje exacto; `sections_none` igual | pytest |
| 18 | Ninguna · Agregar quita la marca (A-2) | POST con marca → `sections_none` sin la sección; e2e ve el aviso y "1 registro" | pytest + Playwright |
| 19 | Ninguna · Deshacer (A-2) | e2e "Deshacer" → "Sin llenar"; pytest none:false | Playwright + pytest |
| 20 | Grupo · Elegir y corregir (A-7) | e2e O+ → "No lo sé" seleccionado tras recargar; pytest PUT/GET y null borra | Playwright + pytest |
| 21 | Grupo · Fuera del catálogo | PUT `blood_type: "C+"` → 422; GET sin cambio | pytest |
| 22 | Solo del paciente · Ajeno indistinguible (A-8) | B crea cirugía; A hace PUT/DELETE sobre esa y sobre un uuid inexistente → mismos status y cuerpo; la de B intacta | pytest |
| 23 | Cifrado en reposo (A-9) | SQL crudo sobre `medical_history_entry.content`, `patient_profile.blood_type` y `sections_none`: sin "Apendicectomía", "surgeries", "fractures" ni "O+", prefijo `gAAAA` | pytest |

Todas las rutas nuevas rechazan sin consentimiento como el resto del perfil (cubierto por la dependencia
compartida; un test de humo en pytest). E2e en los proyectos chromium y s26-ultra (384×832).

## Non-functional constraints addressed

- **NFR-001 cifrado:** decisión 2; test 23 por SQL crudo.
- **NFR-004 consentimiento:** `ConsentedUser` en todas las rutas; test de humo.
- **NFR-009 un test por FR:** la tabla de arriba, `make tdd-check` por grupo.
- **NFR-012 es-MX:** textos en `profile.json` y `detail` de errores asertados literalmente (tests 8, 9, 15, 17).
- **Accesibilidad:** chips con `role="group"` + `aria-pressed` (precedente K5); el formulario con labels
  asociados; foco de regreso a la lista al guardar o cancelar.
- **Móvil:** el spec nuevo entra al `testMatch` de s26-ultra (`playwright.config.ts:54`).

## Risks / Trade-offs

- [El JSON cifrado no es consultable por SQL] → aceptado (decisión 2); los avisos de IA (E5) leerán por dueño.
- [Cambiar un campo del contenido en el futuro exige migrar en Python, descifrando] → los esquemas toleran campos
  ausentes al leer (defaults `None`); renombrar campos queda prohibido sin migración de datos.
- [Carrera entre "marcar ninguna" y crear un registro desde dos pestañas] → ambas rutas releen el estado dentro
  de la transacción; el 409 cubre el orden inverso.
- [El enum `section` crecerá con B y C] → el 422 de "sección fuera de esta story" se retira entonces; las claves
  ya existen (`perfil.tsx:16-23`).
- [El rango por etapa es un supuesto] → una constante del frontend; corregirla no toca datos guardados.

## Migration Plan

Una revisión Alembic solo aditiva: tabla `medical_history_entry` y columnas nulas `blood_type` y `sections_none`
en `patient_profile`. Sin backfill. Rollback = downgrade que las elimina. En dev: `make migrate` (PR #19).

## Gate that closes the work

1. pytest backend completo truly green (0 fallos, 0 errores, 0 skips) con cobertura ≥ 90 %, y mypy limpio.
2. Playwright completo en chromium y s26-ultra truly green.
3. `make tdd-check` verde (un `test:` por grupo test→impl).
4. `openspec validate perfil-eventos --strict` limpio.
5. `validation.md` para Saúl Pérez y PR abierto. El merge es humano.

## Open Questions

(ninguna para esta story; la de la crónica con diagnóstico enlazado es de la Story B)
