---
date: 2026-10-20
status: applied
---

[2026-10-20 · Applied 0.3.1, traído con `make harness-update`] Pedidos de Saúl Pérez al cerrar el review de
perfil-eventos (PR #20): (1) exploración en navegador como paso numerado de epe-3-execute y repetida en
epe-5-apply: explora primero el agente; sin defectos valida el humano; con defectos, el agente rehace o se
detiene si hace falta criterio humano. (2) AGENTS.md § Meta-improvement "Harness first". Saúl la pidió en
CLAUDE.md; va en AGENTS.md porque vale para todos los agentes y CLAUDE.md la importa. (3) Prototipos sin copia
hospedada salvo que se pida. La regla del HTML local ya estaba en el template desde 2026-10-18 (2911d83), pero
aquí no llegó hasta esta actualización: el proyecto se quedó dos días en 0.2.0. Template:
../harness, rama `improve/exploracion-navegador-y-harness-primero` (25b4956). Pendiente upstream, en su inbox:
un guard de `navigate` a URLs locales, un aviso cuando el template es más nuevo que el proyecto, y que
`gate-plan` no ve archivos de worktrees secundarios.
