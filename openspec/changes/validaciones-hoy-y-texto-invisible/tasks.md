# Tasks

Execution según la regla del esquema: cada grupo toca `code` con 2+ archivos de implementación → `test→impl`. Los dos
grupos tocan archivos disjuntos (backend / frontend), así que sus testers y sus implementers pueden correr a la par.

## 1. API: fecha con el «hoy» de México y texto invisible · test→impl

- [x] 1.1 Test: los tres escenarios de backend + T3 (fecha relativa) (red)
- [x] 1.2 Impl: `validate_birth_date(birth_date, today)`, `update_profile` le pasa el «hoy» de México; `_is_filled` con `_is_blank`
- [x] 1.3 Verify: suite truly green (0 failures, 0 errors, 0 skipped); `make tdd-check`

## 2. Pantalla: «¿Cuál fue?» invisible · test→impl

- [x] 2.1 Test: S04b en `profile-history.spec.ts` (red, chromium y s26-ultra)
- [x] 2.2 Impl: `Profile/text.ts` con `isBlank`; `HabitsForm.tsx` la importa; `HistoryEntryForm.tsx` la usa
- [x] 2.3 Verify: e2e de historial y hábitos verdes; tsc y biome

## Close
- [x] evidence.md (red/green numbers per group) · validation.md (non-technical, for whoever approves)
- [x] journal entry in memory/journal/ · PR opened
