---
date: 2026-10-20
status: open
---

**Fix aparte: e2e intermitentes heredados** — `admin.spec.ts:204` pierde la carrera saludo vs redirect de la home (la fila 🔒 2026-10-19 de closed.md ya prescribía "waitForURL tolerante en utils/user.ts"; se reabre con evidencia nueva: 2 fallos en 4 corridas de la review de perfil-cronicas) y `reset-password.spec.ts:90` (Mailpit, sin fila). Decisión de Saúl Pérez (R18 opción b): no en el PR #26

**Why it matters:** Sin esto la suite e2e completa no es truly green y la casilla del PR queda sin marcar

**Status:** abierto
