# Proposal

**Origin:** deuda de la API (FastAPI), del inventario
`memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`:
- B2 (`memory/closed/2026-10-26-b2-texto-invisible-en-otra-del-historial.md`);
- `validate_birth_date` con el «hoy» del servidor (`memory/inbox/2026-10-20-validate-birth-date-backend-app-models.md`);
- T3 (`memory/closed/2026-10-20-t3-backend-tests-api-routes-test.md`).

**Triage:** un cambio (story con escenarios); toca `code` (`backend/app`, `frontend/src`). 2026-10-31, por delegación
de Saúl Pérez (author) con `/epe-autopilot`.

## Why
- **B2:** en el historial, «Otra» con un «¿Cuál fue?» que solo tiene un carácter invisible (`"​"`, `"ㅤ⠀"`) se
  guarda como contestado. La API usa `.strip()` y la pantalla `.trim()`, y ninguno quita los caracteres de formato
  ni los rellenos. Hábitos ya lo resolvió para el nombre de «Otra» del ejercicio (`_is_blank` en
  `backend/app/models.py:1066`, `isBlank` en `HabitsForm.tsx:146`).
- **Fecha de nacimiento:** `validate_birth_date` compara con `date.today()` del servidor
  (`backend/app/models.py:375`). El contenedor del backend corre en UTC (medido el 2026-10-31: `time.tzname` = `UTC`), así que entre las 18:00 y las 24:00 de
  Ciudad de México acepta como fecha de nacimiento la de «mañana». El resto del perfil ya usa el «hoy» de México
  (`routes/profile.py:169`, `:348`, `:646`).
- **T3:** la prueba de la fecha futura usa `2030-01-01` (`backend/tests/api/routes/test_profile.py:209`) y desde
  2030 fallará siempre.

## What Changes
- El historial trata como vacío un texto sin nada visible, en la API y en la pantalla, con el mismo criterio de hábitos.
- `validate_birth_date` recibe el «hoy» de Ciudad de México, igual que los demás validadores.
- La prueba de la fecha futura usa una fecha relativa: pasado mañana en México.

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
- `records/patient-profile`: «Perfil básico del paciente» (la fecha futura se mide con el «hoy» de México; el
  escenario de 2030 pasa a ser relativo) y «Registros de las secciones de eventos» (un texto invisible cuenta como
  vacío).

## Impact
`backend/app/models.py`, `backend/app/api/routes/profile.py`, `frontend/src/components/Profile/HistoryEntryForm.tsx`,
y el `isBlank` de `HabitsForm.tsx`, que pasa a un módulo compartido. Sin migración. El esquema OpenAPI solo cambia la descripción de `updateProfile` (su docstring), y el cliente se regeneró para eso (`5c4580a`).
