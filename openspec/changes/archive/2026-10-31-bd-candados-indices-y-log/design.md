# Design

Status: APPROVED
Approved: 2026-10-31, by delegation of Saúl Pérez (author): «toma las tareas que correspondan a fast api y
resuélvelas de manera autónoma… quiero ver hasta dónde llegas» (`/epe-autopilot`)

## Context
Ver exploration.md §2. La base es Postgres 18 con SQLAlchemy 2.0.51 y SQLModel; las migraciones son de Alembic, y la
cabeza actual es `3b8e5f2a9c61`.

## Goals / Non-Goals
**Goals:** valores fuera de los errores de la base; NUL rechazado en la entrada en claro; nueve índices; ningún
enlace colgando; la fila ilegible registrada.
**Non-Goals:** el interbloqueo con el borrado de cuenta (⏸️, condición no cumplida); renombrar tablas
(`memory/inbox/2026-10-20-nombres-de-tabla-sin-convencion-oauthidentity.md`); los 422 de pydantic en inglés (🔒).

## Interface contract
- `app.core.db.engine` creado con `hide_parameters=True` (se puede afirmar con `engine.hide_parameters`, aunque la
  prueba es de comportamiento: el `str()` de un `DBAPIError` con parámetro no contiene el valor).
- **Entrada en claro sin NUL:** `UserRegister`, `UserCreate`, `UserUpdate`, `UserUpdateMe` (`full_name`) e
  `ItemCreate`/`ItemUpdate` (`title`, `description`) rechazan un `\x00` con un error de validación (422, forma de
  FastAPI, `loc` del campo). Los modelos de tabla no cambian de columna.
- `crud.authenticate(session, email, password)`: con `"\x00"` en `email` devuelve `None` sin consultar (y verifica
  contra `DUMMY_HASH`, igual que con un correo que no existe); la ruta responde 400 «Correo o contraseña incorrectos».
- Migración nueva `<rev>_index_foreign_keys.py`, con `down_revision = "3b8e5f2a9c61"`: `op.create_index` sobre las
  nueve columnas (nombres `ix_<tabla>_<columna>`) y el `downgrade` que los quita.
- `crud.lock_diagnosis(*, session, owner_id, diagnosis_id) -> HealthRecord | None`: la fila del diagnóstico
  `FOR UPDATE`. `delete_health_record` la llama después de `crud.lock_profile` y antes de `crud.unlink_diagnosis`.
- `_check_diagnosis_link` lee el diagnóstico con `.with_for_update(read=True)` (`FOR SHARE`).
- `crud.unlink_diagnosis`: una fila ilegible → `logger.warning("Skipped unreadable medical history entry %s", row.id)`
  (el mismo texto que la lista del historial) y sigue.

## Decisions
1. **Validar el NUL en la entrada**, no atrapar `DataError` (exploration §3).
2. **El login responde como credenciales incorrectas**, sin consultar: no revela nada y conserva el tiempo constante.
3. **Candado en la fila del diagnóstico**, en el orden perfil → diagnóstico en las dos rutas, como pedía el veredicto
   de H1. Perdió: crear el perfil en el DELETE (cambia una regla: borrar no crea perfil).
4. **Por delegación:** índices también en `item.owner_id` y `oauthidentity.user_id`, aunque no son del dominio de
   salud: la regla es «toda llave», y el catálogo es la prueba.

## Test plan (one row per scenario, mandatory)
| Spec · scenario | Test |
|---|---|
| database · Error de base de datos con un valor de prueba | `backend/tests/core/test_database.py::test_db_error_message_hides_parameters` |
| database · Nombre con NUL en el alta | `backend/tests/api/routes/test_users.py::test_signup_full_name_with_nul_is_422` |
| database · Nombre con NUL al editar la cuenta | `test_users.py::test_update_me_full_name_with_nul_is_422` |
| database · NUL en el login | `backend/tests/api/routes/test_login.py::test_login_username_with_nul_is_incorrect_credentials` |
| database · NUL en un elemento | `backend/tests/api/routes/test_items.py::test_create_item_title_with_nul_is_422` |
| database · Catálogo de la base migrada | `backend/tests/core/test_database.py::test_every_foreign_key_has_an_index` |
| database · Primer guardado sin perfil contra el borrado del diagnóstico | `backend/tests/api/routes/test_profile_history.py::test_chronic_link_vs_diagnosis_delete_never_dangles` |
| (R2) fila ilegible registrada | `backend/tests/crud/…::test_unlink_diagnosis_logs_unreadable_row` |

## Non-functional constraints addressed
NFR-001 (los valores salen del log); rendimiento (índices); NFR-009.

## Risks / Trade-offs
- [Un candado más en el DELETE] → la fila es de la propia persona y el candado dura una transacción corta.
- [Crear 9 índices en una base grande bloquea escrituras] → hoy las tablas son chicas. Si crecen, conviene
  `CREATE INDEX CONCURRENTLY` (anotado en la migración).

## Gate that closes the work
`FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` con 0/0/0 y cobertura ≥ 90; ruff y mypy; la
migración sube y baja contra la base de pruebas; `prestart.sh` en la base de desarrollo y el catálogo sin llaves sin
índice; `openspec validate bd-candados-indices-y-log --strict`; `make tdd-check`.
