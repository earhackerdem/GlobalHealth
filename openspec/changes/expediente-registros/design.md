# Design

Status: APPROVED
Approved by: Saúl Pérez (author) on 2026-10-12 ("plan approved")

## Context

- E1 dejó probados y en producción local: `EncryptedString` (Fernet/MultiFernet, claves por propósito — ADR D13),
  la barrera `require_consent` (`ConsentedUser` en `backend/app/api/deps.py`) y el aislamiento por dueño, todo
  ejercitado hoy a través de `HealthRecordStub` (`backend/app/models.py:107`), un stub de una sola nota creado
  explícitamente para que E2 lo sustituya (`backend/app/api/routes/health_records.py:1`).
- Citers del stub (expiran en este cambio): `models.py`, `api/main.py`, `routes/health_records.py`, dos
  migraciones Alembic históricas (se conservan; una nueva lo elimina) y los tests `test_consent.py` y
  `test_account_isolation.py`, que migran a los registros reales sin perder lo que prueban.
- Frontend: patrón de dominio existente en `components/Items/` (DataTable + diálogos add/edit/delete), recursos
  es-MX por namespace (D15), cliente generado por openapi-ts en `src/client/`.
- No existe decisión de almacenamiento de archivos: FR-007 la fuerza → ADR D16 en este cambio.

## Goals / Non-Goals

**Goals:** FR-005 (diagnóstico), FR-006 (receta con dosis y vigencia), FR-007 (adjuntos imagen/PDF) con NFR-001
(contenido clínico cifrado en reposo), aislamiento por dueño, barrera de consentimiento conservada y UI es-MX con
Playwright como contrato; rectificación y eliminación del registro propio (ARCO).
**Non-Goals:** búsqueda y filtros del expediente (FR-009, US-06); historial familiar (FR-008, US-05); compartir
(E3); export/borrado de cuenta completa (US-02); recordatorios (FR-025); OCR o procesado de documentos; quitar el
demo Items del template; thumbnails o preview de adjuntos.

## Interface contract

- **Modelo (una tabla + adjuntos)**: `HealthRecord` — `id` UUID, `owner_id` FK→user CASCADE, `record_type`
  (`"diagnosis" | "prescription"`, texto plano), `occurred_on` (date, plano: ordena el expediente),
  `title` (cifrado: nombre del diagnóstico o del medicamento), `professional` (cifrado, opcional en receta),
  `notes` (cifrado, opcional), `dose` (cifrado, solo receta), `valid_from`/`valid_to` (date, planos, solo receta:
  FR-025 necesitará consultarlos), `created_at`/`updated_at`. Regla de cifrado: **todo texto clínico cifrado;
  solo tipo, fechas e ids en claro** (trade-off documentado en Risks).
  `HealthRecordAttachment` — `id`, `record_id` FK→healthrecord CASCADE, `filename` (cifrado), `media_type`
  (plano, whitelist), `size_bytes` (plano, del original), `content` (cifrado, bytea), `created_at`.
- **`EncryptedBytes`**: tipo SQLAlchemy nuevo junto a `EncryptedString` (mismo MultiFernet por propósito, D13),
  para `content`. Fernet ya es bytes→bytes: sin base64 extra.
- **Migración Alembic**: crea las dos tablas y elimina `healthrecordstub`. Los datos del stub son andamiaje de
  desarrollo y se pierden (documentado en evidence; el dev con datos en el stub los recrea como registros reales).
- **API** (`routes/health_records.py` reescrito; todo tras `ConsentedUser`; details es-MX directos, patrón D15):
  `POST /health-records/` (crea; payload discriminado por `record_type`, receta exige medicamento+dosis+vigencia,
  diagnóstico exige título+fecha; 422 por tipo/campos inválidos) · `GET /health-records/` (solo los propios,
  envelope `{data, count}`, orden `occurred_on` desc) · `GET|PATCH|DELETE /health-records/{id}` (404 idéntico
  para inexistente y ajeno; DELETE arrastra adjuntos) · `POST /health-records/{id}/attachments` (multipart) ·
  `GET /health-records/{id}/attachments/{attachment_id}` (descarga con `Content-Disposition` y media type real) ·
  `DELETE /health-records/{id}/attachments/{attachment_id}`.
- **Adjuntos — contrato de validación**: tipos permitidos `application/pdf`, `image/jpeg`, `image/png`;
  verificación por **magic bytes** del contenido (`%PDF`, `\xff\xd8`, firma PNG), no solo por el content-type
  declarado (un `.exe` renombrado se rechaza con 415); límite **10 MB** por archivo (413); mensajes es-MX.
- **Frontend**: ruta `/_layout/expediente` + entrada "Expediente" en el sidebar; componentes en
  `components/Records/` siguiendo el patrón `Items/` (DataTable, diálogos "Agregar diagnóstico" / "Agregar
  receta", editar, eliminar con confirmación, panel de adjuntos con subir/descargar/eliminar); namespace es-MX
  nuevo `records.json` (patrón dual D15: `useTranslation` en componentes, `i18n.t` en module scope); cliente
  `src/client/` regenerado desde el OpenAPI nuevo.
- **Playwright**: spec nuevo `frontend/tests/health-records.spec.ts` asertando los textos es-MX exactos de los
  recursos (contrato del idioma) sobre los flujos: registrar ambos tipos, corregir, eliminar, adjuntar y
  descargar, y rechazo de archivo inválido.

## Decisions

- **ADR D16 — Adjuntos cifrados en Postgres (bytea), sin servicio de objetos**: un solo almacén = un solo
  respaldo (RPO NFR-008 cubre adjuntos gratis), cero servicios nuevos que operar (NFR-013), borrado efectivo =
  DELETE de fila (ARCO/NFR-004), cifrado con la infraestructura D13 ya probada. Alternativas descartadas: S3/R2
  (otro servicio, otra política de cifrado y de borrado, otro respaldo) y volumen local (no sobrevive al PaaS
  efímero, D8). Límite honesto: con 10 MB/archivo la BD crece rápido; se re-evalúa si el tamaño total supera
  ~1 GB o si entra multiusuario real. Se asienta como D16 en `memory/decisions.md` en este cambio.
- **Una tabla con `record_type`, no dos tablas**: el expediente es una línea de tiempo (US-06 la recorrerá y
  filtrará); tipos como filas evitan UNIONs y duplicar aislamiento/adjuntos; los campos exclusivos de receta son
  anulables y la validación vive en los schemas de la API.
- **Fechas y tipo en claro, texto clínico cifrado**: ordenar y (futuro FR-025) consultar vigencias exige SQL
  sobre fechas; una fecha sin el texto clínico revela poco. El nombre del archivo adjunto sí va cifrado (suele
  nombrar el estudio).
- **El dueño edita y elimina**: no es un expediente institucional inmutable; es el dato personal del paciente
  (rectificación/cancelación LFPDPPP). La trazabilidad clínica formal llegará con los aportes de profesionales
  (E4, FR-016/FR-018), que son de otro autor y ahí sí con marca de origen.

## Test plan (one row per scenario, mandatory)

| Spec · scenario | Test |
|---|---|
| clinical-records · Registrar un diagnóstico | pytest `test_health_records.py` (201 + campos) y Playwright flujo "Agregar diagnóstico" |
| clinical-records · Registrar una receta con dosis y vigencia | pytest (201 + campos de receta; 422 si falta dosis/vigencia) y Playwright "Agregar receta" |
| clinical-records · El contenido clínico queda cifrado en reposo | pytest leyendo la tabla con SQL directo: ciphertext `gAAAA`, sin "Hipotiroidismo"/"Levotiroxina" en claro (patrón E1) |
| clinical-records · Sin consentimiento no entra ni un dato | `test_consent.py` migrado: 403 `CONSENT_REQUIRED` en POST/GET de registros reales |
| clinical-records · Un registro ajeno no existe para mí | `test_account_isolation.py` migrado + casos PATCH/DELETE ajeno → mismo 404 que inexistente |
| clinical-records · Corregir y eliminar un registro propio | pytest (PATCH refleja, DELETE → 404 y adjuntos fuera) y Playwright editar+eliminar |
| clinical-records · Adjuntar y descargar un resultado en PDF | pytest round-trip bytes idénticos + content-type; Playwright sube y descarga |
| clinical-records · Tipo o tamaño fuera de contrato se rechaza | pytest: `.exe` renombrado → 415; >10 MB → 413; nada persistido; Playwright muestra el error es-MX |
| clinical-records · Los adjuntos quedan cifrados en reposo | pytest SQL directo a la tabla de adjuntos: sin `%PDF` en claro, filename ciphertext |

## Non-functional constraints addressed

- **NFR-001**: todo texto clínico y el contenido de adjuntos cifrados con D13; dos escenarios lo prueban contra
  la BD directa.
- **NFR-004**: la barrera de consentimiento se conserva en todos los endpoints nuevos; rectificación y
  cancelación del dato propio quedan ejecutables a nivel registro.
- **NFR-012**: pantallas nuevas 100% desde recursos es-MX; Playwright asierta los textos (contrato D15).
- **NFR-013 / NFR-008**: cero servicios nuevos; los adjuntos viajan en el mismo respaldo de Postgres.

## Risks / Trade-offs

- [Fechas en claro filtran metadatos (cuándo hubo consultas, duración de tratamientos)] → aceptado y documentado:
  sin ellas no hay orden ni recordatorios; el texto clínico que da significado va cifrado. Re-evaluar si se
  adopta cifrado con índices (p.ej. deterministic encryption) más adelante.
- [BD crece con adjuntos grandes] → límite 10 MB/archivo + ADR D16 fija el umbral de re-evaluación (~1 GB).
- [Reemplazar el stub rompe sus tests] → los dos tests citers migran en el MISMO grupo que reescribe la API;
  `tdd-check` y la suite completa lo vigilan.
- [Multipart y descarga binaria en el cliente generado] → openapi-ts soporta multipart; la descarga usa fetch
  directo con el token si el cliente generado no tipa bien el binario (decisión del implementador, documentada).

## Gate that closes the work

`cd backend && uv run pytest -q` verde (0/0/0, cobertura ≥90) + `bunx playwright test --project=chromium` verde
completo (suite existente + spec nuevo) + `make tdd-check` + CI del PR verde.

## Execution per task group

| Grupo | Flavor | Por qué |
|---|---|---|
| 1 Backend registros: modelo + `EncryptedBytes` + migración + CRUD + migrar tests consent/aislamiento | test→impl | rojo = pytest de los 6 escenarios de registros (incl. cifrado y 404 indistinguible) contra la API nueva |
| 2 Backend adjuntos: tabla + endpoints multipart/descarga + validación magic bytes | test→impl | rojo = pytest de los 3 escenarios de adjuntos (round-trip, rechazo, cifrado) |
| 3 Frontend expediente es-MX + Playwright | test→impl | rojo = `health-records.spec.ts` asertando es-MX contra una UI que aún no existe |
| 4 Evidencia, ADR D16, validation, PR | single | cierre documental |
