---
date: 2026-10-18
status: done
---

[2026-10-18] `scripts/generate-client.sh` y `bun run lint` (biome `--write --unsafe`) reformatean también
`frontend/tests/`: el implementer del grupo 2 de receta-mexicana tuvo que restaurar el spec del tester con git.
Candidato: excluir `tests/` del barrido de biome en el script (se suma a la fila existente del blast radius).
**✅ Cerrado (fix/dev-migraciones-y-cliente, 2026-10-20)** en lo que toca al script: ya no lintea. `bun run lint`
a mano sigue formateando todo `frontend/` por diseño; un implementer no lo corre a mitad de tarea.
