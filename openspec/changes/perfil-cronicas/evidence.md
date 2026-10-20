# Evidence — perfil-cronicas

Date: 2026-10-20 · Branch: `feat/perfil-cronicas` · PR: (pendiente)

## Automated tests

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Línea base antes del cambio: `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | 195 passed | 0 | 0 | ✅ |
| Grupo 1, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **240 passed, 0 failed** · cobertura total **96 %** | 0 (solo los UserWarning de configuración dev y de jwt/starlette, los mismos de la línea base) | 0 | ✅ |
| `cd backend && uv run mypy app` · `uv run ruff check app` | Success: no issues found in 25 source files · All checks passed | 0 | — | ✅ |

## Red before green (tasks executed as test→impl)

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1 · backend | `uv run pytest tests/api/routes/test_profile_history.py tests/api/routes/test_health_records.py -q` → **45 failed, 49 passed, 0 errors**: 20 por "does not match any of the expected tags" (sección `chronic` desconocida), 2 por la ruta de "ninguna" que solo acepta las cuatro secciones de la Story A; las de B-5 caen en la misma barrera al sembrar sus crónicas | b39f5d5 | 94/94 del grupo; suite completa 240 passed | ✓ red commit b39f5d5, test paths sin cambios desde entonces |

## Traceability AC → test

| Scenario (design § Test plan) | Test(s) | File | Status |
|---|---|---|---|
| 1 Crónica de la lista con tratamiento (B-1, B-3) | `test_b1_chronic_hypothyroidism_active_round_trip` | `backend/tests/api/routes/test_profile_history.py` | ✅ (e2e en grupo 2) |
| 2 Salud mental sensible por defecto (B-1b) | `test_b1b_sensitive_default_by_condition[13]`, `test_b1b_anxiety_sensitive_by_default` | ídem | ✅ (e2e en grupo 2) |
| 3 El paciente decide la marca (B-1b) | `test_b1b_explicit_sensitive_respected` | ídem | ✅ (e2e en grupo 2) |
| 5 "Hasta" antes de "desde" (B-2) | `test_b2_until_age_before_since_age_rejected`, `test_b2_until_vs_since_by_age_range[11]`, `test_b2_since_until_use_story_a_when_validation` | ídem | ✅ (e2e en grupo 2) |
| 6 "Hasta" con activa no se guarda (B-2) | `test_b2_until_dropped_when_status_active` | ídem | ✅ (e2e en grupo 2) |
| 8 Enlace a un diagnóstico que no es suyo (B-4) | `test_b4_diagnosis_link_must_be_own_diagnosis`, `test_b4_put_diagnosis_link_must_be_own_diagnosis` | ídem | ✅ |
| 9 Falta la condición (B-1) | `test_b1_chronic_without_condition_rejected`, `test_b1_chronic_other_without_text_rejected[3]`, `test_b1_empty_chronic_rejected` | ídem | ✅ (e2e en grupo 2) |
| 14 "No tengo ninguna" en crónicas (B-0) | `test_b0_chronic_none_mark_then_entry_clears_it`, `test_b0_chronic_none_undo`, `test_b0_cannot_mark_chronic_none_with_entries` (409, como la Story A `test_s17`) | ídem | ✅ (e2e en grupo 2) |
| 15 Aislamiento (A-8 con una crónica) | `test_b_isolation_foreign_chronic_indistinguishable_from_missing` | ídem | ✅ |
| 16 Crónica cifrada (B-6) | `test_b6_chronic_encrypted_at_rest` | ídem | ✅ |
| 17 Eliminar un diagnóstico que respalda crónicas (B-5) | `test_b5_delete_diagnosis_unlinks_chronic_entries`, `test_b5_delete_diagnosis_backing_nothing_unchanged`, `test_b5_crud_unlink_diagnosis_counts_and_scopes_by_owner` | `backend/tests/api/routes/test_health_records.py` | ✅ (e2e en grupo 2) |
| 13, 18 Escenarios base de "ninguna" y del expediente | suites de la Story A y del expediente sin cambios | ambos | ✅ |
| Citador `test_s19_none_on_section_outside_story_rejected` | reescrito con `habits` | `test_profile_history.py` | ✅ |

## Notas del grupo 1

- **Rangos de etapa escolar.** El backend no tenía `STAGE_AGE_RANGES`; el implementer lo creó en
  `backend/app/models.py` con los mismos rangos del front (`frontend/src/components/Profile/history.ts:65-70`).
- **"Ninguna" con registros da 409**, no 422: es el comportamiento de la Story A, y el brief del tester lo decía mal.
- **Cliente regenerado** (`scripts/generate-client.sh`). Deja `tsc` rojo en el front (6 errores: `when` no existe en
  `chronic`) hasta el grupo 2; ningún push ocurre antes.
- **Sin cubrir:** `crud.py` (rama de fila ilegible en `unlink_diagnosis`, la misma idea que `_owned_history`) y una
  línea de la Story A en `models.py` (año < `HISTORY_MIN_YEAR`).
- **Fricción del harness:** `lint.py` compila con el `python3` del sistema (3.9) y marca como `SyntaxError` el
  `except A, B:` de PEP 758 que el backend (3.14) usa. Ya está propuesto en `memory/meta-improvements.md:39`.
