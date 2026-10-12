# 2026-10-11 — Ejecución de cuenta-consentimiento (US-01)

## Ronda review→apply (misma fecha, al final del día)
- /epe-4-review completo: 5 finders paralelos → merge/dedupe (21→20) → 4 validadores por reproducción →
  ronda 2 seca. 16 confirmados (login-CSRF y downgrade PKCE reproducidos de verdad), 3 falsos positivos
  (el "SyntaxError crítico": python del sistema vs 3.14 del proyecto → closed.md). Comentarios FINDER y
  VALIDATOR en el PR #1.
- Saúl Pérez aprobó los 13 grupos de hallazgos SIN diferir nada; preguntó si se corrió openspec verify —
  respuesta honesta: no aún; validate --strict sí; /opsx:verify se corre tras el apply.
- /epe-5-apply en dos pasadas (tests c91eb7f rojo 17/83 → impl e8082fe verde): 100 passed/0/0, cobertura
  89.83%→93.69%, Playwright 62, tdd-check ✓ (sanado con el flujo test:), prek 0 fallos. Fixer sin rebotes.
- ADR D13 (cifrado: claves por propósito, MultiFernet, ENCRYPTION_KEY obligatoria fuera de dev). closed.md
  estrenado con 3 veredictos. El guard de force-push bloqueó un amend sobre commit pusheado: se re-emitió
  como commit normal (bien bloqueado).
- Pendiente de Saúl: re-verificación manual del flujo Google con el NUEVO contrato (botón en login →
  Google → /google-callback → sesión en la SPA), porque la 5.1 original se hizo con el flujo viejo.

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
## Ronda de PR y CI (mismo día)
- Repo privado earhackerdem/GlobalHealth creado a pedido de Saúl Pérez; el guard supervisado bloqueó inicializar
  main (correcto) y Saúl lo pushó él mismo. PR #1 abierto (feat → main).
- Investigación de nombre pedida por Saúl: "GlobalHealth" colisiona (aseguradora de Oklahoma con app homónima +
  marca viva en Luxemburgo) → research.md#naming; candidatos Vitacora / Anamnesis; decisión en inbox.
- CI del template adaptado al correr de verdad: (1) playwright.yml necesitaba permissions pull-requests:read para
  paths-filter; (2) pre-commit.yml usaba la GitHub App pr-push del proyecto FastAPI (no instalada aquí) → reescrito
  check-only; (3) typos no sabe español → _typos.toml (excluye prosa es-MX y harness.json); (4) mypy/ty con
  hashed_password nullable → narrowing en tests del template (mantenimiento de tipado, no cambio de aserciones);
  (5) cliente frontend regenerado (faltaba GET /health-records/{id}). pre-commit, test-backend (cobertura 90%) y
  changes en verde en CI.

- Incidente de proceso: un commit (c27cd79) entró con la suite completa aparentemente roja — era interferencia
  del tester del grupo 3 corriendo pytest contra la misma BD en paralelo; verificado aislando (62 passed) después
  del commit. Lección: no correr suites de verificación mientras un subagente ejecuta pytest sobre la misma BD;
  el pipe `pytest | tail` además se traga el exit code (candidato a mejora: verificar exit codes, no solo tail).

## Archivo (2026-10-12)
- cuenta-consentimiento archivado tras el merge del PR #1: deltas fusionados en openspec/specs/{identity,privacy}
  (6 requirements), CHANGELOG estrenado, fila de cobertura cerrada en el inbox (93.69%). Sin sorpresas.
