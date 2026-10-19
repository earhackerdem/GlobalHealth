# Evidence — onboarding-perfil

Fecha: 2026-10-19 · Rama: feat/onboarding-perfil · Orquestador: sesión Claude Code supervisada por Saúl Pérez.
Los números de abajo son corridas re-ejecutadas por el orquestador (no reportes de los subagentes).

## Rojo antes del verde

| Grupo | Commit del rojo | Corrida |
|---|---|---|
| 1 (backend) | 9cfeeb9 `test(onboarding-perfil): rojo del grupo 1` | `uv run pytest tests/api/routes/test_profile.py -q` → **10 failed, 0 errors** (todos por 404: rutas ausentes; colección limpia) |
| 2 (frontend e2e) | fce984e `test(onboarding-perfil): rojo del grupo 2` | `bunx playwright test tests/profile.spec.ts --project=chromium` → **3 failed, 1 passed (setup)** (todos en `getByTestId("onboarding-wizard")`: el wizard no existe; helpers sanos) |
| Corrección de test ajeno | 00a1b5b `test(onboarding-perfil): el test de la migración…` | el test de receta-mexicana anclaba head de Alembic a c91f3b7a52e8; reanclado a su revisión objetivo → `pytest tests/test_migration_receta_mexicana.py -q` → 2 passed |

## Verde del grupo 1 (backend) — commit 1d2bee4

- `uv run pytest tests/api/routes/test_profile.py -q` → **10 passed, 0 failed, 0 skipped**.
- Suite completa desde limpio: `FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` →
  **156 passed, 0 failed, 0 errors, 0 skipped** · cobertura **TOTAL 94%** (gate CI ≥90%).
- `uv run mypy app` → Success: no issues found in 25 source files.
- `make tdd-check` → ✓ (tests intactos desde el rojo).
- Contenedor backend reconstruido (`docker compose up -d --build backend`, lección develop.watch);
  `GET /api/v1/profile` sin token → 401 (la ruta existe en el contenedor).

## Criterio → test → ancla → estado

| # | Escenario del spec | Test | Estado |
|---|---|---|---|
| 1 | Perfil básico + cifrado (la edad se asierta en e2e /perfil, no aquí: es derivada en cliente) | test_ac1_save_basic_profile_and_read_back_encrypted_at_rest + profile.spec.ts Esc. 10 | ✅ |
| 2 | Fecha futura rechazada (es-MX) | test_ac2_future_birth_date_rejected_profile_unchanged | ✅ |
| 3 | Perfil vacío válido | test_ac3_empty_profile_put_is_valid_with_null_fields | ✅ |
| 4 | Medición nueva conserva la anterior | test_ac4_new_measurement_keeps_previous_and_updates_latest | ✅ |
| 5 | Valores implausibles 422 es-MX | test_ac5_implausible_measurement_values_rejected | ✅ |
| 6 | AHF con línea y detalle, cifrado | test_ac6_family_history_with_relatives_and_note_encrypted_at_rest | ✅ |
| 7 | Borrar condición elimina la fila | test_ac7_delete_family_history_removes_entry_and_row | ✅ |
| 8 | Omitir → expediente, no se repite | profile.spec.ts Escenario 8 | ⏳ grupo 2 |
| 9 | Onboarding se cierra una vez (409) | test_ac9_onboarding_closes_once_then_409 | ✅ |
| 10 | Omitir por pasos, completar después | profile.spec.ts Escenario 10 | ⏳ grupo 2 |
| 11 | 6 secciones visibles sin captura | profile.spec.ts Escenario 11 | ⏳ grupo 2 |
| 12 | Ajeno indistinguible de inexistente | test_ac12_foreign_resources_indistinguishable_from_missing | ✅ |
| + | Rutas detrás del consentimiento | test_profile_routes_require_consent | ✅ |

## Verde del grupo 2 (frontend) — commit 49681a9

- `bunx playwright test tests/profile.spec.ts` (chromium + s26-ultra) → **7 passed, 0 failed, 0 skipped**
  (3 escenarios × 2 viewports + setup). Primer intento en móvil falló (navegación tras el sidebar colapsado a
  384px); regresó al tester, que lo endureció sin debilitar aserciones (commit ec5d74d) — hallazgo lateral: el
  sr-only del SidebarTrigger deriva del estado de escritorio (frontend/src/components/ui/sidebar.tsx:274-277),
  anotado para el inbox.
- Suite Playwright COMPLETA como CI: `bunx playwright test` → **103 passed, 0 failed, 0 skipped** (58.8s) —
  las suites del template no se afectaron aunque el usuario del setup tenga onboarding pendiente.
- `bunx tsc --noEmit` limpio · `bun run lint` limpio (reformateo puro commiteado aparte, 6952022).
- `make tdd-check` → ✓.

## Grupo 4 — feedback de Saúl Pérez tras probar el PR (2026-10-19)

Dos puntos: el botón global "Ahora no…" aparecía también en el Resumen (con todo capturado, confunde), y la
sección Antecedentes familiares de /perfil no ofrecía edición — hueco contra el requisito "Nada del onboarding
es obligatorio… completarse y corregirse después".

- Rojo (commit 40ff7f8): Escenario 10 extendido (Resumen sin "Ahora no"; pasos 1-2 con él) + Escenario 13 nuevo
  (agregar AHF desde /perfil tras omitir todo) → `--project=chromium`: **2 failed, 3 passed** por comportamiento
  ausente.
- Verde (commit 7dc5ad1): editor extraído a FamilyHistoryFields y reutilizado en el diálogo "Editar antecedentes"
  (diff → POST/PUT/DELETE contra el API existente; sin cambios de backend). Re-corrido por el orquestador:
  `profile.spec.ts` **9 passed** (ambos viewports) · suite completa **105 passed, 0 failed, 0 skipped** ·
  tsc y lint limpios · `make tdd-check` ✓.

## Exploración real con Claude in Chrome (tarea 3.1, 2026-10-19)

Recorrido como usuario real sobre :5173 (cuenta nueva de prueba local + la cuenta admin de desarrollo):

- ✅ Orden del flujo: cuenta nueva → ConsentGate primero → al aceptar, el wizard aparece de inmediato →
  completar u omitir aterriza en /expediente; el wizard no vuelve a aparecer después.
- ✅ Doble clic en "Guardar perfil": un solo guardado, cero antecedentes duplicados.
- ✅ Datos raros: detalle de AHF con acentos, raya y emoji sobrevive el roundtrip cifrado y se muestra íntegro
  en /perfil.
- ✅ Cambio de pestaña real a medio wizard (peso escrito sin guardar): lo escrito persiste al volver (la
  lección C1 de receta-mexicana no se repite).
- ~~⚠️ Fecha de nacimiento futura: el input la descarta en silencio~~ **CORREGIDO en el review (2026-10-19,
  falso positivo del orquestador):** el validador frontend reprodujo que el valor SÍ se conserva, el PUT devuelve
  422 y el usuario VE el mensaje es-MX exacto en toast — el criterio se cumplía de punta a punta. Lo observado en
  la exploración fue un artefacto del tecleo automatizado. El apply añade además mensaje inline (G16).
- ℹ️ La home redirige a /expediente cuando el onboarding ya cerró: el "Panel" del template dejó de ser el
  aterrizaje para usuarios con consentimiento (consecuencia directa de la decisión 5 del design).
- ℹ️ Cuentas pre-existentes (admin) ven el wizard a su siguiente visita a la home — decisión documentada en el
  design (§ Migration Plan), confirmada en vivo.

## Deuda declarada

- ~~Fecha futura descartada en silencio~~ (falso positivo, ver corrección arriba; el mensaje inline entró en el
  apply del review).
- El contenedor backend NO corre migraciones al (re)arrancar: la BD dev necesitó `alembic upgrade head` a mano
  (lo hizo el implementer del grupo 2 al toparse con el 500). Fila nueva en memory/inbox.md.
- sr-only del SidebarTrigger deriva del estado del sidebar de ESCRITORIO aunque el sheet móvil esté cerrado
  (frontend/src/components/ui/sidebar.tsx:274-277) — hallazgo del tester móvil; fila en memory/inbox.md.
- PUT exitoso de family-history propio sin test directo (solo las ramas 404); profile.py ~294-301 sin cubrir.
- `body_measurement`/`family_history` llevan `created_at` como desempate de orden (no estaba en el boceto del
  design; aditivo y compatible).

## Apply del review adversarial (2026-10-19)

Gate de Saúl Pérez: "todo" (28 confirmados; 2 falsos positivos con prueba — uno del propio orquestador). 3 fixers
con prefijo NO-CLOSED, cero descartes propios, 1 rebote parcial (EditFamilyHistory→RHF, ⏸️ en closed.md).
Números finales re-corridos por el orquestador desde limpio:

- Backend: **168 passed / 0 failed / 0 skipped** · cobertura **95%** · mypy limpio · migración f4b2c7d81e93
  (condition cifrada, re-cifrado idempotente) corrida en BD _test y en el contenedor dev.
- Frontend: tsc limpio · lint limpio · Playwright **109 passed / 0 failed** (profile.spec: 6 escenarios × 2
  viewports + setup = 13 passed).
- Los 2 CRÍTICOS cerrados: AddMeasurement en /perfil (G1) y condition cifrada (G2); el guardado del wizard ya es
  idempotente ante reintentos (G3, verificado por el nuevo flujo que re-lee el servidor + 409 del backend).
- `openspec validate --strict` verde tras las enmiendas del spec (Esc. 12 implementable, frontera de cifrado G19).

## Deuda declarada por los agentes

- PUT exitoso de family-history propio sin test directo (solo las ramas 404 ajeno/inexistente); profile.py
  líneas ~294-301 sin cubrir. Candidata a test en el review.
- `body_measurement`/`family_history` llevan `created_at` como desempate de orden (no estaba en el boceto de
  tablas del design; aditivo y compatible con las aserciones de ciphertext).
