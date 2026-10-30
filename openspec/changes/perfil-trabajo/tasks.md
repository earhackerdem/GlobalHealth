# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [x] 0.1 **Prototipo** `openspec/changes/perfil-trabajo/prototipo.html`, local y navegable, con la paleta D22:
  - la tarjeta Datos básicos con la fila «Trabajo» y el botón «Editar trabajo»;
  - el diálogo con la situación, el trabajo de más años y, solo con «Trabajo», a qué te dedicas, exposiciones con «Nada
    de esto» excluyente y turno;
  - el resumen en la tarjeta al guardar;
  - insignias T-1…T-6 que se prenden y apagan.

  El agente lo recorre primero en Chrome. Verificación: "plan approved" significa "navegué el prototipo y esto es lo
  que quiero".
- [x] 0.2 **Base.** `make up` con la rama al día con `origin/main`; `openspec validate perfil-trabajo --strict` limpio.

## 1. Backend: el bloque Trabajo · test→impl

- [x] 1.1 **Tester.** `backend/tests/api/routes/test_profile_work.py` a partir de la parte pytest del test plan (filas
  1–8) y del Interface contract. Verificación: rojo porque falta la ruta y el esquema, no porque un test esté roto.
  Commit `test:` solo.
- [x] 1.2 **Implementer.** Columna, esquema `Work`, `normalize_work` y migración en `backend/app/`, y las dos rutas en
  `routes/profile.py`. Verificación: los tests de 1.1 verdes sin tocarlos; mypy limpio; la migración sube y baja.
- [x] 1.3 **Orquestador.** Suite backend completa desde limpio (cero fallos, errores y skips; cobertura ≥ 90 %);
  regenerar el cliente (`scripts/generate-client.sh`); números en evidence.md; `make tdd-check`.

## 2. Frontend: diálogo y tarjeta · test→impl

- [x] 2.1 **Tester.** `frontend/tests/profile-work.spec.ts` a partir de la parte Playwright del test plan (filas 1–6 y
  8) y del Interface contract. El orquestador suma `profile-work` al `testMatch` de `s26-ultra`
  (`frontend/playwright.config.ts:54`) en el mismo commit `test:`, y lo declara como asimetría en evidence.md.
  Verificación: rojo por lo que falta. Commit `test:` solo.
- [x] 2.2 **Implementer.** `EditWork.tsx`, la fila y el botón en `perfil.tsx`, la query en `queries.ts` y los textos
  en `profile.json`. Verificación: los tests de 2.1 verdes sin tocarlos (chromium y s26-ultra); `tsc` y `biome`
  limpios.
- [ ] 2.3 **Orquestador.** Rojo y verde de nuevo, `make tdd-check`, imagen reconstruida y suite completa como CI,
  números en evidence.md.

## 3. Verificación final y entrega · single

- [x] 3.1 **Producto y memoria.** `product/dominio.md` § Trabajo, la pantalla de trabajo de
  `product/prototipos/perfil-secciones.html` (C-9) y el dato de la IARC en `memory/research/ocupacion.md`.
- [ ] 3.2 **Exploración en Chrome por el agente.** Cada situación, «Nada de esto» contra cada exposición, cambiar de
  «Trabajo» a otra y volver, textos con espacios y de 200, emoji, doble clic en «Guardar», cerrar sin guardar, claro y
  oscuro, 384 px. Verificación: tabla en evidence.md.
- [ ] 3.3 **Entregables.** `evidence.md`, `validation.md` (no técnico, para Saúl Pérez), el journal y el PR.
- [ ] 3.4 **Revisión y archivo** (`/epe-4-review` → `/epe-5-apply` → `/epe-6-archive` como último commit del PR), con la
  regla de la Decision 7, o archivo sin revisión si Saúl Pérez lo elige.
