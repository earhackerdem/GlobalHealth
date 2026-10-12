# Proposal

**Origin:** product/prd.md NFR-012 (toda la UI en es-MX) + fila del inbox 2026-10-11; decisión de Saúl Pérez
(2026-10-12): con **react-i18next**, no traducción directa.
**Triage:** change — toca `code` en frontend, backend y emails; una sola historia, mecánica pero extendida (2026-10-12).

## Why

Hoy solo las pantallas construidas en E1 (consentimiento, botón de Google) están en es-MX; el resto del template
está en inglés: 12 rutas (login, signup, recover/reset-password, admin, items, settings, sidebar…), los correos
transaccionales (alta y recuperación de contraseña) y los `detail` de error del backend que la UI muestra en toasts
(`login.py:49 "Incorrect email or password"`, asertado tal cual por Playwright en `login.spec.ts:69`). El usuario
objetivo es mexicano; una app de salud a medias en inglés no cumple NFR-012 ni genera confianza.

Medido antes de proponer: **177 aserciones de texto** en `frontend/tests/*.spec.ts` dependen del inglés actual —
el costo dominante del cambio no es traducir, es mantener la suite E2E como contrato del idioma.

## What Changes

- **react-i18next** instalado e inicializado con `es-MX` como ÚNICO locale embarcado (sin selector de idioma: no
  está en el PRD; añadir un idioma después = añadir un JSON y el selector, la infraestructura queda lista).
- Todos los strings visibles del frontend extraídos a recursos `es-MX` (namespaces por dominio) y consumidos con
  `useTranslation`; cero texto hardcodeado en componentes de cara al usuario.
- Playwright actualizado para asertar los textos es-MX (los tests son el contrato del idioma: en rojo contra la UI
  inglesa, en verde con la traducción).
- `detail` de error del backend que llegan a la UI traducidos a es-MX (y sus aserciones en pytest/Playwright).
- Correos transaccionales (React Email: alta, recuperación) en es-MX, incluidos asunto y remitente visible.
- Fuera de alcance: selector de idioma, segundo locale, traducir logs/mensajes internos del servidor, Adminer/docs.

## Capabilities

### New Capabilities
- `ux/localization`: todo contenido que un usuario ve (pantallas, toasts con errores del API, correos
  transaccionales) se entrega en es-MX desde recursos de traducción, no hardcodeado.

### Modified Capabilities
<!-- ninguna: identity/user-auth, privacy/consent y platform/test-isolation no cambian de comportamiento -->

## Impact

- `frontend/` (package.json +i18next/react-i18next, `src/i18n.ts`, `src/locales/es-MX/*.json`, todas las rutas y
  componentes con texto, `src/main.tsx`), `frontend/tests/**` (177 aserciones), `packages/react-email/emails/*`,
  `backend/app/api/routes/*` y `backend/app/utils.py` (details y asuntos de correo) + `backend/tests/**`.
- Hereda el budget NFR (product/technical-brief.md §4): NFR-012 es el objetivo; sin impacto en NFR-001/004.
- Decisión nueva a registrar: ADR D15 (react-i18next, es-MX único, namespaces).
