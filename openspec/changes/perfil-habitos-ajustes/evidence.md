# Evidence — perfil-habitos-ajustes (C-10…C-14)

## Suites

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Línea base (main tras el PR #30): `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | 304 passed | 0 | 0 | ✅ |
| Grupo 1, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests/ -q` | **342 passed, 0 failed** (hábitos 92) · cobertura **96 %** | 0 (los UserWarning de configuración dev de siempre) | 0 | ✅ |
| `uv run mypy app` · `ruff check app` · `ruff format --check app` | limpios (25 archivos) | 0 | — | ✅ |
| Grupo 2, re-corrido por el orquestador (Vite :5173 + backend del contenedor con el contrato nuevo): `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) | **137 passed, 0 failed** | 0 | 0 | ✅ |
| R1 en s26-ultra tras endurecer la conexión de los e2e: `-g "R1 otro paciente" --project=s26-ultra --repeat-each=10` | 11 passed (setup + 10) | 0 | 0 | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/ tests/` | 0 errores · 105 archivos, sin cambios | 0 | — | ✅ |
| Límites escritos a mano: `grep -nE "\b(130\|100\|30\|24\|7)\b" frontend/src/components/Profile/HabitsForm.tsx` | solo `className="w-24"` (ancho, no límite); las escalas salen de `zod.gen.ts` | — | — | ✅ |
| **Revisión ronda 1 (grupos 4 y 5).** Grupo 5, re-corrido por el orquestador: `cd backend && FASTAPI_ENV=development uv run coverage run -m pytest tests -q` · `uv run mypy app` | **345 passed, 0 failed** (hábitos 95) · cobertura **96 %** · mypy limpio (25 archivos) | 0 (los UserWarning de configuración dev de siempre) | 0 | ✅ |
| Grupo 4 y el arreglo del foco, re-corridos por el orquestador: `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) | **141 passed, 0 failed** (antes del arreglo del foco); después, `profile-habits.spec.ts` **65 passed, 0 failed** | 0 | 0 | ✅ |
| `bunx tsc -p tsconfig.build.json --noEmit` · `bunx biome check src/ tests/` · grep de límites en `HabitsForm.tsx` | 0 errores · 104 archivos sin cambios · solo `className="w-24"` | 0 | — | ✅ |
| Suite Playwright COMPLETA como CI tras el grupo 4 (`PLAYWRIGHT_BASE_URL=http://localhost:8000`, imagen reconstruida) | **243 passed, 0 failed**; tras el arreglo del foco (imagen reconstruida otra vez) **245 passed, 0 failed** | 0 | 0 | ✅ |
| **Ronda 2.** Re-corrido por el orquestador: `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) · `tsc` · `biome` | **151 passed, 0 failed** · 0 errores · 104 archivos sin cambios; suite COMPLETA como CI (imagen reconstruida) **253 passed, 0 failed** | 0 | 0 | ✅ |
| **Ronda 3.** Re-corrido por el orquestador: `bunx playwright test tests/profile-habits.spec.ts tests/profile.spec.ts tests/profile-history.spec.ts` (chromium + s26-ultra) · `tsc` · `biome` | **153 passed, 0 failed** · 0 errores · 104 archivos sin cambios; suite COMPLETA como CI (imagen reconstruida) **255 passed, 0 failed** | 0 | 0 | ✅ |
| Suite Playwright COMPLETA como CI (primera entrega) (`PLAYWRIGHT_BASE_URL=http://localhost:8000`, imagen reconstruida con esta rama), 2 corridas | **239 passed** · 238 passed + 1 failed: `login.spec.ts:87`, el heredado del saludo contra el redirect de la home (en el inbox de deudas) | 1 corrida con el heredado | 0 | 🟡 inestabilidad heredada |

## Red before green

| Task | Red run: command → failures | `test:` commit | Green run | `make tdd-check` |
|---|---|---|---|---|
| 1 · backend | `uv run pytest tests/api/routes/test_profile_habits.py -q` → **77 failed, 15 passed, 0 errors**: el modelo viejo rechaza el vapeador como objeto y los campos nuevos (`extra_forbidden`), falta `upgrade_stored_habits` (ImportError dentro de 6 tests) y la fila con la forma anterior se lee vacía | 97074f1 | 92/92 del archivo; suite completa 342 passed | ✓ red 97074f1, tests sin cambios hasta el verde 7e9b05b |
| 2 · frontend | `bunx playwright test tests/profile-habits.spec.ts` → **32 failed, 27 passed** (16 + 13 por proyecto, 0 errores de setup): faltan las preguntas nuevas, el estado, el guardado automático y D20; el vapeador sembrado como objeto no se ve elegido | 1cfa5ce | 59/59 (verde 7b56610) | ✓ red 1cfa5ce, tests sin cambios hasta el verde 7b56610. Después, un `test:` propio (1facd80): formato de biome y `Connection: close` en la API de los e2e (un `socket hang up` de R1 en s26-ultra, sin aserción cambiada). Después hubo otro `test:` (a985310, formato de ruff en un caso fuera de escala), y `make tdd-check` ancló en a985310, no en 1facd80 (*corrección, revisión ronda 1, D1*; deuda T6 conocida: pasa en vacío para ese commit) |

| 4 · frontend sin guardado automático | `bunx playwright test tests/profile-habits.spec.ts` → **7 failed, 25 passed por proyecto**: faltan el texto, el diálogo y `beforeunload`, `aria-disabled`, "nada se manda hasta Guardar", el aviso de Cancelar y la marca que sigue (A3). Filas 18 y 23 ya pasaban (sin diálogo hoy; el formulario ya validaba al salir) | d1c4ab7 | 32/32 por proyecto (verde 50e28b5) | ✓ tests sin cambios desde d1c4ab7 hasta 50e28b5 |
| 5 · backend B1 | `uv run pytest tests/api/routes/test_profile_habits.py -k unreadable_habits_json` → **1 failed, 2 passed**: `RecursionError` en el anidado de 100 000 niveles (500) | d5f668f | 95/95 del archivo; suite completa 345 passed (verde 5c800bb) | ✓ red d5f668f |
| Foco tras "Seguir editando" (defecto de la exploración) | `-g "fila 17"` → **1 failed por proyecto** (fila 17b: foco en `<body>` tras "Seguir editando" y Escape) | 02c1d04 | 33/33 por proyecto (verde 6d43be9) | ✓ red 02c1d04, tests sin cambios hasta el verde |
| Ronda 2 (R2-1…R2-5, R2-7) | `bunx playwright test tests/profile-habits.spec.ts` → **4 failed, 33 passed por proyecto**: falta "Guardando…" (fila 21), el guardado en camino cruza de cuenta (27), los chips no se bloquean (28), el foco no vuelve al título (29). La fila 26 (solo un número) ya pasaba | 97ab624 | 37/37 por proyecto (verde 8de47e1) | ✓ red 97ab624, tests sin cambios hasta el verde |
| Ronda 3 (R3-1…R3-4) | `bunx playwright test tests/profile-habits.spec.ts` → **2 failed, 36 passed por proyecto**: la fila 28 (chips sin atenuar; salir no espera) y la 30 (el 422 se pierde al salir). La 27 endurecida ya pasaba; el tester comprobó que falla si la respuesta se escribe en la caché | 45b73b3 | 38/38 por proyecto (verde b09397f) | ✓ red 45b73b3, tests sin cambios hasta el verde |

## Criterio → prueba

| AC / escenario | Prueba | Estado |
|---|---|---|
| C-1/C-10 Lo dejó, con la edad de inicio y la de fin | `test_c1_c10_quit_alcohol_with_start_and_quit_age_round_trip` · e2e fila 2 | ✅ |
| C-10 Alcohol: empezó después de dejarlo | `test_c2_c10_c12_start_age_after_quit_age_rejected[alcohol]` · e2e fila 3 | ✅ |
| C-1/C-2 Una edad mayor que la actual (las 8 edades) | `test_c1_c2_age_above_current_rejected_nothing_saved`, `test_c1_c2_age_without_birth_date_accepted` · e2e fila 4 | ✅ |
| C-1 Lo que no aplica se descarta | `test_c1_c11_what_does_not_apply_is_dropped`, `test_c1_switch_current_to_never_drops_stored_age_and_audit_c` · e2e fila 5 | ✅ |
| C-2 Tabaco que dejó, y vapeador actual | `test_c2_former_tobacco_and_current_daily_vaping_round_trip` · e2e fila 6 | ✅ |
| C-2 Empezó después de dejarlo | `…start_age_after_quit_age_rejected[tobacco]` · e2e fila 7 | ✅ |
| C-11 Vapeador actual algunos días | `test_c11_current_vaping_some_days_round_trip` · e2e fila 8 | ✅ |
| C-11 Vapeador de antes, y luego todos los días | `test_c11_some_days_then_daily_then_former` · e2e fila 9 | ✅ |
| C-3 Humo ajeno | existentes · e2e fila 10 | ✅ |
| C-4/C-12 Humo de leña de antes, como rango | `test_c4_c12_former_wood_smoke_round_trip`, `…[wood_smoke]` · e2e fila 11 | ✅ |
| Contesta solo una cosa | e2e fila 12 | ✅ |
| Respuestas fuera de su escala | `test_c_out_of_scale_answers_rejected_habits_unchanged` (días 0/31, horas 0/25, vapeador como texto, `years` en el PUT) | ✅ |
| Lo guardado antes se sigue leyendo | `test_legacy_stored_habits_still_read`, `test_upgrade_stored_habits_unit` | ✅ |
| C-6 Sin puntaje ni índice | `test_c6_no_score_or_risk_in_the_response` · e2e fila 15 ("horas-año") | ✅ |
| C-13 Se guarda al tocar "Guardar" | e2e fila 16 | ✅ |
| C-13 Aviso al salir con cambios sin guardar (y el foco vuelve) | e2e filas 17 y 17b | ✅ |
| C-13 Sin cambios no hay aviso | e2e fila 18 | ✅ |
| C-13 Aviso del navegador al recargar | e2e fila 19 (`page.reload()` → diálogo `beforeunload`) | ✅ |
| C-13 Sin aviso cuando la sesión cambió | e2e fila 20 (cierre de sesión en otra pestaña) | ✅ |
| C-13/D20 Botones no disponibles mientras guarda | e2e fila 21 (`aria-disabled`, foco en "Guardar", un solo `PUT`) | ✅ |
| C-13 Cancelar descarta | e2e fila 22 | ✅ |
| C-13 Solo un número cambia (R2-7) | e2e fila 26 | ✅ |
| C-13 Un guardado en camino no llega a otra cuenta (R2-1) | e2e fila 27 (cierre e inicio de sesión reales en la misma pestaña) | ✅ |
| C-13 Mientras guarda no se cambia nada, y salir espera sin preguntar (R2-2, R2-3, R3-1, R3-4) | e2e fila 28 | ✅ |
| C-13 Un rechazo al salir se queda a la vista (R3-3) | e2e fila 30 | ✅ |
| C-13 El foco vuelve al título si su elemento ya no existe (R2-4) | e2e fila 29 (384 px, menú lateral) | ✅ |
| C-14 Fuera de escala al salir del campo | e2e fila 23 (horas, edad mayor que la actual, inicio > fin en vapeador y leña, "12a"; 0 `PUT`) + grep de límites | ✅ |
| C-14 La marca sigue mientras el campo está a la vista | e2e fila 24 | ✅ |
| Lo guardado antes se sigue leyendo · filas ilegibles (B1) | `test_unreadable_habits_json_read_as_null_not_500[…]` (JSON inválido, lista, anidado 100 000) | ✅ |
| Aislados y cifrados | `test_c_habits_isolated_and_encrypted_at_rest` (también `some_days` y `days_last_30` en claro) | ✅ |

## Exploración en Chrome (agente, antes de la validación humana)

### Tras la revisión ronda 1, sin guardado automático

Imagen reconstruida con el grupo 4 en `localhost:8000` (y el arreglo del foco en Vite `localhost:5173`), la misma cuenta
de prueba (36 años, tabaco "Nunca" sembrado). La ventana no baja de 580 px de ancho (el mínimo de Chrome en este
equipo): el ancho de 384 px lo cubre s26-ultra. Los `PUT` se contaron con el lector de red del navegador.

| Intento | Qué pasó |
|---|---|
| Abrir "Hábitos" | "Tus respuestas se guardan cuando tocas «Guardar»." debajo de la introducción |
| Tabaco "Actual", 12 sin salir del campo, "‹ Mi perfil médico" | "¿Salir sin guardar?" con el foco en "Seguir editando" |
| "Seguir editando" y Escape | El diálogo se cierra con "Actual" y 12. **Defecto:** el foco caía a `<body>` → rojo 02c1d04, arreglo 6d43be9; vuelto a probar: foco al enlace (Enter en "Seguir editando") y al campo con su 8 (atrás + Escape) |
| "Salir sin guardar" | `/perfil`; 0 `PUT`; el GET trae tabaco "Nunca" |
| Leña "Actual" y atrás del navegador | Diálogo; mientras pregunta, la barra de direcciones ya dice `/perfil` (así bloquea TanStack Router); con "Seguir editando" vuelve a `/perfil/habitos` con la leña elegida |
| `beforeunload` con un cambio | El evento queda prevenido (el navegador pregunta); la fila 19 lo prueba con una recarga real |
| Triple clic en "Guardar" | 1 solo `PUT`, un aviso "Hábitos guardados", `/perfil`, sin diálogo |
| Alcohol "Lo dejé" y doble clic en "Cancelar" | 0 `PUT`, un aviso "Se descartaron los cambios", sin diálogo; el GET trae alcohol vacío y la leña guardada |
| Alcohol "Actual" sin guardar y otra pestaña quita la sesión (lo que hace "Cerrar sesión") | Esta pestaña llega a `/login` sin diálogo ni aviso del navegador; 0 `PUT` |
| Ancho y consola | Sin scroll horizontal a 580 px; en consola solo el error de una extensión de Chrome ajena a la app |

Sin defectos pendientes dentro del plan.

### Ronda 3 (Vite `localhost:5173`, 580 px)

| Intento | Qué pasó |
|---|---|
| Tabaco "Actual" + 20, "Guardar" con el `PUT` demorado 4 s, y "‹ Mi perfil médico" | Sin diálogo; la pantalla espera en `/perfil/habitos` con los chips atenuados (opacidad < 1) |
| Al terminar el guardado | `/perfil` con "Hábitos guardados" |
| Reabrir "Hábitos" | Tabaco "Actual" con 20: lo guardado |

Sin defectos.

### Ronda 2 (Vite `localhost:5173`, ventana de 580 px, donde el menú es la hoja lateral del celular)

| Intento | Qué pasó |
|---|---|
| Tabaco "Actual" 10 sembrado; solo el número a 20, sin salir del campo; menú lateral → "Mi perfil médico" | "¿Salir sin guardar?" |
| "Seguir editando" | El menú ya se cerró: el foco va al título "Hábitos"; el 20 sigue |
| "Guardar" con el `PUT` demorado 4 s | El botón dice "Guardando…" con `aria-disabled`; los chips con `aria-disabled` y un clic en "Antes" no cambia nada; el número de solo lectura |
| "‹ Mi perfil médico" mientras guarda | `/perfil` sin diálogo; al terminar, sin aviso ni regreso; el GET trae 20 |
| Consola | Solo el error de una extensión de Chrome ajena a la app |

Sin defectos.

### Primera versión, con guardado automático (retirado por la Decision 8; queda como historia)

Imagen reconstruida con esta rama en `localhost:8000`, cuenta de prueba local nueva (nacida el 15/03/1990, 36 años, con
tabaco "Nunca" sembrado), ventana de 580 px. Los `PUT` se contaron con el lector de red del navegador.

| Intento | Qué pasó |
|---|---|
| Alcohol "Actual" | Aparece "¿A qué edad empezaste a tomar?" con "Sin contar probaditas."; el chip se guarda solo ("Guardado", 1 `PUT`) |
| Edad de inicio 40 y Tab | "La edad no puede ser mayor que tu edad actual" junto al campo (`aria-describedby` = ayuda + error), estado "Sin guardar: corrige el campo marcado", el foco sigue al siguiente control, 0 `PUT` |
| Corregido a 17 y Tab, luego recargar | "Guardado" con 1 `PUT`; tras recargar, 17 sigue ahí |
| Vapeador "Actual" → "Algunos días" → 31 días | "Debe estar entre 1 y 30" y 0 `PUT`; con 12, "Guardado". 3 `PUT` en total (dos chips y el número) |
| Leña "Antes" | Aparecen inicio, fin y horas al día; ya no "Años con humo de leña" |
| Escribir 3 horas y, sin salir del campo, tocar "‹ Mi perfil médico" | Al salir se manda lo pendiente (1 `PUT`); al reabrir, 3 horas y 12 días |
| Leña "Actual" y triple clic inmediato en "Guardar" | 1 solo `PUT`, un aviso "Hábitos guardados", vuelve a `/perfil` |
| Tabaco "Actual" (guardado solo) y doble clic en "Cancelar" | Vuelve con un aviso "Se descartaron los cambios"; el GET trae tabaco "Nunca" y la leña como estaba al abrir |
| Otra pestaña quita la sesión (lo que hace "Cerrar sesión") | La pestaña con los hábitos se va sola a `/login` |
| Ancho y consola | Sin scroll horizontal a 580 px (384 lo cubre s26-ultra); en consola solo el error de una extensión de Chrome ajena a la app |

Sin defectos dentro del plan.

## Entorno

- Durante el grupo 2 la imagen no se podía construir (su `bun run build` corre `tsc` y `HabitsForm.tsx` usaba la forma
  vieja hasta el verde). Para que los e2e del rojo hablaran con el contrato nuevo se copiaron `models.py` y
  `routes/profile.py` al contenedor en marcha (`docker compose cp`; `fastapi dev` recarga). Tras el verde se reconstruyó
  la imagen y la suite completa corrió contra ella.

## Deuda

- **Doble clic en el resto de la app (D20):** fila en la tarea de deudas; aquí solo se aplica a hábitos.
- **`ui/loading-button.tsx` pone `disabled` nativo**, que rompe D20 (pierde el foco); hábitos arma su propio botón.
  Darle un modo `aria-disabled` va con la fila de D20 de la tarea de deudas.
- **Un 422 en un grupo de chips que sigue a la vista** (incluido el que se acaba de contestar) se queda hasta el
  siguiente "Guardar"; así lo lee el contrato (A3: solo se borran los errores de lo que se oculta).
- **Atrás del navegador con el diálogo abierto** deja ver `/perfil` en la barra de direcciones mientras pregunta
  (TanStack Router); al elegir "Seguir editando" vuelve a `/perfil/habitos`. Lo mismo pasa durante toda la espera de
  una salida con atrás mientras guarda (ronda 4, R4-7); si el guardado falla, la URL vuelve a `/perfil/habitos`.
- **Atrás mientras guarda y luego otra salida dentro de la app** (R4-2, ⏸️): la primera salida retenida queda sin
  resolver; si el guardado falla, la URL dice `/perfil` con el formulario a la vista, y el historial salta una entrada.
  Camino raro, sin pérdida de datos; arreglarlo pide manejar dos bloqueos a la vez de TanStack Router.
- **Los chips no tienen una propiedad para quedar no disponibles:** `HabitsForm.tsx` les pone `aria-disabled` desde
  fuera (`ChipGroup.tsx` no se toca en este cambio). Darle esa propiedad va con la fila de D20 de la tarea de deudas.
- **Un error del `PUT` que llega con otra cuenta** (cerrar sesión e iniciar otra mientras guarda): un error que no es
  422 muestra el aviso genérico (sin datos) a quien esté usando la app; un 422 no muestra nada. *Corregido en la ronda
  3 (R3-3): antes decía que siempre salía el aviso genérico. Con la misma sesión, salir ya espera al guardado.*
- **Sin guardado automático** (Decision 8): en el celular, si el navegador cierra la pestaña en segundo plano, lo no
  guardado se pierde sin aviso.
- **Flake heredado** `login.spec.ts:87` (en el inbox de deudas).
- **`make tdd-check` ancla en el `test:` más nuevo** (T6, ya ⏸️): para el grupo 2 la medición real es 1cfa5ce → 7b56610.
- **`lint.py` del harness** compila con el Python 3.9 del sistema y marca el `except A, B:` (PEP 758) de
  `profile.py`; ya en el inbox del template.
