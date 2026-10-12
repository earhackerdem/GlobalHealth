# Proposal

**Origin:** pedido directo de Saúl Pérez (2026-10-11), tras la re-verificación manual del flujo Google: "prefiero
tener una base de datos de prueba, también en docker".
**Triage:** change — toca `code` (compose, configuración del backend, conftest); una sola historia (2026-10-11).

## Why

La suite backend corre hoy contra la MISMA base de datos de desarrollo: `backend/tests/conftest.py:15-24` abre
sesión sobre el engine de la app (`app/core/db.py:7`, construido desde `DATABASE_URL` → `localhost:5432/app`) y al
cerrar la sesión **borra todos los `User` e `Item`**. Consecuencias ya sufridas en `cuenta-consentimiento`:

- La cuenta Google real de Saúl y su consentimiento otorgado se borran cada vez que corre pytest (incidente
  documentado: `auth.setup` de Playwright con 400 tras una corrida del backend; hubo que re-ejecutar `prestart.sh`).
- Dos procesos pytest en paralelo (p. ej. un subagente tester) se pisan los datos (incidente c27cd79: suite
  "aparentemente roja" por interferencia sobre la BD compartida).

Una BD de prueba dedicada, también en Docker, elimina ambas clases de incidente y deja de exigir el ritual
"re-sembrar la BD antes de usar la app".

## What Changes

- Nuevo servicio `db-test` en Docker Compose: Postgres efímero (sin volumen persistente), puerto propio en el host,
  base `app_test`. Vive junto a `db` y puede correr a la vez.
- La suite backend (pytest) se conecta SIEMPRE a esa BD de prueba y **se niega a arrancar** si la URL efectiva no
  apunta a una base de prueba (guarda explícita: nunca más una suite contra datos de desarrollo).
- La suite aplica las migraciones Alembic sobre la BD de prueba al arrancar (la BD es efímera: cada arranque del
  contenedor parte vacía).
- CI (`test-backend.yml`, `test-docker-compose.yml` si aplica) usa `db-test` para pytest; el `db` de desarrollo deja
  de ser tocado por tests en todos los entornos.
- `.env.example` documenta la nueva variable de conexión de prueba.
- Playwright NO cambia: ejercita la app viva vía backend y sigue usando la BD de desarrollo (es el entorno real).

## Capabilities

### New Capabilities
- `platform/test-isolation`: aislamiento de los datos de desarrollo frente a la ejecución de pruebas — la suite
  backend corre contra una base de datos de prueba dedicada y efímera, y rehúsa ejecutar contra cualquier otra.

### Modified Capabilities
<!-- ninguna: no cambia comportamiento de producto; identity/user-auth y privacy/consent quedan intactas -->

## Impact

- `compose.yml` / `compose.override.yml`: servicio `db-test` (+ puerto en override).
- `backend/tests/conftest.py`: apuntar la suite a la BD de prueba antes de importar la app; guarda de seguridad;
  migraciones al inicio de sesión de tests.
- `backend/app/core/config.py`: solo si hace falta una variable nueva (p. ej. `TEST_DATABASE_URL`); sin cambios de
  comportamiento en runtime de la app.
- `.env.example`, `.github/workflows/test-backend.yml`.
- Hereda el budget NFR de `product/technical-brief.md` §4 (NFR-010 operable por una persona; sin impacto en
  NFR-001/004). Decisión afectada: ADR D12 (entorno de desarrollo del template) se extiende, no se contradice.
