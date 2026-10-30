---
date: 2026-10-29
---

# CI: los tests del backend y de docker compose solo corren si cambió algo que prueban

**Quién e intención.** Saúl Pérez (autor) notó que el PR #42, que era solo de documentos, corría el CI completo. Preguntó
si tenía sentido saltarse los tests cuando solo cambian `.md`. Dijo «procede» a la propuesta del agente.

**Qué se hizo.**
- `test-backend.yml` y `test-docker-compose.yml` siguen el patrón que ya tenía `playwright.yml`: un job `changes`
  con `dorny/paths-filter` y un job `alls-green` que siempre reporta.
- Se usó una lista positiva por job en vez de «solo `.md`», así un cambio en `scripts/` o en la memoria tampoco
  dispara los tests.
  - **test-backend:** `backend/**`, `.env.example`, `compose*.yml`, `.python-version`, `pyproject.toml`, `uv.lock` y
    su propio workflow.
  - **test-docker-compose:** lo mismo más `frontend/**`, `package.json` y `bun.lock`, porque la imagen del backend
    hace el build del frontend (`backend/Dockerfile:5-12`).
- `pre-commit` sigue corriendo siempre: revisa justo los `.md` (`typos`, espacios, fin de archivo).
- **Fuera de lo pedido, en el mismo archivo:** el filtro de Playwright vigilaba `.env`, que no está en git, en vez de
  `.env.example`, que es lo que usa el CI. También le faltaban `package.json`, `bun.lock` y `uv.lock`, que la imagen
  copia.

**Por qué no `paths-ignore`.** `main` no tiene protección de rama hoy (`gh api …/branches/main/protection` da 404).
Si algún día los checks fueran obligatorios, un workflow que no arranca dejaría el check «pendiente» para siempre. El
job `alls-green` lo evita.

**Verificación.**
- Los tres YAML se leen bien, y prek pasa limpio (`check yaml`, `zizmor`).
- Este PR cambia los dos workflows, así que corre los dos tests: así tiene que ser.
- **Pendiente:** confirmar que un PR solo de documentos se los salta. Se ve en el primer PR de documentos después del
  merge (el #42, una vez rebasado sobre `main`).
