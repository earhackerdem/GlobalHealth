# 2026-10-12 · expediente-registros (US-04, E2)

- Saúl Pérez eligió US-04 como siguiente historia tras archivar ui-es-mx-i18next ("Procede").
- /opsx:propose completo: proposal + delta `records/clinical-records` (3 requirements, 9 escenarios) + design
  (DRAFT, pendiente "plan approved") + tasks (4 grupos: 3 test→impl + cierre).
- Decisión propuesta (ADR D16, se asienta al ejecutar): adjuntos cifrados en Postgres bytea, sin servicio de
  objetos — un respaldo, cero servicios nuevos, borrado efectivo por fila; límite 10 MB y umbral de re-evaluación.
- Citers del stub inventariados: `test_consent.py` y `test_account_isolation.py` migran en el grupo 1; los datos
  del stub se pierden con la migración (andamiaje documentado).

## Ejecución (2026-10-12)
- Saúl Pérez aprobó el plan ("plan approved"); design APPROVED committeado.
- 3 grupos test→impl con barrera tester/implementer, rojos y verdes re-corridos por el orquestador:
  - G1 registros: rojo 12/26 (stub 422 al payload nuevo) → verde 117 passed, 94%. `HealthRecord` sustituye al
    stub; `test_consent.py` y `test_account_isolation.py` migrados sin cambiar su intención.
  - G2 adjuntos: rojo 9/9 (rutas ausentes) → verde 126 passed, 94%. `EncryptedBytes` nuevo junto a
    `EncryptedString`; magic bytes + 10 MB inclusivo.
  - G3 frontend: rojo 6/6 (/expediente → 404) → verde Playwright 71/71. Namespace `records`, patrón Items.
- tdd-check ✓ en los tres grupos (+1 commit test: de formato biome del spec, solo re-formato).
- ADR D16 asentado (adjuntos en Postgres cifrados). Deuda honesta en evidence.md: multipart se bufferiza antes
  del 413 (límite de proxy pendiente); timestamps sin timezone en el modelo (asimetría del template);
  generate-client.sh reformatea todo el árbol (candidato a inbox/meta-mejora).
- Dato perdido consciente: la migración tiró `healthrecordstub` con las notas dev del propietario (documentado
  en design/evidence/validation).

## Ronda review→apply (2026-10-12, mismo PR)
- /epe-4-review: 5 finders → 31 únicos tras dedupe → 4 validadores por reproducción (0 FP completos; 2 medias
  verdades descartadas reproduciendo: el hook del inbox sí lista la fila, no hay bug de timezone). Estrellas:
  descarga 500 con filename es-MX (U+2014, latin-1), PATCH rompiendo el invariante del tipo, listado
  descifrando 5 MB para tirar los bytes, overflow móvil reproducido a 375px.
- Saúl Pérez aprobó "todos": fixer 16/16 sin rebotes + tester 10 casos y helpers endurecidos (verdes a la
  primera). Post-apply: backend 136/0/0 (94%), Playwright 71/0/0, tdd-check ✓. E → 5 filas ⏸️ en closed.md.
- Convergencia: una sola ronda, reportada honestamente como no-seca.
