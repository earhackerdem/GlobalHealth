---
date: 2026-10-19
state: frozen
anchor: journal: 2026-10-19 · onboarding-perfil (apply)
---

"El redirect de la home + superusuario compartido de auth.setup rompe las suites del template"

**Verdict and why:** Falso positivo reproducido: 222 ejecuciones verdes CON el estado supuestamente roto (el saludo asierta ~ms antes de que el redirect dispare — el saludo pinta en el primer render, el redirect necesita 2 round-trips). Nota: carrera latente de ms; si algún día flakea, fix de 1 línea (waitForURL tolerante) en utils/user.ts

**State:** 🔒 frozen

**Anchor (journal: date · title):** journal: 2026-10-19 · onboarding-perfil (apply)
