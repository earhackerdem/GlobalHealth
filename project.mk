# Comandos propios de GlobalHealth — extensión local del Makefile del harness (lo carga vía -include project.mk).
# El Makefile del harness es dependencia vendida y no se edita; lo del producto vive aquí.

.PHONY: setup up front down stop logs

setup: ## Prepara el entorno local: .env desde .env.example (si falta) + dependencias de backend y frontend
	@test -f .env || { cp .env.example .env; echo "⚠ .env creado desde .env.example: revisa SECRET_KEY, FIRST_SUPERUSER* y, si usarás Google, las GOOGLE_*"; }
	cd backend && uv sync
	bun install
	cd frontend && bunx playwright install chromium

up: ## Levanta la aplicación en Docker (API :8000, Mailpit :8025, BD y BD de prueba) y espera a que esté sana
	docker compose up -d --wait db db-test backend mailpit

front: ## Dev server del frontend con recarga (http://localhost:5173); la API la da make up
	cd frontend && bunx vite

down: ## Detiene y ELIMINA los contenedores (la BD de desarrollo conserva su volumen)
	docker compose down

stop: ## Detiene los contenedores sin eliminarlos
	docker compose stop

logs: ## Sigue los logs del backend (Ctrl-C para salir)
	docker compose logs -f backend
