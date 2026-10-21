---
date: 2026-10-20
state: frozen
anchor: journal: 2026-10-20 · perfil-habitos (Story C1: sustancias y humo)
---

R3 (perfil-habitos): los esquemas de hábitos aceptan coerción laxa (`cigarettes_per_day: true` → 1, `"5"`/`5.0` → 5, `exposed: "yes"`/`1` → true, `mostly_weekends: "on"` → true)

**Verdict and why:** Descartado: la coerción laxa de pydantic es la convención de toda la API (ningún esquema de la app usa modo estricto) y la UI no puede enviar esos valores. Cerrado por Saúl Pérez. Si se quiere modo estricto, es un cambio transversal con su propia historia, no un hallazgo por pantalla

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-20 · perfil-habitos (Story C1: sustancias y humo)
