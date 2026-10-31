---
date: 2026-10-31
status: open
---

`alembic check` no está limpio: los modelos declaran `UTCDateTime` y la base tiene `TIMESTAMP()` en
`body_measurement.created_at`, `family_history.created_at`, `medical_history_entry.created_at` y
`patient_profile.onboarding_closed_at`. Es previo a bd-candados-indices-y-log (lo vio su implementer el 2026-10-31). Hasta
alinearlo (una migración de tipo, o un `compare_type` que reconozca `UTCDateTime`), `alembic check` no sirve como gate
de CI para detectar migraciones olvidadas.
