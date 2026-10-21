---
date: 2026-10-11
status: applied
---

tdd-check/barrera test→impl no contempla el caso "la implementación vive en ruta de tests" (conftest.py): el verde entra como commit `test:` y el gate pasa vacuamente para ese grupo. Propuesta: regla explícita en epe-3-execute + tdd-check que distinga conftest/infra de tests de aserciones

**Verdict:** ✅ Applied 0.2.0 como regla declarada (verificado 2026-10-20: `.agents/skills/epe-3-execute/SKILL.md:57`, "Known asymmetry"); `tdd-check` sigue sin distinguir conftest

**Why:** Visto en bd-pruebas-docker (2026-10-11): el verde del grupo 2 vivía en backend/tests/conftest.py, donde guard-tests bloquea al implementer; se commiteó como `test:` y tdd-check pasó sin verificar nada para ese grupo

**Where it lives (PR, file):** openspec/changes/archive/2026-10-12-bd-pruebas-docker/evidence.md § Asimetría documentada del grupo 2
