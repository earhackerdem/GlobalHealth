# 2026-10-20 · perfil-eventos: archivado (PR #20)

**Quién:** Saúl Pérez (author) validó con `validation.md`, mergeó el PR #20 y pidió incluir su validación en el
archivo.

**Qué:** su `validation.md` entra con A-1 a A-8 marcados (commit a su nombre). A-9, el cifrado, no se clickea: lo
cubre la prueba automática de `evidence.md`. `openspec archive` fusionó el delta en
`openspec/specs/records/patient-profile/spec.md` (+5 requisitos, ~1 modificado) y movió la carpeta a
`openspec/changes/archive/2026-10-20-perfil-eventos/`. `openspec validate --specs`: 6 passed, 0 failed.
- Truth refresh: `product/prd.md` (US-18) y `product/dominio.md` (Story A) marcan la Story A como entregada. Ningún
  skill, doc ni README citaba la ruta vieja; solo el journal del cambio, que es registro histórico.
- CHANGELOG actualizado. `.epe/active` borrado.

**Por qué en un PR aparte:** el PR #20 se mergeó antes de archivar. Es el último cambio que sigue ese camino: desde
la 0.3.2 del harness (PR #22) el archivo va como último commit del PR del cambio.

**Para Saúl:** `product/dominio.md` todavía enlaza una copia hospedada del prototipo (`claude.ai/artifact/…`), junto
a la copia local `product/prototipos/perfil-secciones.html`. Con la regla nueva sobra; no la quité sin preguntar.
