---
date: 2026-10-20
status: done
---

[2026-10-20] `validate_birth_date` (backend/app/models.py) compara con `date.today()` del servidor, no con la
fecha de México: entre las 18:00 y las 24:00 de México el "hoy" del servidor en UTC ya es mañana, y una fecha de
nacimiento de "mañana" en México pasaría. Mismo tipo de defecto que la tarea 1.0 de perfil-eventos arregló en el
test de mediciones (visto por el implementer del grupo 1). Candidato: un helper `today_mx()` compartido.

**Closure:** validaciones-hoy-y-texto-invisible, PR #47 (2026-10-31). `validate_birth_date(birth_date, today)` recibe el «hoy» de México, igual que los otros validadores; la web también (`mexicoCityTodayIso`).
