# Proposal

**Origin:** product/dominio.md + product/roles-permisos.md (discovery agreed 2026-10-18) · product/prd.md § E2
(FR-005/FR-006, FR-025) · **Triage:** change — corrige el modelo de datos de `code` y toca la spec
records/clinical-records (2026-10-18). **Story Q4-A:** primera de dos — esta entrega modelo + captura manual +
foto adjunta, SIN IA; la lectura automática (OCR/IA) espera al tech-brief del proveedor.

## Why

El expediente v1 modeló la receta como un registro de UN medicamento con vigencia obligatoria; la evidencia del
discovery (74 fotos reales, 2026-10-18) demostró que la receta mexicana trae **varias medicinas** (1–4), **casi
nunca vigencia** (2 de ~33) y **rara vez diagnóstico escrito** (~⅓). Saúl Pérez lo detectó al probar la v1: "no
es lo que esperaba". Este cambio alinea el modelo con la realidad antes de construir encima (recordatorios,
compartir, IA).

## What Changes

- **BREAKING (modelo):** el tipo "receta" pasa de (medicamento, dosis, vigencia) a **receta con medicinas[]**
  (1..N: nombre, dosis/indicación, frecuencia opcional, vía opcional) + fecha de expedición + médico + diagnóstico
  opcional + notas. La **vigencia desaparece como campo** (Q1-A); migración de los registros existentes incluida.
- **Archivado manual** (Q1-A): una receta activa se archiva cuando el tratamiento termina; las archivadas salen
  de la vista activa pero siguen consultables. Sustituye a cualquier vigencia automática.
- **Frecuencia opcional por medicina** (Q2-A): se captura desde ya para que FR-025 (recordatorios) no exija otra
  migración.
- **Diagnóstico suelto se conserva** (Q3-A) como entrada del expediente, con **estado de confirmación** visible
  ("sin confirmar" por default) — solo el dato en esta story; el flujo de confirmación por un médico llega con
  E3/E4 (enlaces).
- **Frontend es-MX** según el prototipo validado (`product/prototipos/receta-primero.html`, AC-1…AC-6, AC-8,
  AC-9): formulario de captura manual con filas de medicinas, diagnóstico opcional, archivar, sección archivadas;
  la foto de la receta se adjunta al registro reutilizando los adjuntos existentes (AC-4).

## Out of scope (y por qué)

- **Lectura por OCR/IA de la foto** (AC-2 prellenado): segunda story, bloqueada por el tech-brief del proveedor
  (NFR-005; candidatos en memory/research.md 2026-10-18, incl. spike on-device D17).
- **Dictado (AC-7):** en web, las APIs de voz del navegador (Web Speech) envían el audio a servidores del
  fabricante — contrario a privacidad-primero; el dictado en dispositivo es territorio del spike Android (D17).
  Se difiere a esa evaluación con nota en el design.
- **Flujo de confirmación del diagnóstico por un médico:** requiere enlaces (E3/E4).
- Catálogos futuros del discovery (laboratorio, vacunación, nota clínica): registrados en dominio.md, sin modelar.

## Capabilities

### New Capabilities

(ninguna)

### Modified Capabilities

- `records/clinical-records`: la receta cambia de forma (medicinas[], sin vigencia, diagnóstico opcional, médico y
  fecha de expedición), gana archivado manual y el diagnóstico suelto gana estado de confirmación. Los requisitos
  de aislamiento, cifrado, consentimiento y adjuntos se conservan y se re-expresan sobre el modelo nuevo.
