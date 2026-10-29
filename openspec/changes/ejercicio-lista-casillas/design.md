# Design

Status: DRAFT

**En una frase:** en la pantalla de hábitos, el bloque Ejercicio cambia los chips por una lista con casillas siempre a
la vista (como los antecedentes familiares), con los días y minutos de cada actividad justo debajo de su casilla mientras
está marcada, sin tocar el servidor ni lo guardado.

## Context

- Hoy: `ChipMultiGroup` con las 9 actividades y «No hago ejercicio» excluyente (`HabitsForm.tsx:1781-1800`); los campos
  de cada actividad elegida salen después del grupo, en orden de catálogo (`:1802-1811`); el total es una región viva
  (`:1812-1814`).
- Precedente de la casilla que abre campos: `FamilyHistoryFields.tsx:65-84` (`Checkbox` de Radix + `Label`, campos en
  `ml-6` debajo).
- D18 revisada (2026-10-28): lista con casillas cuando cada opción abre sus propias preguntas; chips en lo demás.

## Goals / Non-Goals

- **Goals:** E-1 a E-4 de la spec delta; que C-5 y las reglas de guardado, errores, aviso de salida y D20 sigan igual.
- **Non-Goals:** backend, esquema, datos guardados; «¿Dónde?» del humo ajeno y cualquier otro chip; el resto del
  rediseño de UX (hilos 2 y 3).

## Qué se toca / qué NO

- **Se toca:**
  - `frontend/src/components/Profile/HabitsForm.tsx`: el bloque Ejercicio y, si hace falta, el selector del foco del
    error de grupo (`:1158-1166`).
  - Un componente nuevo `frontend/src/components/Profile/CheckList.tsx`, si el implementer lo prefiere a escribirlo
    dentro de `HabitsForm.tsx`.
  - `frontend/src/locales/es-MX/profile.json`: la «o».
  - `frontend/tests/profile-habits.spec.ts`: lo escribe el tester.
  - `product/prototipos/perfil-secciones.html`: la pantalla de hábitos.
  - Comentarios que citan D18 en `ChipGroup.tsx:105` y `HabitsForm.tsx:1580`, si dejan de ser ciertos.
- **NO se toca:**
  - el backend (`backend/`);
  - el cliente generado;
  - `ChipGroup.tsx`, salvo su comentario;
  - las demás pantallas;
  - `FamilyHistoryFields.tsx`, que solo se lee como precedente.

## Interface contract

Lo que las pruebas ejercitan (Playwright, por rol y nombre, como el resto de `profile-habits.spec.ts`):

- **Grupo:** `getByRole("group", { name: "¿Qué ejercicio haces?" })`, un `fieldset` con `legend`. Con el error de
  grupo, el fieldset lleva `data-invalid` y `aria-describedby` apunta al mensaje «Elige al menos una actividad, o «No
  hago ejercicio»».
- **Casillas:** dentro del grupo, `getByRole("checkbox", { name })` con nombre exacto. Son las nueve actividades en
  orden de catálogo y después «No hago ejercicio». El estado se lee con `toBeChecked()`, que en Radix corresponde a
  `aria-checked`.
- **Separador:** el texto «o» aparece entre «Otra» y «No hago ejercicio».
- **Campos de una actividad:** los mismos nombres accesibles que hoy usan `activityDays` y `activityMinutes`, por
  ejemplo «Días por semana» de caminar mediante `habits.activityField`, y el de «¿Cuál?» de «Otra». En el orden del
  documento quedan después de la casilla de su actividad y antes de la casilla siguiente. Se comprueba con la ayuda
  `expectBefore` que ya existe.
- **Lo que no cambia:** el total (`role="status"`, «Total de lo anotado: N minutos por semana»), los mensajes de error,
  «Guardar» y el `PUT /api/v1/profile/habits`. El cuerpo del `PUT` es idéntico al de hoy para las mismas respuestas.
- **Teclado:** Espacio sobre una casilla la marca y el foco se queda en ella. Tab desde una casilla marcada va al
  primer campo de su actividad: «¿Cuál?» en «Otra», «Días por semana» en las demás.

## Decisions

1. **Componente:** `Checkbox` de Radix con su `Label`, como en antecedentes familiares. Se descartaron
   `<input type="checkbox">` nativo, porque sería otro estilo de casilla en la app, y cambiar `ChipMultiGroup`,
   porque «¿Dónde?» lo sigue usando.
2. **Exclusión:** la misma regla que `ChipMultiGroup`. «No hago ejercicio» vacía las actividades; marcar una actividad
   apaga «No hago ejercicio». El borrador guarda `activities` con la misma forma que hoy (`["none"]` o la lista), así
   que la normalización, la obligatoriedad y el cuerpo del `PUT` no cambian.
3. **Valores al desmarcar:** igual que hoy al quitar un chip. `choose` (`HabitsForm.tsx:1195`) solo cambia
   `activities`, así que los días y minutos escritos se quedan ocultos en el borrador. Si la actividad se vuelve a
   marcar en la misma visita, reaparecen. Mientras está desmarcada no cuentan en el total ni van en el `PUT`
   (`:497`, `:631`).
4. **Citadores:** el comentario de `ChipGroup.tsx:105` («chips for every option, multiple choice included») se ajusta
   a D18 revisada. Los journals antiguos que citan D18 son historia y no se tocan.

## Test plan (one row per scenario, mandatory)

| # | Scenario | Test | Level |
|---|---|---|---|
| 1 | E-1 La lista de actividades siempre a la vista | `profile-habits.spec.ts`: 9 casillas en orden + «o» + «No hago ejercicio», ninguna marcada, ningún campo de días/minutos | e2e (chromium, s26-ultra) |
| 2 | E-2 Marcar abre sus preguntas debajo y desmarcar las quita | marcar Correr, Caminar, Otra → campos entre su casilla y la siguiente («¿Cuál?» primero en Otra); desmarcar Correr con 3×40 → campos fuera, total sin ellos, PUT sin `running` | e2e |
| 3 | E-3 «No hago ejercicio» excluye | Caminar 5×30 → marcar «No hago ejercicio» → Caminar sin marcar, sin campos ni total; marcar Bicicleta → «No hago ejercicio» sin marcar | e2e |
| 4 | E-4 Teclado, lector, foco del error | foco en «Caminar», Espacio → marcada y con foco; Tab → «Días por semana» de caminar; Guardar sin nada → mensaje y foco en «Caminar»; rol y nombre de grupo y casilla | e2e |
| 5 | C-5 Dos actividades con su total | prueba existente (fila 1 de la C2a), ahora con casillas | e2e |
| 6 | C-5 Otra actividad con su nombre | prueba existente, con casillas | e2e |
| 7 | C-5/C-15 Falta un dato de una actividad | prueba existente, con casillas | e2e |
| 8 | C-5 No hago ejercicio | prueba existente, con casillas | e2e |
| 9 | Resto del requisito (movimiento, sueño, fuera de escala, solo el sueño) | pruebas existentes, sin cambios; deben seguir verdes | e2e + pytest sin cambios |

## Non-functional constraints addressed

- Accesibilidad: grupo con nombre, casillas con nombre, error unido al grupo y foco en la primera casilla (fila 4).
- Celular: s26-ultra en cada fila; la lista no desborda a 400 px (prototipo, `memory/research/formularios-ux.md`).
- Sin cambios de privacidad ni de servidor (fila 9: suite backend sin cambios).

## Risks / Trade-offs

- **Pruebas actuales del ejercicio con chips** (unas 38 menciones): el tester las pasa a casillas. Riesgo: que pierdan
  fuerza al reescribirse. Mitigación: el validador de la revisión compara las aserciones antes y después.
- **Foco del error de grupo:** el selector `fieldset[data-invalid] button` encuentra la casilla de Radix porque es un
  `button`. Si el implementer usa otro elemento, la fila 4 lo detecta.
- **El lector de pantalla no anuncia los campos que aparecen:** riesgo aceptado (GOV.UK) porque los campos quedan
  justo después de la casilla.

## Gate that closes the work

Filas 1 a 9 en verde de verdad (chromium y s26-ultra), `make tdd-check`, `tsc` y `biome` limpios, la suite completa
como en CI, y el pase exploratorio del agente en Chrome si la extensión está conectada (si no, headless y declarado).
Después, `validation.md` para Saúl Pérez y el PR, que mergea él.
