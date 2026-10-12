# Proposal

Origin: product/prd.md § E1 (US-01) — FR-001, FR-026, NFR-001, NFR-004
Triage: brief — greenfield con capa de producto completa (brief → PRD → technical brief), primera story de la épica E1 (2026-10-11)

## Why

Todo el producto (expediente, compartir, IA) se construye sobre una cuenta que aísla los datos de salud por usuario
y que no captura ni un dato sensible sin consentimiento expreso registrado (LFPDPPP art. 9; NFR-004). Es la primera
story: también instala el esqueleto del stack decidido en ADR D11 (template full-stack FastAPI) y lo deja corriendo
con CI, para que los siguientes cambios partan de un proyecto vivo.

## What Changes

- Se instala el template oficial full-stack FastAPI (backend/ FastAPI+SQLModel+Postgres+Alembic, frontend/ React/TS)
  como base del monorepo, corriendo en local con su CI en verde (ADR D11).
- Alta e inicio de sesión de paciente con correo/contraseña (lo trae el template) y con Google (OIDC, FR-026);
  Google actúa solo como proveedor de identidad.
- Flujo de consentimiento expreso: en el alta (ambos métodos), el paciente acepta el tratamiento de datos sensibles
  antes de poder capturar cualquier dato de salud; la evidencia del consentimiento (qué texto, cuándo, cómo) queda
  registrada y conservada (NFR-004: la carga de la prueba es del responsable).
- Aislamiento por usuario desde el modelo de datos: ninguna consulta cruza datos de cuentas distintas (FR-001).

## Capabilities

### New Capabilities
- `identity/user-auth`: registro e inicio de sesión del paciente (correo/contraseña y Google OIDC) con datos
  aislados por cuenta.
- `privacy/consent`: consentimiento expreso para el tratamiento de datos sensibles — se recaba antes del primer
  dato de salud, con evidencia conservada y consultable.

### Modified Capabilities
<!-- ninguna: primer cambio del proyecto, no hay specs previas -->

## Impact

- Código: crea `backend/` y `frontend/` (paths gated por harness.json → code; requieren design.md APPROVED).
- Dependencias: template full-stack FastAPI [VERIFIED: github.com/fastapi/full-stack-fastapi-template · 2026-10-11];
  proveedor OIDC de Google (solo identidad, sin datos de salud).
- Sistemas: Postgres local vía Docker Compose del template; CI GitHub Actions del template (sin remoto aún: correrá
  cuando el repo tenga remoto).
- Herencia NFR: NFR-001 (cifrado de campos sensibles — en esta story solo se decide el mecanismo y se aplica a los
  campos del consentimiento si aplica; los campos clínicos llegan en E2), NFR-004 (consentimiento con evidencia).
- No toca: compartir/enlaces (E3), portal (E4), IA (E5), recordatorios (E6).
