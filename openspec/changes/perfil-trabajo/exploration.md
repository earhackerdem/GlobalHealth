# Exploration — perfil-trabajo

Fecha: 2026-10-29 · Entrada: `proposal.md` (C-9, T-1…T-5), del dominio § Trabajo y del prototipo
`product/prototipos/perfil-secciones.html:274-297`.

## 1. Input validation

| Check | Result |
|---|---|
| As/I want/so that story with a concrete role | ✅ «Como paciente, quiero contar a qué me dedico, a qué me expongo en mi trabajo y en qué turno…» |
| Every AC in Given/When/Then with concrete data | ✅ T-1…T-5 son observables con datos; los Given/When/Then van en la spec delta |
| No imposed technical solution | ✅ |

## 2. Coverage matrix per criterion

| AC | Coverage | Where (file:line / URL + date) | Missing |
|---|---|---|---|
| T-1 guardar y ver el trabajo en Datos básicos | ❌ New | La tarjeta existe (`frontend/src/routes/_layout/perfil.tsx:72-115`, `Row` en `:43`) y se edita en un diálogo (`frontend/src/components/Profile/EditBasicData.tsx:115`). El perfil guarda bloques 1:1 como JSON cifrado: `habits` (`backend/app/models.py:443`) con su ruta `PUT /profile/habits` (`backend/app/api/routes/profile.py:668`), que reemplaza el bloque entero, normaliza y valida | Columna `work`, esquema cerrado, `GET`/`PUT /profile/work`, la fila en la tarjeta y su edición |
| Situación laboral, una opción | ❌ New | Chips de una opción: `ChipGroup` (`frontend/src/components/Profile/ChipGroup.tsx:25`), estándar por D18. NIOSH pide la situación laboral en el expediente (`memory/research/ocupacion.md#ocupacion`, 2026-10-19) | El catálogo; ver pregunta 2 |
| A qué te dedicas / el de más años, texto libre | ❌ New | Texto libre opcional como `allergies` (`models.py:426`, límite 2000 en `PatientProfileUpdate`, `:1288`) | Dos campos con su límite |
| T-3 exposiciones con «Nada de esto» excluyente | 🟡 Partial | El patrón existe en humo ajeno: `SecondhandSmoke` (`models.py:897`), lugares múltiples + «No me expongo» (`profile.json:444`) con `ChipMultiGroup` (`ChipGroup.tsx:113`). D18 revisada: opciones múltiples sin datos propios van en chips | El esquema propio; ver pregunta 4 |
| Turno | ❌ New | [VERIFIED] La IARC clasificó el trabajo nocturno como «probablemente cancerígeno» (Grupo 2A), definido como trabajo durante las horas habituales de sueño (Monografías vol. 124, https://www.iarc.who.int/news-events/iarc-monographs-volume-124-night-shift-work, consultado 2026-10-29). Esto quita el `[ASSUMPTION]` que el dominio le puso al turno | Chips de una opción |
| T-2 todo opcional, vacío válido | ✅ Exists | El perfil parcial o vacío es válido (`openspec/specs/records/patient-profile/spec.md:8-25`) | Que el bloque nuevo lo cumpla |
| T-4 jubilado con el de más años | ❌ New | — | Depende de la pregunta 3 |
| T-5 cifrado, aislamiento, consentimiento | ✅ Exists | `EncryptedString` en las columnas del perfil (`models.py:415-447`), `ConsentedUser` en las rutas (`profile.py:660`), el perfil solo del paciente (`spec.md:112`) | Que la columna nueva use lo mismo |
| No califica (C-6) | ✅ Exists | `spec.md:496` prohíbe puntajes y veredictos para hábitos | Extenderlo en palabras al trabajo |

## 3. What looked useful and was discarded (and why)

- **Meter el trabajo en `PUT /profile` (`PatientProfileUpdate`, `models.py:1285`):** ese contrato es parcial
  («ausente = no tocar»). Con chips y una exclusión es más simple reemplazar el bloque entero, como hábitos.
- **Meterlo en el cuestionario de hábitos:** el dominio decidió el Perfil básico (ficha de identificación), y hábitos
  tiene reglas de obligatoriedad (C-15) que aquí no aplican: todo es opcional.
- **Codificar la ocupación con el catálogo de NIOSH (o un vocabulario como D21):** el dominio lo deja fuera, y D21 es
  para diagnósticos y medicinas.
- **El catálogo de situación laboral de NIOSH como fuente de las opciones:** no se pudo leer. La página de HL7 del
  value set dio 404 el 2026-10-29. Un resumen de búsqueda dice que solo tiene tres conceptos (empleado,
  desempleado, fuera de la fuerza laboral), demasiado gruesos para el paciente. [NOT VERIFIED]
- **INEGI (ENOE) para «No puedo trabajar»:** según un resumen de búsqueda, la población no económicamente activa se
  reparte en hogar, estudio, jubilados o pensionados y «tiene impedimentos personales». El PDF del boletín no se pudo
  extraer, así que queda como [NOT VERIFIED] (https://inegi.org.mx/contenidos/saladeprensa/boletines/2024/IOE/IOE2024_09.pdf,
  2026-10-29).
- **Sumar el trabajo al asistente de bienvenida:** FR-027 enumera sus campos y no lo incluye.

## 4. Non-functional constraints

- **NFR-001 / D13:** columna nueva con `EncryptedString`; migración de una columna que admite nulos, como la de
  hábitos (`backend/app/alembic/versions/7d3e9a1c5b42_perfil_habitos_patient_profile_habits.py`).
- **NFR-004:** detrás del consentimiento, como el resto del perfil.
- **NFR-008 / C-6:** sin «riesgo laboral» ni ninguna interpretación.
- **NFR-012 / D15:** textos en `profile.json`.
- **D18 / D20 / D22:** chips para las opciones; deshabilitados mientras guarda; la paleta nueva ya aplica.
- **Accesibilidad:** el grupo de chips con su nombre (`aria-labelledby`), como en hábitos.
- **Relación con C-7 (movimiento del día, PR #34):** ya pregunta «cómo pasas el día en tu trabajo o actividad
  principal», con el nivel «trabajo pesado o cargando cosas pesadas» (`models.py:967-973`). «Cargar peso» en las
  exposiciones repite esa idea; ver pregunta 4.

## 5. Classification and questions

**Extension** del perfil: el mismo patrón que hábitos (bloque 1:1 cifrado, reemplazo entero), con un esquema nuevo y
una fila en la tarjeta.

Saúl Pérez respondió las cuatro con AskUserQuestion el 2026-10-29 y eligió las recomendadas: diálogo propio, una
sola situación más «No puedo trabajar por mi salud», el detalle solo con «Trabajo» y sin «Cargar peso».

Preguntas, con la recomendación primero:
1. **Dónde se edita.** (a) Un diálogo propio, «Editar trabajo», desde la tarjeta Datos básicos, junto a «Editar datos
   básicos» y «Agregar medición». (b) Dentro del diálogo de datos básicos, que se alarga a ocho campos. (c) Una
   pantalla propia, como hábitos.
2. **Situación laboral.** (a) Una sola opción, sumando «No puedo trabajar por mi salud». (b) Las cinco del dominio,
   tal cual. (c) Varias a la vez (por ejemplo, trabajo y estudio).
3. **Qué se pregunta según la situación.** (a) A qué te dedicas, exposiciones y turno solo con «Trabajo»; el de más
   años siempre. (b) Todo siempre, como el prototipo.
4. **Exposiciones.** (a) Quitar «Cargar peso», que ya cubre el movimiento del día. (b) La lista del dominio, tal cual.

Supuestos (se aprueban con el plan): los textos de 200 caracteres como máximo; la fila de la tarjeta como en el
prototipo («ocupación · turno · antes: … · expuesto a …»); el subtítulo del prototipo («El médico lo pregunta porque lo
que haces todo el día también es salud») como descripción del diálogo, sin la mascota (D23 va después).

**Citadores que vencen:** `product/dominio.md` § Trabajo (el `[ASSUMPTION]` del turno, y lo que cambien las preguntas
2 y 4); el prototipo de producto `product/prototipos/perfil-secciones.html` (C-9, `:153`, `:274-297`); la spec canónica
vía la delta.

**Pistas para el plan:** el esquema se puede hacer con `_ClosedSchema` (`models.py:897`); la exclusión de «Nada de esto»
se normaliza en el servidor como `normalize_habits` (`models.py:1096`); la fila de la tarjeta, como `Row`
(`perfil.tsx:43`).
