#! /usr/bin/env bash

set -e
set -x

cd backend
FASTAPI_ENV=development uv run python -c "import app.main; import json; print(json.dumps(app.main.app.openapi()))" > ../openapi.json
cd ..
mv openapi.json frontend/
bun run --filter frontend generate-client
# Sin `bun run lint`: el cliente generado está excluido de biome (frontend/biome.json) y el lint con --write
# --unsafe reformateaba TODO el frontend, frontend/tests incluido, a mitad de la tarea de un implementer.
# El formateo del resto del árbol lo hace el hook local-biome-check al commitear.
