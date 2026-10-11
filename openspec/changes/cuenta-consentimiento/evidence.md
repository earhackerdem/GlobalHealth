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

## Pendiente (bloqueado en Saúl Pérez)

- **Tarea 5.1** — prueba manual del flujo Google real: requiere `GOOGLE_CLIENT_ID`/`GOOGLE_CLIENT_SECRET` de
  Google Cloud Console (OAuth client web, redirect URI `http://localhost:8000/api/v1/login/google/callback`).
  Sin esto el flujo real (incl. PKCE contra Google) no está probado end-to-end; los tests lo cubren con mocks.
- PR: sin remoto configurado no hay dónde abrirlo.

## Deuda anotada (fuera del alcance de esta story)

- Cobertura exactamente en 90%: `app/core/google_oauth.py` (camino real de red, mockeado en tests) e
  `initial_data.py` sin cubrir; cualquier código nuevo sin tests tira el CI.
- Warnings del template en dev: SECRET_KEY/passwords "changethis" (cambiar antes de cualquier deploy).
- lint.py del harness compila con el python3 del sistema (<3.14) y chocó con sintaxis PEP 758 del template
  (parentizada, cambio idéntico semánticamente) → candidato a meta-improvements.
- Si Google devuelve error en el callback, la cookie g_pkce no se borra en esa respuesta (expira a los 600 s).
