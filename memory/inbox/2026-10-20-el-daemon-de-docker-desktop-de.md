---
date: 2026-10-20
status: open
---

[2026-10-20] El daemon de Docker Desktop de la máquina de Saúl no logra bajar imágenes base (ghcr.io/astral-sh/uv,
python:3.14: `DeadlineExceeded` vía el proxy `http.docker.internal:3128`), aunque el host sí llega a ghcr.io. Sin
rebuild, `make migrate` aplica migraciones que el contenedor no trae. Revisar la configuración de proxy de Docker
Desktop; mientras tanto, `docker compose cp backend/app backend:/app/backend/` o `docker compose watch`.
