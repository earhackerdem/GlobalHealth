# 2026-10-18 · receta-mexicana ejecutada (story 1 de 2, sin IA)

**Quién:** Saúl Pérez (author) aprobó el design ("procede", en respuesta directa a la petición de aprobación;
asentado en design.md) tras cerrar el gate del discovery el mismo día.

**Qué:** modelo receta+medicinas[] (tabla hija cifrada), archivado manual, estado "sin confirmar" del diagnóstico
suelto, payload viejo → 422, migración con fold de datos (18 recetas y 25 diagnósticos reales migrados en dev), y
frontend es-MX fiel al prototipo v4 (captura "A mano", filas de medicinas con frecuencia opcional, Archivadas).
Dos grupos test→impl (tester/implementer con barrera, tdd-check ✓ por grupo) + cierre single.

**Verificación:** backend 137 passed/0 skipped; e2e 10/10; mypy y tsc limpios; migración validada contra datos
reales. Números y anchors en evidence.md; validation.md listo para Saúl.

**Deuda:** (1) biome --unsafe de generate-client/lint barre frontend/tests/ — chocará con guard-tests de futuros
implementers; fila en inbox. (2) GET /health-records/ hace lazy-load de medicinas (N+1), fino a esta escala.
(3) La imagen Docker del backend no se reconstruye sola (develop.watch): tras migrar modelo, `docker compose up
-d --build backend`. (4) Dictado y OCR/IA diferidos con razón (design § Non-Goals).

**Siguiente:** PR y /epe-4-review en otra sesión u ojos.
