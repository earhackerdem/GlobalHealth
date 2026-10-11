# Tasks

## 1. Infraestructura: servicio db-test y variables (single)

- [x] 1.1 Añadir servicio `db-test` a `compose.yml` (postgres:18, tmpfs, `POSTGRES_DB=app_test`, healthcheck) y
      puerto `5433:5432` en `compose.override.yml`
- [x] 1.2 Documentar `TEST_DATABASE_URL` en `.env.example` (localhost:5433/app_test, nota de que es efímera) y
      añadirla al `.env` local
- [x] 1.3 Verificar: `docker compose up -d --wait db-test` sano conviviendo con `db`; `psql` conecta a 5433/app_test

## 2. Guarda, redirección y automigración en la suite (test→impl)

- [x] 2.1 (tester, rojo) Tests de subproceso en `backend/tests/scripts/test_db_guard.py`: sin `TEST_DATABASE_URL`
      la suite aborta con mensaje es-MX; con URL a base no-`_test` aborta; con URL válida el pytest hijo arranca
- [x] 2.2 (commit `test:`) rojo verificado por el orquestador
- [x] 2.3 (implementer, verde) Preámbulo de `backend/tests/conftest.py`: lectura de `TEST_DATABASE_URL`
      (entorno o .env raíz), guarda `*_test`, export de `DATABASE_URL`, fixture de sesión `alembic upgrade head`
- [x] 2.4 Suite completa contra db-test recién creada: verde 0/0/0, cobertura ≥90%, `make tdd-check` ✓

## 3. CI y evidencia de aislamiento (single)

- [x] 3.1 `test-backend.yml`: `up -d --wait db-test mailpit`, eliminar el paso "Migrate DB" (la suite se
      automigra); revisar si `test-docker-compose.yml` necesita el servicio nuevo
- [x] 3.2 Evidencia no-suite: snapshot psql de `users`/`oauthidentity`/`consentgrant` en BD dev antes/después de la
      suite completa → diff vacío (escenario "los datos de desarrollo sobreviven"); números en `evidence.md`
- [x] 3.3 ADR D14 en `memory/decisions.md` (BD de prueba efímera en Docker; extiende D12); journal; `validation.md`
      no-técnico; PR
