# Meta-improvements — proposals for the harness itself and their verdict

Includes rejections: a retro that repeats the previous one's menu manufactures friction. Before proposing with
/session-retro, read this; a rejected proposal does not come back without new evidence.

| Date | Proposal | Verdict | Why | Where it lives (PR, file) |
|---|---|---|---|---|
| 2026-10-11 | El skill `product-tech-brief` debería incluir el **entorno de desarrollo local** (¿Docker para la BD? ¿gestor de venv/deps?) en su pregunta bloqueante y como sección del template, no solo hosting/CI | Proposed | Vacío detectado por Saúl Pérez antes de aprobar US-01: stack y hosting decididos, entorno local sin decidir; se resolvió ad hoc con ADR D12. Upstream al template del harness vía rama improve/ cuando se decida | memory/decisions.md § D12 |
| 2026-10-11 | tdd-check/barrera test→impl no contempla el caso "la implementación vive en ruta de tests" (conftest.py): el verde entra como commit `test:` y el gate pasa vacuamente para ese grupo. Propuesta: regla explícita en epe-3-execute + tdd-check que distinga conftest/infra de tests de aserciones | Proposed | Visto en bd-pruebas-docker (2026-10-11): el verde del grupo 2 vivía en backend/tests/conftest.py, donde guard-tests bloquea al implementer; se commiteó como `test:` y tdd-check pasó sin verificar nada para ese grupo | openspec/changes/bd-pruebas-docker/evidence.md § Asimetría documentada del grupo 2 |

- [2026-10-12 · Proposed] El harness no tiene gate entre "commit verde local" y "push": tres fallos de pre-commit en CI
  (PR #2 de GlobalHealth) fueron pushes sin pasada prek local. Propuesta: make install-hooks que instale un pre-push
  corriendo prek sobre el diff vs la rama base (hoy instalado ad-hoc en .git/hooks/pre-push de este repo).
