# Evidence — validaciones-hoy-y-texto-invisible

## Escenario → prueba → estado
| Escenario (`specs/records/patient-profile/spec.md`) | Prueba | Estado |
|---|---|---|
| Fecha de nacimiento futura rechazada (pasado mañana) | `backend/tests/api/routes/test_profile.py::test_ac2_future_birth_date_rejected_profile_unchanged` (antes fijaba `2030-01-01`, T3) | ✅ |
| «Hoy» es el de Ciudad de México | `test_profile.py::test_birth_date_today_is_mexico_city` (reloj congelado a las 20:00 del 2026-03-10 en México) | ✅ |
| «¿Cuál fue?» con un texto invisible | API: `test_profile_history.py::test_past_other_invisible_text_is_required` y `::test_chronic_other_invisible_text_is_required` (U+200B · U+3164 U+2800 · espacios con U+200B) · pantalla: `frontend/tests/profile-history.spec.ts` «S04b», chromium y s26-ultra | ✅ |
| Texto visible con un invisible dentro sí cuenta | `test_profile_history.py::test_past_other_visible_text_with_zero_width_is_saved` | ✅ |

## Rojo antes del verde (`82d7e46`, testers distintos del implementer)
| Grupo | Corrida | Resultado |
|---|---|---|
| 1 · API | `uv run pytest tests/api/routes/test_profile.py tests/api/routes/test_profile_history.py` | **7 failed, 101 passed**: `200 == 422` (fecha con el reloj de México) y `201 == 422` (6 casos de texto invisible). La prueba T3 y la de «Zika» pasan en rojo, como se esperaba (mantenimiento y guarda contra un arreglo que quite de más) |
| 2 · pantalla | `bunx playwright test profile-history.spec.ts -g S04 --project=chromium --project=s26-ultra` | **2 failed, 3 passed**: S04b en los dos proyectos, porque el formulario se cerró y guardó el registro |

## Verde
| Corrida | Resultado | Commit |
|---|---|---|
| `FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **596 passed, 0 failed, 0 errors, 0 skipped**; cobertura 96 %; ruff y mypy limpios | `ffe183a` |
| imagen reconstruida + `prestart.sh`; `PLAYWRIGHT_BASE_URL=http://localhost:8000 bunx playwright test profile-history.spec.ts profile-habits.spec.ts profile.spec.ts --project=chromium --project=s26-ultra` | **243 passed, 0 failed, 0 flaky, 0 skipped** | `7acf8e4` |
| `bunx tsc -p tsconfig.json --noEmit` · `bunx biome check src/components/Profile/` | limpios | ídem |
| `make tdd-check` | ✓ rojo `82d7e46`, pruebas sin tocar desde entonces | ídem |

## Pase exploratorio (Chrome, http://localhost:8000, cuenta de prueba nueva con consentimiento)
| Intento | Resultado |
|---|---|
| «Otra» con dos U+200B en «¿Cuál fue?» → Guardar | la caja queda en rojo con «Elige la condición o escribe cuál fue» y el foco en ella; nada guardado |
| escribir «Zika» detrás de los invisibles y **doble clic** en Guardar | un solo registro, «Zika · Sin más datos», aviso «Guardado»; la API guarda `U+200B U+200B Zika` (cuenta como texto visible, según la spec) |
| consola | sin errores de la app (uno de una extensión de Chrome) |

## Deuda vista y no tomada
- Otros formularios del perfil deciden «vacío» con `.trim()`: `EditBasicData.tsx:91`, `EditFamilyHistory.tsx:78`,
  `EditWork.tsx:66-67`, `OnboardingWizard.tsx:97/132/205/351`, `WhenField.tsx:85` (lo vio el implementer de pantalla).
  Ninguno es un campo requerido del historial; queda en el inbox.

## Revisión, ronda 1 (una ronda: diff de código < 300 líneas)
Dos buscadores (criterios, pruebas y seguridad; casa y restricciones) y un validador distinto. Gate y arreglos por
delegación de Saúl Pérez (author).

| Id | Hallazgo (validado) | Decisión |
|---|---|---|
| A | el paso de la fecha de `validation.md` no se podía ver por la web (la pantalla ya validaba con la fecha del aparato y otro mensaje) | corregido: §3 reescrita, con el mensaje real |
| B | caracteres invisibles escritos tal cual en `text.ts`, pruebas y validación | corregido: escapes en código y pruebas |
| C | `_is_filled` sin prueba para «Llena al menos un dato» ni para nombres requeridos (mutante sobrevivía 596/596) | corregido: `test_invisible_only_datum_is_an_empty_entry`, `test_invisible_required_name_is_missing` |
| D | el reloj congelado devolvía la hora local con `now()` sin zona: un mutante `datetime.now()` sobrevivía en la Mac (CST) | corregido: `now(None)` da el instante en UTC |
| E | la web medía «futura» con la fecha del aparato | corregido: `mexicoCityTodayIso()` en `EditBasicData` y `OnboardingWizard` (también el `measured_on` de la bienvenida); prueba con `timezoneId: Asia/Tokyo` |
| F | la caja de «cuándo» usaba `.trim()`: un U+200B borraba el chip y pedía «solo el número» | corregido: `WhenField` y `draftToWhen` con `isBlank`; S09b |
| G | la propuesta decía que OpenAPI no cambiaba; faltaba `openspec validate` en la evidencia | corregido |
| H | «Zika» + invisible sin prueba de pantalla | corregido: tercera pasada de S04b |
| I | el paso del carácter invisible no se podía seleccionar (la mitad de S04b es falso positivo: el conteo final lo cubre) | corregido: relleno U+3164 entre flechas |
| J | ⏸️ C1 se planeó pagar con B2 | **pagado aquí**: regla común con `Default_Ignorable_Code_Point` |

Rojo de la revisión (`dd14b2b`): backend **15 failed** (C1 en pasadas, crónicas y transfusiones); e2e **6 failed**
(S04b con U+FE0F, S09b y la fecha en Tokio, en chromium y s26-ultra).
Verde (`829b970`): backend **616 passed, 0 failed, 0 errors, 0 skipped**, cobertura 96 %; la prueba de la fecha
también pasa con `TZ=America/Mexico_City`; e2e de perfil, historial y hábitos **247 passed, 0 failed, 0 flaky**; tsc,
`biome check src/components/Profile/` (de solo lectura, en lugar de `bun run lint`, que reescribe archivos), ruff y
mypy limpios; `make tdd-check` ✓; `openspec validate validaciones-hoy-y-texto-invisible --strict` válido.

**Pase exploratorio de los arreglos (Chrome):** en «Transfusiones», un relleno U+3164 en «Edad que tenías» → Enter
→ «Llena al menos un dato» al pie del formulario; nada guardado.
