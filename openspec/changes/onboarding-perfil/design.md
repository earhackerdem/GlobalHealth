Status: APPROVED (Saúl Pérez, "plan approved", 2026-10-19)

# Design — onboarding-perfil

## Context

Motivación en proposal.md § Why; requisitos en specs/records/patient-profile/spec.md (7 ADDED, 12 escenarios).
Infraestructura existente que se reutiliza, verificada:
- Cifrado en reposo: `EncryptedString` (backend/app/core/encrypted.py:89), el mismo de recetas/diagnósticos
  (D13/D16, sin ADR nueva).
- Consentimiento: `ConsentGrant` (backend/app/models.py:77) y la dependencia `require_consent`
  (backend/app/api/deps.py:68) que ya rechaza capturas sin consentimiento vigente.
- Patrón de rutas y envelope `{"data": [...], "count": N}` (backend/app/api/routes/health_records.py:135,150).
- Frontend: `ConsentGate` se monta en la home (frontend/src/routes/_layout/index.tsx:33) y al aceptar invalida la
  query `["consent"]` (frontend/src/components/Consent/ConsentGate.tsx:44-46); navegación en
  frontend/src/components/Sidebar/AppSidebar.tsx con textos en frontend/src/locales/es-MX/layout.json:9; e2e con
  dos proyectos Playwright (chromium y s26-ultra, frontend/playwright.config.ts:49-61).
- Prototipo validado (fuente de la UX, no de la implementación): product/prototipos/onboarding-perfil.html.

## Goals / Non-Goals

- **Goals**: US-17 completa — FR-027 (perfil + onboarding omitible una sola vez + pantalla de secciones) y FR-008
  (AHF con línea), con el estado del onboarding en el servidor (sobrevive dispositivos).
- **Non-Goals**: llenado de las secciones APP/APNP (FR-028/US-18, story siguiente); historial graficable de
  mediciones; cuestionarios por especialidad (E4/FR-022); cambios a consentimiento, expediente o compartir.

## Qué se toca / qué NO (regla del plan)

- Se toca: `backend/app/models.py` (modelos nuevos), migración Alembic nueva (solo aditiva), ruta nueva
  `backend/app/api/routes/profile.py`, `backend/tests/api/routes/test_profile.py`, frontend
  (`routes/_layout/perfil.tsx`, componentes `Profile/`, arranque del onboarding en `index.tsx`, AppSidebar,
  `locales/es-MX/profile.json`), `frontend/tests/profile.spec.ts`.
- NO se toca: health_records (rutas, modelos, tests), ConsentGate salvo el aterrizaje post-aceptación,
  user management del template, ninguna ADR (D13/D16 se reutilizan tal cual — ninguna decisión afectada).
- Gate que cierra el trabajo: pytest backend + Playwright (ambos proyectos) truly green + validation.md para Saúl.

## Decisions

1. **Estado del onboarding en el servidor, no en el navegador**: columna en el perfil (`onboarding_outcome:
   pending|completed|skipped` + timestamp). Alternativa descartada: localStorage — "una sola vez" debe sobrevivir
   cambio de dispositivo y el guidance del repo prohíbe estado confiable en el navegador.
2. **Tres tablas nuevas**: `patient_profile` (1:1 con user; birth_date, sex, allergies cifrados), `body_measurement`
   (type weight|height, value cifrado, measured_on; nunca UPDATE del valor: siempre INSERT) y `family_history`
   (condition enum + other_text cifrado, relatives serializado cifrado, note cifrado). Alternativa descartada:
   columnas sueltas en User (mezcla identidad con dato clínico y rompe el patrón de aislamiento por recurso).
3. **Identificadores en inglés, UI en es-MX** (veredicto congelado en memory/closed.md): enums `sex:
   female|male|unspecified`; `condition: diabetes|cancer|hypertension|heart_disease|other`; `relative: mother|
   father|maternal_grandmother|maternal_grandfather|paternal_grandmother|paternal_grandfather|sibling|other`.
   Mensajes de error en es-MX como en health_records.
4. **Edad derivada en el cliente** a partir del birth_date descifrado que el API ya devuelve al dueño; el servidor
   no persiste la edad. Validaciones Pydantic ANTES de cifrar: birth_date ∈ [1900-01-01, hoy], peso ∈ (0, 400] kg,
   estatura ∈ [30, 250] cm.
5. **Arranque del onboarding**: la home consulta GET /profile; con consentimiento vigente y onboarding `pending`
   muestra el wizard (misma posición que ConsentGate); `completed|skipped` → expediente. Cerrar el onboarding es
   un POST explícito; un segundo cierre responde 409.

## Interface contract (lo que tester e implementer comparten)

Base `/api/v1/profile`, todo detrás de `require_consent`; errores 422 con detalles es-MX; envelope en listas.

| Operación | Request | Response |
|---|---|---|
| GET `/profile` | — | `{ birth_date: date\|null, sex: enum\|null, allergies: str\|null, onboarding: "pending"\|"completed"\|"skipped", latest_weight: {value: float, measured_on: date}\|null, latest_height: {...}\|null }` |
| PUT `/profile` | `{ birth_date?, sex?, allergies? }` (parciales; null borra) | el perfil como GET |
| POST `/profile/onboarding` | `{ outcome: "completed"\|"skipped" }` | 200 perfil; **409** si ya no está `pending` |
| POST `/profile/measurements` | `{ type: "weight"\|"height", value: float }` | 201 `{ id, type, value, measured_on }` (measured_on = hoy, servidor) |
| GET `/profile/measurements?type=` | — | `{ data: [medición…], count }` descendente por fecha |
| POST `/profile/family-history` | `{ condition, other_text?, relatives: [enum…], note? }` | 201 la entrada |
| PUT `/profile/family-history/{id}` | mismos campos | 200 la entrada; 404 indistinguible si ajena/inexistente |
| DELETE `/profile/family-history/{id}` | — | 200 message es-MX; 404 indistinguible |
| GET `/profile/family-history` | — | `{ data: [...], count }` |

Tablas (para aserciones de ciphertext por SQL sin importar los modelos): `patient_profile` (user_id único,
birth_date, sex, allergies, onboarding_outcome, onboarding_closed_at), `body_measurement` (user_id, type, value,
measured_on), `family_history` (user_id, condition, other_text, relatives, note). Los campos sensibles guardan
ciphertext Fernet (prefijo `gAAAA` tras decodificar), como en health_records.

Frontend: ruta `/perfil` ("Mi perfil médico"), wizard de onboarding montado desde la home cuando
`onboarding === "pending"`, navegación nueva en AppSidebar, namespace i18next `profile` (es-MX).

## Test plan — un test por escenario

| # | Escenario (spec) | Test | Dónde |
|---|---|---|---|
| 1 | Guardar perfil básico y ver edad | PUT /profile + GET → valores y cifrado en BD (ciphertext ≠ claro) | pytest |
| 2 | Fecha futura rechazada | PUT birth_date 2030-01-01 → 422 es-MX | pytest |
| 3 | Perfil vacío válido | PUT {} → 200, campos null | pytest |
| 4 | Medición nueva no borra anterior | 2 POST measurements → GET lista 2, latest correcto | pytest |
| 5 | Valor implausible rechazado | peso 0 / estatura 500 → 422 es-MX | pytest |
| 6 | AHF con línea y detalle | POST family-history (diabetes, [paternal_grandfather, mother], nota) → GET | pytest |
| 7 | Quitar condición elimina parentescos | DELETE → GET vacío y fila ausente en BD | pytest |
| 8 | Omitir lleva al expediente y no se repite | e2e: aceptar consentimiento → "Ahora no" → expediente; relogin sin wizard | Playwright |
| 9 | Completarlo tampoco se repite | pytest: POST onboarding completed → GET pending=false; 2º POST → 409 | pytest |
| 10 | Omitir por pasos y completar después | e2e: wizard solo con AHF → "Mi perfil médico" agrega nacimiento | Playwright |
| 11 | Secciones listadas sin captura | e2e: /perfil lista las 6 secciones vacías sin formulario | Playwright |
| 12 | Perfil ajeno indistinguible | pytest: usuario B consulta medición de A vs inexistente → respuestas idénticas | pytest |

E2e corren en chromium y s26-ultra (384×832) como health-records (frontend/playwright.config.ts:49-61: agregar
profile.spec.ts al testMatch del proyecto móvil).

## Risks / Trade-offs

- [El wizard en la home convive con ConsentGate] → orden explícito: sin consentimiento → gate; con consentimiento
  y pending → wizard; después → expediente. Un e2e cubre la secuencia completa (test 8).
- [relatives serializado dentro de un campo cifrado no es consultable por SQL] → aceptado: el filtro/analítica de
  AHF (FR-021) llega con la capa IA; hoy solo se lee por dueño.
- [Enum de condiciones se queda corto] → `other` + texto cifrado cubre el resto; ampliar el catálogo es migración
  trivial aditiva.
- [tests e2e del template no pasan en 384px] → igual que receta: solo profile.spec.ts entra al proyecto s26-ultra
  (deuda registrada en memory/inbox.md 2026-10-19).

## Migration Plan

Una revisión Alembic solo aditiva (3 tablas nuevas, cero cambios a tablas existentes); rollback = downgrade que
las elimina (sin datos de terceros en juego). Sin backfill: el onboarding aplica a cuentas cuyo consentimiento se
acepte después del deploy; cuentas existentes ven `pending` y el wizard a su siguiente entrada a la home (decisión
barata y reversible; Saúl es hoy el único usuario real).

## Open Questions

(ninguna — las 4 del discovery quedaron respondidas el 2026-10-19; ver product/dominio.md § Open questions)
