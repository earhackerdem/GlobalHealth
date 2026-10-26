# Exploration — perfil-habitos-actividad-sueno

Fecha: 2026-10-26 · Entrada: `proposal.md` (C-5, C-7, C-8), con la partición de la C2 que decidió Saúl Pérez el mismo
día (C2a aquí; C2b "Trabajo" después) y sus cuatro respuestas a las preguntas de esta exploración (§ 5).

## 1. Input validation

| Check | Result |
|---|---|
| As/I want/so that story with a concrete role | ✅ "Como paciente, quiero contar mi ejercicio, cómo se mueve mi día y cómo duermo…" |
| Every AC in Given/When/Then with concrete data | ✅ C-5, C-7 y C-8 son observables; los Given/When/Then con datos van en la spec delta |
| No imposed technical solution | ✅ |

## 2. Coverage matrix per criterion

| AC | Coverage | Where (file:line / URL + date) | Missing |
|---|---|---|---|
| C-5 ejercicio como lista con total semanal | ❌ New | El cuestionario es un esquema cerrado que la C2 extiende a propósito (`backend/app/models.py:843`, `Habits` en `:923`). El patrón "elige uno o varios + sus preguntas" ya existe en humo ajeno: `SecondhandSmoke` (`models.py:896`) con `exposed` derivado de los chips en la pantalla (`HabitsForm.tsx:426`, `ChipMultiGroup` en `:1389`). Precedente de N actividades con su frecuencia: NHANES 2005-06 y BRFSS (`memory/research/habitos.md#actividad-sueno`, 2026-10-26); días 0–7 y minutos con tope (EVS, Coleman 2012) | Bloque `exercise` (respuesta "No hago ejercicio" o actividades con días y minutos), su total a la vista |
| C-7 movimiento del día, aparte | ❌ New | GPAQ (versión panamericana OPS/OMS): desplazamiento P7–P8 (sí/no + días) y tiempo sentado P16 sin contar el sueño; ítem de 4 niveles NHANES `PAQ180` para el día (`habitos.md#actividad-sueno`); la paradoja de la actividad física justifica no sumarlo (`memory/research/ocupacion.md#ocupacion`) | Bloque `daily_movement` |
| C-8 sueño | ❌ New | NHIS 2024 `SLPHOURS_A` (horas enteras 1–24 en 24 h), `SLPFLL_A` y `SLPSTY_A` (4 puntos, 30 días), con español oficial (`habitos.md#actividad-sueno`) | Bloque `sleep` |
| Obligatorias, sin "No recuerdo", errores al momento (C-15, C-16, C-14, C-17) | 🟡 Partial | Las reglas existen para la C1: `HABITS_REQUIRED` (`models.py:1021`) y su copia en la pantalla (`HabitsForm.tsx:393`); `habits_errors` (`models.py:1060`) devuelve `(bloque, campo, mensaje)` de un solo nivel | Filas nuevas en la tabla; un `loc` de cuatro niveles para los campos de cada actividad (`exercise.activities.<tipo>.<campo>`) |
| La app no interpreta (C-6) | 🟡 Partial | `openspec/specs/records/patient-profile/spec.md:496-501` prohíbe puntajes, índices y veredictos | Aclarar que el total semanal es una suma a la vista, sin compararlo con nada |
| Tarjeta "Con datos" | ✅ Exists | `hasHabits` cuenta cualquier bloque no nulo (`frontend/src/components/Profile/history.ts:298-301`) | Nada |
| Guardar, aviso de salida, D20, cifrado, aislamiento | ✅ Exists | Requisitos vigentes de la spec (`spec.md:509-576`, `:274-277`) | Que los bloques nuevos entren en los mismos caminos (lo hacen por ser el mismo JSON y el mismo formulario) |

## 3. What looked useful and was discarded (and why)

- **Lista de filas con "Agregar"/"Quitar" (como la receta, `frontend/src/components/Records/PrescriptionForm.tsx:115`):**
  permite repetir una actividad y obliga a manejar índices en errores y foco. Un chip por tipo de actividad (D18), como
  los lugares del humo ajeno, evita repetidos y da un `loc` estable por tipo.
- **Un diccionario de actividades con claves libres:** el cliente Zod generado con claves enumeradas es frágil; un
  objeto con una propiedad opcional por tipo (cerrado) se genera limpio.
- **Las escalas de insomnio validadas (Atenas, ISI, PROMIS, PSQI):** dan una puntuación que la app no calcula (C-6), y
  el PSQI no se puede modificar sin permiso.
- **Separar el sueño en días laborales y libres (MCTQ, NHANES 2017-18):** sirve para el desfase de horario, no para
  registrar el hábito.
- **Confirmaciones suaves (≤5 h de sueño, >240 min por vez, sentado + sueño > 24 h):** útiles, pero agregan un patrón
  nuevo de interfaz; fuera de este cambio.
- **Sumar el desplazamiento al total del ejercicio:** sin el tiempo (GPAQ P9) no se puede, y la paradoja de la
  actividad física desaconseja mezclarlo.

## 4. Non-functional constraints

- **NFR-001 / D13:** el mismo JSON cifrado; los bloques nuevos no cambian el cifrado.
- **NFR-008 / C-6:** sin puntajes ni veredictos; el total semanal no se compara con 150 minutos ni con la OMS.
- **Accesibilidad:** nombres accesibles distintos por actividad (R7: "Días por semana de caminar"), errores junto a su
  campo (R5), foco al primero.
- **es-MX (D15):** textos nuevos en `profile.json`; redacción a partir del español oficial de NHIS y GPAQ.
- **D18 / D20:** chips para las opciones; no disponibles mientras guarda.

## 5. Classification and questions

**Extension** de la C1 de hábitos. Las cuatro preguntas se respondieron con AskUserQuestion; Saúl Pérez eligió las
recomendadas (2026-10-26):
1. **Insomnio:** dos preguntas de NHIS, "nunca · algunos días · casi todos los días · todos los días", últimos 30 días.
2. **Tu día:** los 4 niveles de NHANES `PAQ180`, que también sirven para hogar, estudio o jubilación.
3. **Sin ejercicio:** chip "No hago ejercicio", explícito (como "Nunca" y "No me expongo").
4. **Horas de sueño:** en un día (24 horas), horas enteras de 1 a 24.

Supuestos (se aprueban con el prototipo): el catálogo de actividades del dominio (caminar, correr, bicicleta, nadar,
pesas o gimnasio, fútbol u otro deporte, yoga o pilates, baile, otra) con "¿Cuál?" para "Otra"; días por semana 1–7 y
minutos por vez 1–600 por actividad; el desplazamiento "de al menos 10 minutos seguidos" (GPAQ) con días 1–7; horas
sentado 0–24 sin contar el sueño; ninguna pregunta de estos bloques admite "No recuerdo".

**Citadores que vencen:** `product/dominio.md` § Hábitos (filas ejercicio, movimiento del día, sueño: la escala de 3
del sueño y del día, "horas por noche" y "sin actividades = no hago ejercicio" cambian); el prototipo de producto
`product/prototipos/perfil-secciones.html` (C-5, C-7, C-8 y su leyenda, `:134-137`, `:507-540`); la spec canónica vía la
delta. Faltaban en este inventario y se actualizaron en la ronda 1 de la revisión del PR #34 (2026-10-26):
`proposal.md` (C-5 "lista de actividades" y "ejercicio (lista)" → un chip por tipo de actividad, Decision 2 del diseño;
C-8 "horas por noche" y "se despierta en la noche" → horas en un día de 24 horas, enteras, y por separado le costó
dormirse y le costó seguir durmiendo o despertó demasiado temprano, últimos 30 días); `product/dominio.md` § Partición
("lista anidada" → un chip por actividad con sus días y minutos) y el encabezado de § Hábitos ("cada hábito tiene
'Nunca'", que ya no vale para el ejercicio, el movimiento del día ni el sueño).
