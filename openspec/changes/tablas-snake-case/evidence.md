# Evidence — tablas-snake-case

## Criterio → prueba → estado
| Criterio (design.md § Test plan) | Prueba | Estado |
|---|---|---|
| Catálogo en snake_case, sin prefijos viejos, con los `ix_` esperados | `backend/tests/core/test_database.py::test_domain_tables_are_snake_case` | ✅ |
| Los datos sobreviven a subir y bajar, y la cascada sigue | `backend/tests/test_migration_tablas_snake_case.py::test_rename_keeps_rows_and_cascade_both_ways` (base aislada, como la de la receta) | ✅ |
| El SQL crudo de las pruebas usa los nombres nuevos | `test_health_records.py`, `test_health_record_attachments.py`, `test_account_isolation.py` | ✅ |
| La migración vieja de la receta sigue probándose | `backend/tests/test_migration_receta_mexicana.py`, sin cambios (baja a través del `downgrade` nuevo) | ✅ |

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
| `FASTAPI_ENV=development uv run pytest tests/ -q` | **643 passed, 0 failed, 0 errors, 0 skipped**; cobertura 97 % (corrida del implementer) |
| ruff y mypy | limpios (los dos excluyen `alembic/`) |
| migración `c4a9e1d7b2f5` en la base de pruebas: sube → baja → sube | antes, 5 tablas viejas, 39 de 78 restricciones y 10 de 23 índices con prefijo viejo; después, 0, 0 y 0; los totales no cambian (nada se borró) |
| `alembic check` (pruebas) | sin diferencias de tablas, índices ni restricciones; solo las 4 de tipo `TIMESTAMP` previas (inbox) |
| OpenAPI | 86 619 caracteres antes y después |
| `make tdd-check` | ✓ rojo `7c34d94` |

## Pase real
| Intento | Resultado |
|---|---|
| imagen reconstruida + `prestart.sh` en la base de desarrollo | `Running upgrade 26de7399b12f -> c4a9e1d7b2f5, Snake case table names` |
| filas después de migrar | `health_record` 2 386 y `consent_grant` 26 312, igual que antes en `healthrecord` y `consentgrant` |
| objetos y restricciones con prefijo viejo en desarrollo | 0 y 0 |
| e2e del expediente, historial, perfil, login y alta (chromium) | **82 passed, 0 failed** |
