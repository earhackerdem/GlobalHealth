---
date: 2026-10-20
status: done
---

[2026-10-20] El daemon de Docker Desktop de la máquina de Saúl no logra bajar imágenes base (ghcr.io/astral-sh/uv,
python:3.14: `DeadlineExceeded` vía el proxy `http.docker.internal:3128`), aunque el host sí llega a ghcr.io. Sin
rebuild, `make migrate` aplica migraciones que el contenedor no trae. Revisar la configuración de proxy de Docker
Desktop; mientras tanto, `docker compose cp backend/app backend:/app/backend/` o `docker compose watch`.

**Cerrado 2026-10-28 (barrido de memoria):** `docker pull ghcr.io/astral-sh/uv:0.9.26` y `docker pull busybox:1.37` bajan sin error, y el 2026-10-26 `docker compose up -d --build` reconstruyó el backend. No se sabe qué lo arregló; si vuelve, reabrir con el error literal.
