# 2026-10-11 — Ejecución de cuenta-consentimiento (US-01)

- Saúl Pérez aprobó el design ("plan approved") tras resolver el vacío de entorno (ADR D12) y pedir login con
  Google (FR-026). Rama feat/cuenta-consentimiento desde docs/product-brief.
- Grupo 1 (single): template instalado copiando el repo oficial (método vigente: botón "Use this template",
  commit 7257e60 del 2026-10-08; hallazgos empíricos en memory/research.md#stack). bun instalado vía Homebrew.
  Nota de método: los archivos del template entraron por `cp` (vendored, no autoría propia); los hooks de edición
  no los vieron — límite conocido y declarado en CLAUDE.md.
- Grupos 2-4 (test→impl con subagentes tester/implementer, barrera guard-tests respetada): Google OIDC con PKCE
  y OAuthIdentity.subject en columna cifrada Fernet (NFR-001); consentimiento como dato con evidencia
  {versión, sha256, timestamp, método} + ConsentGate es-MX; aislamiento con 404 uniforme. El design se actualizó
  dos veces durante ejecución (punto de mock de Google; router stub /health-records y GET /consent/text) —
  artefactos vivos, no fosilizados.
- PKCE faltaba tras el primer verde del grupo 2: detectado por el reporte del implementer, devuelto y corregido
  antes del commit (no se recortó el design en silencio). Lo mismo con la pantalla de consentimiento del 3.2.
- Cierre: 73 passed / 0 failed / 0 skipped, Playwright 62 passed, cobertura 90% (= umbral del CI, sin margen),
  tdd-check ✓ (un rojo por grupo). evidence.md y validation.md escritos.
- Bloqueado en Saúl Pérez: credenciales Google para la prueba manual 5.1 y remoto git para abrir el PR.
- Incidente de proceso: un commit (c27cd79) entró con la suite completa aparentemente roja — era interferencia
  del tester del grupo 3 corriendo pytest contra la misma BD en paralelo; verificado aislando (62 passed) después
  del commit. Lección: no correr suites de verificación mientras un subagente ejecuta pytest sobre la misma BD;
  el pipe `pytest | tail` además se traga el exit code (candidato a mejora: verificar exit codes, no solo tail).
