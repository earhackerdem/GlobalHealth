# Design

Status: APPROVED
Approved by: Saúl Pérez (author) on 2026-10-11 ("plan approved")

## Context

- `backend/tests/conftest.py:15-24` usa el engine global de la app (`app/core/db.py:7`), creado en import desde
  `settings.DATABASE_URL`; el teardown de la fixture `db` borra todos los `User` e `Item`.
- `settings` (`backend/app/core/config.py:16-21`) lee `../.env` pero **las variables de entorno del proceso ganan**
  sobre el archivo (comportamiento estándar de pydantic-settings): fijar `DATABASE_URL` en el entorno antes de
  importar la app basta para redirigir toda la suite.
- El esquema vive en migraciones Alembic (`backend/app/alembic/`); una BD vacía necesita `alembic upgrade head`
  antes del primer test (`init_db` NO crea tablas, solo el superusuario).
- CI `test-backend.yml` ya levanta servicios compose y destruye todo con `down -v` al final.

## Goals / Non-Goals

**Goals:** pytest nunca toca la BD de desarrollo; BD de prueba efímera en Docker que se automigra; guarda que
aborta la suite ante una URL que no sea de prueba; CI sobre la misma BD de prueba.
**Non-Goals:** paralelismo entre DOS corridas de pytest simultáneas (una BD de prueba, una corrida; el aislamiento
por-worker tipo pytest-xdist queda fuera); cambiar Playwright/e2e (siguen sobre el stack de desarrollo real);
cambiar el runtime de la app (la app en dev/prod sigue usando `DATABASE_URL` tal cual).

## Interface contract

- **compose.override.yml** — nuevo servicio `db-test` (en el override, no en compose.yml: el deploy compone
  `compose.yml + compose.deploy.yml`, así producción nunca levanta la BD de prueba; local y CI cargan el override
  por defecto):
  - `image: postgres:18` (idéntica a `db` para no probar contra otra versión)
  - `tmpfs: [/var/lib/postgresql]` — efímera por construcción, sin volumen
  - `environment`: `POSTGRES_PASSWORD=${POSTGRES_PASSWORD}`, `POSTGRES_DB=app_test`
  - healthcheck `pg_isready -U postgres -d app_test`
  - `ports: ["5433:5432"]` (5433 en el host; dentro de la red compose sigue 5432)
- **.env.example** — nueva variable documentada:
  `TEST_DATABASE_URL=postgresql://postgres:${POSTGRES_PASSWORD}@localhost:5433/app_test`
- **backend/tests/conftest.py** — ANTES de cualquier import de `app.*` (primeras líneas del módulo):
  1. resuelve `TEST_DATABASE_URL`: el entorno gana; **definida pero vacía = desactivada explícitamente, aborta SIN
     fallback**; solo la variable NO definida cae al `.env` raíz. Si al final no hay valor → `pytest.exit` con
     mensaje es-MX que dice qué variable definir y cómo levantar `db-test`
  2. valida que el nombre de base de la URL termina en `_test`; si no → `pytest.exit` ("la base configurada no es
     de prueba; me niego a correr la suite contra ella")
  3. exporta `DATABASE_URL = TEST_DATABASE_URL` en `os.environ` y recién entonces importa la app
  4. fixture de sesión (autouse, antes de `db`): `alembic upgrade head` sobre la BD de prueba
     (`alembic.config.Config` sobre `backend/alembic.ini` + `script_location` absoluto; la URL llega vía `env.py`
     → `settings.DATABASE_URL`, poblada por el export del paso 3). Antes del upgrade, assert de que el nombre de
     base efectivo en settings sigue terminando en `_test` (cierra la brecha "algo importó `app.*` antes de la
     guarda"); si la BD está caída (`OperationalError`) → `pytest.exit` con la remediación
     (`docker compose up -d --wait db-test`)
- **backend/pyproject.toml** — coverage con `omit = ["app/alembic/*"]`: las migraciones corren en-proceso al
  automigrar la suite, son DDL de esquema y quedan fuera del gate de cobertura
- **.github/workflows/test-backend.yml** — `up -d --wait db-test mailpit`; el paso "Migrate DB" (prestart sobre la
  BD dev) se elimina (la suite se automigra); `TEST_DATABASE_URL` sale del `.env` creado desde `.env.example`
- **backend/scripts/tests-start.sh / test.sh** — sin cambio de firma; siguen siendo `pytest` + coverage (la
  redirección vive en conftest, no en los scripts)

## Decisions

- **BD de prueba como servicio Docker separado, no como segunda base en el mismo contenedor `db`**: pedido
  explícito de Saúl ("también en docker"); además un contenedor efímero con tmpfs arranca limpio siempre y puede
  destruirse sin tocar el volumen de desarrollo. Alternativa descartada: `CREATE DATABASE app_test` dentro de `db`
  (menos contenedores, pero comparte ciclo de vida y volumen con los datos reales).
- **Redirección en conftest, no en los scripts**: cubre también el `uv run pytest` directo (el camino que causó los
  incidentes); un wrapper solo protege a quien lo usa.
- **Guarda por nombre de base (`*_test`)**: barata, legible y suficiente; el riesgo residual (alguien nombra su BD
  real `algo_test`) es auto-infligido.
- **Automigración en la suite**: la BD efímera parte vacía en cada arranque del contenedor; pedir un prestart
  manual recrearía el ritual que queremos eliminar.
- Extiende ADR D12 (entorno de desarrollo del template); se registra como ADR D14 en `memory/decisions.md` en este
  mismo cambio.

## Test plan (one row per scenario, mandatory)

| Spec · scenario | Test |
|---|---|
| test-isolation · Los datos de desarrollo sobreviven a la suite completa | verificación no-suite en evidence.md: snapshot de `users`/`consentgrant` en BD dev (psql) antes y después de la suite completa; diff vacío |
| test-isolation · La BD de prueba es efímera y se reconstruye sola | `docker compose rm -sf db-test && docker compose up -d --wait db-test` + suite completa verde sin pasos manuales (números en evidence.md) |
| test-isolation · Sin configuración de BD de prueba, la suite no corre | test de subproceso `tests/scripts/test_db_guard.py`: pytest lanzado sin `TEST_DATABASE_URL` → exit code ≠ 0, mensaje esperado en stderr, 0 tests ejecutados |
| test-isolation · Una URL que apunta a la base de desarrollo es rechazada | mismo arnés de subproceso con `TEST_DATABASE_URL` → `.../app` → exit ≠ 0 y mensaje "no es de prueba" |
| test-isolation · CI verde con la BD de prueba | workflow `test-backend` verde en el PR (checks del PR como evidencia) |

Nota: los dos tests de subproceso corren pytest "hijo" con entorno controlado (`subprocess.run` con `env` limpio y
`-p no:cacheprovider`, colectando un solo archivo trivial); no tocan red ni servicios reales.

## Non-functional constraints addressed

- **NFR-010 (operable por una persona)**: un servicio más en compose, cero pasos manuales nuevos (la suite se
  automigra); `docker compose up -d db-test` es todo el setup.
- **NFR-001/NFR-004**: sin impacto en cifrado ni consentimiento; el beneficio lateral es que los datos reales de
  salud/identidad del entorno dev dejan de ser borrados por tests.

## Risks / Trade-offs

- [Suite más lenta al migrar en cada sesión de pytest] → `alembic upgrade head` sobre BD vacía toma segundos; solo
  corre una vez por sesión de pytest, no por test.
- [Postgres 18 con tmpfs pierde todo al reiniciar el contenedor] → deseado (efímera); documentado en .env.example.
- [Divergencia dev/test si alguien migra dev pero no test] → imposible por construcción: test se automigra a head
  en cada corrida.
- [CI: `cp .env.example .env` debe dejar `TEST_DATABASE_URL` funcional] → la URL de ejemplo usa el password default
  `changethis` del propio .env.example, igual que `DATABASE_URL` hoy.

## Gate that closes the work

`cd backend && uv run pytest -q` verde (0/0/0) con `db` de desarrollo intacta (snapshot psql antes/después) +
`make tdd-check` + workflows `test-backend` y `test-docker-compose` verdes en el PR.

## Execution per task group

| Grupo | Flavor | Por qué |
|---|---|---|
| 1 Infra compose + env (db-test, override, .env.example) | single | configuración declarativa sin lógica testeable unitariamente; la verifica el gate del grupo 2 |
| 2 Guarda + redirección + automigración en conftest | test→impl | lógica con criterios claros (los 2 escenarios de rechazo + arranque automigrado); el rojo son los tests de subproceso |
| 3 CI (test-backend.yml) + evidencia de aislamiento | single | YAML de workflow + verificación no-suite; se prueba en el PR real |
