---
id: D15
date: 2026-10-12
status: accepted
---

## D15 — Localización: react-i18next con es-MX como único locale embarcado
- **Status:** Accepted · 2026-10-12 · decided by: Saúl Pérez (author/owner), a pedido directo ("prefiero el
  paquete de React"). Cubre NFR-012.
- **Decision:** react-i18next + i18next (pins exactos) con `es-MX` único, recursos estáticos en 7 namespaces por
  dominio (`frontend/src/locales/es-MX/`), sin selector de idioma ni detección de locale. El backend NO usa
  biblioteca i18n: `detail=`/`message=` visibles y asuntos de correo son strings es-MX directos; los correos
  transaccionales se redactan en las plantillas React Email y se regeneran con `bun run export`. Los códigos de
  máquina (p. ej. `CONSENT_REQUIRED`) no se traducen. El chrome de UI del gate de consentimiento se mueve a
  recursos byte a byte; el texto legal sigue sirviéndose desde el backend (consent_text.py) y no se toca.
- **Why:** un solo locale con infraestructura lista para el segundo (añadir JSON + selector, con recarga; el
  cambio de idioma en caliente exigiría mover los `i18n.t` de module scope a render-time) sin pagar hoy
  gettext/babel en el backend; la suite Playwright con textos es-MX queda como contrato del idioma (177+
  aserciones), que es donde se rompería una regresión.
- **Discarded:** traducción directa sin biblioteca (decisión explícita de Saúl en contra, inbox 2026-10-12);
  i18n también en backend (cero variación de locale no lo justifica); claves = texto inglés (ata los recursos a
  la redacción vieja).
- **Consequence:** todo string nuevo de UI nace en `locales/es-MX/<ns>.json` y se consume con `t()`; los tests
  E2E asiertan el texto es-MX exacto del recurso; `components/ui/` (shadcn) queda fuera del barrido por no tener
  texto propio.
