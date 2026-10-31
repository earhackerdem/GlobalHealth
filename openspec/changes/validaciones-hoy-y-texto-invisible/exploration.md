# Exploration — validaciones-hoy-y-texto-invisible

**Matriz aceptada por delegación de Saúl Pérez (author), 2026-10-31 (`/epe-autopilot`).**

## 1. Entrada
Cuatro escenarios GIVEN/WHEN/THEN con datos concretos (dos MODIFIED de «Perfil básico», dos ADDED a «Registros de
las secciones de eventos»). Ninguno impone tecnología.

## 2. Cobertura por escenario
| Escenario | Estado | Evidencia (2026-10-31) |
|---|---|---|
| Fecha futura rechazada (pasado mañana) | ✅ existe; la prueba fija `2030-01-01` | `validate_birth_date` (`backend/app/models.py:373-380`); la prueba `backend/tests/api/routes/test_profile.py:209` fallará desde 2030 (T3) |
| «Hoy» es el de Ciudad de México | ❌ nuevo | `models.py:375` compara con `date.today()`, que es el reloj del proceso: el contenedor corre en UTC (`time.tzname` = `('UTC','UTC')` dentro de `backend`; la Mac está en CST). Los demás validadores reciben `datetime.now(MEXICO_CITY).date()` (`routes/profile.py:169`, `:348`, `:646`). Las pruebas congelan ese reloj con `freeze_routes_clock` (`backend/tests/api/routes/test_profile_history.py:79-91`), que parcha `profile_routes.datetime`; `date.today()` no lo ve |
| «¿Cuál fue?» con un texto invisible | ❌ nuevo | API: `_is_filled` usa `.strip()` (`models.py:733-738`), usado en `validate_history_content` (`:813`, `:818`, `:824`); confirmado por reproducción el 2026-10-26 (B2: `other_text: "​"` → 201). Pantalla: `HistoryEntryForm.tsx:393` usa `.trim()`, que no quita U+200B ni U+3164/U+2800. Ya existe el criterio correcto: `_is_blank` (`models.py:1066-1074`) e `isBlank` (`frontend/src/components/Profile/HabitsForm.tsx:146-147`), de hábitos. El mensaje de la pantalla es el mismo que el de la API (`frontend/src/locales/es-MX/profile.json:369`, `models.py:727`) |
| Texto visible con un invisible dentro sí cuenta | ✅ existe | `.strip()` hoy y `_is_blank` después: «Zika» + U+200B tiene caracteres visibles |

## 3. Lo que parecía útil y no lo fue
- Un `today_mx()` compartido en `app/core`: los validadores de la casa reciben `today` como parámetro (`habits_errors`,
  `validate_history_content`), y así se congelan en las pruebas. Seguir ese patrón es más barato que un helper nuevo.
- Sanear el texto invisible al guardarlo (convertirlo en `None`), como hace el ejercicio (`_normalize_exercise`): en el
  historial el campo es requerido, así que lo correcto es rechazarlo con el mensaje de requerido, no vaciarlo.

## 4. Restricciones no funcionales
NFR-012 (es-MX): los mensajes no cambian. NFR-009: una prueba por escenario. La edad en la web con la fecha local del
aparato (`frontend/src/components/Profile/format.ts:38-48`) es otra deuda, de la web, y no se toca aquí
(`memory/closed/2026-10-29-fuera-de-alcance-de-android-base.md`).

## 5. Clasificación
**Extensión.** Sin preguntas abiertas. Pista para el plan: mover `isBlank` a un módulo compartido del perfil.
