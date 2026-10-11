# Tasks

Each group carries its Execution: `single` (one agent writes the red, commits it as `test:`, then the green) ·
`test→impl` (a `tester` agent writes the red from the scenarios and the interface contract, the orchestrator commits
it as `test:`, an `implementer` agent makes it green without touching tests) · `parallel` (only with the interface
contract filled and disjoint files). Rule: a group that touches `code` and covers 3+ scenarios or 2+ implementation
files is `test→impl`; smaller groups are `single`. `make tdd-check` requires one `test:` commit per `test→impl` group.

## 1. Esqueleto: template full-stack FastAPI corriendo · single

- [x] 1.1 Verificar empíricamente el método oficial de instalación del template (README del repo con fecha a
      memory/research.md#stack) e instalarlo en la raíz (`backend/`, `frontend/`); verificar: árbol creado y
      `docker compose up` levanta API, frontend y Postgres sanos — método hoy: "Use this template" (commit 7257e60);
      copiado excluyendo .claude/.agents/README/workflows de mantenimiento; db+mailpit sanos, fastapi dev arriba
- [x] 1.2 Suites del template en verde local tal cual (pytest backend; build + Playwright frontend); números base
      anotados para evidence.md; actualizar en design.md las rutas reales de signup/login si difieren del contrato
      — backend 58 passed/0 failed/0 skipped; Playwright chromium 62 passed; rutas coinciden (users.py:146)
- [x] 1.3 Ajustes mínimos al repo (env de ejemplo, .gitignore, es-MX en las pantallas que esta story toca después);
      verificar: `make doctor` y lint del harness pasan — .gitignore fusionado, harness.json tests → backend/tests/,
      doctor OK; es-MX queda en los grupos 2-3 que tocan pantallas

## 2. Login y alta con Google (OIDC) · test→impl

- [x] 2.1 Test (red): Alta con Google · Google con correo ya registrado · callback con correo no verificado
      rechaza — mocks de Google, nunca el servicio real; commit `test:` — 4fb44c1, 4 failed/0 errors
- [x] 2.2 Impl (green): rutas `/login/google` y `/login/google/callback`, `OAuthIdentity` (con `subject` en columna
      cifrada: primer uso del tipo NFR-001), vinculación por correo verificado, `hashed_password` nullable; sin
      tocar los tests — c27cd79, incluye PKCE (S256 + verifier en cookie cifrada)
- [x] 2.3 Verify: suite truly green (0 failures, 0 errors, 0 skipped); `make tdd-check`; lectura directa a BD
      muestra ciphertext en `subject` — 62 passed; ciphertext Fernet verificado (gAAAAAB…)

## 3. Consentimiento expreso con evidencia · test→impl

- [x] 3.1 Test (red): captura sin consentimiento → 403 · otorgamiento en el alta → 201 y fila {v1, timestamp,
      método} · consultable por el titular · alta con Google no implica consentimiento — 71f2bce, 6 failed/0 errors
- [x] 3.2 Impl (green): `ConsentGrant` + endpoints POST/GET `/consent` + dependencia `require_consent` + router
      mínimo de prueba que la usa; pantalla de consentimiento es-MX (texto v1-placeholder marcado) en el flujo de
      alta de ambos métodos — API + ConsentGate.tsx (tarjeta es-MX en dashboard, backend bloquea con 403)
- [x] 3.3 Verify: suite truly green; `make tdd-check` — backend 68 passed, Playwright 62 passed, build OK

## 4. Aislamiento por cuenta y cierre de escenarios de correo · test→impl

- [ ] 4.1 Test (red): alta exitosa con correo (adaptar el del template si existe) · correo ya registrado · acceso a
      recurso ajeno por id → 404/403 · listados solo propios — sobre el router de prueba; commit `test:`
- [ ] 4.2 Impl (green): filtros por `user_id` de sesión en el router de prueba como patrón documentado para E2+
- [ ] 4.3 Verify: suite truly green; `make tdd-check`

## 5. Flujo real y CI · single

- [ ] 5.1 Prueba manual del flujo Google completo con credenciales reales en local (una vez, fuera de la suite);
      capturas/notas a evidence.md
- [ ] 5.2 CI del template adaptada al repo y en verde (correrá en GitHub al existir remoto; mientras, el comando
      local equivalente documentado); verificar: mismo comando que usará CI pasa local

## Close
- [ ] evidence.md (red/green numbers per group) · validation.md (non-technical, for whoever approves)
- [ ] journal entry in memory/journal/ · PR opened (push only if asked)
