# Exploration — tablas-snake-case

**Matriz aceptada por delegación de Saúl Pérez (author), 2026-10-31 (`/epe-autopilot`).**

## 1. Entrada
Un pedido explícito de Saúl Pérez, que ya conocía el riesgo (renombres con datos). Los criterios están en el diseño:
nombres en el catálogo, datos que sobreviven a la subida y a la bajada, y el SQL de las pruebas.

## 2. Lo medido (2026-10-31, base de desarrollo, Postgres 18.6)
| Qué | Evidencia |
|---|---|
| Tablas con el nombre del default | `models.py:91` `OAuthIdentity`, `:104` `ConsentGrant`, `:140` `HealthRecord`, `:176` `HealthRecordMedicine`, `:360` `HealthRecordAttachment`, sin `__tablename__`; las demás lo declaran (`:443`, `:487`, `:505`, `:550`) |
| Datos | 2 386 filas en `healthrecord` y 26 312 en `consentgrant` (casi todo de las pruebas); hay que conservarlas |
| Restricciones con el prefijo viejo | por tabla: `<t>_pkey`, `<t>_<col>_fkey` y, en Postgres 18, `<t>_<col>_not_null` (consulta a `pg_constraint`); 39 de 78 en la base de pruebas |
| Índices | `<t>_pkey` y los `ix_<t>_<col>` de la migración `26de7399b12f`; SQLModel espera `ix_<tabla>_<col>` con el nombre nuevo, o `alembic check` vería una diferencia |
| Llaves que apuntan a estas tablas | `healthrecordmedicine.record_id` y `healthrecordattachment.record_id` → `healthrecord.id` (`models.py:182`, `:363`); las de `user` no cambian |
| Citadores vivos | `models.py:182,363`; SQL crudo en `test_health_records.py:392,400,409,645,653`, `test_health_record_attachments.py:198,318`, `test_account_isolation.py:239`; `D16` (texto de una decisión vigente) |
| Citadores que NO se tocan | `test_migration_receta_mexicana.py`: sube una base nueva hasta `c91f3b7a52e8`, donde las tablas se llamaban así; no llega a la migración nueva (corrección de la revisión F2: no la prueba). Lo archivado (`openspec/changes/archive/`, journals, `memory/closed/`) describe el pasado |

## 3. Lo que parecía útil y no lo fue
- Editar las migraciones viejas para que creen las tablas con el nombre nuevo: no corren otra vez en bases existentes
  (lo dice la propia nota del inbox).
- Renombrar con `op.rename_table` solamente: deja `healthrecord_pkey`, las `…_fkey`, los `…_not_null` y los `ix_…` con
  el prefijo viejo, y los `ix_…` harían que `alembic check` pida quitarlos y crearlos de nuevo.
- Escribir a mano los 40 nombres de restricciones en la migración: dependen de la versión de Postgres (antes de la 18
  no hay `…_not_null` con nombre). Es más robusto renombrar lo que el catálogo diga que existe con el prefijo viejo.

## 4. Restricciones no funcionales
Renombrar es un cambio de catálogo (`ALTER TABLE … RENAME`): no copia filas, pero toma un candado exclusivo breve. Sin
despliegue hoy (no hay producción). NFR-009: una prueba por criterio.

## 5. Clasificación
**Extensión** con migración. Sin preguntas abiertas.
