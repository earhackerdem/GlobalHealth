# Design

Status: DRAFT

**En una frase:** "Enfermedades crónicas" se vuelve llenable como una sección más del historial de la Story A, con
estado Activa / Ya no la tengo, "desde" y "hasta", la marca "Sensible" que decide el paciente y un enlace cifrado a
un diagnóstico del expediente, que se quita (con aviso) si el diagnóstico se borra.

## Context

perfil-eventos (PR #20, archivado el 2026-10-20) dejó la infraestructura:
- una tabla genérica `medical_history_entry` con el JSON del registro cifrado, sección incluida (Decision 2);
- "ninguna" por sección (Decision 3);
- "cuándo" guardado como se dijo (Decision 4);
- una pantalla por sección en el front.

Crónicas es la quinta sección y la única que se enlaza con otra parte de la app: el expediente. La exploración
(`exploration.md`) la clasificó como extensión. Saúl Pérez respondió el gate el 2026-10-20: la marca "Sensible" va
como interruptor por crónica, y las adicciones entran al grupo sensible (§8).

## Goals / Non-Goals

- **Goal:** que el paciente registre sus crónicas con lo que el médico pregunta, y marque cuáles son sensibles,
  sin que el enlace al diagnóstico deje datos colgando cuando lo borra.
- **Non-goals:**
  - hábitos y trabajo (Story C);
  - compartir y ocultar por la marca (FR-014, E3/E4; inbox 2026-10-20);
  - un catálogo propio de enfermedades (descartado en el gate);
  - el enlace tratamiento ↔ medicinas de receta (dominio, ronda 2);
  - migrar el formulario a RHF+zod (H5, diferido en `closed.md`).

## Qué se toca / qué NO

**Se toca:**
- **Modelo:** `backend/app/models.py` (`HistorySection` `:488`, `HISTORY_SECTIONS` `:489`, la unión de contenido
  `:603-645`, `HISTORY_REQUIRED` `:656` y `validate_history_content` `:700`).
- **Rutas del historial:** `backend/app/api/routes/profile.py` (validación `:153`, POST y PUT `:483-530`).
- **Expediente:** `backend/app/api/routes/health_records.py` (DELETE `:217`).
- **Helper nuevo:** `backend/app/crud.py`.
- **Front, perfil:** `frontend/src/components/Profile/{history.ts, HistoryEntryForm.tsx, HistorySection.tsx,
  WhenField.tsx}` y `frontend/src/routes/_layout/perfil.tsx` (tarjetas `:151-190`).
- **Front, expediente:** `frontend/src/components/Records/DeleteRecord.tsx` (`:28`).
- **Textos:** `frontend/src/locales/es-MX/{profile,records}.json`.
- **Cliente generado:** `frontend/src/client/`.

**NO se toca:**
- el esquema de la base: no hay migración, porque la sección nueva vive en el mismo JSON cifrado;
- las secciones de la Story A, salvo las listas comunes;
- onboarding, AHF y mediciones;
- la lógica del expediente fuera del borrado de un diagnóstico.

## Interface contract

Base `/api/v1`, todo detrás de `ConsentedUser`. Errores con `detail` string es-MX. Es el mismo contrato de la
Story A, ampliado.

**Tipos**
- `section`: se suma `"chronic"`, primero en el orden canónico: `chronic · past · surgeries · fractures ·
  transfusions`.
- Contenido `chronic` (todos opcionales salvo `condition`; textos ≤ 2000):
  - `condition` (**req**): `"type2_diabetes" | "hypertension" | "asthma" | "hypothyroidism" | "high_cholesterol" |
    "copd" | "arthritis" | "epilepsy" | "depression" | "anxiety" | "bipolar_disorder" | "substance_use" | "other"`;
  - `other_text`: requerido si `condition` es `other`;
  - `sensitive: bool`: si no viene, el servidor pone `true` para `depression · anxiety · bipolar_disorder ·
    substance_use` y `false` para las demás. Se guarda siempre explícito;
  - `status: "active" | "resolved"`;
  - `since: When`;
  - `until: When`: el servidor lo descarta si `status` no es `resolved`;
  - `treatment`, `note`;
  - `diagnosis_id: uuid`.

**Validación (servidor, antes de cifrar)**
- Requerido: "Elige la condición o escribe cuál es". Registro vacío: "Llena al menos un dato", como en la Story A.
- `since` y `until` pasan por `validate_when`, con las mismas reglas y mensajes de la Story A.
- `until` antes de `since` → 422 "No puede ser antes de «desde cuándo»". Se compara por rango de edad: una edad es
  `[v, v]`, una etapa es su rango de `STAGE_AGE_RANGES` y un año es `año − año de nacimiento`, solo si hay fecha de
  nacimiento. `unknown`, o un año sin fecha de nacimiento, no se compara. Se rechaza solo si el máximo de `until` es
  menor que el mínimo de `since`.
- `diagnosis_id` que no sea un `HealthRecord` con `record_type="diagnosis"` del mismo paciente → 422 "Ese
  diagnóstico no está en tu expediente". Es el mismo mensaje para uno ajeno, una receta o un id inexistente.

**Operaciones**
- **Nuevas para `chronic`:** las de la Story A: `GET/POST /profile/history`, `PUT/DELETE /profile/history/{id}` y
  `PUT /profile/history/sections/chronic/none`.
- **Ruta de "ninguna":** acepta `chronic`. Una sección que no existe sigue dando 422.
- **`DELETE /health-records/{id}` de un diagnóstico:** en la misma transacción llama a
  `crud.unlink_diagnosis(session, owner_id, diagnosis_id) -> int`. Esa función descifra las crónicas del paciente,
  quita `diagnosis_id` de las que apuntan a ese diagnóstico y devuelve cuántas cambió. La respuesta de la ruta no
  cambia.

**Tablas:** ninguna nueva. Las aserciones de ciphertext van sobre `medical_history_entry.content`, como en la A-9.

**Frontend**
- **URL:** `/perfil/cronicas`. La tarjeta `history-card-chronic` pasa a ser enlace, con chevron (O1). Solo
  `history-card-habits` sigue sin enlace.
- **Formulario de crónica:** son etiquetas y textos de UI, no nombres de campo.
  - grupo "¿Cuál?" con las 12 condiciones y "Otra"; las cuatro sensibles van bajo el subtítulo "Salud mental y
    adicciones";
  - casilla "Sensible" con la ayuda "Podrás ocultarla cuando compartas tu expediente". Su valor por defecto sigue a
    la condición mientras el paciente no la toque;
  - chips "Activa" / "Ya no la tengo";
  - `WhenField` dos veces: "¿Desde cuándo?" y, solo con "Ya no la tengo", "¿Hasta cuándo?";
  - "Tratamiento actual" y "Nota" (`Textarea`);
  - el select "Diagnóstico del expediente que la respalda", con la opción "Ninguno" y solo diagnósticos. Lo llena
    `GET /health-records` con `limit=1000`.
- **Resumen en la lista:**
  - activa: "Hipotiroidismo · desde los 31 años (≈2021) · activa · Levotiroxina…";
  - resuelta: "Asma · desde la primaria (≈1996–2001) · hasta los 16 años (≈2006)";
  - etiqueta "sensible" (`data-testid="sensitive-badge"`) y la línea "Respaldo: <título del diagnóstico>" si el
    enlace resuelve.
- **"Ninguna" en crónicas:** "No tengo ninguna".
- **`DeleteRecord` de un diagnóstico:** si respalda crónicas, la descripción agrega "Respalda tu crónica
  «Hipotiroidismo». La crónica se queda, sin respaldo." (con varias: «A», «B»). Al terminar invalida
  `["profile", "history"]`.

## Decisions

1. **Crónica = sección `chronic` en la tabla genérica, enlace dentro del JSON cifrado.** Descartado: una tabla
   propia con llave foránea, porque pondría en claro la relación paciente ↔ diagnóstico ↔ crónica.
2. **"Sensible" es un campo explícito del registro, con valor por defecto en el servidor según la condición.** Así
   un cliente viejo o la API no dejan una crónica de salud mental sin marca. Descartado: derivarla siempre de la
   condición, porque Saúl Pérez la quiere decidir él (§8).
3. **Al borrar un diagnóstico, el servidor quita el enlace en la misma transacción.** Descartado: resolverlo solo al
   leer, porque dejaría guardado el id de un dato que el paciente borró (ARCO, FR-003).
4. **El aviso de B-5 se arma en el front con `GET /profile/history`.** Descartado: un endpoint nuevo de "crónicas
   enlazadas", que sería otra ruta para el mismo dato.
5. **`until` se descarta si la crónica está activa** (servidor y front), como en el prototipo.
6. **Comparación `until`/`since` por rango de edad.** El servidor solo rechaza lo imposible (Decision 4 de la Story
   A); con datos ambiguos no se rechaza.

**ADRs afectados:** ninguno. Se respetan D13 (cifrado), D15 (es-MX) y el veredicto de `closed.md` "todo campo de
salud se cifra desde su primera migración".

**Citadores (caducan en este cambio):**
- La spec `records/patient-profile` (delta).
- La spec `records/clinical-records` (delta).
- `backend/tests/api/routes/test_profile_history.py:559-565` hoy espera 422 para `chronic`; pasa a `habits`.
- `frontend/tests/profile.spec.ts:317-319` y `frontend/tests/profile-history.spec.ts:262` hoy esperan crónicas sin
  enlace; pasan a solo hábitos.
- Los comentarios de contrato de esos specs (`profile.spec.ts:15,58`, `profile-history.spec.ts:24-27`).
- Las claves `pending.sections.chronic` (`profile.json:81`).
- Al archivar: `product/dominio.md` (Story B entregada) y `product/prd.md` US-18.

## Test plan (one row per scenario, mandatory)

| # | Spec · scenario | Test | Dónde |
|---|---|---|---|
| 1 | Crónicas · Crónica de la lista con tratamiento (B-1, B-3) | POST hypothyroidism/active/since age 31/treatment → GET; e2e ve el resumen exacto | pytest + Playwright |
| 2 | Crónicas · Salud mental sensible por defecto (B-1b) | POST anxiety sin `sensitive` → `sensitive: true`; POST hypertension sin `sensitive` → `false`; e2e: "Ansiedad" sin tocar la casilla → etiqueta "sensible" | pytest + Playwright |
| 3 | Crónicas · El paciente decide la marca (B-1b) | e2e: "otra"+"TOC" con la casilla → sensible; editar hipertensión on/off → la etiqueta aparece y desaparece; pytest `sensitive` explícito se respeta | Playwright + pytest |
| 4 | Crónicas · Ya no la tengo, desde y hasta (B-2) | e2e: asma resolved, desde "En la primaria", hasta 16 → resumen exacto | Playwright |
| 5 | Crónicas · "Hasta" antes de "desde" (B-2) | pytest: age 20 / age 12 → 422 con el mensaje; stage vs age por rango; year vs age con y sin fecha de nacimiento (sin fecha no se rechaza); e2e: el error junto a "¿Hasta cuándo?" | pytest + Playwright |
| 6 | Crónicas · "Hasta" con activa no se guarda (B-2) | pytest: PUT status active con until → GET sin until; e2e: el campo desaparece al elegir "Activa" | pytest + Playwright |
| 7 | Crónicas · Enlace a un diagnóstico (B-4) | e2e: diagnóstico sembrado por API → seleccionarlo → "Respaldo: Hipotiroidismo subclínico"; el select no lista recetas | Playwright |
| 8 | Crónicas · Enlace a un diagnóstico que no es suyo (B-4) | pytest: id de B, receta propia, uuid aleatorio → 422 mismo mensaje; nada persistido | pytest |
| 9 | Crónicas · Falta la condición (B-1) | pytest: sin condition / other sin texto → 422 "Elige la condición o escribe cuál es"; e2e: el foco va al grupo | pytest + Playwright |
| 10 | Pantalla · Estado de cada sección en su tarjeta (A-1; con crónica, B-0) | e2e del escenario con crónica → "1 registro"; solo hábitos sin enlace | Playwright |
| 11 | Pantalla · Secciones listadas sin captura | `profile.spec.ts` (C8): solo hábitos sin inputs, enlace ni "Agregar" | Playwright |
| 12 | Pantalla · La tarjeta abre la pantalla de su sección | clic en crónicas → `/perfil/cronicas` con "Agregar" | Playwright |
| 13 | Ninguna · Marcar, no con registros, agregar quita, deshacer (A-2) | sin cambios: suite de la Story A en verde | Playwright + pytest |
| 14 | Ninguna · "No tengo ninguna" en crónicas (B-0) | pytest: PUT none chronic → `sections_none` la trae; POST chronic la quita; e2e: "Ninguna" → "1 registro" con aviso | pytest + Playwright |
| 15 | Aislados y cifrados · Ajeno indistinguible / Cifrado (A-8, A-9) | sin cambios: suite de la Story A; el aislamiento de crónicas, con una crónica de B | pytest |
| 16 | Aislados y cifrados · Crónica cifrada (B-6) | SQL directo: ni `anxiety`, ni "Sertralina", ni `"sensitive"`, ni el uuid del diagnóstico en claro | pytest |
| 17 | Expediente · Eliminar un diagnóstico que respalda crónicas (B-5) | pytest: DELETE del diagnóstico → la crónica sigue y su `diagnosis_id` es null; otro paciente con una crónica no se toca. e2e: el diálogo nombra «Hipotiroidismo»; tras confirmar, la crónica ya no muestra "Respaldo" | pytest + Playwright |
| 18 | Expediente · escenarios base de borrado (ajeno, corregir, receta con adjuntos) | sin cambios: suite del expediente en verde | pytest |

## Non-functional constraints addressed

- **NFR-001:** el contenido completo va cifrado (fila 16).
- **S3 (`closed.md:36`):** la longitud del ciphertext revela la sección; el veredicto diferido cubre `chronic`.
- **H5 (`closed.md:37`):** el formulario crece sin RHF; es deuda declarada.
- **`limit=1000` en el selector:** un paciente supera los 100 registros con el tiempo; 1000 basta para el supuesto
  "decenas por paciente".
- **Accesibilidad:** los patrones del apply de la Story A (foco, errores junto al campo, nombres accesibles); la
  casilla "Sensible" con su descripción asociada.

## Risks / Trade-offs

- **Desincronización de la marca:** si el paciente cambia la condición después de tocar la casilla, la marca no se
  recalcula. Es intencional: decidió él.
- **Costo de `unlink_diagnosis`:** descifra todas las crónicas del paciente en cada borrado de diagnóstico. Son
  decenas de filas, el mismo supuesto de S1.
- **Un diagnóstico borrado desde otra pestaña** mientras se edita la crónica: el PUT con un `diagnosis_id` que ya
  no existe da 422, y el formulario muestra el mensaje junto al selector.

## Migration Plan

Sin migración de base. El orden canónico de `sections_none` cambia, pero se reordena al leer (`_sections_none`).

## Gate that closes the work

1. La suite completa de pytest del backend, truly green (0 fallos, 0 errores, 0 skips), con cobertura ≥ 90 % y mypy
   limpio.
2. La suite completa de Playwright en chromium y s26-ultra, truly green.
3. `make tdd-check` verde.
4. `openspec validate perfil-cronicas --strict` limpio.
5. La exploración en Chrome hecha por el agente, sin defectos (`epe-3-execute`, paso 2), y el archivo como último
   commit del PR (`epe-6-archive`, 0.3.2). Después, la validación de Saúl Pérez con `validation.md`. El merge es
   humano.

## Open Questions

Ninguna bloqueante: la exploración no dejó preguntas abiertas (§8).
