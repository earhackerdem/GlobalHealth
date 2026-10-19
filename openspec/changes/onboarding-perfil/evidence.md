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
| 1 | Perfil básico + edad + cifrado | test_ac1_save_basic_profile_and_read_back_encrypted_at_rest | ✅ |
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

## Exploración real con Claude in Chrome (tarea 3.1, 2026-10-19)

Recorrido como usuario real sobre :5173 (cuenta nueva de prueba local + la cuenta admin de desarrollo):

- ✅ Orden del flujo: cuenta nueva → ConsentGate primero → al aceptar, el wizard aparece de inmediato →
  completar u omitir aterriza en /expediente; el wizard no vuelve a aparecer después.
- ✅ Doble clic en "Guardar perfil": un solo guardado, cero antecedentes duplicados.
- ✅ Datos raros: detalle de AHF con acentos, raya y emoji sobrevive el roundtrip cifrado y se muestra íntegro
  en /perfil.
- ✅ Cambio de pestaña real a medio wizard (peso escrito sin guardar): lo escrito persiste al volver (la
  lección C1 de receta-mexicana no se repite).
- ⚠️ Fecha de nacimiento futura: el input del navegador la DESCARTA en silencio (el campo queda vacío, nadie
  avisa). El backend la rechazaría con 422 es-MX (test AC2), pero por el camino del cliente el usuario no ve
  mensaje. UX menor → deuda declarada abajo.
- ℹ️ La home redirige a /expediente cuando el onboarding ya cerró: el "Panel" del template dejó de ser el
  aterrizaje para usuarios con consentimiento (consecuencia directa de la decisión 5 del design).
- ℹ️ Cuentas pre-existentes (admin) ven el wizard a su siguiente visita a la home — decisión documentada en el
  design (§ Migration Plan), confirmada en vivo.

## Deuda declarada

- Fecha futura descartada en silencio por el input del wizard (sin aviso al usuario); el backend sí la rechaza.
  Candidata a mensaje de validación en cliente.
- El contenedor backend NO corre migraciones al (re)arrancar: la BD dev necesitó `alembic upgrade head` a mano
  (lo hizo el implementer del grupo 2 al toparse con el 500). Fila nueva en memory/inbox.md.
- sr-only del SidebarTrigger deriva del estado del sidebar de ESCRITORIO aunque el sheet móvil esté cerrado
  (frontend/src/components/ui/sidebar.tsx:274-277) — hallazgo del tester móvil; fila en memory/inbox.md.
- PUT exitoso de family-history propio sin test directo (solo las ramas 404); profile.py ~294-301 sin cubrir.
- `body_measurement`/`family_history` llevan `created_at` como desempate de orden (no estaba en el boceto del
  design; aditivo y compatible).

## Deuda declarada por los agentes

- PUT exitoso de family-history propio sin test directo (solo las ramas 404 ajeno/inexistente); profile.py
  líneas ~294-301 sin cubrir. Candidata a test en el review.
- `body_measurement`/`family_history` llevan `created_at` como desempate de orden (no estaba en el boceto de
  tablas del design; aditivo y compatible con las aserciones de ciphertext).
