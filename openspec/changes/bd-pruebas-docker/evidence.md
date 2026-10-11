# Evidence — bd-pruebas-docker

Fecha: 2026-10-11 · Rama: feat/bd-pruebas-docker · Ejecutor: Claude (orquestador) + subagente tester (grupo 2)

## Números por grupo

| Grupo | Rojo (commit `test:`) | Verde |
|---|---|---|
| 1 Infra db-test (single) | n/a | `db-test` healthy conviviendo con `db`; psql a `app_test` OK; host:5433 OK (562252c) |
| 2 Guarda + automigración (test→impl) | 2 failed / 1 passed (658da3f) | **103 passed / 0 failed / 0 errors / 0 skipped** · cobertura **93.69%** (133f056, e18ad8e) |
| 3 CI + evidencia aislamiento (single) | n/a | ver §Aislamiento; CI corre en el PR |

- `make tdd-check` ✓ (2 commits `test:` ≥ 1 grupo test→impl; rutas de tests sin diff tras el último).
- Comando: `cd backend && uv run coverage run -m pytest -q && uv run coverage report --precision=2 --fail-under=90`.

## Asimetría documentada del grupo 2

La implementación del verde vive en `backend/tests/conftest.py` — ruta de tests, donde `guard-tests` bloquea al
implementer. La escribió el orquestador y se commiteó con prefijo `test:` (133f056) para que `tdd-check` siga
verificando la barrera por git. El tester solo escribió el rojo (test_db_guard.py) y no tocó conftest.

## Ajuste de contrato durante el verde (no se recortó el design)

`TEST_DATABASE_URL=""` explícita = desactivada (aborta SIN fallback al .env raíz); solo la variable NO definida cae
al `.env`. Sin esta semántica, el escenario "sin configuración" era intesteable en cualquier máquina cuyo `.env` ya
define la variable (todas las de desarrollo). design.md §Interface contract refleja la versión final.

## Escenario: la BD de prueba es efímera y se reconstruye sola

`docker compose rm -sf db-test && docker compose up -d --wait db-test` (contenedor nuevo, tmpfs vacío) → suite
completa inmediata: verde 103/0/0 con `alembic upgrade head` ejecutado por la propia suite (fila en
`alembic_version` de `app_test` verificada vía psql). Cero pasos manuales.

## Escenario: los datos de desarrollo sobreviven a la suite (aislamiento)

Snapshot psql de la BD dev `app` (count de user/oauthidentity/consentgrant + md5 de emails|ids ordenados):

```
antes:   1|0|0|f3c7951797a069c31f14b0b82540450a
después: 1|0|0|f3c7951797a069c31f14b0b82540450a   (tras DOS suites completas)
diff: vacío
```

Nota honesta: la corrida ROJA del grupo 2 aún ejecutó el conftest viejo y barrió la BD dev una última vez (borró el
usuario Google y el consentimiento que Saúl Pérez acababa de crear en su re-verificación manual). Es exactamente el
incidente que este cambio elimina; la BD se re-sembró con prestart antes del snapshot. Desde 133f056 la suite no
puede abrir conexión alguna contra una base que no termine en `_test`.

## Cobertura: por qué apareció y se fue un 85.70%

Al migrar en-proceso, coverage empezó a contar `app/alembic/versions/*` (módulos importados por Alembic, cuerpos no
ejecutados en BD ya migrada) → 85.70% espurio. Se añadió `omit = ["app/alembic/*"]` en pyproject (DDL de esquema, no
lógica unit-testeable). Total real sin migraciones: **93.69%**, idéntico al cierre del cambio anterior.

## CI (grupo 3)

`test-backend.yml`: `up -d --wait db-test mailpit` y paso "Migrate DB" eliminado (la suite se automigra).
`test-docker-compose.yml` sin cambios (no ejecuta pytest; `up` con servicios nombrados no arranca db-test).
Playwright sin cambios (stack real). Resultado esperado en el PR: los 4 workflows verdes.
