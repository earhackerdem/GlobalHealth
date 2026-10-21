# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [ ] 0.1 **Prototipo** `openspec/changes/perfil-habitos-ajustes/prototipo.html`, local y navegable:
  - la pantalla de hábitos con las preguntas nuevas, el estado del guardado y "Guardar"/"Cancelar" desactivados
    mientras guarda;
  - "Cancelar" que restaura;
  - insignias C-10…C-14 que se prenden y apagan.

  El agente lo recorre primero en Chrome (`file://`). Verificación: "plan approved" significa "navegué el prototipo y
  esto es lo que quiero".
- [ ] 0.2 **Base.** `make up` con la rama al día con `origin/main`; `openspec validate perfil-habitos-ajustes --strict`
  limpio.

## 1. Backend: alcohol, vapeador, leña y lo guardado antes · test→impl

- [ ] 1.1 **Tester.** Actualiza y amplía `backend/tests/api/routes/test_profile_habits.py` a partir de dos fuentes:
  la parte pytest del test plan (filas 2–5, 8, 9, 11, 13, 14, 15, 22) y el Interface contract. Ajusta los citadores
  (vapeador como texto, `years` de leña). Verificación: rojo porque faltan los campos, la conversión y las reglas, no
  porque un test esté roto. Commit `test:` solo.
- [ ] 1.2 **Implementer.**
  - Esquemas, normalización y `habits_errors` en `backend/app/models.py`;
  - `upgrade_stored_habits` y su uso en `_stored_habits` (`backend/app/api/routes/profile.py`).

  Verificación: los tests de 1.1 verdes sin tocarlos; mypy limpio.
- [ ] 1.3 **Orquestador.**
  - Suite backend completa desde limpio: cero fallos, errores y skips; cobertura ≥ 90 %.
  - Agrega el plugin `zod` a `frontend/openapi-ts.config.ts` y regenera el cliente (`scripts/generate-client.sh`).
  - Números en evidence.md § Grupo 1; `make tdd-check`.

## 2. Frontend: preguntas nuevas, guardado automático y validación al momento · test→impl

- [ ] 2.1 **Tester.** Actualiza y amplía `frontend/tests/profile-habits.spec.ts` a partir de dos fuentes: la parte
  Playwright del test plan (filas 1–4, 8, 9, 11, 12, 15–21) y el Interface contract. Ajusta los e2e de la C1 que tocan
  "Guardar" para el guardado automático. Verificación: rojo por las preguntas y el guardado que faltan. Commit `test:`
  solo.
- [ ] 2.2 **Implementer.** `HabitsForm.tsx` (preguntas nuevas, validación al salir de cada campo con `zod.gen.ts`,
  guardado automático, estado, "Guardar"/"Cancelar" con D20) y `profile.json`. Verificación: los tests de 2.1 verdes
  sin tocarlos (chromium y s26-ultra); `tsc` y `biome` limpios; `grep` sin límites literales en `HabitsForm.tsx`.
- [ ] 2.3 **Orquestador.** Corre de nuevo el rojo y el verde, `make tdd-check`, y anota los números en evidence.md
  § Grupo 2.

## 3. Verificación final, decisiones y entrega · single

- [ ] 3.1 **D20 y deudas.**
  - `memory/decisions/D20-…md`: botones que envían, desactivados mientras hay un envío.
  - Una fila en `memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`: revisar el doble
    clic en el resto de la app.
  - `product/dominio.md` § Hábitos: vapeador y leña.
- [ ] 3.2 **Exploración en Chrome por el agente.** Recorrer el cuestionario completo: guardado al elegir y al salir de
  campos, doble y triple clic en "Guardar" y "Cancelar", salir a media escritura por el menú, recargar, cambiar de
  cuenta en otra pestaña, 384 px. Verificación: tabla en evidence.md; los defectos dentro del plan se arreglan.
- [ ] 3.3 **Entregables.** `evidence.md`, `validation.md` (no técnico, para Saúl Pérez), el journal y el PR.
- [ ] 3.4 **Revisión y archivo** (`/epe-4-review` → `/epe-5-apply` → `/epe-6-archive` como último commit del PR):
  `openspec archive perfil-habitos-ajustes`, fragmento en `changelog.d/`, `.epe/active` a la carpeta archivada.
  Verificación: `openspec validate --specs` limpio.
