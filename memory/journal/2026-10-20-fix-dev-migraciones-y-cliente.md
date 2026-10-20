# 2026-10-20 · fix: migraciones al levantar y codegen sin lint

**Quién:** Saúl Pérez (author) eligió, en el gate de la exploración de perfil-eventos, arreglar estos dos
tropiezos del inbox en un PR aparte antes de ejecutar la story.

**Qué:**
- **Migraciones:** el `compose.yml` del repo no trae el servicio `prestart` del template. Por eso `make up` no
  migraba, y solo `scripts/test.sh` y el CI corrían `prestart.sh`. Ahora `make up` termina llamando a
  `make migrate`, que corre `docker compose exec -T backend bash scripts/prestart.sh` y también sirve a mano
  después de crear una migración.
- **Codegen:** `scripts/generate-client.sh` ya no corre `bun run lint`. Ese paso era `biome --write --unsafe`
  sobre todo `frontend/`, y el cliente generado ya está excluido de biome.

**Verificación:**
- `make up`: verde.
- `make migrate` dos veces: exit 0; `alembic current` = `heads` = f4b2c7d81e93.
- `generate-client.sh`: exit 0, cliente idéntico, cero archivos tocados fuera de los dos editados.
