---
id: D14
date: 2026-10-11
status: accepted
---

## D14 — BD de prueba efímera en Docker; pytest se niega a correr contra otra cosa
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner), a pedido directo. Extiende D12.
- **Decision:** servicio `db-test` en `compose.override.yml` (postgres:18, **tmpfs**, base `app_test`, host
  5433) solo para dev/CI: el stack de deploy (`compose.yml + compose.deploy.yml`) nunca lo levanta. La suite
  backend resuelve `TEST_DATABASE_URL` (entorno > `.env` raíz; vacía explícita = desactivada), **aborta** si
  falta o si el nombre de base no termina en `_test`, exporta `DATABASE_URL` antes de importar `app.*` y corre
  `alembic upgrade head` por sesión (la BD parte vacía en cada arranque del contenedor). Migraciones fuera del
  gate de cobertura (`omit = ["app/alembic/*"]`: DDL, no lógica).
- **Why:** el conftest del template corre contra la BD de desarrollo y su teardown borra User/Item: borró dos
  veces datos reales de Saúl (auth.setup 400 en Playwright; el usuario Google + consentimiento de la
  re-verificación manual). La guarda en conftest cubre también `uv run pytest` directo, que fue el camino real
  de los incidentes; un wrapper solo protege a quien lo usa.
- **Discarded:** segunda base `app_test` dentro del contenedor `db` (comparte ciclo de vida y volumen con datos
  reales; Saúl pidió contenedor aparte); redirección en scripts en vez de conftest (no cubre pytest directo);
  volumen persistente para db-test (la efimeridad ES la garantía de partir limpio).
- **Consequence:** correr pruebas exige `docker compose up -d --wait db-test` una vez por sesión de trabajo;
  dos corridas de pytest simultáneas siguen compartiendo db-test (paralelismo por-worker queda fuera, se decide
  si duele); Playwright sigue sobre el stack real de desarrollo.
