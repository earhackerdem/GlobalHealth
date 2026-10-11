# Evidence — cuenta-consentimiento

Fecha: 2026-10-11 · Rama: feat/cuenta-consentimiento · Ejecutor: Claude (orquestador) con subagentes tester/implementer

## Números por grupo (rojo → verde, re-ejecutados por el orquestador antes de cada commit)

| Grupo | Rojo (commit `test:`) | Verde |
|---|---|---|
| 1 Esqueleto (single) | n/a | base del template: backend 58 passed · Playwright chromium 62 passed (cb48c3a) |
| 2 Google OIDC (test→impl) | 4 failed / 0 errors — endpoints inexistentes (4fb44c1) | 62 passed / 0 failed / 0 skipped (c27cd79) |
| 3 Consentimiento (test→impl) | 6 failed / 0 errors — 404 de /consent y /health-records (71f2bce) | backend 68 passed · Playwright 62 passed · build OK (eed4a9a) |
| 4 Aislamiento (test→impl) | 1 failed — faltaba GET /health-records/{id}; alta/duplicado ya verdes vía template (eb067eb) | **73 passed / 0 failed / 0 errors / 0 skipped** (4bda918) |

- `make tdd-check` ✓ tras cada grupo (un commit rojo por grupo test→impl).
- Comandos: `cd backend && uv run pytest -q` · `cd frontend && bunx playwright test --project=chromium` ·
  `bun run --filter frontend build`.

## Verificaciones no-suite

- **NFR-001 (cifrado)**: fila temporal en `oauthidentity` — el ORM lee `test-subject-123`, la BD cruda
  (`psql` directo) muestra `gAAAAAB…` (Fernet). Fila limpiada después.
- **NFR-004 (evidencia del consentimiento)**: fila leída directa de Postgres tras POST /consent →
  `text_sha256 = 7e8fe418e56e313330db0d779fbd6c127d2d84a4929f82f5ff5df5cc00c6e4fb` (= sha256 del texto v1),
  `granted_at` tz-aware UTC, `auth_method` correcto (reporte del implementer del grupo 3).
- **PKCE**: redirect 307 con `code_challenge` + `code_challenge_method=S256`; cookie `g_pkce` HttpOnly+Secure+
  SameSite=Lax cifrada con Fernet, borrada en el callback.
- **Cobertura backend**: 90% total — exactamente el umbral del CI (`coverage report --fail-under=90`).
  Margen cero: deuda anotada abajo.

## CI (tarea 5.2)

Workflows del template adaptados/copiados: test-backend.yml, playwright.yml, test-docker-compose.yml,
pre-commit.yml (sin referencias al repo del template; los de mantenimiento del template no se copiaron).
Sin remoto git aún: correrán en el primer push. Equivalentes locales ejecutados en este cambio:
backend `uv run coverage run -m pytest && uv run coverage report --fail-under=90`; frontend
`bunx playwright test --project=chromium`; compose `docker compose up -d --wait db mailpit`.

## Tarea 5.1 — flujo Google REAL verificado (2026-10-11)

Ejecutada vía Chrome (Saúl Pérez presente, credenciales suyas en .env local no rastreado):
- `GET /login/google` → 307 a accounts.google.com con `code_challenge` + `code_challenge_method=S256` en la URL
  (PKCE real observado en el navegador).
- Selector de cuenta → consentimiento "Accede a GlobalHealth" mostrando SOLO nombre, foto y correo (Google actúa
  únicamente como proveedor de identidad, como exige el PRD §7).
- Callback → 200 con `{access_token, token_type: "bearer"}` tras intercambio real del código (con code_verifier
  desde la cookie cifrada) y validación del id_token contra el JWKS de Google.
- BD verificada: usuario `earhackerdem@gmail.com` creado con `hashed_password NULL`, activo; fila `oauthidentity`
  con `provider=google` y `subject` en ciphertext Fernet (`gAAAAAB…`); log del server: callback 200 OK.

## PR

PR #1 abierto (feat/cuenta-consentimiento → main) con CI completo en verde en el head final:
pre-commit, test-backend (cobertura 90%), test-docker-compose, Playwright 4/4 + merge de reportes.

## Ronda /epe-4-review → /epe-5-apply (2026-10-11)

Saúl Pérez aprobó los 13 hallazgos de la revisión adversarial (ninguno rechazado). Aplicados en dos pasadas
(tests → impl, barrera respetada): rojo c91eb7f (17 failed esperados / 83 passed), verde e8082fe.
- Números tras el apply: backend **100 passed / 0 failed / 0 errors / 0 skipped** · cobertura **93.69%**
  (antes 89.83% real) · Playwright chromium **62 passed** · `make tdd-check` ✓ · pre-commit completo ✓.
- Cambios de contrato (design.md §Interface contract actualizado): state anti-CSRF sellado en la cookie PKCE,
  PKCE estricto sin downgrade, callback → 307 a `/google-callback#access_token=…` con no-store, claim `amr`
  (auth_method real de la sesión), `require_consent` con vigencia de versión, rutas `/` + wrapper {data,count},
  `HealthRecordStub.note` cifrada (migración a7f3c9e2), claves separadas datos/cookie + MultiFernet (ADR D13),
  botón "Continuar con Google" + aterrizaje del token en la SPA, bind de handleError, errores es-MX.
- Falsos positivos de la revisión documentados en el comentario VALIDATOR del PR (el principal: "SyntaxError
  crítico" reproducido con el python del sistema; el proyecto es 3.14 de punta a punta).
- NOTA: la prueba manual del flujo Google real (5.1) se hizo ANTES de este endurecimiento; el flujo real cambió
  (redirect a la SPA). Re-verificación manual pendiente de Saúl con el nuevo flujo (ahora sí con botón).

## Deuda anotada (fuera del alcance de esta story)

- Cobertura exactamente en 90%: `app/core/google_oauth.py` (camino real de red, mockeado en tests) e
  `initial_data.py` sin cubrir; cualquier código nuevo sin tests tira el CI.
- Warnings del template en dev: SECRET_KEY/passwords "changethis" (cambiar antes de cualquier deploy).
- lint.py del harness compila con el python3 del sistema (<3.14) y chocó con sintaxis PEP 758 del template
  (parentizada, cambio idéntico semánticamente) → candidato a meta-improvements.
- Si Google devuelve error en el callback, la cookie g_pkce no se borra en esa respuesta (expira a los 600 s).
