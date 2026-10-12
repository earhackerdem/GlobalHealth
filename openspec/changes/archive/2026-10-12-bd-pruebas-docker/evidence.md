# Evidence — bd-pruebas-docker

Fecha: 2026-10-11 · Rama: feat/bd-pruebas-docker · Ejecutor: Claude (orquestador) + subagente tester (grupo 2)

## Números por grupo

| Grupo | Rojo (commit `test:`) | Verde |
|---|---|---|
| 1 Infra db-test (single) | n/a | `db-test` healthy conviviendo con `db`; psql a `app_test` OK; host:5433 OK (562252c) |
| 2 Guarda + automigración (test→impl) | 2 failed / 1 passed (658da3f) | **103 passed / 0 failed / 0 errors / 0 skipped** · cobertura **93.69%** (133f056, e18ad8e) |
| 3 CI + evidencia aislamiento (single) | n/a | ver §Aislamiento; CI corre en el PR |

94 warnings, todos preexistentes (89 InsecureKeyLengthWarning de pyjwt por el SECRET_KEY de dev, 4 UserWarning de
config.py, 1 StarletteDeprecationWarning); ninguno introducido por este cambio.

- `make tdd-check` ✓ (2 commits `test:` ≥ 1 grupo test→impl; rutas de tests sin diff tras el último).
- Comando: `cd backend && uv run coverage run -m pytest -q && uv run coverage report --precision=2 --fail-under=90`.

## Asimetría documentada del grupo 2

La implementación del verde vive en `backend/tests/conftest.py` — ruta de tests, donde `guard-tests` bloquea al
implementer. La escribió el orquestador y se commiteó con prefijo `test:` (133f056) para que `tdd-check` siga
verificando la barrera por git. El tester solo escribió el rojo (test_db_guard.py) y no tocó conftest.

## Ajuste de contrato durante el verde (no se recortó el design)

`TEST_DATABASE_URL=""` explícita = desactivada (aborta SIN fallback al .env raíz); solo la variable NO definida cae
al `.env`. Sin esta semántica, el escenario "sin configuración" era intesteable en cualquier máquina cuyo `.env` ya
define la variable (todas las de desarrollo). design.md §Interface contract refleja la versión final (corregido en
el apply de la revisión: los pasos 1 y 4 habían quedado desactualizados y esta afirmación era falsa hasta entonces).

## Escenario: la BD de prueba es efímera y se reconstruye sola

`docker compose rm -sf db-test && docker compose up -d --wait db-test` (contenedor nuevo, tmpfs vacío) → suite
completa inmediata: verde 103/0/0 con `alembic upgrade head` ejecutado por la propia suite (fila en
`alembic_version` de `app_test` verificada vía psql). Cero pasos manuales.

## Escenario: los datos de desarrollo sobreviven a la suite (aislamiento)

**Re-ejecutado en el apply de la revisión** (la primera toma era vacua: BD degenerada con 0 identidades/consentimientos,
hallazgo confirmado; y el md5 de emails commiteado resultó ser del placeholder de .env.example — falso positivo de PII,
pero el criterio queda: no se commitean hashes derivados de datos). GIVEN real sembrado vía los modelos de la app:
usuario con OAuthIdentity google (subject cifrado `gAAAAAB…` verificado en crudo), ConsentGrant v1, Item y
HealthRecordStub (note cifrada). Snapshot = counts de las CINCO tablas + md5 local del pg_dump completo normalizado
(pg_dump 18 inserta un token aleatorio `\restrict` por dump; se filtra). El hash NO se commitea.

```
antes:   2|1|1|1|1   (user|oauthidentity|consentgrant|item|healthrecordstub)
después: 2|1|1|1|1   tras DOS suites completas (104 passed cada una)
dumps normalizados: md5 local idéntico · diff de counts: vacío
xmin: todas las filas conservan xmin 4019–4021 con txid_current=4022 tras ambas suites
      → ninguna transacción escribió en esas tablas durante las corridas (prueba más fuerte que el dump)
```

Nota honesta: la corrida ROJA del grupo 2 aún ejecutó el conftest viejo y barrió la BD dev una última vez (borró el
usuario OAuth real y el consentimiento recién creados en la re-verificación manual del flujo Google). Es exactamente el
incidente que este cambio elimina; la BD se re-sembró con prestart antes del snapshot. Desde 133f056 la suite no
puede abrir conexión alguna contra una base que no termine en `_test`.

## Cobertura: por qué apareció y se fue un 85.70%

Al migrar en-proceso, coverage empezó a contar `app/alembic/versions/*` (módulos importados por Alembic, cuerpos no
ejecutados en BD ya migrada) → 85.70% espurio. Se añadió `omit = ["app/alembic/*"]` en pyproject (DDL de esquema, no
lógica unit-testeable). Total real sin migraciones: **93.69%**, idéntico al cierre del cambio anterior.

## CI (grupo 3)

`test-backend.yml`: `up -d --wait db-test mailpit` y paso "Migrate DB" eliminado (la suite se automigra).
`test-docker-compose.yml` sin cambios (no ejecuta pytest; `up` con servicios nombrados no arranca db-test).
Playwright sin cambios (stack real). 11/11 checks verdes en el head 2aede4d (run test-backend 38185638754, 52 s).
