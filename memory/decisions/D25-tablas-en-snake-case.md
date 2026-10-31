---
id: D25
date: 2026-10-31
status: accepted
---

## D25 — Las tablas se llaman en snake_case; las cinco del default de SQLModel se renombran

- **Status:** Accepted · 2026-10-31 · decided by: Saúl Pérez (autor), «procede con el nombre de las tablas», después
  de que el agente le avisó que eran renombres con datos.
- **Context:** cinco tablas salieron del default de SQLModel (`cls.__name__.lower()`): `oauthidentity`,
  `consentgrant`, `healthrecord`, `healthrecordmedicine` y `healthrecordattachment`. Desde onboarding-perfil, las
  tablas nuevas declaran `__tablename__` en snake_case (`patient_profile`, `medical_history_entry`). Lo vio Saúl
  Pérez explorando la base (`memory/inbox/2026-10-20-nombres-de-tabla-sin-convencion-oauthidentity.md`).
- **Decision:**
  1. Toda tabla del dominio declara `__tablename__` en snake_case.
  2. Las cinco se renombran a `oauth_identity`, `consent_grant`, `health_record`, `health_record_medicine` y
     `health_record_attachment`, con una migración nueva. Las migraciones viejas no se editan: no vuelven a correr en
     bases existentes.
  3. Con la tabla se renombran sus restricciones (llave primaria, foráneas, `NOT NULL` con nombre de Postgres 18) y
     sus índices `ix_…`, para que ningún nombre conserve el prefijo viejo.
  4. `user` e `item` se quedan: son del template, ya son una sola palabra en minúsculas, y `user` lo usan el login,
     el template y la cascada de todo el esquema.
- **Alternative rejected:** fijar la convención solo para tablas nuevas. Deja dos estilos para siempre en las tablas
  más consultadas del expediente.
- **Consequences:** una migración más (sube y baja con los datos); el SQL crudo de las pruebas usa los nombres nuevos;
  quien tenga una base local la migra con `make migrate`.
