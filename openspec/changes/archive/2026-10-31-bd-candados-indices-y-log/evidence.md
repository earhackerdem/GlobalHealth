# Evidence — bd-candados-indices-y-log

## Escenario → prueba → estado
| Escenario (`specs/platform/database/spec.md`) | Prueba | Estado |
|---|---|---|
| Error de base de datos con un valor de prueba | `backend/tests/core/test_database.py::test_db_error_message_hides_parameters` | ✅ |
| Nombre con NUL en el alta | `backend/tests/api/routes/test_users.py::test_signup_full_name_with_nul_is_422` | ✅ |
| Nombre con NUL al editar la cuenta | `test_users.py::test_update_me_full_name_with_nul_is_422` | ✅ |
| NUL en el login | `backend/tests/api/routes/test_login.py::test_login_username_with_nul_is_incorrect_credentials` | ✅ |
| NUL en un elemento | `backend/tests/api/routes/test_items.py::test_create_item_title_with_nul_is_422` | ✅ |
| Catálogo de la base migrada | `test_database.py::test_every_foreign_key_has_an_index` | ✅ |
| Primer guardado sin perfil contra el borrado del diagnóstico | `backend/tests/api/routes/test_profile_history.py::test_chronic_link_vs_diagnosis_delete_never_dangles` | ✅ (8 corridas seguidas, ~1.4 s) |
| (R2) fila ilegible registrada | `backend/tests/crud/test_profile_crud.py::test_unlink_diagnosis_logs_unreadable_row` | ✅ |

## Rojo antes del verde (`b008ae0`, tester distinto del implementer)
`uv run pytest tests/core/test_database.py tests/api/routes/test_users.py tests/api/routes/test_login.py
tests/api/routes/test_items.py tests/api/routes/test_profile_history.py tests/crud` → **8 failed, 136 passed**:
- `[parameters: {'p': 'Valor-Prueba-M1'}]` en el mensaje;
- 9 llaves sin índice;
- `500 != 422` (alta, edición y elemento);
- `500 != 400` (login);
- la crónica apuntaba al diagnóstico borrado (el POST respondió 201 durante la pausa del DELETE);
- la fila ilegible no dejó aviso.

Nota del tester: la consulta de la prueba 1 es `length(CAST(:p AS text)) / 0`. Con un `cast` a entero, Postgres repite
el valor en su propio mensaje, y eso `hide_parameters` no lo puede ocultar.

## Verde (`ed9efd1`)
| Corrida | Resultado |
|---|---|
| `FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **596 passed, 0 failed, 0 errors, 0 skipped**; cobertura **97 %** |
| ruff y mypy | limpios |
| migración `26de7399b12f` contra la base de pruebas | sube (9 índices), baja (0), sube otra vez; `alembic current` = cabeza |
| OpenAPI | 86 605 caracteres antes y después, mismo texto: el cliente no cambia |
| `make tdd-check` | ✓ rojo `b008ae0` |

## Pase real (API reconstruida + `prestart.sh`, base de desarrollo)
| Intento | Resultado |
|---|---|
| `alembic upgrade head` en la base de desarrollo | `3b8e5f2a9c61 -> 26de7399b12f, Index foreign keys` |
| llaves foráneas sin índice (`pg_constraint`/`pg_index`) | **0** (antes 9) |
| `EXPLAIN` del historial de una persona | `Index Scan using ix_medical_history_entry_user_id` |
| alta con `full_name` `"NUL-Final-C3\u0000x"` | **422** `nul_character` en `["body","full_name"]` «El texto no puede contener el carácter nulo» (antes 500) |
| login con `username` con NUL | **400** «Correo o contraseña incorrectos» (antes 500) |
| `docker compose logs backend` | 0 apariciones de los valores |

El 422 de esta rama todavía repite `input`, porque el handler del PR #46 no está en `main`. Al mergear los dos, deja
de hacerlo.

## Deuda vista y no tomada
`alembic check` reporta cuatro cambios de tipo previos a este cambio (`TIMESTAMP` → `UTCDateTime` en
`body_measurement.created_at`, `family_history.created_at`, `medical_history_entry.created_at` y
`patient_profile.onboarding_closed_at`). Por eso todavía no sirve como gate. Va al inbox.

## Revisión, ronda 1 (una ronda)
Dos buscadores: seguridad, candados y pruebas; casa, migración y restricciones. **Desviación declarada:** no hubo un
agente validador aparte. El orquestador reprodujo él mismo los dos hallazgos que cambiaban código (M-1 con `curl`, L-1
con el alta de 256 caracteres) y el mutante del orden de candados (invertido en el árbol: `assert 500 == 422`,
restaurado). Los buscadores ya traían reproducción contra la API real y mutantes en copias. Gate por delegación de
Saúl Pérez (author).

| Id | Hallazgo | Decisión |
|---|---|---|
| M-1 | `POST /password-recovery/{email}` con NUL daba 500 sin sesión: el guard estaba solo en `authenticate` | corregido: el guard pasó a `crud.get_user_by_email` (todos sus llamadores); prueba `test_password_recovery_with_nul_answers_like_an_unknown_email` |
| L-1 | `PlainText \| None = Field(max_length)` cambiaba `string_too_long` por `too_long` | corregido: la longitud va dentro del `Annotated` (`StringConstraints`); OpenAPI idéntico (86 605 caracteres, mismo texto) |
| L-2 | el error del NUL usaba `PydanticCustomError`; la casa usa `ValueError` | corregido: `value_error` |
| F3 | el orden perfil → diagnóstico no tenía prueba (un mutante invertido pasaba 127/127) | corregido: `test_diagnosis_delete_locks_profile_before_diagnosis` |
| F4b | `UserCreate`, `UserUpdate`, `ItemUpdate` y `description` sin prueba de NUL | corregido: `test_every_plain_text_input_rejects_nul` (8 casos) |
| L-3 | la nota de `CONCURRENTLY` no se podía seguir tal cual | corregido: dice que hace falta `autocommit_block()` |
| L-4 | números del rojo sin comando; `openspec validate` sin registrar; cita a un archivo del PR #46 | corregido |
| L-5 | `make up` no reconstruye la imagen; el interbloqueo mal descrito | corregido en `validation.md` |
| F2 | en la carrera de dos altas con el mismo correo, el `DETAIL` de Postgres repite el correo en el log | deuda: `memory/closed/2026-10-31-ronda-1-de-bd-candados-indices-y-log.md` |
| F4a | la rama de NUL de `authenticate` no fijaba `DUMMY_HASH` | sin efecto: ese `if` se quitó; `get_user_by_email` devuelve `None` y `authenticate` ya usa `DUMMY_HASH` |
| L-6 | el commit `f217b5f` repite el asunto del anterior | congelado: ya está subido y no se reescribe historia con `--force` |

**Visto y no tomado:** el buscador de casa bajó la base de pruebas un momento para probar el `downgrade`. Dos corridas
de la carrera fallaron con 404 por las limpiezas de `conftest` de otros procesos de pytest en paralelo. No es del
cambio, y en serie pasa estable.

Rojo de la revisión (`12fb92e`): **3 failed** (forma del error, longitud y recuperación con NUL); la prueba del orden
y la de los esquemas pasaron, porque el código ya era correcto (son guardas).
Verde (`60840d1`): **608 passed, 0 failed, 0 errors, 0 skipped**, cobertura 97 %; ruff y mypy limpios; las dos
carreras 3 de 3; `make tdd-check` ✓; `openspec validate bd-candados-indices-y-log --strict` válido.
Pase real con la API reconstruida: recuperación con NUL → 200 con el mismo mensaje que un correo inexistente; alta con
NUL → `value_error`; nombre de 256 caracteres → `string_too_long`.
