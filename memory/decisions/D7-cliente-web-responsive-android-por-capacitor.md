---
id: D7
date: 2026-10-11
status: revised
---

## D7 — Cliente: web responsive + Android por Capacitor
- **Status:** Revised · 2026-10-29 → ver D24 (Android nativo en Kotlin + Jetpack Compose) · original: Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner)
- **Decision:** paciente y profesional usan la misma web responsive; la app Android de v1 es un shell Capacitor
  (notificaciones locales para FR-025, cámara para FR-007, vía futura a Health Connect por plugin/módulo nativo).
- **Why:** Saúl no tiene experiencia Android y está abierto a alternativas; Kotlin nativo son meses de curva sin
  beneficio en los FR de v1.
- **Discarded:** Kotlin nativo en v1 (se revisita si Health Connect lo exige al integrar wearables); PWA pura
  (recordatorios de medicación menos fiables que notificaciones locales nativas).
