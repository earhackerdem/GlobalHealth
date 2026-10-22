# Exploration — perfil-habitos-completitud

Fecha: 2026-10-22 · Entrada: `proposal.md` (C-15…C-17), con el feedback de Saúl Pérez al validar perfil-habitos-ajustes
y su decisión del mismo día: obligatorias, con "No recuerdo".

## 1. Input validation

| Check | Result |
|---|---|
| As/I want/so that story with a concrete role | ✅ "Como paciente, quiero que la app me pida completar lo que mi respuesta implica…" |
| Every AC in Given/When/Then with concrete data | 🟡 C-15…C-17 son observables y llevan sus textos literales; los Given/When/Then con datos van en la spec delta |
| No imposed technical solution | ✅ |

## 2. Coverage matrix per criterion

| AC | Coverage | Where (file:line / URL + date) | Missing |
|---|---|---|---|
| C-15 lo que abre una respuesta es obligatorio | ❌ New (contradice la spec vigente) | La spec dice "cada respuesta es opcional y se guarda lo que haya contestado" (`openspec/specs/records/patient-profile/spec.md:341-342`); la pantalla, "Contesta solo lo que quieras" (`frontend/src/locales/es-MX/profile.json:338`). Todos los campos de hábitos son `| None` (`backend/app/models.py:858-911`). La normalización ya sabe qué aplica a cada respuesta (`models.py:937-1004`) y `habits_errors` ya devuelve errores por `loc` (`models.py:1006`) | Reglas de obligatoriedad después de normalizar, en `habits_errors` (servidor) y en la validación del cliente al tocar "Guardar" |
| C-16 "No recuerdo" en lo que pasó | ❌ New | Ningún campo distingue "no recuerda" de "sin respuesta". Investigación (`memory/research/habitos.md#no-recuerdo`, 2026-10-22): las encuestas lo guardan aparte (NHIS 99, NSDUH 994), FHIR tiene `asked-unknown`; el AUDIT no tiene "no sé"; ofrecerlo en todo invita a contestar sin pensar (Krosnick 2002) | `"unknown"` como valor propio en las edades y en las cantidades de "Antes"; reglas de comparación que lo ignoran |
| C-17 el error se va al corregirlo | 🟡 Partial | El número se revisa solo al salir del campo (`onBlur={() => leave(key)}`); `onChange` actualiza el borrador sin revisar el error (`frontend/src/components/Profile/HabitsForm.tsx:927-931`) | Con un error ya marcado, revisar ese campo en cada cambio y quitar el error si el valor es válido (sin marcar errores nuevos mientras se escribe) |
| Lo guardado incompleto se sigue leyendo | ✅ Exists | El GET valida con el esquema (`profile.py` `_stored_habits`); un campo `None` sigue siendo válido | Nada en la lectura; el `PUT` siguiente pedirá lo que falta |

## 3. What looked useful and was discarded (and why)

- **Un número especial (99, 994) para "no sabe":** contamina promedios si alguien suma; las encuestas lo usan en
  columnas que se analizan con su libro de códigos, no aquí.
- **`null` para "No recuerdo":** se confundiría con "sin respuesta" de lo guardado antes de este cambio.
- **Un booleano aparte por campo (`start_age_unknown`):** dobla los campos y permite estados contradictorios (número y
  "no recuerda" a la vez).
- **"No recuerdo" en las preguntas de frecuencia del alcohol:** el instrumento de la OMS no lo tiene y su puntuación
  necesita las tres respuestas.
- **"Mejor estimación" por rangos tras "No recuerdo" (como NCHS RSS-8):** útil, pero agrega una pregunta más por campo;
  queda fuera.
- **"Prefiero no responder" (`asked-declined`):** las encuestas lo separan; Saúl Pérez no lo pidió. Fuera.

## 4. Non-functional constraints

- **NFR-001 / D13:** el mismo JSON cifrado; `"unknown"` no cambia el cifrado.
- **NFR-008 / C-6:** "No recuerdo" no se interpreta ni se calcula.
- **Accesibilidad:** cada "No recuerdo" con nombre accesible distinto (R7); errores junto a su campo (R5).
- **es-MX (D15):** textos nuevos en `profile.json`.
- **D18 / D20:** "No recuerdo" es un chip; no disponible mientras guarda.

## 5. Classification and questions

**Extension** de la C1 y de perfil-habitos-ajustes. Sin preguntas bloqueantes: la decisión de Saúl Pérez y la
investigación fijan el alcance. Supuestos (se aprueban con el prototipo): dónde va "No recuerdo" (C-16) y el texto de
la introducción.

**Citadores que vencen:** la spec canónica (vía la delta); los escenarios con respuestas a medias que ahora no se
podrían guardar (alcohol "Actual" sin edad de inicio, vapeador "Actual" sin edad, tabaco "Actual" sin edad); las
semillas de pytest y e2e con bloques incompletos (`SEED` y `seedHabits` en `backend/tests/api/routes/test_profile_habits.py`
y `frontend/tests/profile-habits.spec.ts`, se ubican con `grep -n "seedHabits\|status"`); `profile.json` § `habits.intro`.
