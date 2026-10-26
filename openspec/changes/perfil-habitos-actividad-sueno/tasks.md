# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [x] 0.1 **Prototipo** `openspec/changes/perfil-habitos-actividad-sueno/prototipo.html`, local y navegable:
  - ejercicio con chips por actividad, "No hago ejercicio", días y minutos por actividad, "¿Cuál?" en "Otra" y el total
    "de lo anotado";
  - movimiento del día con los 4 niveles, el desplazamiento con sus días y las horas sentado;
  - sueño con las horas y las dos frecuencias;
  - "Guardar" marca lo que falta; los errores de escala al salir y que se van al corregir;
  - insignias C-5, C-7, C-8 (y C-6, C-15) que se prenden y apagan.

  El agente lo recorre primero en Chrome. Verificación: "plan approved" significa "navegué el prototipo y esto es lo
  que quiero".
- [ ] 0.2 **Base.** `make up` con la rama al día con `origin/main`; `openspec validate perfil-habitos-actividad-sueno
  --strict` limpio.

## 1. Backend: los tres bloques · test→impl

- [ ] 1.1 **Tester.** Amplía `backend/tests/api/routes/test_profile_habits.py` a partir de la parte pytest del test plan
  (filas 1–11) y del Interface contract. Verificación: rojo porque faltan los bloques y las reglas, no porque un test
  esté roto. Commit `test:` solo.
- [ ] 1.2 **Implementer.** Bloques, normalización y obligatoriedad en `backend/app/models.py` (incluido el `loc` de
  cuatro niveles). Verificación: los tests de 1.1 verdes sin tocarlos; mypy limpio.
- [ ] 1.3 **Orquestador.** Suite backend completa desde limpio (cero fallos, errores y skips; cobertura ≥ 90 %);
  regenerar el cliente (`scripts/generate-client.sh`); números en evidence.md; `make tdd-check`.

## 2. Frontend: los tres bloques en la pantalla · test→impl

- [ ] 2.1 **Tester.** Amplía `frontend/tests/profile-habits.spec.ts` a partir de la parte Playwright del test plan
  (filas 1–10, 12, 13) y del Interface contract. Verificación: rojo por lo que falta. Commit `test:` solo.
- [ ] 2.2 **Implementer.** `HabitsForm.tsx` y `profile.json`. Verificación: los tests de 2.1 verdes sin tocarlos
  (chromium y s26-ultra); `tsc` y `biome` limpios; `grep` sin límites literales en `HabitsForm.tsx`.
- [ ] 2.3 **Orquestador.** Rojo y verde de nuevo, `make tdd-check`, imagen reconstruida y suite completa como CI,
  números en evidence.md.

## 3. Verificación final y entrega · single

- [ ] 3.1 **Producto.** `product/dominio.md` § Hábitos y la pantalla de hábitos de
  `product/prototipos/perfil-secciones.html` (C-5, C-7, C-8 y su leyenda).
- [ ] 3.2 **Exploración en Chrome por el agente.** Cada bloque: elegir y quitar actividades, "No hago ejercicio",
  "Otra" sin nombre, total con valores a medias, desplazamiento *Sí*/*No*, sueño, valores fuera de escala y corregirlos,
  doble clic en "Guardar", salir con cambios, 384 y 580 px. Verificación: tabla en evidence.md.
- [ ] 3.3 **Entregables.** `evidence.md`, `validation.md` (no técnico, para Saúl Pérez), el journal y el PR.
- [ ] 3.4 **Revisión y archivo** (`/epe-4-review` → `/epe-5-apply` → `/epe-6-archive` como último commit del PR), con la
  regla de cierre de la Decision 7.
