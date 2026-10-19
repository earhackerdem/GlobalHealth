# Design

Status: APPROVED
Approved by: Saúl Pérez (author) on 2026-10-18 — "procede", en respuesta directa a la petición de aprobación del plan

## Context

El modelo vigente (`backend/app/models.py:109` `HealthRecord`) asume receta = un medicamento (en `title`), `dose`
y vigencia obligatoria (`valid_from`/`valid_to`, validadas en `validate_health_record_fields_by_type`,
`models.py:136`). El discovery agreed (product/dominio.md 2026-10-18) lo corrige: receta con medicinas[] 1..N,
sin vigencia, diagnóstico opcional, archivado manual. Los endpoints CRUD + adjuntos de US-04
(`backend/app/api/routes/health_records.py`) y el frontend `frontend/src/components/Records/*` +
`routes/_layout/expediente.tsx` + `locales/es-MX/records.json` existen y se remodelan, no se recrean. El
prototipo validado es `product/prototipos/receta-primero.html` (AC-1…AC-9; esta story cubre AC-1, AC-3…AC-6,
AC-8, AC-9).

## Goals / Non-Goals

**Goals:** modelo receta+medicinas[] con migración de los datos existentes; archivado manual reversible; estado
"sin confirmar" del diagnóstico suelto; frontend es-MX fiel al prototipo (captura manual, foto adjunta vía
adjuntos existentes).
**Non-Goals:** OCR/IA (story 2, tras tech-brief del proveedor); dictado (AC-7 — Web Speech envía audio a
servidores del navegador, contrario a privacidad-primero; va al spike Android D17); flujo de confirmación por
médico (E3/E4); desduplicación de fotos; catálogos futuros (laboratorio, vacunas).

## Interface contract

```
POST /api/v1/health-records/            (consentimiento requerido, como hoy)
  receta:      {record_type: "prescription", occurred_on: "2026-10-12",
                professional?: str, diagnosis?: str, notes?: str,
                medicines: [{name: str (1..255, req), dose?: str, frequency?: str, route?: str}]}  # 1..N
  diagnóstico: {record_type: "diagnosis", title: str (req), occurred_on, professional?, notes?}
  → 201 HealthRecordPublic | 422 (detail string es-MX) | 403 CONSENT_REQUIRED

HealthRecordPublic: {id, record_type, occurred_on, title: str|None, professional, diagnosis: str|None, notes,
                     archived: bool, confirmation_status: "unconfirmed"|None (solo diagnosis),
                     medicines: [{id, name, dose, frequency, route}] (orden de captura), created_at, updated_at}

PATCH /api/v1/health-records/{id}
  campos parciales; `medicines` presente = REEMPLAZO completo de la lista (valida 1..N resultante);
  `archived: bool` archiva/desarchiva. Valida el ESTADO RESULTANTE con el helper compartido → 422 es-MX.
GET /api/v1/health-records/  → {data: [...], count}  (incluye archivadas; el front separa por `archived`)
GET/DELETE /{id}, adjuntos: sin cambios de contrato (404 "Registro no encontrado" indistinguible se mantiene).
```

Modelo: `HealthRecordMedicine` (tabla nueva): id, record_id FK CASCADE, position int, name/dose/frequency/route
`EncryptedString` (name NOT NULL). `HealthRecord`: `title` pasa a nullable (solo diagnosis lo exige), +`diagnosis`
EncryptedString nullable, +`archived` bool NOT NULL default false (plano), +`confirmation_status` str nullable
(plano, "unconfirmed" para diagnosis), −`dose`, −`valid_from`, −`valid_to`.

## Decisions

1. **Medicinas en tabla hija, no JSON**: cifrado por campo con `EncryptedString` ya probado (D13), consultas
   futuras por medicina (FR-025) y CASCADE limpio. Alternativa JSON cifrado: descartada, opaca para FR-025.
2. **PATCH con reemplazo completo de `medicines`**: una receta trae 1–4 medicinas (evidencia), el reemplazo es
   simple y atómico. Alternativa endpoints por medicina: descartada, API más grande sin necesidad.
3. **`archived` y `confirmation_status` en claro**: son metadatos de flujo, no contenido clínico — extiende el
   trade-off documentado de `record_type` plano (design de expediente-registros § Risks); se re-documenta aquí.
4. **Migración con datos**: cada prescription existente genera 1 medicina (name=title, dose=dose) y su vigencia
   se preserva anexada a `notes` ("Vigencia migrada: …"); después title→NULL en recetas y se tiran las columnas.
   Alternativa descartar vigencia: descartada, no se destruye dato del usuario en una migración.
5. **Sin campo vigencia nuevo**: Q1-A; la derivada queda en inbox (Q1-B).
6. **La foto de la receta usa los adjuntos existentes** (D16): el formulario del front ofrece adjuntar tras crear;
   sin endpoint nuevo.

## Test plan (one row per scenario, mandatory)

| Spec · scenario | Test |
|---|---|
| Registrar receta con varias medicinas (AC-1) | pytest `test_health_records.py::test_create_prescription_with_medicines` |
| Diagnóstico y frecuencia opcionales (AC-3/AC-9) | pytest `::test_prescription_optional_diagnosis_and_frequency` |
| Receta sin medicinas se rechaza (AC-1) | pytest `::test_prescription_requires_medicines` (lista vacía y name vacío) |
| Registrar un diagnóstico (suelto, Q3-A) | pytest `::test_create_diagnosis` (actualizado) |
| Registrar una receta con dosis y vigencia (payload viejo → 422) | pytest `::test_legacy_prescription_payload_rejected` |
| Corregir y eliminar un registro propio (diagnóstico) | pytest `::test_update_and_delete_own_diagnosis` |
| Contenido clínico cifrado en reposo | pytest `::test_clinical_content_encrypted_at_rest` (incluye medicinas) |
| Sin consentimiento no entra ni un dato | pytest `::test_consent_required` (existente, re-verificado) |
| Un registro ajeno no existe para mí | pytest `::test_foreign_record_indistinguishable_404` (+ archivar ajeno) |
| Corregir medicinas de receta propia (AC-6) | pytest `::test_patch_replaces_medicines_validates_result` |
| Eliminar receta arrastra medicinas y adjuntos | pytest `::test_delete_cascades_medicines_and_attachments` |
| Archivar una receta activa (AC-8) | pytest `::test_archive_prescription` + e2e `health-records.spec.ts` (sección Archivadas) |
| Desarchivar devuelve a activas | pytest `::test_unarchive_prescription` |
| Diagnóstico nace sin confirmar | pytest `::test_diagnosis_confirmation_status_unconfirmed` |
| Flujo completo de captura manual (prototipo) | Playwright `health-records.spec.ts` (form medicinas[], dx opcional, archivar) |

## Non-functional constraints addressed

- **NFR-001 (cifrado):** medicinas, diagnóstico y lo ya cifrado siguen en `EncryptedString`; test de reposo lo
  prueba. `archived`/`confirmation_status` planos: metadatos, documentado (Decisión 3).
- **NFR-004 (consentimiento):** sin cambios; la dependencia existente cubre los endpoints remodelados.
- **es-MX:** todos los mensajes 422 nuevos y claves de `records.json` en es-MX; dd/mm/aaaa vía split (TZ bug ya
  conocido).
- **NFR-005:** no aplica aún (sin IA en esta story).

## Risks / Trade-offs

- [Migración destruye info si falla el fold de vigencia] → migración probada con registros sembrados en ambos
  tipos; downgrade recrea columnas.
- [SDK del frontend desincronizado] → hook Generate-Frontend-SDK en el gate; tras gate rojo, `git status` (lección
  conocida: los hooks auto-arreglan el árbol).
- [Reemplazo completo de medicines pierde ediciones concurrentes] → aceptado: una sola usuaria por cuenta en v1.
- [e2e frágiles por menús por fila] → reutilizar helpers endurecidos de US-04 (`getByRole` scoped).

## Gate that closes the work

`bash scripts/test.sh` backend truly green + `bunx playwright test health-records.spec.ts` verde + `make
tdd-check` (un commit `test:` por grupo test→impl) + CI del PR en verde.
