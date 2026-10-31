---
date: 2026-10-31
---

# api-errores-sin-datos: los errores de la API no repiten datos de salud (B1 y S2)

**Quién:** Saúl Pérez (author) pidió, con `/epe-autopilot`, tomar las tareas de FastAPI y resolverlas de manera
autónoma («quiero ver hasta dónde llegas»). Primer cambio del lote: el grupo «privacidad» del inventario de deudas.

**Qué se hizo:**
- **B1:** un handler de `RequestValidationError` en `backend/app/main.py`. El 422 ya no devuelve `input` y siempre
  serializa: un surrogate suelto, también en el nombre de una clave que llega a `loc`, se cambia por `?`.
- **S2:** `SENTRY_OPTIONS` con `max_request_body_size="never"`, `include_local_variables=False` y
  `send_default_pii=False`. La sonda del 2026-10-31 mostró que el veredicto de S2 se quedaba corto: con los valores
  por defecto, el dato también viaja en las variables de los frames, no solo en el cuerpo.

**Por delegación:**
- Matriz aceptada y diseño aprobado.
- Quitar `input` de todos los 422.
- `send_default_pii` explícito.
- `traces_sample_rate=1.0` en lugar del `enable_tracing` obsoleto.

**Verificación:**
- Rojo de 4 fallas (`ec3968e`).
- Verde de 592/0/0/0, cobertura 96 %, ruff y mypy limpios, `tdd-check` en ✓.
- Pase real con `curl` contra la API reconstruida: 422 y 0 apariciones en el log.

**Tropiezo:** edité el archivo de prueba después del rojo (el valor de reserva de `getattr`) y lo revertí antes del
commit, para que `tdd-check` mida desde el rojo real.

**Deuda:** ninguna nueva.
