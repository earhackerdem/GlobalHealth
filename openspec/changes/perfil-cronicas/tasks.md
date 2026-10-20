# Tasks

Each group carries its Execution:
- **`single`:** one agent writes the red, commits it as `test:`, then the green.
- **`test→impl`:** a `tester` agent writes the red from the scenarios and the interface contract; the orchestrator
  commits it as `test:`; an `implementer` agent makes it green without touching tests.
- **`parallel`:** only with the interface contract filled and disjoint files.

Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation files is `test→impl`; smaller groups
are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Prototipo y base · single

- [ ] 0.1 **Prototipo.** `product/prototipos/perfil-secciones.html` gana:
  - la casilla "Sensible" (B-1b), con su valor por defecto según la condición;
  - "Consumo de alcohol u otras sustancias" en el grupo "Salud mental y adicciones";
  - el resumen "hasta los N años";
  - una vista del expediente con "Eliminar registro" sobre un diagnóstico que respalda una crónica (B-5);
  - insignias B-1b y B-5;
  - la historia B en la leyenda.

  Verificación: Saúl Pérez lo navega antes de "plan approved".
- [ ] 0.2 **Base.** Con #24 y #25 mergeados: `git rebase origin/main`, `openspec validate perfil-cronicas --strict`
  limpio y `make up`. Verificación: la rama solo tiene commits del cambio.

## 1. Backend: sección chronic, validación, enlace y desenlace · test→impl

- [ ] 1.1 **Tester.** Escribe `backend/tests/api/routes/test_profile_history.py` (crónicas) y
  `backend/tests/api/routes/test_health_records.py` (B-5) a partir de dos fuentes: la parte pytest del test plan
  (filas 1, 2, 3, 5, 6, 8, 9, 14, 15, 16 y 17) y el Interface contract.
  - Reescribe el citador `test_s19…` (`:559-565`) con `habits`.

  Verificación: la suite queda roja porque falta el comportamiento (422 por sección desconocida, `sensitive`
  ausente, enlace no limpiado), no porque un test esté roto. Commit `test:` solo.
- [ ] 1.2 **Implementer.**
  - `chronic` en `HistorySection` y en `HISTORY_SECTIONS` (primero), con su contenido, su requerido y el valor por
    defecto de `sensitive`;
  - la validación de `since`/`until` (rango de edad) y de `diagnosis_id` en `backend/app/models.py` y
    `backend/app/api/routes/profile.py`;
  - `crud.unlink_diagnosis`, llamado desde el DELETE de `backend/app/api/routes/health_records.py`.

  Verificación: los tests de 1.1 verdes sin tocarlos, y mypy limpio.
- [ ] 1.3 **Orquestador.**
  - Corre la suite backend completa desde limpio: cero fallos, errores y skips; cobertura ≥ 90 %.
  - Regenera el cliente (`scripts/generate-client.sh`).
  - Escribe los números en evidence.md § Grupo 1 y corre `make tdd-check`.

## 2. Frontend: tarjeta, formulario de crónica, marca sensible, selector y aviso de borrado · test→impl

- [ ] 2.1 **Tester.** Escribe `frontend/tests/profile-history.spec.ts` (crónicas) y
  `frontend/tests/health-records.spec.ts` (B-5) a partir de dos fuentes: la parte Playwright del test plan (filas 1,
  2, 3, 4, 5, 6, 7, 9, 10, 11, 12, 14 y 17) y el Interface contract.
  - Reescribe los citadores `profile.spec.ts:317-319` y `profile-history.spec.ts:262` para que solo hábitos quede
    sin enlace.

  Verificación: la suite queda roja por comportamiento ausente. Commit `test:` solo.
- [ ] 2.2 **Implementer.**
  - `history.ts` (sección, slug `cronicas`, resumen con "desde"/"hasta");
  - `HistoryEntryForm.tsx` (campos de crónica, casilla "Sensible" con su valor por defecto, dos `WhenField`, el
    selector de diagnóstico);
  - `HistorySection.tsx` (la etiqueta "sensible" y "Respaldo");
  - `perfil.tsx` (la tarjeta enlazada);
  - `DeleteRecord.tsx` (el aviso y la invalidación);
  - los textos es-MX.

  Verificación: los tests de 2.1 verdes sin tocarlos; tsc y biome limpios.
- [ ] 2.3 **Orquestador.** Corre la suite Playwright completa como en CI (chromium + s26-ultra), escribe los
  números en evidence.md y corre `make tdd-check`.

## 3. Verificación final, archivo y entrega · single

- [ ] 3.1 **Exploración en Chrome por el agente** (`epe-3-execute`, paso 2): flujo completo de crónicas, la marca
  sensible, "desde"/"hasta", el respaldo y el borrado del diagnóstico. También intenta romperla (doble envío,
  emoji, datos largos, ancho de 500 px). Verificación: tabla en evidence.md; si hay defectos, se arreglan o se
  escalan.
- [ ] 3.2 **Entregables.** `evidence.md`, `validation.md` (no técnico, para Saúl Pérez), el journal y el PR.
- [ ] 3.3 **Archivo como último commit del PR** (`epe-6-archive`, 0.3.2):
  - `openspec archive perfil-cronicas`;
  - CHANGELOG;
  - `product/dominio.md` y `product/prd.md`, con la Story B entregada;
  - `.epe/active` apuntando a la carpeta archivada.

  Verificación: `openspec validate --specs` limpio.
