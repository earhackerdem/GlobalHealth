# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [x] 0.1 **Prototipo** `openspec/changes/perfil-habitos-completitud/prototipo.html`, local y navegable:
  - "Guardar" marca lo que falta;
  - "No recuerdo" donde lo dice la tabla del diseño;
  - el error que se va al corregirlo;
  - insignias C-15…C-17 que se prenden y apagan.

  El agente lo recorre primero en Chrome. Verificación: "plan approved" significa "navegué el prototipo y esto es lo
  que quiero".
- [x] 0.2 **Base.** `make up` con la rama al día con `origin/main`; `openspec validate perfil-habitos-completitud
  --strict` limpio.

## 1. Backend: "unknown" y obligatoriedad · test→impl

- [x] 1.1 **Tester.** Actualiza y amplía `backend/tests/api/routes/test_profile_habits.py` a partir de dos fuentes: la
  parte pytest del test plan (filas 1, 2, 4, 5, 7–10, 13) y el Interface contract. Completa las semillas y casos que
  hoy guardan a medias. Verificación: rojo porque faltan los tipos y las reglas, no porque un test esté roto. Commit
  `test:` solo.
- [x] 1.2 **Implementer.** Tipos y reglas en `backend/app/models.py`. Verificación: los tests de 1.1 verdes sin
  tocarlos; mypy limpio.
- [x] 1.3 **Orquestador.** Suite backend completa desde limpio (cero fallos, errores y skips; cobertura ≥ 90 %);
  regenerar el cliente (`scripts/generate-client.sh`); números en evidence.md; `make tdd-check`.

## 2. Frontend: "No recuerdo", obligatorias y el error que se va · test→impl

- [x] 2.1 **Tester.** Actualiza y amplía `frontend/tests/profile-habits.spec.ts` a partir de dos fuentes: la parte
  Playwright del test plan (filas 1–7, 10–12) y el Interface contract. Completa las semillas y recorridos que hoy
  guardan a medias. Verificación: rojo por lo que falta. Commit `test:` solo.
- [x] 2.2 **Implementer.** `HabitsForm.tsx` y `profile.json`. Verificación: los tests de 2.1 verdes sin tocarlos
  (chromium y s26-ultra); `tsc` y `biome` limpios; `grep` sin límites literales en `HabitsForm.tsx`.
- [x] 2.3 **Orquestador.** Rojo y verde de nuevo, `make tdd-check`, números en evidence.md.

## 3. Verificación final y entrega · single

- [x] 3.1 **Producto.** `product/dominio.md` § Hábitos y la pantalla de hábitos de
  `product/prototipos/perfil-secciones.html`.
- [x] 3.2 **Exploración en Chrome por el agente.** Guardar a medias, "No recuerdo" en cada bloque, escribir sobre
  "No recuerdo", corregir un error, lo guardado a medias, doble clic, 580 px. Verificación: tabla en evidence.md.
- [x] 3.3 **Entregables.** `evidence.md`, `validation.md` (no técnico, para Saúl Pérez), el journal y el PR.
- [x] 3.4 **Revisión y archivo** (`/epe-4-review` → `/epe-5-apply` → `/epe-6-archive` como último commit del PR).
