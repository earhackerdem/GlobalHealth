---
date: 2026-10-12
status: done
---

**Receta a la mexicana** (feedback de Saúl Pérez tras probar el PR #6; no leyó las delta specs y el resultado no cumplió su expectativa): una receta real trae varias medicinas, fecha de expedición y nombre del paciente; NO trae vigencia inicio/fin y normalmente NO trae diagnóstico (se dice de palabra) → el modelo debería ser receta con medicinas[] y diagnóstico como campo opcional, no dos tipos con vigencia obligatoria. Intención de fondo: subir foto de la receta (o cámara) y que OCR+IA llene los campos. Prototipo clickeable para validar el flujo: https://claude.ai/artifact/PJUNDJ5d2c8R8YHq6qPXtZ

**Why it matters:** Toca el modelo recién fusionable (PR #6), el PRD (FR-005/FR-006; la captura por foto no tiene FR) y FR-025 (recordatorios usaban la vigencia); merece story propia (reshape) + story de captura foto/OCR tras decidir proveedor IA (NFR-005)

**Status:** ✅ cerrado el reshape (PR #13 mergeado 2026-10-19: receta+medicinas[], sin vigencia, dx opcional/suelto, archivado; prototipo en product/prototipos/receta-primero.html); la captura foto/OCR sigue pendiente del proveedor IA (story 2)
