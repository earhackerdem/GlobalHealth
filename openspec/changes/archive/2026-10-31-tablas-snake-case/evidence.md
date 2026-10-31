# Evidence — tablas-snake-case

## Criterio → prueba → estado
| Criterio (design.md § Test plan) | Prueba | Estado |
|---|---|---|
| Catálogo en snake_case, sin prefijos viejos, con los `ix_` esperados | `backend/tests/core/test_database.py::test_domain_tables_are_snake_case` | ✅ |
| Los datos sobreviven a subir y bajar, y la cascada sigue | `backend/tests/test_migration_tablas_snake_case.py::test_rename_keeps_rows_and_cascade_both_ways` (base aislada, como la de la receta) | ✅ |
| El SQL crudo de las pruebas usa los nombres nuevos | `test_health_records.py`, `test_health_record_attachments.py`, `test_account_isolation.py` | ✅ |
| La migración vieja de la receta sigue probándose | `backend/tests/test_migration_receta_mexicana.py`, sin cambios (sube hasta `c91f3b7a52e8`; no recorre la migración nueva) | ✅ |

## Rojo antes del verde (`7c34d94`, tester distinto del implementer)
`uv run pytest tests/core/test_database.py tests/test_migration_tablas_snake_case.py tests/api/routes/test_health_records.py tests/api/routes/test_health_record_attachments.py tests/api/routes/test_account_isolation.py tests/test_migration_receta_mexicana.py`
→ **43 failed, 19 passed, 1 error**.

Las fallas propias son 6:
- faltan las 5 tablas nuevas en el catálogo;
- «no migration after 26de7399b12f»;
- `UndefinedTable "health_record"` en 4 pruebas de SQL crudo.

Las otras 37 y el error son arrastre: la sesión `db` compartida queda abortada tras el primer `UndefinedTable`. La
receta, sola, pasa.

## Verde (`fix` de este cambio)
| Corrida | Resultado |
|---|---|
| `FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` (corrida del orquestador, después de la revisión) | **643 passed, 0 failed, 0 errors, 0 skipped**; cobertura 97 % |
| ruff y mypy | limpios (los dos excluyen `alembic/`) |
| migración `c4a9e1d7b2f5` en la base de pruebas: sube → baja → sube | antes, 5 tablas viejas, 39 de 78 restricciones y 10 de 23 índices con prefijo viejo; después, 0, 0 y 0; los totales no cambian (nada se borró) |
| `alembic check` (pruebas) | sin diferencias de tablas, índices ni restricciones; solo las 4 de tipo `TIMESTAMP` previas (inbox) |
| OpenAPI | 86 619 caracteres antes y después |
| `make tdd-check` | ✓ rojo `7c34d94` (y el de la revisión, `e3aa6e9`) |
| `openspec validate tablas-snake-case --strict` | válido |

## Pase real
| Intento | Resultado |
|---|---|
| imagen reconstruida + `prestart.sh` en la base de desarrollo | `Running upgrade 26de7399b12f -> c4a9e1d7b2f5, Snake case table names` |
| filas después de migrar | `health_record` 2 386 y `consent_grant` 26 312, igual que antes en `healthrecord` y `consentgrant` |
| objetos y restricciones con prefijo viejo en desarrollo | 0 y 0 |
| e2e del expediente, historial, perfil, login y alta (chromium) | **82 passed, 0 failed** |
| la base de desarrollo baja (`alembic downgrade -1` en el contenedor) y vuelve a subir (`prestart.sh`) | `healthrecord` 2 405 / `consentgrant` 26 373 abajo; `health_record` 2 405 / `consent_grant` 26 373 arriba; 0 restricciones con prefijo viejo (las filas crecieron respecto de la primera medición por los e2e de en medio) |

## Revisión, ronda 1 (un buscador con todas las lentes; diff chico)
El buscador reprodujo cada hallazgo en bases desechables del servidor `db-test`, con mutantes en copias. No hubo
validador aparte (lo declara el brief). Gate y arreglos por delegación de Saúl Pérez (author).

| Id | Hallazgo | Decisión |
|---|---|---|
| F1 (medio) | la prueba de la migración no miraba restricciones ni índices: un `downgrade` que solo renombra tablas pasaba todo y rompía cualquier bajada posterior | corregido: la prueba toma el catálogo antes, revisa que no quede prefijo viejo y que estén los `ix_` al subir, y exige el mismo catálogo al bajar. El mutante muere (rojo `e3aa6e9`, comprobado en el árbol y restaurado) |
| F2 | los documentos decían que la prueba de la receta recorre el `downgrade` nuevo; no lo hace | corregido en exploración, evidencia y PR |
| F3 | `validation.md` esperaba ver el `upgrade` en una base que ya estaba migrada | corregido: el paso dice qué ver en cada caso |
| F4 | «40 restricciones»: son 39 de 78 | corregido |
| F5 | el comentario del orden de los pares no era cierto (cada pasada es de una sola tabla) | corregido: comentario y `reversed(RENAMES)` en el `downgrade` |
| F6 | faltaban `openspec validate`, la bajada en desarrollo y el verde corrido por el orquestador | corregido (filas de arriba) |
| F7 | `alembic upgrade --sql` (sin conexión) falla porque se lee el catálogo | congelado: `a7f3c9e21d54` ya necesita conexión igual, y nada usa `--sql` (`memory/closed/2026-10-31-ronda-1-de-tablas-snake-case.md`) |

Verde después de la revisión: **643 passed, 0 failed, 0 errors, 0 skipped**, cobertura 97 %; `make tdd-check` ✓.
