# Proposal

**Origin:** `memory/inbox/2026-10-20-nombres-de-tabla-sin-convencion-oauthidentity.md`; decisión D25.
**Triage:** un cambio; toca `code` (`backend/app/models.py`, una migración) y una decisión. 2026-10-31: Saúl Pérez
(author) pidió «procede con el nombre de las tablas» después del aviso de que eran renombres con datos. El resto del
ciclo corre por delegación (`/epe-autopilot`).

## Why
Cinco tablas no siguen la convención del resto (snake_case con `__tablename__`): `oauthidentity`, `consentgrant`,
`healthrecord`, `healthrecordmedicine` y `healthrecordattachment`. Son las más consultadas del expediente, y quien lee
la base o el SQL de las pruebas mezcla dos estilos.

## What Changes
- `__tablename__` en snake_case en los cinco modelos, y sus `foreign_key` apuntan a `health_record.id`.
- Una migración nueva que renombra las tablas, sus restricciones y sus índices, y en el `downgrade` los regresa.
- El SQL crudo de las pruebas usa los nombres nuevos.

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
Ninguna: el comportamiento no cambia (`skip_specs: true`). La decisión queda en D25.

## Impact
`backend/app/models.py`, `backend/app/alembic/versions/<nueva>`, las pruebas con SQL crudo
(`test_health_records.py`, `test_health_record_attachments.py`, `test_account_isolation.py`). La API, el OpenAPI, la
web y Android no cambian (los nombres de tabla no salen de la base). Las bases existentes se migran con `make migrate`.
