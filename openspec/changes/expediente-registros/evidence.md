# Evidence — expediente-registros

Criterio → test → ancla → estado. Suites corridas por el orquestador desde limpio; los números de cada rojo
provienen del re-run del orquestador, no del reporte del tester.

## Red before green

| Grupo | Commit `test:` | Rojo (re-run del orquestador) | Causa del rojo |
|---|---|---|---|
| 1 Backend registros | `cebb715` | 26 tests: **12 failed / 14 passed** | el stub exige `{"note"}` y responde 422 al payload discriminado; los 14 verdes son el gate de consentimiento ya existente y los 422 vacuamente verdes que atan el contrato |
| 2 Backend adjuntos | `15f1314` | 9 tests: **9 failed / 0 errors** | las rutas `/health-records/{id}/attachments*` no existen (404 de FastAPI) |
| 3 Frontend expediente | `a5ddac3` (+ `551f4f4` solo formato biome) | 6 tests: **6 failed / 0 errores de colección** | `/expediente` cae en la página 404 es-MX; login y consentimiento verificados funcionando |

## Green (verificación del orquestador, no delegada)

- Backend, suite completa desde limpio: `cd backend && uv run coverage run -m pytest -q tests/` →
  **126 passed / 0 failed / 0 errors / 0 skipped** · `coverage report` → **TOTAL 94%** (gate ≥90).
- Playwright, suite completa: `cd frontend && bunx playwright test --project=chromium` →
  **71 passed / 0 failed / 0 skipped** (6 nuevos de `health-records.spec.ts`; ninguno existente roto).
- `make tdd-check` → ✓ (commit `test:` más reciente `88722a4`, formato puro; rutas de tests intactas después).
  Los commits sobre tests posteriores a la medición del rojo (`2acd594`, `88722a4`) fueron formato puro
  (re-envoltura ruff), verificado: aserciones intactas.
- Lint/types: `bun run lint` (biome) limpio · `tsc --noEmit` limpio.

## Criterio → test

| Escenario del spec | Test | Estado |
|---|---|---|
| Registrar un diagnóstico | `test_ac1_register_diagnosis_returns_201_and_appears_in_list` + Playwright AC1 | ✅ |
| Registrar una receta con dosis y vigencia | `test_ac2_register_prescription_with_dose_and_validity` (+422 paramétricos) + Playwright AC2 | ✅ |
| Contenido clínico cifrado en reposo | `test_ac3_clinical_content_is_encrypted_at_rest` (SQL directo: `gAAAA`, sin "Hipotiroidismo"/"Levotiroxina" en claro) + `test_health_record_note_is_encrypted_at_rest` | ✅ |
| Sin consentimiento no entra ni un dato | probe migrado de `test_consent.py` + `test_ac4_without_consent_get_and_post_are_blocked_and_nothing_persists` | ✅ |
| Un registro ajeno no existe para mí | `test_ac5_foreign_record_is_indistinguishable_from_nonexistent` (GET/PATCH/DELETE, mismo 404) + 3 migrados de `test_account_isolation.py` | ✅ |
| Corregir y eliminar un registro propio | `test_ac6_patch_own_prescription_dose_is_reflected`, `test_ac6_delete_own_record_then_gone` + Playwright AC3/AC4; cascada de adjuntos en `test_ac5_deleting_record_cascades_over_attachment_rows` | ✅ |
| Adjuntar y descargar un resultado en PDF | `test_ac1_attach_pdf_...` (bytes idénticos + content-type) + Playwright AC5 (evento download) | ✅ |
| Tipo o tamaño fuera de contrato se rechaza | `test_ac2_renamed_exe_is_rejected_415...`, `test_ac2_file_over_10mb_is_rejected_413...`, `test_ac2_exactly_10mb_is_accepted` + Playwright AC6 (toast con el detail es-MX) | ✅ |
| Los adjuntos quedan cifrados en reposo | `test_ac3_attachment_is_encrypted_at_rest` (sin `%PDF` en claro, filename `gAAAA`) | ✅ |

## Guard de idioma (grep documentado)

Barrido sobre los archivos nuevos (`frontend/src/components/Records/`, `frontend/src/routes/_layout/expediente.tsx`):
solo identificadores no visibles (`"diagnosis"`, `"prescription"`, `"dose"`, query keys, nombres de namespace) —
dentro del carve-out del spec de localización. Cero strings visibles en inglés.

## Notas honestas

- La migración `f8b2d6c` elimina `healthrecordstub` con sus datos: eran andamiaje de desarrollo (design
  §Interface contract); las notas de prueba del dev se recrean como registros reales si hacen falta.
- Deuda anotada (fuera de alcance, también en D16): el cuerpo multipart se lee en memoria antes del 413 — un
  límite a nivel proxy/servidor protegería contra cuerpos arbitrariamente grandes.
- Deuda del template (preexistente, reportada por el implementer del grupo 1): `created_at`/`updated_at` sin
  `DateTime(timezone=True)` en el modelo (la migración sí lo fija), asimetría heredada de ConsentGrant.
- `scripts/generate-client.sh` reformatea todo el árbol del frontend como efecto colateral (`--write --unsafe`);
  sorprendió al implementer del grupo 3. Anotado para meta-mejora/inbox.
