# Tasks

## 1. Backend registros (modelo, cifrado, migración, CRUD, tests del stub migrados) · test→impl

- [ ] 1.1 Test: los 6 escenarios de registros en rojo — registrar diagnóstico, registrar receta (y 422 por campos
      de tipo), cifrado en reposo (SQL directo), `CONSENT_REQUIRED` (migrando `test_consent.py` a los endpoints
      reales), aislamiento/404 indistinguible incl. PATCH/DELETE ajeno (migrando `test_account_isolation.py`),
      corregir y eliminar propio
- [ ] 1.2 Impl: `HealthRecord` + `EncryptedBytes` + migración Alembic (crea tablas, elimina `healthrecordstub`),
      `routes/health_records.py` reescrito (POST/GET/GET id/PATCH/DELETE, details es-MX), hasta verde
- [ ] 1.3 Verify: pytest 0/0/0, cobertura ≥90; `make tdd-check`

## 2. Backend adjuntos (tabla, multipart, descarga, validación) · test→impl

- [ ] 2.1 Test: los 3 escenarios de adjuntos en rojo — round-trip PDF íntegro con content-type, rechazo 415/413
      (magic bytes, >10 MB) sin persistir, cifrado en reposo del contenido y filename
- [ ] 2.2 Impl: `HealthRecordAttachment` + endpoints attach/download/delete + whitelist y magic bytes, hasta verde
- [ ] 2.3 Verify: pytest 0/0/0, cobertura ≥90; `make tdd-check`

## 3. Frontend expediente es-MX + Playwright · test→impl

- [ ] 3.1 Test: `frontend/tests/health-records.spec.ts` en rojo asertando los textos es-MX de `records.json`
      sobre: agregar diagnóstico, agregar receta, editar, eliminar, adjuntar y descargar, error de archivo
      inválido
- [ ] 3.2 Impl: cliente regenerado, ruta `/_layout/expediente`, `components/Records/` (patrón Items), namespace
      `records.json`, entrada del sidebar, hasta Playwright verde completo
- [ ] 3.3 Verify: suite Playwright completa verde; grep de strings visibles en inglés en los archivos nuevos

## 4. Cierre documental · single

- [ ] 4.1 ADR D16 (adjuntos en Postgres cifrados) en `memory/decisions.md`
- [ ] 4.2 evidence.md con números reales por grupo (rojo y verde) + validation.md no técnico
- [ ] 4.3 Journal + PR con cuerpo fiel

## Close
- [ ] evidence.md (red/green per group) · validation.md · journal · PR
