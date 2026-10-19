# Tasks

## 1. Backend: perfil, mediciones y AHF · test→impl

- [x] 1.1 Tester: `backend/tests/api/routes/test_profile.py` desde los escenarios 1–7, 9 y 12 del spec y el
      Interface contract del design (9 tests, incluyendo ciphertext en BD, 422 es-MX, envelope en listas, 409 del
      onboarding y aislamiento indistinguible). Verificación: suite roja por comportamiento ausente (404 de rutas),
      no por tests rotos; commit `test:` solo.
- [x] 1.2 Implementer: modelos `PatientProfile`, `BodyMeasurement`, `FamilyHistory` en `backend/app/models.py`
      (EncryptedString en campos sensibles, enums del contract), migración Alembic solo aditiva, rutas
      `backend/app/api/routes/profile.py` detrás de `require_consent` con errores es-MX y envelope `{data,count}`.
      Verificación: los 9 tests de 1.1 verdes sin tocarlos + `make tdd-check` + mypy limpio.
- [x] 1.3 Orquestador: suite backend completa desde limpio (cero fallos/errores/skips, números a evidence.md
      § Grupo 1) y `docker compose up -d --build backend` para que el contenedor traiga los modelos nuevos.

## 2. Frontend: onboarding, "Mi perfil médico" y e2e · test→impl

- [x] 2.1 Tester: `frontend/tests/profile.spec.ts` desde los escenarios 8, 10 y 11 (flujo completo de omitir y no
      re-ofrecer, omitir por pasos y completar después desde /perfil, secciones visibles sin captura), con los
      textos es-MX como contrato. Verificación: suite roja contra la app actual; commit `test:` solo.
- [x] 2.2 Implementer: cliente regenerado (`scripts/generate-client.sh`), wizard de onboarding (3 pasos calcados
      del prototipo validado: básicos con edad derivada, AHF con chips de línea materna/paterna y detalle opcional,
      resumen) montado en la home cuando `onboarding === "pending"`, ruta `/perfil` ("Mi perfil médico": datos +
      mediciones recientes + AHF + 6 secciones vacías), entrada en AppSidebar y namespace
      `frontend/src/locales/es-MX/profile.json`. Verificación: los tests de 2.1 verdes sin tocarlos + tsc + lint.
- [x] 2.3 Orquestador: agregar `profile.spec.ts` al testMatch del proyecto s26-ultra
      (frontend/playwright.config.ts) y correr TODA la suite Playwright como CI (`bunx playwright test`, ambos
      proyectos) desde limpio; números a evidence.md § Grupo 2.

## 3. Verificación final y entrega · single

- [x] 3.1 Exploración real con Claude in Chrome sobre la app corriendo: crear cuenta → consentimiento → wizard
      (llenar, omitir, datos raros, cambio de pestaña, doble submit) y anotar lo visto en evidence.md.
- [x] 3.2 evidence.md completo (criterio → test → ancla → estado, rojo-antes-del-verde por grupo) y validation.md
      no técnico para Saúl Pérez con el guion de los 3 caminos (completar, omitir, editar después) y "Qué NO hace
      todavía" (secciones sin captura: FR-028).
- [x] 3.3 Journal del cambio, inventario de citers (prd.md FR-027/FR-008, dominio.md, prototipo — ninguno debe
      quedar mintiendo) y PR con gh pr create sobre rama feat/onboarding-perfil. Verificación: gates del push
      verdes y PR abierto.

## Workflow follow-up

- /epe-4-review adversarial sobre el PR; merge humano (Saúl Pérez); /epe-6-archive al mergear.
