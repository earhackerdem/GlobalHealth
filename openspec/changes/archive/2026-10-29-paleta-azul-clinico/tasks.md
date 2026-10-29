# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [x] 0.1 **Prototipo** `product/prototipos/paleta.html` con insignias P-1 a P-5. Saúl Pérez eligió B y lo dejó en
  D22.
- [x] 0.2 **Base.** `openspec validate paleta-azul-clinico --strict` limpio; rama al día con `origin/main`;
  `make up`.

## 1. Paleta, casillas y jerarquía · test→impl

- [x] 1.1 **Tester.** `frontend/tests/visual-accessibility.spec.ts` con las filas 1 a 5 del test plan, escrito desde la
  spec delta y el Interface contract. Verificación: rojo porque faltan los tokens y el tamaño, no porque la prueba
  esté rota. Commit `test:` solo.
- [x] 1.2 **Implementer.** `index.css` (tabla de Tokens), `checkbox.tsx`, la variante `outline` de `button.tsx` y
  los dos `className` de `HabitsForm.tsx`. Verificación: las pruebas de 1.1 en verde sin tocarlas (chromium y
  s26-ultra); `tsc` y `biome` limpios.
- [x] 1.3 **Orquestador.**
  - rojo y verde de nuevo;
  - `make tdd-check`;
  - suite completa como CI;
  - commit `feat:`.

## 2. Cierre · single

- [x] 2.1 **Pase exploratorio en Chrome**, en claro y en oscuro: login, expediente, perfil, hábitos, antecedentes
  familiares y ajustes. Más la emulación de daltonismo (fila 6).
- [x] 2.2 **Entregables.** `evidence.md`, `validation.md` para Saúl Pérez y el journal. PR con la plantilla.
