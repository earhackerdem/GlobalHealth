---
id: D13
date: 2026-10-11
status: accepted
---

## D13 — Cifrado app-level: Fernet/MultiFernet vía EncryptedString, claves por propósito
- **Status:** Accepted · 2026-10-11 · decided by: Saúl Pérez (author/owner), al aprobar la revisión adversaria de
  `cuenta-consentimiento` (/epe-4-review → /epe-5-apply)
- **Decision:** el cifrado de datos sensibles en reposo (NFR-001) es app-level con **Fernet** (simétrico,
  autenticado) a través del TypeDecorator `EncryptedString` (`backend/app/core/encrypted.py`), aplicado hoy a
  `OAuthIdentity.subject` y `HealthRecordStub.note` (nota 2026-10-12: `HealthRecordStub` fue sustituido por
  `HealthRecord` en expediente-registros; su texto clínico usa el mismo mecanismo). Derivación de claves **por
  propósito** desde el mismo
  material: la clave de datos es `ENCRYPTION_KEY` tal cual (o, solo en dev, derivada determinista de `SECRET_KEY`)
  y la de la cookie PKCE se deriva con tag (`sha256(key material + b"pkce")`), de modo que comprometer una no
  expone la otra. **`ENCRYPTION_KEY` es obligatoria fuera de development** (el arranque falla sin ella; en dev solo
  advierte, mismo mecanismo que el enforcement de `SECRET_KEY` del template). Rotación: `ENCRYPTION_KEY_PREVIOUS`
  se añade como clave solo-descifrado (**MultiFernet**) mientras se re-cifra el dato existente; después se retira.
- **Why:** Fernet ya viene con `cryptography` (dependencia del template), es autenticado (tampering → token
  inválido, no plaintext corrupto) y MultiFernet da rotación sin migración big-bang. La separación por propósito y
  la obligatoriedad en prod salieron de los hallazgos aprobados de la revisión (clave única para cookie y datos +
  fallback silencioso a SECRET_KEY eran riesgo).
- **Discarded:** cifrado at-rest de Postgres/disco (no protege ante acceso SQL con credenciales); pgcrypto (ata el
  cifrado al motor y mete la clave en el SQL/logs); una sola Fernet para cookie y datos (el estado anterior).
- **Consequence:** columnas cifradas no se filtran por valor en SQL (comparar tras descifrar); E2+ usa
  `EncryptedString` para todo campo clínico; los deploys definen `ENCRYPTION_KEY` dedicada (urlsafe base64, 32
  bytes) y rotan con `ENCRYPTION_KEY_PREVIOUS`.
