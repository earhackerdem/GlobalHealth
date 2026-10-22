# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [x] 0.1 **Prototipo** `openspec/changes/perfil-habitos-ajustes/prototipo.html`, local y navegable:
  - la pantalla de hábitos con las preguntas nuevas, el estado del guardado y "Guardar"/"Cancelar" desactivados
    mientras guarda;
  - "Cancelar" que restaura;
  - insignias C-10…C-14 que se prenden y apagan.

  El agente lo recorre primero en Chrome (`file://`). Verificación: "plan approved" significa "navegué el prototipo y
  esto es lo que quiero".
- [x] 0.2 **Base.** `make up` con la rama al día con `origin/main`; `openspec validate perfil-habitos-ajustes --strict`
  limpio.

## 1. Backend: alcohol, vapeador, leña y lo guardado antes · test→impl

- [x] 1.1 **Tester.** Actualiza y amplía `backend/tests/api/routes/test_profile_habits.py` a partir de dos fuentes:
  la parte pytest del test plan (filas 2–5, 8, 9, 11, 13, 14, 15, 22) y el Interface contract. Ajusta los citadores
  (vapeador como texto, `years` de leña). Verificación: rojo porque faltan los campos, la conversión y las reglas, no
  porque un test esté roto. Commit `test:` solo.
- [x] 1.2 **Implementer.**
  - Esquemas, normalización y `habits_errors` en `backend/app/models.py`;
  - `upgrade_stored_habits` y su uso en `_stored_habits` (`backend/app/api/routes/profile.py`).

  Verificación: los tests de 1.1 verdes sin tocarlos; mypy limpio.
- [x] 1.3 **Orquestador.**
  - Suite backend completa desde limpio: cero fallos, errores y skips; cobertura ≥ 90 %.
  - Agrega el plugin `zod` a `frontend/openapi-ts.config.ts` y regenera el cliente (`scripts/generate-client.sh`).
  - Números en evidence.md § Grupo 1; `make tdd-check`.

## 2. Frontend: preguntas nuevas, guardado automático y validación al momento · test→impl

- [x] 2.1 **Tester.** Actualiza y amplía `frontend/tests/profile-habits.spec.ts` a partir de dos fuentes: la parte
  Playwright del test plan (filas 1–4, 8, 9, 11, 12, 15–21) y el Interface contract. Ajusta los e2e de la C1 que tocan
  "Guardar" para el guardado automático. Verificación: rojo por las preguntas y el guardado que faltan. Commit `test:`
  solo.
- [x] 2.2 **Implementer.** `HabitsForm.tsx` (preguntas nuevas, validación al salir de cada campo con `zod.gen.ts`,
  guardado automático, estado, "Guardar"/"Cancelar" con D20) y `profile.json`. Verificación: los tests de 2.1 verdes
  sin tocarlos (chromium y s26-ultra); `tsc` y `biome` limpios; `grep` sin límites literales en `HabitsForm.tsx`.
- [x] 2.3 **Orquestador.** Corre de nuevo el rojo y el verde, `make tdd-check`, y anota los números en evidence.md
  § Grupo 2.

## 3. Verificación final, decisiones y entrega · single

- [x] 3.1 **D20 y deudas.**
  - `memory/decisions/D20-…md`: botones que envían, desactivados mientras hay un envío.
  - Una fila en `memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`: revisar el doble
    clic en el resto de la app.
  - `product/dominio.md` § Hábitos: vapeador y leña.
- [x] 3.2 **Exploración en Chrome por el agente.** Recorrer el cuestionario completo: guardado al elegir y al salir de
  campos, doble y triple clic en "Guardar" y "Cancelar", salir a media escritura por el menú, recargar, cambiar de
  cuenta en otra pestaña, 384 px. Verificación: tabla en evidence.md; los defectos dentro del plan se arreglan.
  *Corrección (revisión ronda 1, D6): ese recorrido fue a 580 px y con cierre de sesión en otra pestaña, no con cambio
  de cuenta ni a 384 px; la 6.3 los cubre.*
- [x] 3.3 **Entregables.** `evidence.md`, `validation.md` (no técnico, para Saúl Pérez), el journal y el PR.
- [x] 3.4a **Revisión ronda 1** (`/epe-4-review`): 22 hallazgos confirmados (PR #32, comentarios finder y validator).
  Saúl Pérez decidió quitar el guardado automático (design.md Decision 8); los grupos 4–6 aplican la revisión.

## 4. Frontend: "Guardar" con aviso al salir, y los hallazgos A1 y A3 · test→impl

- [x] 4.1 **Tester.** Reescribe en `frontend/tests/profile-habits.spec.ts` las filas del guardado automático a partir
  de dos fuentes: las filas 16–24 del test plan y el Interface contract (Frontend). Ajusta las demás filas que dependían
  del guardado automático (esperar "Guardado", recargar sin "Guardar") para que guarden con "Guardar". Verificación:
  rojo porque faltan el texto, los avisos y `aria-disabled`, no porque un test esté roto. Commit `test:` solo.
- [x] 4.2 **Implementer.** `HabitsForm.tsx` sin guardado automático: "Guardar" por `useMutation`, "Cancelar" sin `PUT`,
  `aria-disabled` (D20), cambios sin guardar con `useBlocker` y `beforeunload`, la condición de la sesión, y los errores
  que se borran solo al ocultar su pregunta. Se borra `useAutosave.ts`; `profile.json` sin `habits.autosave.*` y con
  los textos nuevos. Verificación: los tests de 4.1 verdes sin tocarlos (chromium y s26-ultra); `tsc` y `biome`
  limpios; `grep` sin límites literales en `HabitsForm.tsx`.
- [x] 4.3 **Orquestador.** Rojo y verde de nuevo, `make tdd-check`, números en evidence.md § Grupo 4.

## 5. Backend: filas ilegibles (hallazgo B1) · single

- [x] 5.1 Rojo: en `backend/tests/api/routes/test_profile_habits.py`, JSON inválido, una lista y uno anidado 100 000
  niveles → GET 200 vacío con el aviso en el log (fila 14). Commit `test:`. Verde: `_stored_habits` lee con
  `pydantic_core.from_json`. Suite backend completa, cobertura ≥ 90 %, mypy.

## 6. Documentos, decisiones y verificación · single

- [x] 6.1 **D20 revisada** (`aria-disabled`, no `disabled`). **Documentos del cambio:** evidence (ancla de `tdd-check`,
  grupos 4 y 5), validation.md para el nuevo C-13, journal, design.md (ubicación de textos). **Investigación:**
  etiquetas de `memory/research/habitos.md` y `humo-lena.md` (hallazgos D4, D5). **Producto:** la pantalla de hábitos de
  `product/prototipos/perfil-secciones.html` (D3). Las afirmaciones de la exploración en Chrome (D6).
- [x] 6.2 **Cerrados:** `memory/closed/` con los hallazgos que dejó sin objeto la Decision 8 y el falso positivo D11.
- [x] 6.3 **Exploración en Chrome** otra vez, con los avisos de salida (menú, atrás, recargar, cerrar sesión en otra
  pestaña), el doble clic y 384 px. Suites completas (gate). Ronda 2 de la revisión sobre lo que cambió.
  *Corrección (ronda 2, R2-9): no cubre un cambio de cuenta (solo el cierre de sesión en otra pestaña), y la ventana de
  Chrome no bajó de 580 px; 384 px lo cubre s26-ultra.*

## 7. Ronda 2 de la revisión · test→impl

Aprobada por Saúl Pérez el 2026-10-21 ("procede con tu recomendación"): R2-1…R2-4, R2-7, el texto "Guardando…" (R2-5)
y los documentos (R2-6, R2-8, R2-9).

- [x] 7.1 **Tester.** Filas 21 (texto "Guardando…"), 26–29 del test plan en `frontend/tests/profile-habits.spec.ts`.
  Commit `test:` solo.
- [x] 7.2 **Implementer.** `HabitsForm.tsx`: efectos del guardado solo con la pantalla abierta y el mismo token (si no,
  invalidar), sin diálogo mientras guarda, preguntas bloqueadas mientras guarda, foco al título como respaldo,
  "Guardando…". Verificación: el archivo completo verde en chromium y s26-ultra; `tsc` y `biome`.
- [x] 7.3 **Orquestador.** Rojo y verde de nuevo, `make tdd-check`, documentos (R2-6, R2-8, R2-9), exploración en Chrome
  por el menú lateral, suite completa, ronda 3.

## 8. Ronda 3 de la revisión · test→impl

Aprobada por Saúl Pérez el 2026-10-21 ("procede con tu recomendación"): salir mientras guarda espera a que termine
(R3-1, R3-3), la fila 27 endurecida (R3-2), chips atenuados (R3-4) y el texto de la deuda.

- [x] 8.1 **Tester.** Filas 27, 28 y 30 del test plan. Commit `test:` solo.
- [x] 8.2 **Implementer.** `HabitsForm.tsx`: retener la salida mientras guarda (misma sesión), seguir al destino o
  cancelarla según el resultado; chips atenuados. Verificación: el archivo completo verde en chromium y s26-ultra.
- [x] 8.3 **Orquestador.** Rojo y verde, `make tdd-check`, evidencia, exploración en Chrome, suite completa, ronda 4.

## 9. Ronda 4 de la revisión · test→impl

Aprobada por Saúl Pérez el 2026-10-21 ("aprobado"): R4-1, R4-3, R4-6 y los documentos (R4-5, R4-7, R4-8); R4-2 y R4-4 a
deuda. Regla de cierre aprobada: si la ronda 5 trae solo hallazgos bajos, quedan como deuda registrada y se archiva.

- [ ] 9.1 **Tester.** Fila 31 del test plan. Commit `test:` solo.
- [ ] 9.2 **Implementer.** `HabitsForm.tsx`: resolver la salida retenida solo con el mismo token; foco al título si
  la salida se cancela y su elemento ya no existe.
- [ ] 9.3 **Orquestador.** Rojo y verde, `make tdd-check`, evidencia, suite completa, ronda 5.

- [ ] 3.4 **Archivo** (`/epe-6-archive` como último commit del PR, después de la ronda que salga seca):
  `openspec archive perfil-habitos-ajustes`, fragmento en `changelog.d/`, `.epe/active` a la carpeta archivada.
  Verificación: `openspec validate --specs` limpio.
