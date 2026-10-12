# 2026-10-12 · expediente-registros (US-04, E2)

- Saúl Pérez eligió US-04 como siguiente historia tras archivar ui-es-mx-i18next ("Procede").
- /opsx:propose completo: proposal + delta `records/clinical-records` (3 requirements, 9 escenarios) + design
  (DRAFT, pendiente "plan approved") + tasks (4 grupos: 3 test→impl + cierre).
- Decisión propuesta (ADR D16, se asienta al ejecutar): adjuntos cifrados en Postgres bytea, sin servicio de
  objetos — un respaldo, cero servicios nuevos, borrado efectivo por fila; límite 10 MB y umbral de re-evaluación.
- Citers del stub inventariados: `test_consent.py` y `test_account_isolation.py` migran en el grupo 1; los datos
  del stub se pierden con la migración (andamiaje documentado).
