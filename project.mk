# Comandos propios de GlobalHealth — extensión local del Makefile del harness (lo carga vía -include project.mk).
# El Makefile del harness es dependencia vendida y no se edita; lo del producto vive aquí.

.PHONY: setup up migrate front down stop logs

setup: ## Prepara el entorno local: .env desde .env.example (si falta) + dependencias de backend y frontend
	@test -f .env || { cp .env.example .env; echo "⚠ .env creado desde .env.example: revisa SECRET_KEY, FIRST_SUPERUSER* y, si usarás Google, las GOOGLE_*"; }
	cd backend && uv sync
	bun install
	cd frontend && bunx playwright install chromium

up: ## Levanta la aplicación en Docker (API :8000, Mailpit :8025, BD y BD de prueba), espera a que esté sana y migra la BD
	docker compose up -d --wait db db-test backend mailpit
	@$(MAKE) --no-print-directory migrate

# El compose de este repo no trae el servicio prestart del template: sin este paso, una migración nueva deja
# la BD de desarrollo atrás y la API responde 500 ("relation ... does not exist") hasta migrar a mano.
migrate: ## Aplica las migraciones pendientes y los datos iniciales a la BD de desarrollo (idempotente; correr tras crear una migración)
	docker compose exec -T backend bash scripts/prestart.sh

front: ## Dev server del frontend con recarga (http://localhost:5173); la API la da make up
	cd frontend && bunx vite

down: ## Detiene y ELIMINA los contenedores (la BD de desarrollo conserva su volumen)
	docker compose down

stop: ## Detiene los contenedores sin eliminarlos
	docker compose stop

logs: ## Sigue los logs del backend (Ctrl-C para salir)
	docker compose logs -f backend
