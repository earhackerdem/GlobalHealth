# Proposal

**Origin:** deuda de la API (FastAPI). B1 (`memory/closed/2026-10-26-b1-surrogate-suelto-500-y-log.md`) y S2
(`memory/closed/2026-10-20-s2-si-se-configura-sentry-dsn.md`), del inventario
`memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md` (grupo «privacidad»).
**Triage:** un cambio (story con escenarios); toca `code` (`backend/app/main.py`). 2026-10-31, por delegación de
Saúl Pérez (author) con `/epe-autopilot`: «toma las tareas que correspondan a fast api y resuélvelas de manera
autónoma».

## Why
Dos caminos sacan datos de salud de donde deben estar:
- **B1:** un texto con un surrogate UTF-16 suelto (`"\ud800"`) en cualquier campo del cuerpo hace que el 422 de
  pydantic no se pueda serializar. La API responde **500** y el traceback que queda en `docker logs` lleva el valor
  recibido en claro. Reproducido el 2026-10-31 en `POST /users/signup`: 500 y el texto en el log.
- **S2:** si algún día se configura `SENTRY_DSN`, un error inesperado envía a Sentry el cuerpo de la petición y las
  variables locales de cada frame. Medido el 2026-10-31 con `sentry_sdk` 2.70.0 y un transporte en memoria: el
  diagnóstico de prueba aparece en `request.data` y en `frames[].vars`. El veredicto de S2 solo veía el cuerpo.

## What Changes
- Un handler de `RequestValidationError` para toda la API: el 422 conserva `detail[]` con `loc`, `msg`, `type`
  (y `ctx`), pero **ya no devuelve `input`**, y su cuerpo es siempre UTF-8 válido.
- La inicialización de Sentry no captura el cuerpo de la petición ni las variables locales.

## Capabilities

### New Capabilities
- `privacy/error-reports`: lo que un error (de validación o inesperado) puede devolver, escribir en el log o mandar
  al servicio de reportes, sin datos de salud.

### Modified Capabilities
Ninguna.

## Impact
- `backend/app/main.py`. Sin migración ni cambios en el cliente generado: el esquema OpenAPI de `HTTPValidationError`
  no se toca, y ni la web ni la app de Android leen `input` (`grep` en `frontend/src` y `android/`, 2026-10-31).
