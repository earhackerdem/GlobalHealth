# Inbox

Entry is cheap (one row: what and why it matters, no research, no decision). Exit is mandatory: ✅ done (anchor to
the PR or commit), ❌ discarded (reason), 💤 snoozed until YYYY-MM-DD. Nothing is deleted. An inbox item is not a
task: if the person you work with doesn't mention it, it is not started.

## Open

| Date | What | Why it matters | Status |
|---|---|---|---|
| 2026-10-11 | Decidir nombre del producto (repo hoy: GlobalHealth). Candidatos investigados en research.md#naming: Vitacora (sin colisiones encontradas, pegajoso, semántico es), Anamnesis (muy semántico, solo usos académicos). GlobalHealth descartable: aseguradora con app homónima + marca viva | El nombre aparecerá en tiendas y marca; renombrar el repo es trivial (gh repo rename, GitHub redirige), renombrar una marca publicada no | abierto |
| 2026-10-11 | Traducir es-MX el resto de la UI del template (login, settings, sidebar…); hoy solo las pantallas nuevas están en español (NFR-012) | NFR-012 exige toda la UI es-MX; merece story propia | abierto |
| 2026-10-11 | Cobertura backend exactamente en 90% (= umbral del CI): cubrir app/core/google_oauth.py (camino real) o ajustar estrategia antes de que un cambio legítimo tire el CI | Margen cero rompe PRs futuros por razones ajenas al cambio | abierto |
| 2026-10-11 | Decidir si despersonalizar los artefactos de bd-pruebas-docker (narran con nombre el uso de la identidad Google real como dato dev) antes de cualquier apertura del repo — observación G20 de la revisión | Los artefactos quedan en el repo; si el repo se abre, exponen que la identidad Google real de una persona nombrada se usa como dato de desarrollo | abierto |

## Closed

| Date | What | Closure |
|---|---|---|
