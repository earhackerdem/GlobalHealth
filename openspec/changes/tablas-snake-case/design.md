# Design

Status: APPROVED
Approved: 2026-10-31, by delegation of Saúl Pérez (author): «procede con el nombre de las tablas» (y antes, «toma las
tareas que correspondan a fast api y resuélvelas de manera autónoma», `/epe-autopilot`)

## Context
Ver exploration.md §2. Cabeza de Alembic: `26de7399b12f`.

## Goals / Non-Goals
**Goals:** las cinco tablas en snake_case, sin ningún nombre de restricción o índice con el prefijo viejo, con los
datos intactos al subir y al bajar.
**Non-Goals:** `user` e `item` (D25 §4); la deriva de tipos de `alembic check`
(`memory/inbox/2026-10-31-alembic-check-tipos-timestamp.md`); cambiar columnas.

## Interface contract
- `__tablename__`: `OAuthIdentity` → `"oauth_identity"`, `ConsentGrant` → `"consent_grant"`, `HealthRecord` →
  `"health_record"`, `HealthRecordMedicine` → `"health_record_medicine"`, `HealthRecordAttachment` →
  `"health_record_attachment"`; `foreign_key="health_record.id"` en los dos hijos.
- Migración `<rev>_snake_case_table_names.py`, `down_revision = "26de7399b12f"`. `upgrade`: para cada par
  (viejo, nuevo), `op.rename_table`; después, cada restricción de esa tabla cuyo nombre empieza con `"<viejo>_"`
  (`pg_constraint`) se renombra con el prefijo `"<nuevo>_"` (`ALTER TABLE … RENAME CONSTRAINT`), y cada índice cuyo
  nombre empieza con `"ix_<viejo>_"` o `"<viejo>_"` y no es de una restricción (`pg_indexes`) se renombra igual
  (`ALTER INDEX … RENAME TO`). El orden de los pares va de la más larga a la más corta, para que `healthrecord` no
  se coma el prefijo de `healthrecordmedicine`. `downgrade`: lo mismo al revés.
- Resultado esperado en el catálogo: existen las cinco tablas nuevas; no existe ninguna vieja; ningún nombre de
  restricción o índice del esquema `public` empieza con un prefijo viejo; existen `ix_health_record_owner_id`,
  `ix_health_record_medicine_record_id`, `ix_health_record_attachment_record_id`, `ix_consent_grant_user_id` e
  `ix_oauth_identity_user_id`.

## Decisions
1. **Renombrar lo que el catálogo dice**, no una lista fija (exploration §3).
2. **Una sola migración** para las cinco tablas: la convención es una, y un deploy a medias es peor.
3. **El SQL crudo de las pruebas pasa a los nombres nuevos**, y la prueba de migración de la receta no se toca
   (exploration §2).

## Test plan (one row per criterion, mandatory)
| Criterio | Test |
|---|---|
| Catálogo en snake_case, sin prefijos viejos, con los `ix_` esperados | `backend/tests/core/test_database.py::test_domain_tables_are_snake_case` |
| Los datos sobreviven a subir y bajar la migración (registro con medicina y adjunto, consentimiento, identidad de Google), y la cascada sigue funcionando | `backend/tests/test_migration_tablas_snake_case.py::test_rename_keeps_rows_and_cascade_both_ways` |
| El SQL crudo de las pruebas usa los nombres nuevos | las pruebas existentes de `test_health_records.py`, `test_health_record_attachments.py`, `test_account_isolation.py` |
| La migración vieja de la receta sigue probándose | `backend/tests/test_migration_receta_mexicana.py` sin cambios, verde |

## Non-functional constraints addressed
Candado breve por `ALTER TABLE … RENAME`; NFR-009.

## Risks / Trade-offs
- [Una base local queda atrás y la API responde 500 «relation … does not exist»] → `make migrate`
  (`project.mk`), y el `validation.md` lo dice.
- [Otro cambio abierto usa los nombres viejos en SQL crudo] → hoy no hay PRs abiertos (`gh pr list`, 2026-10-31).

## Gate that closes the work
`FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` con 0/0/0 y cobertura ≥ 90; ruff y mypy; la
migración sube y baja contra la base de pruebas y la de desarrollo; el catálogo de desarrollo sin prefijos viejos;
e2e del expediente en chromium contra la imagen reconstruida; `openspec validate tablas-snake-case --strict`;
`make tdd-check`.
