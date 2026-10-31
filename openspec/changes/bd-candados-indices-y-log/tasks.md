# Tasks

Un solo grupo `test→impl`: toca `code` en 5 archivos más una migración, con 7 escenarios; los archivos se cruzan
(`crud.py` lo tocan el login, el candado y R2), así que no hay paralelo.

## 1. Base de datos: valores ocultos, NUL, índices, candado y log · test→impl

- [ ] 1.1 Test: los 7 escenarios + R2 (red)
- [ ] 1.2 Impl: `hide_parameters`; validación de NUL; `authenticate`; migración de índices; `lock_diagnosis` y `FOR SHARE`; `logger.warning`
- [ ] 1.3 Verify: suite truly green (0 failures, 0 errors, 0 skipped); migración arriba y abajo; `make tdd-check`

## Close
- [ ] evidence.md (red/green numbers per group) · validation.md (non-technical, for whoever approves)
- [ ] journal entry in memory/journal/ · PR opened
