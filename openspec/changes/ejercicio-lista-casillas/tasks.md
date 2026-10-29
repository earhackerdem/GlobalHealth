# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [x] 0.1 **Prototipo** `product/prototipos/ejercicio-variantes.html`, variante E, con insignias E-1 a E-4. Saúl Pérez
  la eligió («ok procede con la E»).
- [ ] 0.2 **Base.** `openspec validate ejercicio-lista-casillas --strict` limpio; rama al día con `origin/main`;
  `make up`.

## 1. Frontend: la lista con casillas · test→impl

- [ ] 1.1 **Tester.** En `frontend/tests/profile-habits.spec.ts`:
  - pruebas nuevas de las filas 1 a 4 del test plan;
  - las pruebas del ejercicio que eligen con chips pasan a casillas (filas 5 a 8), sin quitarles aserciones.

  Verificación: rojo porque faltan las casillas, no porque una prueba esté rota. Commit `test:` solo.
- [ ] 1.2 **Implementer.** `HabitsForm.tsx` (y `CheckList.tsx` si conviene), `profile.json`, el comentario de
  `ChipGroup.tsx:105`. Verificación: las pruebas de 1.1 en verde sin tocarlas (chromium y s26-ultra); `tsc` y `biome`
  limpios.
- [ ] 1.3 **Orquestador.**
  - rojo y verde de nuevo;
  - `make tdd-check`;
  - imagen reconstruida;
  - suites de perfil y suite completa como en CI;
  - suite backend sin cambios;
  - números en `evidence.md`.

## 2. Verificación final y entrega · single

- [ ] 2.1 **Producto.** La pantalla de hábitos de `product/prototipos/perfil-secciones.html` pasa a la lista con
  casillas (C-5 y su leyenda).
- [ ] 2.2 **Pase exploratorio del agente.**
  - marcar y desmarcar;
  - «No hago ejercicio» en los dos sentidos;
  - «Otra» sin nombre;
  - Guardar sin nada;
  - teclado;
  - 9 actividades a 384 px;
  - salir con cambios.

  Se hace en Chrome; si la extensión no conecta, en headless y se declara. Verificación: tabla en `evidence.md`.
- [ ] 2.3 **Entregables.** `evidence.md`, `validation.md` (no técnico, para Saúl Pérez), el journal y el PR.
- [ ] 2.4 **Revisión y archivo** (`/epe-4-review` → `/epe-5-apply` → `/epe-6-archive` como último commit del PR).
