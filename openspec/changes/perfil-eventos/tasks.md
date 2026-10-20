# Tasks

Each group carries its Execution: `single` (one agent writes the red, commits it as `test:`, then the green) ·
`test→impl` (a `tester` agent writes the red from the scenarios and the interface contract, the orchestrator commits
it as `test:`, an `implementer` agent makes it green without touching tests) · `parallel` (only with the interface
contract filled and disjoint files). Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation
files is `test→impl`; smaller groups are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 0. Base · single

- [ ] 0.1 Con #17, #18 y #19 mergeados: `git rebase origin/main` de `feat/perfil-eventos` (los commits del
      discovery ya están en `main` y se descartan solos), `openspec validate perfil-eventos --strict` limpio contra
      la spec base ya archivada, y `make up` (migra con el fix de #19). Verificación: rama sin commits ajenos al
      cambio y validate limpio.

## 1. Backend: registros, "ninguna", "cuándo" y grupo sanguíneo · test→impl

- [ ] 1.0 Orquestador (single, solo test): `backend/tests/api/routes/test_profile.py:251` compara
      `measured_on` con `date.today()` del runner (UTC), pero el servidor fecha en America/Mexico_City
      (`backend/app/api/routes/profile.py:204`): el test falla cada día entre 00:00 y 06:00 UTC (visto en el CI
      del PR #17, 2026-10-20 00:11 UTC: `'2026-10-19' == '2026-10-20'`). Calcular `today` con la misma zona.
      Reabre con evidencia la fila diferida de `memory/closed.md` 2026-10-19 ("flake de medianoche… ventana de
      ms"): la ventana es de 6 h diarias en CI. Verificación: el test pasa con el reloj del proceso en UTC
      00:30 (`faketime` o monkeypatch) y en hora normal; commit `test:`.
- [ ] 1.1 Tester: `backend/tests/api/routes/test_profile_history.py` desde los escenarios 3, 4, 5, 8, 9, 10, 11, 15,
      16, 17, 18, 19, 20, 21, 22 y 23 (parte pytest del test plan) y el Interface contract del design: round-trip
      por sección, requeridos y vacío con el `detail` es-MX exacto, imposibles de `when` con y sin fecha de
      nacimiento, 409 de "ninguna", la marca que se quita al crear, `blood_type` válido/nulo/inválido, 404
      idéntico ajeno/inexistente, ciphertext por SQL crudo y humo sin consentimiento. Verificación: suite roja por
      comportamiento ausente (404/422 de rutas o columnas inexistentes), no por tests rotos; commit `test:` solo.
- [ ] 1.2 Implementer: tabla `medical_history_entry` y columnas `blood_type`/`sections_none` en
      `backend/app/models.py` (EncryptedString, esquemas pydantic por sección como unión discriminada, `When`),
      migración Alembic solo aditiva, rutas en `backend/app/api/routes/profile.py` detrás de `ConsentedUser`.
      Verificación: los tests de 1.1 verdes sin tocarlos + mypy limpio.
- [ ] 1.3 Orquestador: `make migrate`, suite backend completa desde limpio (cero fallos/errores/skips, cobertura
      ≥ 90 %), números a evidence.md § Grupo 1, `make tdd-check`.

## 2. Frontend: tarjetas con estado, pantalla por sección y "cuándo" · test→impl

- [ ] 2.1 Tester: `frontend/tests/profile-history.spec.ts` desde los escenarios 1, 2, 3, 5, 6, 7, 9, 10, 11, 12, 13,
      14, 16, 18, 19 y 20 (parte Playwright), con los textos es-MX y los `data-testid` del contract; y el citer
      `frontend/tests/profile.spec.ts:14,52,280-300` reescrito: crónicas y hábitos siguen sin captura ni enlace y
      con "Sin llenar"; las 4 de eventos ya no se asiertan ahí. Verificación: suite roja contra la app actual;
      commit `test:` solo.
- [ ] 2.2 Implementer: cliente regenerado (`scripts/generate-client.sh`, ya sin lint), tarjetas con estado y
      enlace en `perfil.tsx`, ruta `routes/_layout/perfil_.$seccion.tsx`, componentes `HistorySection`,
      `HistoryEntryForm`, `WhenField`, `BloodTypePicker` en `components/Profile/`, textos en
      `locales/es-MX/profile.json` (incluye `pending.description` y "Sin llenar"). Verificación: los tests de 2.1
      verdes sin tocarlos + `tsc --noEmit` + lint.
- [ ] 2.3 Orquestador: `profile-history.spec.ts` al `testMatch` de s26-ultra (`frontend/playwright.config.ts:54`) y
      TODA la suite Playwright como CI (ambos proyectos) desde limpio; números a evidence.md § Grupo 2;
      `make tdd-check`.

## 3. Verificación final y entrega · single

- [ ] 3.1 Exploración real con Claude in Chrome sobre la app corriendo: las 4 secciones (llenar, editar, eliminar
      y cancelar, "ninguna" y deshacer, edad/etapa/año, grupo sanguíneo), datos raros (edad 0, año del
      nacimiento, textos largos), cambio de pestaña, doble submit y 384 px; hallazgos a evidence.md.
- [ ] 3.2 evidence.md (escenario → test → ancla → estado, rojo antes del verde por grupo) y validation.md no técnico
      para Saúl Pérez: guion por sección y "Qué NO hace todavía" (crónicas y hábitos: Stories B y C).
- [ ] 3.3 Inventario de citers del design (ninguno mintiendo), journal del cambio,
      `openspec validate perfil-eventos --strict` y PR con `gh pr create` sobre `feat/perfil-eventos`.
      Verificación: gates del push verdes y PR abierto.
