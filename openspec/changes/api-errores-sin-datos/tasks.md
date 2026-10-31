# Tasks

Each group carries its Execution: `single` · `test→impl` · `parallel` (ver la plantilla del esquema). Los dos grupos
tocan un solo archivo de implementación (`backend/app/main.py`) y cubren menos de 3 escenarios cada uno: `single`.

## 1. 422 sin eco y siempre serializable · single

- [x] 1.1 Test: surrogate en el alta, 422 ordinario, clave desconocida con surrogate (red)
- [x] 1.2 Impl: `validation_error_content` + handler de `RequestValidationError` en `main.py`
- [x] 1.3 Verify: suite truly green (0 failures, 0 errors, 0 skipped)

## 2. Sentry sin cuerpo ni variables · single

- [x] 2.1 Test: evento de una falla inesperada en `POST /profile/history` (red)
- [x] 2.2 Impl: `SENTRY_OPTIONS` en `main.py`
- [x] 2.3 Verify: suite truly green; `curl` real a la API reconstruida

## Close
- [x] evidence.md (red/green numbers per group) · validation.md (non-technical, for whoever approves)
- [ ] journal entry in memory/journal/ · PR opened
