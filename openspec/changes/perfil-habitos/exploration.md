# Exploration — perfil-habitos

Date: 2026-10-20 · Base branch: `feat/perfil-habitos` (sale de `origin/main` 7e724c3, con perfil-cronicas archivada y la
memoria ya en un archivo por entrada) · Explored by: el agente (orquestador), para Saúl Pérez (author)

## 1. Input validation

| Check | Result |
|---|---|
| As/I want/so that story with a concrete role | ✅ Como paciente, quiero contar mis hábitos (alcohol, tabaco, humo, ejercicio, movimiento y sueño) y mi trabajo, para que el médico y la IA los conozcan sin preguntarlos en cada consulta (product/prd.md § E2, US-18, FR-028 Story C; product/dominio.md § Hábitos y § Trabajo) |
| Every AC in Given/When/Then with concrete data | 🟡 C-1…C-9 son observables y traen sus opciones literales en el prototipo v4 (`product/prototipos/perfil-secciones.html`, `pintarHabitos` y `pintarTrabajo`) y en el dominio, pero aún no tienen forma GWT. Con `engine: openspec` se escriben como escenarios en la delta spec |
| No imposed technical solution | ✅ Ninguno dicta tecnología. C-6 es una regla de producto (NFR-008), no técnica |

## 2. Coverage matrix per criterion

| AC | Coverage | Where (file:line / dependency / URL + date) | Missing |
|---|---|---|---|
| C-1 alcohol: nunca / lo dejé (edad) / actual + AUDIT-C + "sobre todo fines de semana" | ❌ New (con patrón) | Respuestas de opción única = `ChipGroup` (`frontend/src/components/Profile/ChipGroup.tsx:18-24`, D18). "Edad" ≤ edad actual: `impossibleWhen` (`frontend/src/components/Profile/history.ts:185`) y `validate_when`/`_age_on` (`backend/app/models.py:729-745`), con "hoy" de México (`format.ts:27`) | Esquema `habits.alcohol`; escalas AUDIT-C como literales cerrados; descartar las preguntas AUDIT-C si no es "actual" |
| C-2 tabaco (nunca/antes/actual, cigarros, edad de inicio, edad en que lo dejó) + vapeador | ❌ New (con patrón) | Mismos helpers de edad que C-1 | "Empezó" ≤ "lo dejó" ≤ edad actual; "lo dejó" solo con "antes" |
| C-3 humo ajeno: dónde (varios) + días por semana, o "no me expongo" | ❌ New | `ChipGroup` es de **una** opción (`ChipGroup.tsx:18`). Antecedentes familiares usa checkboxes (`FamilyHistoryFields.tsx:4`), anterior a D18 | Variante de chips **múltiple** (D18: chips para opciones); "no me expongo" excluyente; días 0–7 |
| C-4 humo de leña: nunca/antes/actual + años | ❌ New (con patrón) | `ChipGroup`; riesgo [VERIFIED] en `memory/research/humo-lena.md` | Años solo si no es "nunca" |
| C-5 ejercicio: lista de actividades con días/semana y minutos/vez + total semanal | ❌ New | Ninguna lista anidada dentro de un formulario hoy; los registros de sección son filas propias (`medical_history_entry`, `models.py:507`) | Lista dentro de los hábitos (dominio: hábitos 1→0..1 → actividad física 1→0..N); total = Σ días × minutos, calculado al mostrar, **sin veredicto** OMS |
| C-6 sin puntajes ni riesgos | ✅ Regla (se prueba en negativo) | Regla C-6 en `product/dominio.md` § Hábitos; NFR-008 | Pruebas de que ni la API ni la UI devuelven puntaje AUDIT-C, "riesgo" ni "cumples" |
| C-7 movimiento del día (no se suma al ejercicio) | ❌ New | Forma GPAQ, `memory/research/ocupacion.md` | Tres respuestas; el total de C-5 no las incluye |
| C-8 sueño: horas + dificultad | ❌ New (con patrón) | `ChipGroup` | Horas 0–24 |
| C-9 "Trabajo" en el Perfil básico | ❌ New (con patrón) | Bloque del Perfil básico: `perfil.tsx:63-110` (filas `Row`) y su diálogo `EditBasicData.tsx`. Dato 1:1 cifrado en `patient_profile`: el patrón de `blood_type` y `sections_none` (`models.py:431-439`, perfil-eventos Decision 3), servido por `GET/PUT /profile` (`backend/app/api/routes/profile.py:265,272`) | Columna cifrada `work`; diálogo "Editar trabajo"; exposiciones múltiples con "nada de esto" excluyente (misma variante de chips que C-3) |
| Tarjeta "Hábitos" abre su pantalla | 🟡 Partial | La tarjeta existe sin enlace (`perfil.tsx:150-166`, `history.ts:25-33`); la ruta de sección es `perfil_.$seccion.tsx:17-23` con slug | Slug `habitos` (no es una sección de lista); estado de la tarjeta "Sin llenar" / "Con datos" (prototipo `pillDe`), sin "ninguna" |
| Cifrado, aislado, tras consentimiento | ✅ Exists (infra) | `EncryptedString` (D13), perfil 1:1 por usuario (`models.py:411-417`), `ConsentedUser` y `_lock_profile` (`profile.py:140-147`) | Nada nuevo: las columnas nuevas usan lo mismo |

## 3. What looked useful and was discarded (and why)

- **Hábitos como una sección más de `medical_history_entry`:** es una tabla de listas (1→0..N con "ninguna"), y los
  hábitos son un cuestionario 1→0..1 sin "ninguna" (dominio). Obligaría a un "solo un registro de esta sección"
  que no existe en esa tabla. El patrón de `blood_type` (una columna cifrada en el perfil) es el que encaja.
- **Una tabla `physical_activity` para el ejercicio:** pondría en claro cuántas actividades tiene cada paciente y
  agregaría altas y bajas sueltas. La lista vive dentro del JSON cifrado de los hábitos y se guarda con el mismo
  "Guardar" de la pantalla, como en el prototipo.
- **Reutilizar `WhenField` para las edades:** el dominio pide **edad** en estos campos (ronda 8), no edad, etapa o
  año. Basta un número con la misma validación de edad.
- **Checkboxes para las opciones múltiples** (como los antecedentes familiares): contradice D18, que fija chips
  para opciones. Los antecedentes familiares se quedan como están; no se tocan aquí.

## 4. Non-functional constraints detected

| Constraint | Status | How it is met |
|---|---|---|
| NFR-001 / D13: cifrado en reposo | 🟢 | Dos columnas `EncryptedString` en `patient_profile`; nada en claro |
| LFPDPPP art. 3-VI: datos de salud sensibles | 🟢 | Mismo consentimiento y aislamiento por cuenta que el resto del perfil |
| NFR-008 / C-6: la app no interpreta | 🟢 | Sin puntajes; el total de ejercicio es una suma de minutos, no un veredicto |
| D18: chips para opciones | 🟡 | Hace falta la variante múltiple de `ChipGroup` (C-3, C-9) |
| WCAG 2.2 / lecciones de la review de B | 🟡 | Nombres accesibles distintos por grupo (R7 de perfil-cronicas: dos campos con el mismo nombre); errores junto a su campo (R5); "hoy" de México (R11) |
| Móvil 384 px | 🟡 | La pantalla es larga (8 bloques): debe caber sin scroll horizontal y con el botón de guardar alcanzable |
| Fatiga de uso (Saúl Pérez, 2026-10-20) | 🟡 | Todo opcional, guardar lo que se tenga, "Nunca" con un toque. La experiencia "casi como Duolingo" sigue en el inbox, fuera de este cambio. No premiar revelar datos sensibles (`memory/research/mascota-color.md`) |
| es-MX (D15) | 🟢 | Textos en `frontend/src/locales/es-MX/profile.json` |

## 5. Change classification

**Extension.** Sin tabla nueva: dos columnas cifradas en `patient_profile`, un endpoint por bloque (o el `PUT
/profile` existente), una pantalla de cuestionario, un diálogo en el Perfil básico y una variante de `ChipGroup`.

Es la story más grande de las tres. B tenía 7 criterios y su review tomó tres rondas (24 → 12 → 2 hallazgos). C
tiene 9, ocho bloques en una pantalla, una lista anidada y un diálogo aparte.

## 6. Blocking questions (max 4)

1. **¿Una story o dos?** Recomendación: **dos PRs**, para que cada review sea del tamaño de la de B:
   - **C1 — sustancias y humo:** alcohol, tabaco y vapeador, humo ajeno, leña, y la regla sin puntajes (C-1…C-4,
     C-6). Crea la pantalla de hábitos y la variante múltiple de chips.
   - **C2 — cuerpo, descanso y trabajo:** ejercicio, movimiento del día, sueño y el bloque Trabajo (C-5, C-7,
     C-8, C-9).

   Alternativa: una sola story con dos grupos de tareas, en un PR más grande.
2. **Respuestas que se contradicen** (por ejemplo, alcohol "Nunca" con preguntas AUDIT-C contestadas). Recomendación:
   el servidor descarta lo que no aplica, como el "hasta" de una crónica activa en la Story B. Lo asumo salvo que
   digas otra cosa.
3. **Edades imposibles** ("lo dejé a los 50" con 38 años, o empezar después de dejarlo). Recomendación: rechazarlas
   con el mensaje junto al campo, con la misma regla de la Story A: sin fecha de nacimiento no se rechaza nada que
   pueda ser cierto.

## 7. Sources consulted

- `product/dominio.md` § Hábitos, § Trabajo, Regla C-6 (líneas 386–418), y § Partición en stories (:313-319).
- `product/prototipos/perfil-secciones.html`: `pintarHabitos`, `pintarTrabajo`, `pillDe`, criterios C-1…C-9.
- `memory/research/habitos.md`, `ocupacion.md`, `humo-lena.md`, `mascota-color.md`.
- `memory/decisions/D13-…`, `D15-…`, `D18-opciones-en-la-ui-chips-como.md`.
- Código citado en §2, en `origin/main` 7e724c3.

## 8. Respuestas del gate (Saúl Pérez, 2026-10-20)

Saúl Pérez aceptó la matriz ("Procede con tus sugerencias").
1. **Dos stories.** Este cambio es la **C1: sustancias y humo** (C-1…C-4, C-6), que crea la pantalla de hábitos y
   los chips de selección múltiple. La **C2** (ejercicio, movimiento del día, sueño y trabajo: C-5, C-7, C-8, C-9)
   será su propio cambio, sobre la misma pantalla y el mismo dato.
2. **Contradicciones:** el servidor descarta lo que no aplica (recomendación aceptada).
3. **Edades imposibles:** se rechazan con el mensaje junto al campo; sin fecha de nacimiento no se rechaza nada que
   pueda ser cierto (recomendación aceptada).
