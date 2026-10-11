# Design

Status: APPROVED
Approved by: Saúl Pérez (author/owner) on 2026-10-11

## Context

Repo sin código de producto aún (`backend/` y `frontend/` no existen; harness.json ya los declara como `code`
gated). Stack fijado en ADR D11: template oficial full-stack FastAPI — backend FastAPI + SQLModel + Postgres +
Alembic con auth JWT correo/contraseña incluida, frontend React/TS + Vite, Docker Compose, CI GitHub Actions,
pytest + Playwright [VERIFIED: memory/research.md#stack · 2026-10-11]. Budget NFR heredado de
product/technical-brief.md §4. Ver proposal.md para la motivación.

## Goals / Non-Goals

**Goals:** esqueleto del template corriendo en local con suites verdes; alta/login con Google (OIDC) además del
correo/contraseña del template; consentimiento expreso con evidencia antes de cualquier dato de salud; mecanismo de
cifrado de campos sensibles decidido y disponible (NFR-001).
**Non-Goals:** registros clínicos (E2), enlaces compartidos (E3), portal (E4), IA (E5), recordatorios (E6),
shell Capacitor, deploy a PaaS (otra story), texto legal definitivo del consentimiento (placeholder v1 marcado).

## Interface contract

- `POST /api/v1/users/signup` y `POST /api/v1/login/access-token` — los trae el template (correo/contraseña);
  confirmar rutas exactas empíricamente en T1 y actualizar aquí si difieren.
- `GET /api/v1/login/google` → redirige a Google (Authorization Code + PKCE).
- `GET /api/v1/login/google/callback?code=…` → crea cuenta o vincula por correo **verificado por Google**; responde
  `Token {access_token, token_type: "bearer"}` (mismo modelo que `/login/access-token`). Correo no verificado → 400.
- **Punto de mock (fijado en T1):** `app/core/google_oauth.py` expone
  `async def exchange_code(code: str) -> GoogleClaims` con `GoogleClaims {sub: str, email: str, email_verified: bool}`;
  las rutas lo llaman vía `google_oauth.exchange_code(...)` y los tests parchean `app.core.google_oauth.exchange_code`.
  Google real nunca se toca en tests.
- `POST /api/v1/consent` body `{"version": "v1"}` → 201 `{version, granted_at, auth_method}`; idempotente por versión.
- `GET /api/v1/consent` → 200 `{version, granted_at}` o 404 si no se ha otorgado.
- `GET /api/v1/consent/text` → `{version, text}` (añadido en T3: el frontend muestra EXACTAMENTE el texto cuya
  sha256 queda en la evidencia; fuente única app/core/consent_text.py).
- UI del consentimiento (decisión T3): tarjeta-gate es-MX en el dashboard mientras no haya otorgamiento
  (ConsentGate.tsx); no bloquea las páginas del template (el bloqueo real de datos de salud es del backend, 403
  CONSENT_REQUIRED), así el Playwright del template sigue verde y el alta por ambos métodos pasa por la tarjeta.
- Dependencia `require_consent` (FastAPI Depends): sin consentimiento vigente → 403 `{"detail": "CONSENT_REQUIRED"}`.
  Todo router futuro de datos de salud (E2+) la declara; en esta story se prueba con un router mínimo de prueba
  (fijado en T3): `POST /api/v1/health-records` body `{"note": str}` → requiere usuario autenticado + consentimiento;
  con consentimiento → 201 `{"id", "note", "owner_id"}` persistido con owner_id del usuario de sesión;
  `GET /api/v1/health-records` → lista SOLO los del usuario de sesión (sirve además a los escenarios de aislamiento
  del grupo 4; E2 lo reemplaza por los registros clínicos reales).
- Modelo `ConsentGrant`: `user_id FK · version · text_sha256 · granted_at · auth_method`; usuario del template con
  `hashed_password` nullable + tabla `OAuthIdentity (user_id, provider='google', subject, email)`.
- Tipo de columna cifrada (NFR-001): TypeDecorator con cifrado simétrico app-level (clave por env), disponible para
  E2; en esta story se aplica a `OAuthIdentity.subject` como primer uso real.

## Decisions

- **Entorno de desarrollo = el del template (ADR D12)**: Docker Compose para Postgres/stack (`watch` para hot
  reload) y uv para el venv y dependencias del backend [VERIFIED: migración a uv y compose watch, sept 2024 —
  memory/research.md#stack]; T1 confirma los comandos exactos contra el development.md oficial.
- **Instalación del template por el método oficial** (T1 lo confirma empíricamente: copier/clon según README del
  template [NOT VERIFIED aún — regla de explore: empírico antes que documental]) en la raíz del repo (`backend/`,
  `frontend/`), adaptando su CI al repo. Alternativa descartada: escribir FastAPI desde cero (pierde authn/CI/tests
  ya resueltos, ADR D11).
- **OAuth con Authlib sobre la auth del template** [OPINION: librería OIDC estándar del ecosistema; confirmar en
  T1]. Alternativa descartada: migrar a fastapi-users por su OAuth integrado — reemplaza toda la auth del template,
  más riesgo que beneficio.
- **Vinculación de cuentas por correo verificado**: Google con `email_verified=true` y correo igual al de una
  cuenta existente accede a esa cuenta. Alternativa descartada: cuentas separadas por proveedor (duplica pacientes).
- **Consentimiento como dato, no como flag**: fila por otorgamiento con versión y hash del texto (carga de la
  prueba, NFR-004). Afecta ADR: ninguno nuevo; implementa D2/D11.

## Test plan (one row per scenario, mandatory)

| Spec · scenario | Test |
|---|---|
| user-auth · Alta exitosa con correo | backend/app/tests: signup + login devuelve token (adaptar el del template si ya existe) |
| user-auth · Correo ya registrado | signup duplicado → 4xx sin filtrar datos |
| user-auth · Alta con Google | callback con id_token mock (Google NUNCA real en tests) → cuenta sin password local + token |
| user-auth · Google con correo ya registrado | cuenta previa por password + callback mismo correo verificado → mismo user_id, 0 cuentas nuevas |
| user-auth · Acceso a recurso ajeno por id | con el router de prueba: A pide recurso de B → 404/403 |
| user-auth · Listados solo propios | A lista → exactamente sus 2, no los 3 de B |
| consent · Intento de captura sin consentimiento | router de prueba con `require_consent` → 403 CONSENT_REQUIRED |
| consent · Otorgamiento en el alta | POST /consent → 201 y fila {v1, timestamp, método}; después la captura pasa |
| consent · Consultable por el titular | GET /consent → versión y fecha |
| consent · Alta con Google no implica consentimiento | cuenta por Google sin POST /consent → captura bloqueada |

## Non-functional constraints addressed

- NFR-001 (cifrado): tipo de columna cifrada creado y aplicado a `OAuthIdentity.subject`; prueba: lectura directa a
  la BD muestra ciphertext. Campos clínicos llegan en E2 ya con el mecanismo listo.
- NFR-004 (consentimiento): evidencia {versión, hash del texto, timestamp, método} conservada; texto v1 es
  placeholder redactado por Saúl Pérez, revisión legal pendiente (NEEDS CLARIFICATION del budget, antes de usuarios
  externos).
- NFR-009 (maintainability): un test por escenario (tabla anterior), CI del template activa.
- NFR-012 (es-MX): las pantallas añadidas (consentimiento, botón Google) en es-MX; traducir el resto del template
  queda para una story propia (registrado en inbox al ejecutar).
- NFR-005/013: no aplican aún (sin IA ni deploy en esta story).

## Risks / Trade-offs

- [El template evoluciona y el README difiere de lo investigado] → T1 verifica empíricamente y el design se
  actualiza antes de seguir.
- [Mocks de Google mal hechos esconden errores del flujo real] → prueba manual del flujo completo con credenciales
  reales de Google en local, documentada en evidence.md (una vez, fuera de la suite).
- [Vincular por correo verificado: si Google reporta un correo no verificado] → se rechaza la vinculación (escenario
  cubierto por el error del callback).
- [Texto de consentimiento sin valor legal] → marcado v1-placeholder; bloqueo explícito: no abrir a usuarios
  distintos de Saúl antes de la revisión legal (NFR-004).

## Gate that closes the work

`make tdd-check` (un commit rojo por grupo test→impl) + suite backend (pytest) y frontend (build + Playwright del
template) **truly green** (0 failures, 0 errors, 0 skipped) con números en evidence.md + `docker compose up` local
sirviendo signup, login Google (manual) y flujo de consentimiento.
