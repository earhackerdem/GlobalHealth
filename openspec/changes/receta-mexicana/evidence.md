# Evidence — receta-mexicana

Fecha: 2026-10-18 · Rama: `feat/receta-mexicana` · Ejecutores: tester/implementer (subagentes) + orquestador
(re-corrió rojo y verde y commiteó).

## Red before green

- Grupo 1 (backend): `cd backend && uv run pytest -q tests/api/routes/test_health_records.py` →
  **15 collected · 12 failed · 3 passed** (conservados: consentimiento, corregir/eliminar diagnóstico propio,
  orden DESC). Commit `test:` 4fbbabf.
- Grupo 2 (e2e): `cd frontend && bunx playwright test tests/health-records.spec.ts --reporter=line` →
  **10 collected · 9 failed · 1 passed** (solo el setup de autenticación). Commit `test:` 4f0605f.

## Verde (re-corrido por el orquestador desde limpio)

- Backend suite completa: `uv run pytest -q tests/` → **137 passed, 0 failed, 0 errors, 0 skipped** (11.75 s).
- E2E: `bunx playwright test tests/health-records.spec.ts` → **10 passed (9.0 s)**.
- `uv run mypy app` → Success (24 archivos). `bunx tsc --noEmit` → limpio. `make tdd-check` → ✓ un commit
  `test:` por grupo, tests intactos desde cada rojo.
- Migración contra datos reales de dev: `alembic upgrade head` (0b7c5e1d94aa → c91f3b7a52e8) — 18 recetas
  generaron 18 medicinas (recifradas, descifrables), vigencias preservadas en notas ("Vigencia migrada: …"),
  25 diagnósticos recibieron `confirmation_status='unconfirmed'`, columnas `dose/valid_from/valid_to` eliminadas.

## Criterio → test → anchor → estado

| Escenario (spec delta) | Test | Anchor | Estado |
|---|---|---|---|
| Registrar receta con varias medicinas (AC-1) | `test_create_prescription_with_medicines` | backend/tests/api/routes/test_health_records.py | ✅ |
| Dx y frecuencia opcionales (AC-3/AC-9) | `test_prescription_optional_diagnosis_and_frequency` | ídem | ✅ |
| Receta sin medicinas → 422 (AC-1) | `test_prescription_requires_medicines` | ídem | ✅ |
| Registrar un diagnóstico | `test_create_diagnosis` | ídem | ✅ |
| Payload viejo (dosis+vigencia) → 422 | `test_legacy_prescription_payload_rejected` | ídem | ✅ |
| Contenido clínico cifrado en reposo (incl. medicinas) | `test_clinical_content_encrypted_at_rest` | ídem | ✅ |
| Sin consentimiento, nada persiste | `test_consent_required` | ídem | ✅ |
| Registro ajeno indistinguible (incl. archivar) | `test_foreign_record_indistinguishable_404` | ídem | ✅ |
| Corregir medicinas: reemplazo + 1..N (AC-6) | `test_patch_replaces_medicines_validates_result` | ídem | ✅ |
| Corregir y eliminar un registro propio | `test_update_and_delete_own_diagnosis` | ídem | ✅ |
| DELETE arrastra medicinas y adjuntos | `test_delete_cascades_medicines_and_attachments` | ídem | ✅ |
| Archivar receta activa (AC-8) | `test_archive_prescription` + e2e "AC5" | ídem + frontend/tests/health-records.spec.ts | ✅ |
| Desarchivar | `test_unarchive_prescription` + e2e "AC5" | ídem | ✅ |
| Diagnóstico nace "sin confirmar" | `test_diagnosis_confirmation_status_unconfirmed` + e2e "AC6" | ídem | ✅ |
| Flujo completo de captura manual (prototipo) | e2e AC1–AC7 + adjuntos conservados | frontend/tests/health-records.spec.ts | ✅ |

## Superficie visible ejercitada de verdad

Los e2e recorren la UI real contra el backend Docker migrado (:8000): captura con 2 medicinas, validación es-MX,
edición con reemplazo, archivar/desarchivar con sección "Archivadas", diagnóstico "sin confirmar", foto adjunta
(PNG con magic bytes reales) y los dos tests de adjuntos conservados (PDF descarga íntegra, rechazo de tipo).

## Incidencias de ejecución (sin impacto en el resultado)

- La imagen Docker del backend estaba desfasada tras el grupo 1 (compose usa `develop.watch`); se reconstruyó con
  `docker compose up -d --build backend`.
- `scripts/generate-client.sh` y `bun run lint` (biome `--write --unsafe`) reformatean también `frontend/tests/`;
  el implementer restauró el spec al commit del tester (`git checkout --`), cero cambio semántico. Deuda anotada
  en memory/inbox.md.

## Grupo 4 — delta del gate humano (2026-10-18, tarde)

- **Red:** e2e → 16 tests · 12 failed (6 nuevos AC8–AC11+renombre, 6 existentes rojos por el renombre esperado).
  Commit `test:` 8634b3c.
- **Verde (re-corrido por el orquestador):** e2e **16/16** (14.7 s) · `tsc --noEmit` limpio · `make tdd-check` ✓.
- **Causa raíz del cierre del modal (bug reportado por Saúl):** el estado `open` de los diálogos de editar y
  adjuntos vivía dentro de `DropdownMenuContent`/celda de la tabla; Radix desmonta ese contenido al perder el foco
  de la ventana y se llevaba el diálogo con lo escrito. Arreglo: `RecordDialogsProvider` a nivel de página (por id);
  `refetchOnWindowFocus` sigue activo y los formularios no se remontan (los e2e AC8 esperan el refetch real).
- **Pruebas exploratorias con Claude in Chrome (2026-10-18):** happy path de captura verificado en el navegador
  real; bug de Enter-en-notas reproducido antes del fix; el modal de CREAR ya sobrevivía el cambio de pestaña con
  lista vacía (el caso real era el de editar/menú).
- Deuda nueva: `DeleteRecord.tsx` conserva su Dialog dentro del menú (misma familia del bug AC8, sin test); clave
  `records:attachments.openPanel` sin uso.
