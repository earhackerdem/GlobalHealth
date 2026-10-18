# Inbox

Entry is cheap (one row: what and why it matters, no research, no decision). Exit is mandatory: ✅ done (anchor to
the PR or commit), ❌ discarded (reason), 💤 snoozed until YYYY-MM-DD. Nothing is deleted. An inbox item is not a
task: if the person you work with doesn't mention it, it is not started.

## Open

| Date | What | Why it matters | Status |
|---|---|---|---|
| 2026-10-12 | Atomic Design + Storybook para el frontend (pedido de Saúl Pérez al decidir i18n). Objeción anotada del harness: el template ya trae su propia organización (shadcn/ui + components/ por dominio) y Storybook es mantenimiento no funcional continuo para un solo dev pre-producto; alternativa barata: posponer a cuando haya un segundo consumidor de componentes (diseñador, segundo dev, design system). Si Saúl reafirma, va como story propia con ADR | Reorganizar components/ toca TODO el frontend; mejor decidirlo con exploración y no de pasada | abierto |
| 2026-10-12 | `scripts/generate-client.sh` reformatea TODO el árbol del frontend (`biome --write --unsafe`) como efecto colateral de regenerar el cliente; sorprendió al implementer del grupo 3 de expediente-registros | Un script de codegen no debería tocar archivos ajenos a `src/client/`; radio de daño inesperado en working trees sucios | abierto |

## Closed

| Date | What | Closure |
|---|---|---|
| 2026-10-11 | Traducir es-MX el resto de la UI del template (login, settings, sidebar…) — NFR-012. Decisión de Saúl Pérez (2026-10-12): con **react-i18next**, no traducción directa | ✅ Resuelto por el cambio ui-es-mx-i18next (PR #4, fusionado 2026-10-12): toda la UI, errores del API y correos en es-MX desde recursos i18next; Playwright asierta los textos como contrato. Archivado en openspec/changes/archive/2026-10-12-ui-es-mx-i18next |
| 2026-10-11 | Cobertura backend exactamente en 90% (= umbral del CI) | ✅ Resuelto en el apply de la revisión del PR #1 (tests de google_oauth con httpx mockeado + decrypt_str): 93.69% real, ~3.7 pts de margen. Archivado con cuenta-consentimiento (2026-10-12) |
| 2026-10-11 | Decidir nombre del producto (candidatos: Vitacora, Anamnesis; colisiones de GlobalHealth en research.md#naming) | 💤 Decisión de Saúl Pérez (2026-10-12): se queda GlobalHealth por el momento; re-evaluar ANTES de publicar en tiendas o abrir el repo (ahí la colisión de marca sí muerde). Candidatos siguen en research.md#naming |
| 2026-10-11 | Despersonalizar los artefactos (identidad Google real narrada como dato dev — G20) | ✅ Aplicado a pedido de Saúl Pérez (2026-10-12, PR #3): specs, evidence y journal reescritos a "usuario OAuth real"/"cuenta Google del propietario"; correo literal retirado de evidence. LÍMITE honesto: la historia de git conserva las versiones viejas — una apertura del repo exigiría además squash/reescritura de historia o repo nuevo. La identidad git de los commits (nombre+correo) se mantiene: es metadato de autoría presente en cada commit |
