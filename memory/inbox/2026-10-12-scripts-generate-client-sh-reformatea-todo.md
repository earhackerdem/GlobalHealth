---
date: 2026-10-12
status: done
---

`scripts/generate-client.sh` reformatea TODO el árbol del frontend (`biome --write --unsafe`) como efecto colateral de regenerar el cliente; sorprendió al implementer del grupo 3 de expediente-registros

**Why it matters:** Un script de codegen no debería tocar archivos ajenos a `src/client/`; radio de daño inesperado en working trees sucios

**Status:** ✅ cerrado (fix/dev-migraciones-y-cliente, 2026-10-20): el script ya no corre `bun run lint`; el cliente está excluido de biome y el resto se formatea al commitear (hook local-biome-check)
