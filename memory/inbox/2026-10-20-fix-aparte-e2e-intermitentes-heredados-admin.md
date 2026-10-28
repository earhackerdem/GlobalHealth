---
date: 2026-10-20
status: open
---

**Fix aparte: e2e intermitentes heredados** — `admin.spec.ts:204` pierde la carrera saludo vs redirect de la home (la fila 🔒 2026-10-19 de closed.md ya prescribía "waitForURL tolerante en utils/user.ts"; se reabre con evidencia nueva: 2 fallos en 4 corridas de la review de perfil-cronicas) y `reset-password.spec.ts:90` (Mailpit, sin fila). Se suma `login.spec.ts:87`, de la misma familia (saludo "¡Qué gusto verte de nuevo!" vs redirect de la home): 1 fallo en 3 corridas de la suite completa en perfil-habitos (PR #30), 5/5 aislado. Decisión de Saúl Pérez (R18 opción b): no en el PR #26
 · 2026-10-26 (perfil-habitos-actividad-sueno): `reset-password.spec.ts:90` falló en 2 de 2 suites completas y 1 de 3 aislada (más frecuente que antes); Mailpit tenía 12 mensajes, así que no es acumulación. Tras la ronda 1 fallaron `reset-password.spec.ts:32` y `:90` en una corrida: Mailpit tenía los correos de recuperación de otros usuarios pero ninguno del que falló, y el backend registró solo 2 `POST /password-recovery` en 15 minutos, así que el pedido parece no salir de la pantalla (carrera del formulario), no un retraso de Mailpit. También (ronda 2 de perfil-habitos-actividad-sueno): "socket hang up" en `createUser` (`frontend/tests/utils/privateApi.ts`), en 3 de 6 corridas de las suites de perfil; el cliente axios compartido no tiene la mitigación `Connection: close` de `profile-habits.spec.ts:192-197` y el backend corta las conexiones inactivas a los 5 s.

**Why it matters:** Sin esto la suite e2e completa no es truly green y la casilla del PR queda sin marcar

**Status:** abierto
