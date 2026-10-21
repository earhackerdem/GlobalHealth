# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [ ] 0.1 **Prototipo.** Ya cubre C-1…C-4 y C-6 (`product/prototipos/perfil-secciones.html`, `pintarHabitos`, v4),
  validado por Saúl Pérez en las rondas 6–8. No cambia. Verificación: "plan approved" significa "navegué el
  prototipo y esto es lo que quiero" para los bloques de la C1.
- [ ] 0.2 **Base.** `make up` con la rama al día con `origin/main`, y `openspec validate perfil-habitos --strict`
  limpio. `product/dominio.md` § Partición en stories registra la partición C1/C2.

## 1. Backend: hábitos, normalización, validación y cifrado · test→impl

- [ ] 1.1 **Tester.** Escribe `backend/tests/api/routes/test_profile_habits.py` a partir de dos fuentes: la parte
  pytest del test plan (filas 1–11 y 16) y el Interface contract. Verificación: la suite queda roja porque faltan
  las rutas (404), no porque un test esté roto. Commit `test:` solo.
- [ ] 1.2 **Implementer.**
  - Esquemas `Habits`, `AlcoholHabit`, `TobaccoHabit`, `SecondhandSmoke`, `WoodSmokeHabit` y su normalización en
    `backend/app/models.py`;
  - la columna `patient_profile.habits` y su migración Alembic;
  - `GET`/`PUT /profile/habits` en `backend/app/api/routes/profile.py`, con la validación de edades y los 422 con
    `loc`.

  Verificación: los tests de 1.1 verdes sin tocarlos, y mypy limpio.
- [ ] 1.3 **Orquestador.**
  - Corre la suite backend completa desde limpio: cero fallos, errores y skips; cobertura ≥ 90 %.
  - Regenera el cliente (`scripts/generate-client.sh`).
  - Escribe los números en evidence.md § Grupo 1 y corre `make tdd-check`.

## 2. Frontend: tarjeta, pantalla de hábitos y chips múltiples · test→impl

- [ ] 2.1 **Tester.** Escribe `frontend/tests/profile-habits.spec.ts` a partir de dos fuentes: la parte Playwright
  del test plan (filas 1–9, 11–14) y el Interface contract. Reescribe los citadores que afirman que hábitos no
  tiene enlace (`grep -n habits frontend/tests/*.spec.ts`). Verificación: la suite queda roja por comportamiento
  ausente. Commit `test:` solo.
- [ ] 2.2 **Implementer.**
  - `ChipMultiGroup` en `ChipGroup.tsx`;
  - `HabitsForm.tsx` y la ruta `perfil_.habitos.tsx`, con la validación en el cliente y los 422 ubicados por `loc`;
  - la tarjeta enlazada con "Sin llenar" / "Con datos" en `perfil.tsx`, y `queries.ts`;
  - los textos es-MX y los comentarios citadores (`perfil.tsx`, `history.ts`, `profile.json:79`).

  Verificación: los tests de 2.1 verdes sin tocarlos; tsc y biome limpios.
- [ ] 2.3 **Orquestador.** Corre la suite Playwright completa como en CI (chromium + s26-ultra), escribe los
  números en evidence.md y corre `make tdd-check`.

## 3. Verificación final, archivo y entrega · single

- [ ] 3.1 **Exploración en Chrome por el agente** (`epe-3-execute`, paso 2): el cuestionario completo, cambiar de
  respuesta y ver qué se descarta, edades imposibles, "No me expongo", reabrir. También intenta romperla (doble
  envío, números raros, ancho de 384 px, volver atrás sin guardar). Verificación: tabla en evidence.md; si hay
  defectos, se arreglan o se escalan.
- [ ] 3.2 **Entregables.** `evidence.md`, `validation.md` (no técnico, para Saúl Pérez), el journal y el PR.
- [ ] 3.3 **Archivo como último commit del PR** (`epe-6-archive`):
  - `openspec archive perfil-habitos`;
  - el fragmento en `changelog.d/` (sin generar `CHANGELOG.md`);
  - `product/dominio.md` y `product/prd.md`, con la Story C1 entregada;
  - `.epe/active` apuntando a la carpeta archivada.

  Verificación: `openspec validate --specs` limpio.
