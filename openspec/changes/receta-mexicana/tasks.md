# Tasks

Each group carries its Execution: `single` (one agent writes the red, commits it as `test:`, then the green) ·
`test→impl` (a `tester` agent writes the red from the scenarios and the interface contract, the orchestrator commits
it as `test:`, an `implementer` agent makes it green without touching tests) · `parallel` (only with the interface
contract filled and disjoint files). Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation
files is `test→impl`; smaller groups are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 1. Backend: modelo receta+medicinas, migración y API · test→impl

- [ ] 1.1 Test (red): escenarios de registro (varias medicinas, opcionales dx/frecuencia, rechazo sin medicinas,
      diagnóstico suelto, cifrado en reposo incl. medicinas, consentimiento), dueño (404 indistinguible incl.
      archivar ajeno, PATCH reemplaza medicinas y valida resultado, DELETE arrastra medicinas+adjuntos), archivar/
      desarchivar y `confirmation_status` — en `backend/tests/api/routes/test_health_records.py` según el
      Interface contract. Commit `test:`.
- [ ] 1.2 Impl: `HealthRecordMedicine` + cambios de `HealthRecord` y schemas (`models.py`), helper de validación
      por tipo actualizado, rutas (`health_records.py`: create/patch/list con medicines, archived), migración
      Alembic con fold de datos (Decisión 4). Verde sin tocar tests; `make tdd-check`.
- [ ] 1.3 Orquestador: re-correr rojo y verde, commits, `git status` tras cada gate (hooks auto-arreglan).

## 2. Frontend: captura manual según el prototipo, archivar y es-MX · test→impl

- [ ] 2.1 Test (red): Playwright `frontend/tests/health-records.spec.ts` — crear receta con 2 medicinas (una con
      frecuencia, otra sin), dx opcional, corregir medicinas, archivar → sección "Archivadas", desarchivar,
      diagnóstico suelto "sin confirmar", foto adjunta visible en la receta (AC-4). Commit `test:`.
- [ ] 2.2 Impl: regenerar SDK; `components/Records/*` (form con filas de medicinas + frecuencia opcional, campo
      diagnóstico opcional, acción archivar, lista activas/archivadas), `routes/_layout/expediente.tsx`,
      `locales/es-MX/records.json` (claves nuevas; dd/mm/aaaa vía split). Verde sin tocar tests.
- [ ] 2.3 Orquestador: rojo/verde re-corridos, `make tdd-check`, commits.

## 3. Cierre: evidencia, validación y PR · single

- [ ] 3.1 `evidence.md` (criterio → test → anchor → números reales, § Red before green por grupo) y
      `validation.md` no técnico para Saúl (un bloque por AC del prototipo, con "What it does NOT do yet":
      OCR/IA, dictado, confirmación por médico).
- [ ] 3.2 Journal + PR con template; cuerpo fiel al alcance.
