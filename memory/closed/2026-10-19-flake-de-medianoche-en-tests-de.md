---
date: 2026-10-19
state: partial
anchor: journal: 2026-10-19 · onboarding-perfil (apply)
---

Flake de medianoche en tests de fecha (date.today() del test vs servidor, misma máquina, ventana de ms) + migrar EditFamilyHistory a RHF+zod (rebote parcial del fixer: el diálogo no tiene campos escalares ni reglas que mostrar — solo checkboxes con updates funcionales que setValue no soporta)

**Verdict and why:** Diferidos: el flake es remotísimo y el wrapper RHF no aporta un solo FormMessage posible; si Saúl Pérez reafirma la migración, se hace. **Reabierto con evidencia (2026-10-20) para el flake de fecha:** la ventana no era de ms sino de 6 h diarias en CI (UTC 00–06, CI del PR #17); arreglado en perfil-eventos tarea 1.0 (commit 79a5cc9: `today` en America/Mexico_City), verde con TZ Tokio/UTC/México. La migración RHF sigue diferida

**State:** 🧩 partial

**Anchor (journal: date · title):** journal: 2026-10-19 · onboarding-perfil (apply)
