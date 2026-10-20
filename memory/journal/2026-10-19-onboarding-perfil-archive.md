# 2026-10-19 · onboarding-perfil: archivado (PR #16)

**Quién:** Saúl Pérez (author) aprobó y mergeó el PR #16 y pidió archivar la spec.

**Qué:** `openspec archive` fusionó el delta en `openspec/specs/records/patient-profile/spec.md` (spec nueva, 106
líneas) y movió la carpeta a `openspec/changes/archive/2026-10-19-onboarding-perfil/`; CHANGELOG e inbox (✅ en la
fila del onboarding) actualizados. Truth refresh: ningún skill, doc ni README afirmaba el estado anterior
(`grep` sin resultados). `openspec validate --specs` → 6 passed / 0 failed.

**Sorpresa:** el commit de archivo se había hecho sobre `feat/onboarding-perfil` ya mergeada y sin push; se llevó
por cherry-pick a `docs/archive-onboarding-perfil` desde `origin/main` (mismo flujo que el PR #14).

**Siguiente (FR-028/US-18):** la pantalla "Mi perfil médico" muestra 6 secciones APP/APNP "Sin registros" con la
promesa "se podrán capturar próximamente"; es lo que el spec pide hoy (patient-profile spec:86-88), no un defecto.
