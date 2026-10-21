---
date: 2026-10-20
status: open
---

[2026-10-20] Nombres de tabla sin convención: `oauthidentity`, `consentgrant`, `healthrecord`,
`healthrecordmedicine` y `healthrecordattachment` salen del default de SQLModel (`cls.__name__.lower()`,
sqlmodel/main.py:907), y desde onboarding-perfil las tablas nuevas declaran `__tablename__` en snake_case
(`patient_profile`, `medical_history_entry`). Lo detectó Saúl Pérez explorando la BD. Decidir con un ADR:
renombrar (cambio propio `fix/tablas-snake-case`: `__tablename__` + migración nueva con `op.rename_table`, FKs a
`healthrecord.id`, índices y constraints, y 4 tests con nombres crudos) o fijar la convención solo para tablas
nuevas. Editar las migraciones viejas no sirve: no corren otra vez en las BD existentes.
