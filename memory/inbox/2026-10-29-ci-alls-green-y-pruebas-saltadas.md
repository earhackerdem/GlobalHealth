---
date: 2026-10-29
status: open
---
CI: `alls-green-*` no espera al job `changes`, y ningún workflow falla con pruebas saltadas (X4 y D7 de la revisión del PR #44)

**Why it matters:** los dos huecos son de las compuertas de CI.
- **`alls-green-*`:** en `test-android.yml`, `test-backend.yml`, `test-docker-compose.yml` y `playwright.yml` solo
  tiene `needs: <job de pruebas>`. Si `changes` (dorny/paths-filter) falla, el job de pruebas queda en skipped,
  `allowed-skips` lo acepta y la compuerta sale verde sin haber probado nada.
- **Pruebas saltadas:** «truly green» exige 0 saltadas (AGENTS.md), pero hoy eso se comprueba a mano en
  `evidence.md`.

Se arregla en los cuatro workflows a la vez, en una rama `fix/` o `improve/` aparte, no dentro de un cambio de
producto.
