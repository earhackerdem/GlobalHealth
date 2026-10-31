---
date: 2026-10-31
---

# bd-candados-indices-y-log: la base de datos con candados, índices y sin valores en el registro (M1, H1, R2, índices)

**Quién:** Saúl Pérez (author), con `/epe-autopilot`. Tercer cambio del lote de deudas de FastAPI.

**Qué se hizo (`test→impl`):**
- `hide_parameters=True` en el engine.
- El NUL se rechaza con 422 en los textos en claro (cuenta y elementos), y el login con NUL responde como credenciales
  incorrectas sin consultar.
- Migración `26de7399b12f` con índices en las 9 llaves foráneas que no tenían.
- `crud.lock_diagnosis` (`FOR UPDATE`) en el DELETE de diagnóstico y `FOR SHARE` al enlazar: el enlace ya no queda
  colgando (H1).
- `unlink_diagnosis` registra la fila ilegible (R2).

**Por delegación:**
- Matriz aceptada y diseño aprobado.
- Validar el NUL en la entrada, en lugar de atrapar `DataError`.
- Índices también en `item` y `oauthidentity`.
- El interbloqueo con el borrado de cuenta sigue diferido: su condición no se cumple.

**Verificación:**
- Rojo de 8 fallas (`b008ae0`).
- Verde de 596/0/0/0, cobertura 97 %; la carrera estable en 8 corridas; `tdd-check` en ✓.
- La migración sube y baja.
- Pase real: 0 llaves sin índice, `Index Scan`, 422 y 400 con NUL, 0 apariciones en el log.

**Deuda:** `alembic check` con 4 cambios de tipo previos (`memory/inbox/2026-10-31-alembic-check-tipos-timestamp.md`).

## Revisión y archivo

**Ronda 1:** dos buscadores. El orquestador reprodujo los hallazgos que cambiaban código, sin validador aparte
(desviación declarada en la evidencia).
- **Corregidos:**
  - **M-1:** la recuperación de contraseña con NUL daba 500. El guard pasó a `get_user_by_email`; la exploración solo
    había inventariado el login, cuando debía haber inventariado los llamadores.
  - **L-1:** `string_too_long` conservado.
  - **L-2:** `value_error`.
  - **F3:** prueba del orden de candados. Mutante verificado: invertido da 500.
  - **F4b:** prueba de los esquemas.
  - **L-3, L-4, L-5:** documentos.
- **Deuda:** F2 (el `DETAIL` de unicidad en la carrera del alta).
- **Congelados:** F4a y L-6.

**Verde final:** 608/0/0/0, cobertura 97 %.

**Lección:** la exploración de la carrera de diagnóstico fue buena (mutantes, pausa en el punto exacto). La del NUL
falló en lo de siempre: sin inventario de los llamadores del punto que se blinda. Blindar el punto común
(`get_user_by_email`) y no el que se vio primero.
