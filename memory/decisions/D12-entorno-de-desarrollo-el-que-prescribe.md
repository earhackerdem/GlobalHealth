---
id: D12
date: 2026-10-11
status: accepted
---

## D12 — Entorno de desarrollo: el que prescribe el template (Docker Compose + uv)
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner), al detectar el vacío antes de aprobar US-01
- **Decision:** el entorno local es el documentado por el propio template: **Docker Compose** para Postgres y el
  stack completo (con `watch` para hot reload) y **uv** como gestor de entorno virtual y dependencias de Python
  (el template migró de Poetry a uv en sept 2024 [VERIFIED: memory/research.md#stack]); Node para el frontend.
  Nada de Postgres instalado nativo ni venvs manuales. T1 de `cuenta-consentimiento` lo confirma empíricamente
  contra el development.md oficial y actualiza este ADR si difiere.
- **Why:** mantener el entorno que el template mantiene es cero fricción de upgrade y cero documentación propia;
  un entorno custom diverge en el primer update. Detectado por Saúl Pérez: ni el technical brief ni el harness
  tenían un paso explícito de entorno de desarrollo (→ meta-mejora propuesta).
- **Discarded:** Postgres nativo en la máquina (drift entre sesiones/máquinas); pip/poetry manual (el template ya
  no lo usa).
