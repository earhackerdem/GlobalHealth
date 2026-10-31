# Proposal

**Origin:** deuda de la API (FastAPI) en la base de datos, del inventario
`memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`:
- M1 de api-errores-sin-datos (`memory/closed/2026-10-31-nul-500-y-parametros-sql-en-el-log.md`, que llega a `main` con el PR #46);
- FKs sin índice (`memory/closed/2026-10-12-sin-indices-en-fks-nuevas-healthrecord.md`);
- H1 (`memory/closed/2026-10-20-ronda-3-de-perfil-cronicas-h1.md`);
- R2 (`memory/closed/2026-10-20-deuda-de-perfil-cronicas-r2-unlink.md`).

**Triage:** un cambio; toca `code` (`backend/app`, una migración). 2026-10-31, por delegación de Saúl Pérez (author)
con `/epe-autopilot`.

## Why
- **M1:** un carácter NUL (`\u0000`) en el nombre de la cuenta, en el `username` del login o en un elemento da 500.
  El error de SQLAlchemy escribe en el log los parámetros de la consulta en claro: correo, nombre y hash argon2. Con
  Sentry encendido, viajarían en el evento. Reproducido el 2026-10-31 por el validador del PR #46.
- **Índices:** nueve llaves foráneas no tienen índice (medido en la base de desarrollo el 2026-10-31 con
  `pg_constraint` y `pg_index`): `healthrecord.owner_id`, `healthrecordattachment.record_id`,
  `healthrecordmedicine.record_id`, `medical_history_entry.user_id`, `family_history.user_id`,
  `body_measurement.user_id`, `consentgrant.user_id`, `oauthidentity.user_id` e `item.owner_id`. Cada listado por
  paciente y cada borrado de cuenta (en cascada) recorre la tabla completa.
- **H1:** una persona sin perfil cuyo primer POST de crónica enlazada a un diagnóstico corre a la vez que el DELETE de
  ese diagnóstico deja el enlace colgando, porque `crud.lock_profile` no bloquea cero filas.
- **R2:** `unlink_diagnosis` se salta una fila ilegible sin `logger.warning`, y su comentario es inexacto.

## What Changes
- `create_engine(..., hide_parameters=True)`.
- Un NUL en un texto que se guarda en claro se rechaza con 422. En el login responde como credenciales incorrectas.
- Una migración con los nueve índices.
- El DELETE de un diagnóstico bloquea su fila (`FOR UPDATE`) antes de desenlazar, y enlazar la lee con `FOR SHARE`.
- `unlink_diagnosis` registra la fila ilegible por su id.

## Capabilities

### New Capabilities
- `platform/database`: lo que la base garantiza: valores fuera de los errores, índices en las llaves, enlaces que
  nunca quedan colgando y textos que se pueden guardar.

### Modified Capabilities
Ninguna.

## Impact
`backend/app/core/db.py`, `backend/app/models.py`, `backend/app/crud.py`, `backend/app/api/routes/profile.py`,
`backend/app/api/routes/health_records.py` y una migración nueva en `backend/app/alembic/versions/`. El esquema
OpenAPI no cambia, salvo que los 422 nuevos del NUL usan la forma de siempre.
