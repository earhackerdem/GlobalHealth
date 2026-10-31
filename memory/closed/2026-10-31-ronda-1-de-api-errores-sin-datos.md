---
date: 2026-10-31
state: deferred
anchor: journal: 2026-10-31 · api-errores-sin-datos: los errores de la API no repiten datos de salud (B1 y S2)
---
Ronda 1 de api-errores-sin-datos (PR #46): L1 y L8 quedan como deuda; L9 es un falso positivo como defecto. Los demás (M2, M3, L2–L7, L10) se corrigieron en el PR

**Verdict and why:** gate por delegación de Saúl Pérez (author), con la reproducción del validador del 2026-10-31.
- **L1 (deuda, baja):** un valor de discriminador inválido (`POST /profile/history` con `{"section": "<texto>"}`,
  o `when.kind`) vuelve en `msg` («Input tag '…' found using 'section'») y en `ctx.tag`. Una clave desconocida
  (`extra_forbidden`) vuelve en `loc`. Solo regresa a quien la mandó, no se escribe en el log, y la UI solo envía
  valores del catálogo. La spec se limitó a `input`. Para pagarla, el handler reescribe `msg` y quita `ctx` en
  `union_tag_invalid`.
- **L8 (deuda, baja, preexistente):** con `traces_sample_rate=1.0`, cada transacción lleva `request.query_string`;
  `GET /login/google/callback?code=…&state=…` manda el `code` de OAuth, que es de un solo uso y va atado a PKCE.
  Hoy no hay DSN. Para pagarla, un `before_send_transaction` que quite `query_string`, antes de encender Sentry.
- **L9 (falso positivo como defecto):** el teardown `sentry_sdk.init()` leería `SENTRY_DSN` del entorno, pero ese
  entorno no lo define en ninguna parte (`compose.yml` lo deja vacío; `.github/` no lo tiene).

**State:** ⏸️ deferred

**Anchor (journal: date · title):** journal: 2026-10-31 · api-errores-sin-datos: los errores de la API no repiten datos de salud (B1 y S2)
