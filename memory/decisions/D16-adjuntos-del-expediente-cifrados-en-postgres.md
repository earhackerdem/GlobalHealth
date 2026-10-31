---
id: D16
date: 2026-10-12
status: accepted
---

## D16 — Adjuntos del expediente: cifrados en Postgres (bytea), sin servicio de objetos
- **Status:** Accepted · 2026-10-12 · decided by: Saúl Pérez (author/owner) al aprobar el design de
  expediente-registros ("plan approved"). Cubre FR-007 con NFR-001, NFR-008 y NFR-013.
- **Decision:** los documentos adjuntos (PDF/JPEG/PNG, límite 10 MB inclusivo por archivo) se guardan en la tabla
  `health_record_attachment` (antes `healthrecordattachment`, renombrada por D25) con contenido y nombre cifrados app-level (`EncryptedBytes`/`EncryptedString`, mismas
  claves por propósito de D13); validación por magic bytes del contenido, no solo por el content-type declarado.
  FK `ON DELETE CASCADE` al registro: borrar el registro borra sus adjuntos.
- **Why:** un solo almacén = un solo respaldo (el RPO de NFR-008 cubre adjuntos sin trabajo extra), cero
  servicios nuevos que operar (NFR-013), borrado efectivo = DELETE de fila (ARCO/NFR-004), y el cifrado reutiliza
  la infraestructura D13 ya probada.
- **Discarded:** S3/R2 (otro servicio, otra política de cifrado/borrado/respaldo); volumen local (no sobrevive al
  PaaS efímero de D8).
- **Consequence:** la BD crece con los adjuntos; re-evaluar esta decisión si el total supera ~1 GB o si entra
  multiusuario real. El límite de 10 MB se valida en la app: un cuerpo multipart mayor se bufferiza antes del
  413 (mitigable con límite en el reverse proxy; anotado como deuda).
