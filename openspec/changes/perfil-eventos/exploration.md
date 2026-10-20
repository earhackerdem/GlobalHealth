# Exploration — perfil-eventos

Date: 2026-10-20 · Base branch: `feat/perfil-eventos` (sale de `docs/discovery-perfil-secciones`; se rebasa sobre
`main` cuando se mergeen #17 y #18, antes de abrir el PR) · Explored by: el agente (orquestador), para Saúl Pérez
(author)

## 1. Input validation

| Check | Result |
|---|---|
| As/I want/so that story with a concrete role | ✅ "Como paciente, quiero registrar mis enfermedades pasadas, cirugías, fracturas y transfusiones (o decir que no he tenido ninguna)…" (proposal.md § User story) |
| Every AC in Given/When/Then with concrete data | 🟡 A-1…A-9 son observables y traen los datos concretos (listas, valores, mensajes) del prototipo v4, pero aún no están en forma GWT. Con `engine: openspec` se escriben como scenarios en `specs/records/patient-profile/spec.md` dentro de `/epe-2-plan`; no bloquea |
| No imposed technical solution | ✅ Ninguno dicta tecnología. A-9 (cifrado) es el NFR-001 heredado, no una solución impuesta |

## 2. Coverage matrix per criterion

| AC | Coverage | Where (file:line / dependency / URL + date) | Missing |
|---|---|---|---|
| A-1 estado por tarjeta | 🟡 Partial | Las 6 tarjetas existen pero son estáticas: `frontend/src/routes/_layout/perfil.tsx:148-160` pinta `t("noEntries")` = "Sin registros" (`frontend/src/locales/es-MX/profile.json:8`) para todas; claves de sección `perfil.tsx:16-23` (chronic, past, surgeries, fractures, transfusions, habits) | Estado derivado de los datos (sin llenar / ninguna / N registros) para past, surgeries, fractures, transfusions; las tarjetas pasan a ser navegables |
| A-2 "ninguna" por sección | ❌ New | No existe el concepto en el modelo (`backend/app/models.py:411-468`: perfil, mediciones, AHF) | Dato "ninguna" por sección, su regla (solo sin registros; agregar uno la quita) y deshacer |
| A-3 "cuándo" por edad/etapa/año | ❌ New (con piezas) | La fecha de nacimiento ya vive cifrada en `PatientProfile.birth_date` (`models.py:411-428`) y el server la lee vía `_get_or_create_profile` (`backend/app/api/routes/profile.py:47`); la validación de fechas sigue el patrón `validate_birth_date` (`models.py:372`) con 422 es-MX; el front ya calcula la edad con `ageFrom` (`frontend/src/components/Profile/format.ts`) | Tipo "cuándo" (edad · etapa · año · no recuerdo), validación contra la edad actual y el año de nacimiento cuando existe, y el cálculo del año aproximado al mostrar (con rangos por etapa [ASSUMPTION] del dominio) |
| A-4 enfermedad pasada | ❌ New | Patrón reutilizable: catálogo + "otra" de AHF (`FamilyHistoryCreate.condition` Literal + `other_text`, `models.py:514-531`) | Catálogo de 10 condiciones + otra, sí/no/no sé, secuelas, nota |
| A-5 cirugía/hospitalización | ❌ New | Mismo patrón de campos opcionales con `max_length=2000` (`models.py:514-531`) | Tipo, nombre requerido, 7 campos opcionales, sí/no/no sé con detalle |
| A-6 fractura/lesión | ❌ New | ídem | Lado, ¿requirió cirugía?, material implantado |
| A-7 transfusión + grupo sanguíneo | 🟡 Partial | El perfil 1:1 cifrado (`models.py:411-428`) y su PUT parcial con "null explícito borra" (`PatientProfileUpdate`, `models.py:472`; ruta `profile.py:136-162`) ya dan el lugar y la semántica para un dato único como el grupo sanguíneo | Campo `blood_type` en el perfil; registros de transfusión (componente, reacción con detalle) |
| A-8 solo el paciente; eliminar con confirmación; vacío no se guarda | 🟡 Partial | Aislamiento con 404 idéntico para ajeno e inexistente: `_get_owned_family_history` (`profile.py:115-125`), requirement "El perfil es solo del paciente" de la spec vigente; consentimiento obligatorio: `require_consent`/`ConsentedUser` (`backend/app/api/deps.py:68,87`) | Mismas garantías para los registros nuevos; regla "registro vacío no se guarda" (front y 422 back) |
| A-9 cifrado, aislado, tras consentimiento | ✅ Exists (infra) | `EncryptedString` (`backend/app/core/encrypted.py:89`), D13; veredicto `memory/closed.md` 2026-10-11 "TODO campo con contenido de salud se cifra desde su primera migración" (↩️ reopenable) | Aplicarlo a cada campo nuevo desde la primera migración (ver §4 sobre qué puede ir en claro) |

## 3. What looked useful and was discarded (and why)

- **`HealthRecord` del expediente** (`models.py:114-137`): ya guarda diagnósticos con estado y archivado, pero exige
  fecha exacta (`occurred_on`) y representa un **documento o evento con fecha**. El dominio separa a propósito
  "cuándo" (edad/etapa/año) de `occurred_on` (product/dominio.md, mecánica "Cuándo"). Meter cirugías ahí mezclaría
  dos conceptos que el glosario distingue.
- **`BodyMeasurement`** (`models.py:430-446`): es una serie fechada de un valor numérico; no sirve para registros
  con varios campos de texto.
- **`formatDateMx`** y la fila del inbox sobre su duplicación (2026-10-19): esta story **no muestra fechas
  exactas**, así que no crea la tercera copia; la fila sigue abierta para cuando aplique.
- **Validar el año con `validate_birth_date`** tal cual: valida una fecha completa ISO, no un año ni una edad; se
  reutiliza el patrón (422 con detalle es-MX, antes de cifrar), no la función.

## 4. Non-functional constraints detected

| # | AC | Finding | Traffic light | Alternative / condition for the plan |
|---|---|---|---|---|
| 1 | A-9, A-2 | **NFR-001 / closed.md 2026-10-11**: cualquier campo con contenido de salud va cifrado. El precedente G19 (mediciones) dejó `type` y fecha **en claro** porque el sistema consulta por ellos. Aquí, la sección en claro revela "tuvo una cirugía" o "tuvo una transfusión", y "ninguna" en claro revela "nunca lo han operado" | 🟡 | Cifrar también la sección y el "ninguna", y agrupar en la app: el volumen por paciente es de decenas de filas, así que listar todo y agrupar en memoria es barato (precedente: dedupe por descifrado de AHF, `models.py:449-452`). Pregunta 2 |
| 2 | A-8 | NFR-004 consentimiento: `ConsentedUser` (`deps.py:87`) en todas las rutas nuevas | 🟢 | Reutilizar |
| 3 | todos | NFR-009: un test por criterio; NFR-012 es-MX: namespace i18next `profile` (`profile.json:79-87` ya tiene los nombres de las secciones) | 🟢 | Plan con un test por A-n; textos y errores 422 en es-MX como contrato |
| 4 | A-1 | **Test existente que se rompe a propósito:** `frontend/tests/profile.spec.ts:280-300` asierta que las secciones NO tienen inputs ni botón Guardar/Agregar ("Read-only by design", `perfil.tsx:148`) | 🟡 | Es un citer: el plan reescribe esa aserción para crónicas y hábitos (siguen sin captura) y la invierte para las 4 secciones de esta story, en el mismo cambio |
| 5 | spec | La spec base `records/patient-profile` llega a `openspec/specs/` con el PR #17 (archivo de onboarding-perfil), aún sin mergear; este cambio la **MODIFICA** (requirement "Pantalla 'Mi perfil médico' con secciones visibles", spec:86-88) | 🟡 | Mergear #17 antes del archive de este cambio; el delta usa MODIFIED sobre ese requirement |
| 6 | todos | Móvil 384×832: el proyecto Playwright `s26-ultra` corre solo `health-records` y `profile` (`frontend/playwright.config.ts:54`) | 🟢 | Si los tests nuevos van en un spec nuevo, sumarlo al `testMatch`; o vivir en `profile.spec.ts` |
| 7 | A-4…A-7 | Accesibilidad de los grupos de chips: precedente K5 del apply de receta-mexicana (semántica de grupo) | 🟢 | `role="group"` + `aria-pressed`/radio, como en el prototipo |
| 8 | A-5, A-7 | Médico y hospital son datos de terceros aportados por el titular (como AHF): LFPDPPP art. 3-VI | 🟢 | Opcionales y cifrados (minimización), sin cambio de aviso |

## 5. Change classification

**Extension** de `records/patient-profile`: modelos y rutas nuevos sobre el router y la pantalla del perfil que ya
existen, con la infraestructura de cifrado y consentimiento tal cual. Hints for the plan:

- **Grupo sanguíneo** (resuelve el MISSING del proposal): campo `blood_type` cifrado en `PatientProfile` +
  `PatientProfileUpdate` (un solo dato del paciente, 1:1). La UI lo pinta dentro de la sección de transfusiones,
  como el prototipo.
- **Registros:** una tabla genérica (`user_id`, contenido cifrado con la sección y los campos como JSON dentro del
  cifrado, `created_at`) + esquemas pydantic por sección (unión discriminada). Ventaja: una migración, un CRUD y un
  aislamiento, y las stories B y C la reutilizan. Alternativa: 4 tablas tipadas (4 veces el CRUD). Pregunta 1.
- **"Ninguna":** lista cifrada de secciones en `PatientProfile`. Marcar con registros → 409 es-MX; crear un
  registro la quita en la misma transacción.
- **"Cuándo":** se guarda `{kind: age|stage|year|unknown, value}` dentro del JSON cifrado. Valida en el back: edad
  ≤ edad actual y año ∈ [año de nacimiento, hoy] si hay fecha de nacimiento; si no, edad ≤ 130 y año ≤ hoy. El año
  aproximado se calcula al mostrar (front), no se guarda.
- **Rutas:** `GET/POST /profile/history`, `PUT/DELETE /profile/history/{id}` (404 idéntico ajeno/inexistente),
  `PUT /profile/history/sections/{section}` con `{none: bool}`. El blood_type va por el `PUT /profile` existente.
- **Frontend:** componente `WhenField` (edad/etapa/año) reutilizable por B y C; pantalla por sección (pregunta 3).
- **Tropiezos conocidos del inbox que este cambio va a pisar:** (a) el contenedor backend no corre Alembic al
  arrancar (fila 2026-10-19): la migración nueva dará 500 en dev sin `alembic upgrade head` manual; (b)
  `generate-client.sh`/`bun run lint` reformatean `frontend/tests/` (filas 2026-10-12 y 2026-10-18), lo que ya le
  pisó un spec del tester a un implementer. Pregunta 4.

## 6. Blocking questions (max 4)

1. **Modelo de los registros** — A (recomendada): una tabla genérica con el contenido cifrado y esquemas por
   sección; B: 4 tablas tipadas. Importa porque B y C reutilizan A y porque son 4× migraciones y rutas.
2. **¿Qué va en claro?** — A (recomendada): nada, ni la sección ni el "ninguna" (se agrupa en la app; decenas de
   filas por paciente); B: la sección en claro, como el `type` de las mediciones (G19), para filtrar en SQL. Importa
   porque "tuvo una transfusión" ya es dato de salud (veredicto de closed.md 2026-10-11).
3. **Navegación** — A (recomendada): una pantalla por sección (`/perfil/<seccion>`) con la lista, el "ninguna" y
   el formulario, como el prototipo validado y con espacio en 384 px; B: todo en diálogos sobre "Mi perfil médico",
   como AHF hoy.
4. **Los dos tropiezos del inbox (Alembic al arrancar y el reformateo de tests)** — A (recomendada): arreglarlos
   en un PR `fix/` chico ANTES de ejecutar esta story; B: como tareas de este cambio (mezcla alcance); C: dejarlos
   y documentar el paso manual en el plan.

## 7. Sources consulted

- Código: `backend/app/models.py:114-137, 372, 411-546`; `backend/app/api/routes/profile.py:47, 115-125, 129-162`;
  `backend/app/api/deps.py:68, 87`; `backend/app/core/encrypted.py:89`; `frontend/src/routes/_layout/perfil.tsx:16-23,
  141-161`; `frontend/src/locales/es-MX/profile.json:8, 79-87`; `frontend/src/components/Profile/format.ts`;
  `frontend/tests/profile.spec.ts:280-300`; `frontend/playwright.config.ts:54`.
- Specs: `openspec/changes/onboarding-perfil/specs/records/patient-profile/spec.md` (en `openspec/specs/` tras #17).
- Memoria: `memory/decisions.md` D13 (cifrado), D15 (i18n), D16; `memory/closed.md` filas 2026-10-11 (cifrar todo
  campo de salud) y 2026-10-19 (onboarding-perfil); `memory/inbox.md` filas 2026-10-12, 2026-10-18, 2026-10-19;
  `product/technical-brief.md` §4 (NFR-001, 004, 009, 012); `product/dominio.md` rebanada FR-028;
  `product/prototipos/perfil-secciones.html` v4.

## 8. Respuestas del gate (Saúl Pérez, 2026-10-20)

Matriz aceptada al responder las cuatro preguntas, todas con la opción recomendada:
1. Una **tabla genérica** con el contenido cifrado y esquemas por sección.
2. **Nada en claro**: la sección y el "ninguna" también se cifran; se agrupa en la app.
3. **Una pantalla por sección** (`/perfil/<seccion>`), como el prototipo.
4. Los tropiezos del inbox (Alembic al arrancar y el reformateo de `frontend/tests/`) se arreglan en un **PR
   `fix/` aparte, antes** de ejecutar esta story.
