# Inbox

Entry is cheap (one row: what and why it matters, no research, no decision). Exit is mandatory: ✅ done (anchor to
the PR or commit), ❌ discarded (reason), 💤 snoozed until YYYY-MM-DD. Nothing is deleted. An inbox item is not a
task: if the person you work with doesn't mention it, it is not started.

## Open

| Date | What | Why it matters | Status |
|---|---|---|---|
| 2026-10-11 | Traducir es-MX el resto de la UI del template (login, settings, sidebar…); hoy solo las pantallas nuevas están en español (NFR-012) | NFR-012 exige toda la UI es-MX; merece story propia | abierto |
| 2026-10-11 | Decidir si despersonalizar los artefactos de bd-pruebas-docker (narran con nombre el uso de la identidad Google real como dato dev) antes de cualquier apertura del repo — observación G20 de la revisión | Los artefactos quedan en el repo; si el repo se abre, exponen que la identidad Google real de una persona nombrada se usa como dato de desarrollo | abierto |

## Closed

| Date | What | Closure |
|---|---|---|
| 2026-10-11 | Cobertura backend exactamente en 90% (= umbral del CI) | ✅ Resuelto en el apply de la revisión del PR #1 (tests de google_oauth con httpx mockeado + decrypt_str): 93.69% real, ~3.7 pts de margen. Archivado con cuenta-consentimiento (2026-10-12) |
| 2026-10-11 | Decidir nombre del producto (candidatos: Vitacora, Anamnesis; colisiones de GlobalHealth en research.md#naming) | 💤 Decisión de Saúl Pérez (2026-10-12): se queda GlobalHealth por el momento; re-evaluar ANTES de publicar en tiendas o abrir el repo (ahí la colisión de marca sí muerde). Candidatos siguen en research.md#naming |
