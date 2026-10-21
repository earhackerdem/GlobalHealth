## Stack y proveedores (technical brief) <a id="stack"></a>
- **Fact:** Anthropic no entrena modelos con contenido de clientes de la API por defecto (Commercial Terms);
  retención por defecto reportada en conflicto entre fuentes (7 días desde sept 2025 vs 30 días); ZDR existe pero
  se solicita, no es automático.
- **Source:** https://aibusiness.com/nlp/anthropic-will-not-train-its-ai-on-clients-data ·
  https://char.com/blog/anthropic-data-retention-policy (secundarias) · consulted 2026-10-11
- **Confidence:** [VERIFIED] el no-training por defecto (múltiples fuentes coincidentes); NOT VERIFIED la ventana
  de retención exacta → ir a Commercial Terms/DPA oficiales antes del primer dato real (NFR-005).
- **Re-check if:** SIEMPRE antes de mandar el primer dato de salud real; política puede cambiar.

- **Fact:** El template full-stack de tiangolo vive hoy en la org fastapi (github.com/fastapi/full-stack-fastapi-template):
  FastAPI + SQLModel + Postgres + Alembic, React/TS + Vite + Tailwind + shadcn, Docker Compose + Traefik, GH Actions,
  pytest + Playwright. MIT. Snapshot feb 2026.
- **Source:** https://github.com/fastapi/full-stack-fastapi-template y https://fastapi.tiangolo.com/project-generation ·
  consulted 2026-10-11
- **Confidence:** [VERIFIED]
- **Re-check if:** se reconsidera el stack (ADR D6 lo descartó para v1).

- **Fact:** El template migró de Poetry a uv (#1356) y adoptó `docker compose watch` para desarrollo local (#1354),
  ambos en septiembre 2024; los archivos compose fueron renombrados a compose.yml (#2106). Entorno local documentado:
  Docker Compose para los servicios + uv para el venv/deps del backend.
- **Source:** https://code.morphllm.com/fastapi/full-stack-fastapi-template/commits/0.8.0/master/backend/README.md
  (mirror del commit log) · consulted 2026-10-11
- **Confidence:** [VERIFIED] la migración a uv y compose watch (commit log); los comandos exactos del development.md
  vigente NOT VERIFIED → T1 los confirma contra el repo oficial.
- **Re-check if:** T1 de cuenta-consentimiento (instalación real).

- **Fact (T1, empírico):** el método oficial de instalación HOY es el botón "Use this template" de GitHub (ya no
  copier; hooks/post_gen_project.py es residuo del generador). Clonado el repo oficial (commit 7257e60,
  2026-10-08): el frontend usa **bun** (workspaces: frontend + packages/react-email) y biome, el backend sirve el
  frontend construido desde backend/app/frontend (los tests lo exigen), tests del backend en `backend/tests/`,
  flujo dev: `docker compose up -d db mailpit` + `uv sync` + `uv run bash scripts/prestart.sh` + `uv run fastapi dev`
  + `bun install` + `bun run dev`. Playwright levanta Vite solo (webServer) y lee credenciales del .env raíz.
  OJO: la suite de pytest limpia datos de la BD local compartida (re-correr prestart tras pytest para re-sembrar).
- **Source:** clon local del template (scratchpad), README.md y development.md del commit 7257e60 · verified 2026-10-11
- **Confidence:** [VERIFIED] (ejecutado: pytest 58 passed, Playwright chromium 62 passed)
- **Re-check if:** make harness-update del template / upgrade del template.

- **Fact:** LFPDPPP: datos de salud = sensibles; art. 9 exige consentimiento expreso y por escrito (o equivalente)
  para tratarlos, con carga de la prueba en el responsable; existe excepción de transferencia para
  prevención/diagnóstico médico (citada como art. 36 o 37 según la fuente — numeración por confirmar en DOF).
  La reforma 2025 habría cambiado la autoridad (ya no INAI) — NOT VERIFIED.
- **Source:** https://sdv.com.mx/compendio/ley-proteccion-datos-personales/articulo-9/ ·
  https://sdv.com.mx/compendio/ley-proteccion-datos-personales/articulo-37/ ·
  https://iapp.org/news/a/la-proteccion-de-datos-personales-en-los-expedientes-clinicos · consulted 2026-10-11
- **Confidence:** [VERIFIED] el principio (consentimiento expreso para sensibles); NOT VERIFIED numeración vigente,
  reforma 2025 y autoridad competente → texto en DOF + abogado antes de abrir a usuarios distintos de Saúl (NFR-004).
- **Re-check if:** antes del primer cambio de cumplimiento; antes de cualquier usuario externo.
