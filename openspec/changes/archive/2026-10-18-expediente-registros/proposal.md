# Proposal

Origin: product/prd.md § E2 (US-04) — FR-005, FR-006, FR-007; NFR-001, NFR-012, NFR-013
Triage: change — toca `code`, una decisión nueva (almacenamiento de adjuntos) y varios artefactos encadenados; una sola story (2026-10-12)

## Why

La cuenta y el consentimiento existen (E1), pero el expediente real no: hoy solo hay un stub (`HealthRecordStub`,
una nota de texto) construido explícitamente para que E2 lo sustituya. El valor central del producto — "todo el
historial en un lugar recuperable" (O1) — empieza aquí: sin registros clínicos reales no hay nada que compartir
(E3), consultar (E4) ni citar por la IA (E5).

## What Changes

- El stub se sustituye por el expediente real: registros clínicos de dos tipos — **diagnóstico** (fecha,
  profesional, notas; FR-005) y **receta/medicación** (medicamento, dosis, vigencia; FR-006) — con todo el
  contenido clínico cifrado en reposo campo a campo (NFR-001, patrón `EncryptedString` existente), aislados por
  dueño y detrás de la barrera de consentimiento (se conserva `require_consent`). **BREAKING** interno: la tabla
  y los endpoints del stub se reemplazan con migración; los tests que hoy prueban consentimiento y aislamiento a
  través del stub (`test_consent.py`, `test_account_isolation.py`) migran a los registros reales en este cambio.
- **Adjuntos** (FR-007): imagen o PDF anexable a un registro propio, almacenado cifrado en Postgres (sin servicio
  de objetos nuevo — NFR-013; decisión y alternativas en design.md → ADR), con tipos permitidos y límite de
  tamaño, descargable íntegro.
- El dueño puede **corregir y eliminar** sus registros (derecho ARCO de rectificación/cancelación sobre su propio
  dato, LFPDPPP); borrar un registro arrastra sus adjuntos.
- **UI es-MX** nueva sección "Expediente": listar, crear, ver, editar y eliminar registros y gestionar adjuntos,
  con recursos react-i18next (namespace nuevo) y la suite Playwright asertando los textos como contrato (NFR-012,
  patrón D15).

## Capabilities

### New Capabilities
- `records/clinical-records`: el expediente clínico del paciente — registrar diagnósticos y recetas, adjuntar
  documentos (imagen/PDF), corregir y eliminar lo propio; contenido clínico cifrado en reposo y aislado por
  cuenta, detrás del consentimiento.

### Modified Capabilities
<!-- vacío: privacy/consent, identity/user-auth y ux/localization no cambian de requisitos; los nuevos
     endpoints y pantallas quedan cubiertos por sus requirements existentes (barrera de consentimiento,
     aislamiento, toda UI en es-MX) -->

## Impact

- Backend: `models.py` (nuevas tablas, fuera el stub), migración Alembic, `routes/health_records.py` reescrito,
  tests de consent/aislamiento migrados + tests nuevos de registros y adjuntos.
- Frontend: ruta nueva `/expediente` + componentes, namespace es-MX nuevo, specs Playwright nuevos.
- Sin servicios nuevos ni cambios de infraestructura (NFR-013); API del stub desaparece (ningún consumidor
  externo: el frontend aún no la usa).
