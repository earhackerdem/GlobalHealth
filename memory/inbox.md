# Inbox

Entry is cheap (one row: what and why it matters, no research, no decision). Exit is mandatory: ✅ done (anchor to
the PR or commit), ❌ discarded (reason), 💤 snoozed until YYYY-MM-DD. Nothing is deleted. An inbox item is not a
task: if the person you work with doesn't mention it, it is not started.

## Open

| Date | What | Why it matters | Status |
|---|---|---|---|
| 2026-10-12 | Atomic Design + Storybook para el frontend (pedido de Saúl Pérez al decidir i18n). Objeción anotada del harness: el template ya trae su propia organización (shadcn/ui + components/ por dominio) y Storybook es mantenimiento no funcional continuo para un solo dev pre-producto; alternativa barata: posponer a cuando haya un segundo consumidor de componentes (diseñador, segundo dev, design system). Si Saúl reafirma, va como story propia con ADR | Reorganizar components/ toca TODO el frontend; mejor decidirlo con exploración y no de pasada | abierto |
| 2026-10-12 | `scripts/generate-client.sh` reformatea TODO el árbol del frontend (`biome --write --unsafe`) como efecto colateral de regenerar el cliente; sorprendió al implementer del grupo 3 de expediente-registros | Un script de codegen no debería tocar archivos ajenos a `src/client/`; radio de daño inesperado en working trees sucios | abierto |

| 2026-10-12 | **Receta a la mexicana** (feedback de Saúl Pérez tras probar el PR #6; no leyó las delta specs y el resultado no cumplió su expectativa): una receta real trae varias medicinas, fecha de expedición y nombre del paciente; NO trae vigencia inicio/fin y normalmente NO trae diagnóstico (se dice de palabra) → el modelo debería ser receta con medicinas[] y diagnóstico como campo opcional, no dos tipos con vigencia obligatoria. Intención de fondo: subir foto de la receta (o cámara) y que OCR+IA llene los campos. Prototipo clickeable para validar el flujo: https://claude.ai/artifact/PJUNDJ5d2c8R8YHq6qPXtZ | Toca el modelo recién fusionable (PR #6), el PRD (FR-005/FR-006; la captura por foto no tiene FR) y FR-025 (recordatorios usaban la vigencia); merece story propia (reshape) + story de captura foto/OCR tras decidir proveedor IA (NFR-005) | abierto |
| 2026-10-12 | **Prototipo mock como paso del ciclo**: pedido de Saúl Pérez — antes de (o junto con) las specs, generar un frontend solo-mock para que usuarios no programadores validen la idea sin leer delta specs; opciones: artifact clickeable generado por el harness (demostrado hoy), o emitir un prompt para Claude Design / v0 / Stitch | El gate humano del propose hoy exige leer specs; un prototipo navegable detecta expectativas rotas ANTES de ejecutar (hoy costó un ciclo completo) → meta-mejora al harness | abierto |

## Closed

| Date | What | Closure |
|---|---|---|
| 2026-10-11 | Traducir es-MX el resto de la UI del template (login, settings, sidebar…) — NFR-012. Decisión de Saúl Pérez (2026-10-12): con **react-i18next**, no traducción directa | ✅ Resuelto por el cambio ui-es-mx-i18next (PR #4, fusionado 2026-10-12): toda la UI, errores del API y correos en es-MX desde recursos i18next; Playwright asierta los textos como contrato. Archivado en openspec/changes/archive/2026-10-12-ui-es-mx-i18next |
| 2026-10-11 | Cobertura backend exactamente en 90% (= umbral del CI) | ✅ Resuelto en el apply de la revisión del PR #1 (tests de google_oauth con httpx mockeado + decrypt_str): 93.69% real, ~3.7 pts de margen. Archivado con cuenta-consentimiento (2026-10-12) |
| 2026-10-11 | Decidir nombre del producto (candidatos: Vitacora, Anamnesis; colisiones de GlobalHealth en research.md#naming) | 💤 Decisión de Saúl Pérez (2026-10-12): se queda GlobalHealth por el momento; re-evaluar ANTES de publicar en tiendas o abrir el repo (ahí la colisión de marca sí muerde). Candidatos siguen en research.md#naming |
| 2026-10-11 | Despersonalizar los artefactos (identidad Google real narrada como dato dev — G20) | ✅ Aplicado a pedido de Saúl Pérez (2026-10-12, PR #3): specs, evidence y journal reescritos a "usuario OAuth real"/"cuenta Google del propietario"; correo literal retirado de evidence. LÍMITE honesto: la historia de git conserva las versiones viejas — una apertura del repo exigiría además squash/reescritura de historia o repo nuevo. La identidad git de los commits (nombre+correo) se mantiene: es metadato de autoría presente en cada commit |
- [2026-10-18] Spike Android / IA en dispositivo (pedido implícito de Saúl Pérez al anunciar su S26 Ultra 1TB/16GB):
  evaluar ML Kit GenAI (Gemini Nano on-device) leyendo recetas del corpus real de 74 fotos como candidato a
  proveedor Q4/NFR-005 — cero retención por construcción, costo cero. Acotado: un spike con criterios medibles
  (¿cuántas recetas impresas/manuscritas extrae bien? ¿límite de tokens de salida alcanza?), NO la app Android
  completa. Entra vía tech-brief cuando se cierre el gate del discovery. Recomendación del harness registrada:
  web primero mientras el modelo de dominio se asienta.
- [2026-10-18] Q1-B diferida (decisión de Saúl Pérez al cerrar Q1 con A): vigencia derivada de la duración del
  tratamiento (inferida por IA, editable) como complemento del archivado manual — retomar cuando el proveedor de
  IA (Q4/tech-brief) esté resuelto.
- [2026-10-18] BYOK para la capa IA (idea de Saúl Pérez): el usuario elige proveedor/API key propia; opción
  "gratis" vía Google AI Studio DESCARTADA para datos reales (términos permiten entrenamiento + revisores humanos;
  memory/research.md 2026-10-18). Diseñar con lista blanca de proveedores/modos compatibles con NFR-005 y análisis
  LFPDPPP. Entra al tech-brief del proveedor junto con el spike on-device (D17).
- [2026-10-18] `scripts/generate-client.sh` y `bun run lint` (biome `--write --unsafe`) reformatean también
  `frontend/tests/`: el implementer del grupo 2 de receta-mexicana tuvo que restaurar el spec del tester con git.
  Candidato: excluir `tests/` del barrido de biome en el script (se suma a la fila existente del blast radius).
