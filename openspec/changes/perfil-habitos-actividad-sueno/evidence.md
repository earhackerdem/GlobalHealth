# Evidence — perfil-habitos-actividad-sueno (C-5, C-7, C-8)

## Suites

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Línea base (main tras el PR #33, fd6a7da): `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | 442 passed (cierre del PR #33; la ronda 2 no tocó código) | 0 | 0 | ✅ |
| Grupo 1, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **551 passed, 0 failed** (hábitos 301) · cobertura **96 %** | 0 (los UserWarning de configuración dev de siempre) | 0 | ✅ |
| `uv run mypy app` · `ruff check app` · `ruff format --check app` | limpios (25 archivos) | 0 | — | ✅ |
| Grupo 2, re-corrido por el orquestador (Vite :5173 + API del contenedor con el contrato nuevo): `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) | **227 passed, 0 failed** | 0 | 0 | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/ tests/` · `grep -nE "\b(600\|60\|24\|7)\b" HabitsForm.tsx` | 0 errores · 104 archivos sin cambios · solo `className="w-24"` (ancho; ya estaba) | 0 | — | ✅ |
| Suite Playwright COMPLETA como CI (`PLAYWRIGHT_BASE_URL=http://localhost:8000`, imagen reconstruida con 0d49477), 2 corridas | **328 passed + 1 failed** en las dos: `reset-password.spec.ts:90` (chromium), timeout esperando el correo en Mailpit (`utils/mailpit.ts:45`), heredado (`memory/inbox/2026-10-20-fix-aparte-e2e-intermitentes-heredados-admin.md`); aislada con `--repeat-each=3` falla 1 de 3. El diff contra `main` no toca autenticación, correo ni recuperación (solo `models.py`, una línea de `routes/profile.py`, el cliente, `HabitsForm.tsx` y `profile.json`) | 0 | 0 | 🟡 intermitencia heredada ajena a hábitos; más frecuente que en el PR #33 (2/2 frente a 1/2) |
| Suite Playwright COMPLETA como CI tras el arreglo de la exploración (imagen reconstruida con 090e257) | **331 passed, 0 failed** | 0 | 0 | ✅ |
| Cliente regenerado (`scripts/generate-client.sh`) · `bunx tsc -p tsconfig.build.json --noEmit` | `zod.gen.ts` con días 1–7, minutos 1–600, horas sentado 0–24, nombre ≤ 60 · tsc 0 errores; imagen reconstruida, `Habits` del OpenAPI con `exercise`, `daily_movement`, `sleep` | 0 | — | ✅ |

## Criterio → prueba → anclaje → estado

| Escenario (spec delta) | Prueba backend | Prueba de pantalla | Estado |
|---|---|---|---|
| Dos actividades con su total (C-5) | `backend/tests/api/routes/test_profile_habits.py:2097`, `:2132` (los 9 tipos) | `frontend/tests/profile-habits.spec.ts:2860` | ✅ |
| Otra actividad con su nombre (C-5) | `:2164` (omitido, null, solo espacios), `:2180` (recortado) | `:2915` | ✅ |
| Falta un dato de una actividad (C-5, C-15) | `:2221` (9 tipos × días/minutos × omitido/null) | `:2959` | ✅ |
| No hago ejercicio (C-5) | `:2242`, `:2260`, `:2293` (true sin actividades) | `:2991` | ✅ |
| Movimiento del día aparte (C-7) | `:2342`, `:2356` | `:3029` | ✅ |
| Desplazamiento sin días (C-7, C-15) | `:2388`, `:2414` | `:3075` | ✅ |
| Sueño con las dos frecuencias (C-8) | `:2443`, `:2464` | `:3110` | ✅ |
| Fuera de escala en los bloques nuevos | `:2712` (36 casos: escalas, `"unknown"`, tipos y niveles desconocidos, propiedades extra) | `:3152`, `:3205` (dos cajas seguidas, hallazgo de la exploración) | ✅ |
| Solo el sueño | `:2737` | `:3228` | ✅ |
| Sin puntaje ni riesgo (C-6) y Total semanal sin veredicto (C-5, C-6) | `:2765`, `:2824` | `:3266` | ✅ |
| Hábitos solo del paciente y cifrados (vigente) | `:2881` ("Senderismo", `trouble_falling_asleep`… no aparecen en claro) | — | ✅ |
| Accesibilidad y D20 (fila 12 del plan) | — | `:3305` | ✅ |
| C-17 en los bloques nuevos (fila 13) | — | `:3384` | ✅ |

## Red before green

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1 · backend | Re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` → **285 failed, 266 passed, 0 errors** (551). 117 por `extra_forbidden` en `["body","exercise"]`, `["body","daily_movement"]` o `["body","sleep"]` (los bloques no existen); el resto, comparaciones del cuerpo completo que ya esperan las tres claves nuevas en `null` (incluida la de "lo guardado no cambia" de los rechazos) | be8ae0f | 301/301 del archivo; suite completa 551 passed (verde 4556d92) | ✓ red be8ae0f, tests sin cambios hasta el verde |
| 2 · frontend | Re-corrido por el orquestador: `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` → **24 failed, 203 passed** (12 por proyecto, 0 errores de setup): la pantalla no tiene el grupo "¿Qué ejercicio haces?", ni el desplazamiento, ni el sueño; las 203 previas pasan | d630f04 · 7d5d76a (fila 10 corregida por el tester) | 227/227 de las tres suites de perfil (verde 0d49477) | ✓ red 7d5d76a, tests sin cambios hasta el verde |
| 3.2 · arreglo de la exploración | `bunx playwright test tests/profile-habits.spec.ts -g "dos cajas dejadas seguidas" --repeat-each=3` → **6 failed** (3 × proyecto) en la caja de horas sentado | 641e976 | 10/10 con `--repeat-each=5`; tres suites de perfil 229 passed (arreglo 090e257) | ✓ red 641e976, tests sin cambios hasta el arreglo |

Nota del grupo 1: el implementer se detuvo con 39 rojos porque `routes/profile.py:649` armaba siempre un `loc` de tres
elementos y el contrato pide cinco para los campos de cada actividad; el plan decía "NO se toca" la ruta. Era una
contradicción del plan: el orquestador corrigió `design.md` (una línea de la ruta, el campo partido por puntos) y el
implementer la aplicó; los errores de un solo nivel conservan su `loc`. El nombre de "Otra" quedó sin mínimo en el
esquema (vacío = sin contestar, "Escribe cuál."), así que `zod.gen.ts` lleva `max(60)` pero no `min(1)`.

Nota del grupo 2: el implementer devolvió la fila 10 (C-6) como prueba equivocada: `page.locator("main")` choca con el
modo estricto porque el layout anida dos `<main>` (`ui/sidebar.tsx:325` y `routes/_layout.tsx:31`, del esqueleto
`cb48c3a`). Volvió al tester, que la acotó a `main` interior (`.last()`) y agregó que ese contenedor tenga las
preguntas de hábitos antes de buscar palabras prohibidas; commit propio `test:` 7d5d76a. El `<main>` anidado quedó como
deuda (`memory/inbox/2026-10-26-main-anidado-en-el-layout.md`). El implementer también hizo que los chips del día
partan su texto (por `className` de `ChipGroup`, sin tocarlo): "Cargando cosas ligeras o subiendo escaleras seguido"
ensanchaba la página más allá de 384 px y rompía tres pruebas móviles previas que abren el menú lateral.

## Exploración en Chrome (tarea 3.2), por el agente

App en `http://localhost:8000` (imagen reconstruida), cuenta de prueba nueva creada por la API local (datos solo en el
scratchpad). Chrome de Saúl Pérez con la extensión; los anchos, sin interfaz (Playwright) porque la ventana de Chrome no
baja de su ancho mínimo.

| Intento | Qué pasó |
|---|---|
| "Caminar" 5×30 y "Pesas o gimnasio" 2×45 | "Total de lo anotado: 240 minutos por semana" mientras se escribe |
| Total con valores a medias: "Otra" 1×90 y "Caminar" con solo 5 días | 90; al escribir los 30 minutos, 240 |
| "Otra" con 8 días y 601 minutos, Tab | "Debe estar entre 1 y 7" y "Debe estar entre 1 y 600" junto a cada caja |
| 25 horas sentado, clic en las horas de sueño, 0 y Tab enseguida | ❌ **defecto**: la caja de horas sentado se quedaba sin error (las de sueño sí). Reproducido 5/5 sin interfaz y acotado (ver abajo); arreglado en 090e257 y vuelto a recorrer en Chrome: las cuatro cajas marcan su error |
| "Guardar" con "¿Cuál?" vacío, desplazamiento *Sí* sin días y los fuera de escala | seis errores, cada uno junto a su caja ("Escribe cuál.", "Contesta esta pregunta.", las escalas); foco en "¿Cuál?"; ningún `PUT` |
| "¿Cuál?" con "Senderismo 🥾" (emoji) | se guarda y se reabre igual |
| "¿Cuál?" con 65 caracteres | la caja corta en 60 (`maxlength` del esquema) |
| Desplazamiento *Sí* → *No* | la pregunta de días y su error se van; se guarda `active_travel: false`, sin días |
| Doble clic en "Guardar" | un solo `PUT` (200), "Hábitos guardados", vuelve al perfil |
| Reabrir | "Caminar" y "Otra" en el orden del catálogo, sus números, el nombre, total 240, *No*, 9 horas sentado, 6 de sueño, "Algunos días" y "Casi todos los días" cada uno en su pregunta |
| "No hago ejercicio" con actividades guardadas | desmarca los chips de actividades y quita sus cajas y el total; se guarda `does_exercise: false` con las actividades en `null` |
| Salir por el menú con cambios sin guardar | "¿Salir sin guardar?" con "Seguir editando" |
| 384 y 580 px con "Otra", "Fútbol u otro deporte", *Sí*, el nivel más largo del día y "Guardar" con faltantes | `scrollWidth` = ancho de la ventana en los dos; el chip largo parte su texto; consola sin errores |
| Consola de la app en Chrome | sin errores propios; solo el 401 de la extensión de Chrome |

Un clic hecho por la herramienta mientras aparecía la línea de error de los minutos cayó fuera del chip *Sí*
(la página se movió); repetido, el chip responde. No es defecto de la app.

### Defecto de la exploración: dos cajas dejadas seguidas (C-14)

- **Síntoma:** salir de una caja con un clic en otra y salir de esa otra (Tab) antes de que el clic termine dejaba sin
  error de escala a la primera.
- **Causa:** al salir con un clic, la revisión de la caja espera a que termine el clic (`afterPress` en
  `HabitsForm.tsx`, para que la línea de error no mueva lo que se está tocando); era una sola casilla y la salida de la
  segunda caja la reemplazaba. Con las teclas más rápidas que el temporizador (herramienta, o máquina cargada: la misma
  familia que el defecto C-17 de perfil-habitos-completitud) la primera revisión se perdía. Viene de ese cambio, no de
  los bloques nuevos: afecta a cualquier par de cajas de hábitos.
- **Arreglo** (090e257, solo `leave()`): una segunda salida durante el clic encadena su revisión a la pendiente en vez
  de reemplazarla. Prueba roja primero (641e976), determinista: 6/6 rojo, 10/10 verde.
