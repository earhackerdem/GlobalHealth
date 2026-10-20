# Meta-improvements — proposals for the harness itself and their verdict

Includes rejections: a retro that repeats the previous one's menu manufactures friction. Before proposing with
/session-retro, read this; a rejected proposal does not come back without new evidence.

| Date | Proposal | Verdict | Why | Where it lives (PR, file) |
|---|---|---|---|---|
| 2026-10-11 | El skill `product-tech-brief` debería incluir el **entorno de desarrollo local** (¿Docker para la BD? ¿gestor de venv/deps?) en su pregunta bloqueante y como sección del template, no solo hosting/CI | Proposed | Vacío detectado por Saúl Pérez antes de aprobar US-01: stack y hosting decididos, entorno local sin decidir; se resolvió ad hoc con ADR D12. Upstream al template del harness vía rama improve/ cuando se decida | memory/decisions.md § D12 |
| 2026-10-11 | tdd-check/barrera test→impl no contempla el caso "la implementación vive en ruta de tests" (conftest.py): el verde entra como commit `test:` y el gate pasa vacuamente para ese grupo. Propuesta: regla explícita en epe-3-execute + tdd-check que distinga conftest/infra de tests de aserciones | Proposed | Visto en bd-pruebas-docker (2026-10-11): el verde del grupo 2 vivía en backend/tests/conftest.py, donde guard-tests bloquea al implementer; se commiteó como `test:` y tdd-check pasó sin verificar nada para ese grupo | openspec/changes/archive/2026-10-12-bd-pruebas-docker/evidence.md § Asimetría documentada del grupo 2 |

- [2026-10-12 · Proposed] El harness no tiene gate entre "commit verde local" y "push": tres fallos de pre-commit en CI
  (PR #2 de GlobalHealth) fueron pushes sin pasada prek local. Propuesta: make install-hooks que instale un pre-push
  corriendo prek sobre el diff vs la rama base (hoy instalado ad-hoc en .git/hooks/pre-push de este repo).

- [2026-10-12 · Proposed] El gate humano de /opsx:propose–/epe-2-plan es textual (specs/design) y los no programadores
  no lo leen: la expectativa rota de expediente-registros (receta ≠ modelo mexicano real) se detectó DESPUÉS de un
  ciclo completo. Propuesta upstream: paso opcional de prototipo mock navegable junto a las specs (artifact clickeable
  con datos de ejemplo, o prompt generado para Claude Design/v0/Stitch), y el gate pide validar el prototipo además
  de aprobar el plan. Demostrado ad hoc en GlobalHealth: https://claude.ai/artifact/PJUNDJ5d2c8R8YHq6qPXtZ
| 2026-10-18 | Prototype gate: el HTML del mock se versiona en el repo (`product/prototipos/`) — los artifacts hospedados están ligados a una cuenta (Saúl usa varias) — y el panel de criterios abre con la historia de usuario textual | ✅ aplicado upstream (template commit 2911d83: product-discovery paso 6 + epe-2-plan prototype gate); llega aquí con el próximo `make harness-update` | Saúl Pérez |

- [2026-10-20 · Applied 0.3.1, traído con `make harness-update`] Pedidos de Saúl Pérez al cerrar el review de
  perfil-eventos (PR #20): (1) exploración en navegador como paso numerado de epe-3-execute y repetida en
  epe-5-apply: explora primero el agente; sin defectos valida el humano; con defectos, el agente rehace o se
  detiene si hace falta criterio humano. (2) AGENTS.md § Meta-improvement "Harness first". Saúl la pidió en
  CLAUDE.md; va en AGENTS.md porque vale para todos los agentes y CLAUDE.md la importa. (3) Prototipos sin copia
  hospedada salvo que se pida. La regla del HTML local ya estaba en el template desde 2026-10-18 (2911d83), pero
  aquí no llegó hasta esta actualización: el proyecto se quedó dos días en 0.2.0. Template:
  ../harness, rama `improve/exploracion-navegador-y-harness-primero` (25b4956). Pendiente upstream, en su inbox:
  un guard de `navigate` a URLs locales, un aviso cuando el template es más nuevo que el proyecto, y que
  `gate-plan` no ve archivos de worktrees secundarios.

- [2026-10-20 · Applied 0.3.2, traído con `make harness-update`] Archivar dentro del PR del cambio (propuesta de
  Saúl Pérez): `/epe-6-archive` es el último commit del mismo PR, al final de `/epe-5-apply`, y archivar tras el merge
  queda solo como respaldo. Evidencia de aquí: #14 y #17 fueron PRs solo de archivo; #17 necesitó cherry-pick y
  rebase. Template: PR earhackerdem/harness#1. `openspec/config.yaml` (del proyecto) se corrigió a mano porque
  `harness-update` no lo toca.

