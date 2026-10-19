# 2026-10-19 · onboarding-perfil (propose + execute)

**Quién:** Saúl Pérez (author) aprobó el plan ("plan approved") tras cerrar el gate del discovery el mismo día;
el harness orquestó propose y execute con tester/implementer separados por grupo.

**Intención:** US-17 — FR-027 (onboarding de perfil post-consentimiento, omitible, una sola vez) + FR-008 (AHF
con línea materna/paterna), con la pantalla "Mi perfil médico" mostrando las secciones futuras vacías.

**Qué se hizo:**
- Propose: proposal + delta spec `records/patient-profile` (7 requisitos, 12 escenarios) + design (Interface
  contract y test plan 1:1 por escenario) + tasks; `openspec validate --strict` verde; gate abierto y aprobado.
- Grupo 1 (backend, test→impl): tester → 10 tests rojos por 404 (commit 9cfeeb9); implementer → 3 tablas
  cifradas (EncryptedString, D13/D16), migración aditiva d5f2a8c41e07, rutas /api/v1/profile tras
  require_consent (commit 1d2bee4). Un test AJENO (receta-mexicana) anclaba head de Alembic y rompía con
  cualquier migración nueva: reanclado a su revisión objetivo (00a1b5b). Verde re-corrido por el orquestador:
  156 passed, cobertura 94%, mypy limpio, tdd-check ✓.
- Grupo 2 (frontend+e2e, test→impl): tester → 3 e2e rojos (fce984e); implementer → wizard 3 pasos en la home,
  /perfil, sidebar, namespace profile es-MX, cliente regenerado (49681a9). Primer verde móvil falló (navegación
  tras el sidebar colapsado a 384px): regresó al tester, que endureció el spec sin debilitar aserciones
  (ec5d74d). Suite Playwright completa como CI: 103 passed (chromium + s26-ultra).
- Exploración real con Claude in Chrome (paso nuevo del ciclo, pedido de Saúl): flujo completo, doble submit,
  datos raros con emoji, cambio de pestaña a medio wizard — todo sano; hallazgos menores a evidence § Deuda.

**Verificación (números re-corridos por el orquestador):** backend 156 passed / 0 fail / 0 skip, cobertura 94%,
mypy limpio; Playwright 103 passed / 0 fail (ambos proyectos); tdd-check ✓ en ambos grupos; exploración manual
documentada en evidence.md.

**Deuda:** fecha futura descartada en silencio en el cliente (el backend sí la rechaza); el contenedor backend
no corre migraciones al arrancar (fila en inbox); sr-only del SidebarTrigger derivado del estado de escritorio
(fila en inbox); PUT feliz de family-history sin test directo; llenado de secciones APP/APNP = FR-028/US-18.

**Siguiente:** PR para review adversarial (/epe-4-review) y merge humano. El PR #15 (discovery) sigue abierto y
es independiente.
