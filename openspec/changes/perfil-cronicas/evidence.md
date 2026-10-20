# Evidence — perfil-cronicas

Date: 2026-10-20 · Branch: `feat/perfil-cronicas` · PR: (pendiente)

## Automated tests

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Línea base antes del cambio: `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | 195 passed | 0 | 0 | ✅ |
| Grupo 1, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **240 passed, 0 failed** · cobertura total **96 %** | 0 (solo los UserWarning de configuración dev y de jwt/starlette, los mismos de la línea base) | 0 | ✅ |
| `cd backend && uv run mypy app` · `uv run ruff check app` | Success: no issues found in 25 source files · All checks passed | 0 | — | ✅ |
| Grupo 2, re-corrido por el orquestador (Vite :5173 + backend del árbol): `bunx playwright test tests/profile-history.spec.ts tests/profile.spec.ts tests/health-records.spec.ts` (chromium + s26-ultra) | **103 passed, 0 failed** (51 × 2 + setup); igual tras el arreglo de la exploración | 0 | 0 | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/` | 0 errores (7 antes del grupo 2) · 85 files, no fixes | 0 | — | ✅ |
| Suite Playwright COMPLETA como CI (ambos proyectos, imagen reconstruida servida en :8000), 3 corridas | 1 × **167 passed**; 2 × 166 passed + 1 failed, cada vez una prueba distinta que este cambio no toca: `reset-password.spec.ts:90` y `admin.spec.ts:204` ("¡Qué gusto verte de nuevo!" no apareció en 5 s). Aisladas con `--repeat-each=8`: 17 passed en una corrida y 16 + 1 fallo en otra | 2 corridas con un fallo | 0 | 🟡 inestabilidad heredada, ver deuda |

## Red before green (tasks executed as test→impl)

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1 · backend | `uv run pytest tests/api/routes/test_profile_history.py tests/api/routes/test_health_records.py -q` → **45 failed, 49 passed, 0 errors**: 20 por "does not match any of the expected tags" (sección `chronic` desconocida), 2 por la ruta de "ninguna" que solo acepta las cuatro secciones de la Story A; las de B-5 caen en la misma barrera al sembrar sus crónicas | b39f5d5 | 94/94 del grupo; suite completa 240 passed | ✓ red commit b39f5d5, test paths sin cambios desde entonces |
| 2 · frontend | `bunx playwright test tests/profile-history.spec.ts tests/profile.spec.ts tests/health-records.spec.ts --project=chromium` → **13 failed, 39 passed, 0 errores de setup**: sin pantalla `/perfil/cronicas` (no hay "Agregar"), tarjeta de crónicas sin enlace, S01 sin "1 registro"; el sembrado por API funcionó | 5a0664f | 103 passed (chromium + s26-ultra) | ✓ red commit 5a0664f, test paths sin cambios desde entonces |

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
| e2e 1, 2, 3, 4, 5, 6, 7, 9, 12, 14 | "E1 B-1 B-3 …", "E2 B-1b …", "E3 B-1b …", "E4 B-2 …", "E5 B-2 …", "E6 B-2 …", "E7 B-4 …", "E9 B-1 …", "E12 …", "E14 B-0 …" | `frontend/tests/profile-history.spec.ts` | ✅ |
| e2e 10, 11 | S01 extendido (A-1 con crónicas) · "Escenario 11 … solo hábitos sin inputs, enlace ni 'Agregar'" | `profile-history.spec.ts` · `profile.spec.ts` | ✅ |
| e2e 17 (B-5) | "E17 B-5 eliminar el diagnóstico que respalda «Hipotiroidismo» …" | `frontend/tests/health-records.spec.ts` | ✅ |
| Citadores `profile.spec.ts:317-319`, `profile-history.spec.ts:262` y comentarios de contrato | reescritos: solo hábitos sin enlace | ambos | ✅ |

## Exploración en Chrome por el agente (3.1)

Imagen reconstruida servida en `http://localhost:8000`, ventana de 500 × 711, cuenta de prueba local nueva (fecha de
nacimiento 15/03/1990), un diagnóstico y una receta sembrados por API. 2026-10-20.

| Intento | Qué pasó | Veredicto |
|---|---|---|
| Tarjeta "Enfermedades crónicas" en /perfil | Enlace a `/perfil/cronicas`, "Sin llenar"; al final "4 registros". Solo hábitos sin enlace | ✅ |
| Hipotiroidismo, Activa, desde 31, tratamiento, nota con emoji 💊✅, respaldo | Resumen exacto "Hipotiroidismo · desde los 31 años (≈2021) · activa · Levotiroxina 50 mcg en ayunas" + "Respaldo: Hipotiroidismo subclínico"; la nota con emoji se guarda intacta; casilla "Sensible" apagada | ✅ |
| Selector de respaldo | Solo "Ninguno" y el diagnóstico; la receta no aparece | ✅ |
| Doble clic en "Guardar" | Un solo registro en `GET /profile/history` | ✅ |
| Ansiedad sin tocar la casilla | La casilla se prende sola (`aria-checked=true`, descrita por su ayuda); etiqueta "sensible" | ✅ |
| Epilepsia, desde 20, hasta 12 | "No puede ser antes de «desde cuándo»" junto a "¿Hasta cuándo?", nada guardado | ✅ |
| Asma, Ya no la tengo, desde "En la primaria", hasta 16 | "Asma · desde la primaria (≈1996–2001) · hasta los 16 años (≈2006)" | ✅ |
| Editar Asma a "Activa" | "¿Hasta cuándo?" desaparece; el servidor guarda `until: null`; la lista dice "· activa" | ✅ |
| "Otra" = "TOC 🧠" + Sensible + tratamiento de >2000 caracteres tecleados | El textarea corta en 2000 (`maxLength`), se guarda; etiqueta "sensible"; el texto largo hace wrap sin scroll horizontal (`scrollWidth` 500 = `clientWidth`) | ✅ |
| Guardar sin condición | **Defecto:** el foco iba a la primera opción (y=296) y el mensaje quedaba bajo las 13 opciones (y=919), fuera de pantalla. Arreglado en 64333d0 (el error va bajo "¿Cuál?"); re-explorado: visible bajo la etiqueta; suites del cambio 103 passed | ✅ tras arreglo |
| "Otra" sin texto | Foco en "¿Cuál es?" (y=338) y el mensaje debajo (y=380) | ✅ |
| B-5: Eliminar el diagnóstico desde /expediente | El diálogo dice "Respalda tu crónica «Hipotiroidismo». La crónica se queda, sin respaldo."; al confirmar, la crónica sigue sin "Respaldo" y su `diagnosis_id` es `null` | ✅ |
| Atrás / adelante con el formulario abierto | Vuelve a la lista sin errores; el borrador se pierde, igual que en la Story A | ✅ (comportamiento conocido) |
| Consola | 9 errores, todos de `chrome-extension://…` (una extensión del navegador, "Flags error response: status=401"); ninguno de la app | ✅ |

Nota de la cuenta de prueba: el endpoint privado `POST /private/users/` con un correo `@example.test` crea el
usuario y luego responde 500 (validación de la respuesta). Es del template (solo entornos locales), fuera de alcance.

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

## Notas del grupo 2

- **Sin ruta nueva:** `/perfil/cronicas` entra por la ruta con parámetro `perfil_.$seccion.tsx` de la Story A en
  cuanto existe el slug `cronicas`.
- **Clave de query:** el historial vive en `["history"]` (no `["profile", "history"]` como decía el diseño);
  `DeleteRecord` invalida esa.
- **`WhenField`** ganó una prop opcional `legend` ("¿Desde cuándo?" / "¿Hasta cuándo?"), compatible hacia atrás. No
  estaba en la lista de archivos del plan.
- **Error de edad o año imposible con desde y hasta enviados:** el servidor no dice cuál campo falló, así que va
  como alerta del formulario. Mejora posible: que la API devuelva el campo.
- **Mientras el front no compilaba** (entre el cliente regenerado y el grupo 2), los e2e corrieron contra el backend
  del árbol (`fastapi dev`, :8000) y Vite :5173; la suite completa final corrió contra la imagen reconstruida.

## Deuda

- **Inestabilidad heredada en la suite e2e completa:** `reset-password.spec.ts:90` y `admin.spec.ts:204` fallan de
  forma intermitente (1 de 3 corridas cada una aquí; la Story A registró lo mismo con `reset-password`). No tocan
  código de este cambio. El CI del PR corre con `--fail-on-flaky-tests`.
- **H5 (`closed.md`):** el formulario crece sin RHF+zod.
- **Dos líneas sin cubrir** en `crud.py` y `models.py` (ver notas del grupo 1).
