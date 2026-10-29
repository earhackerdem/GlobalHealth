# Evidence — ejercicio-lista-casillas (E-1…E-4)

## Suites

| Command | Result (numbers) | Errors in log | Skipped | Truly-green verdict |
|---|---|---|---|---|
| Verde del implementer: `cd frontend && bunx playwright test tests/profile-habits.spec.ts` (Vite :5173 + API :8000) | 161 passed · 0 failed (6.5 min). Corridas intermedias: subconjunto `-g "E-1…"` 35 passed; `biome` falló una vez por formato, ya corregido | 0 | 0 | ✅ |
| Mismo comando, re-corrido por el orquestador (commit `f1cf272`) | **161 passed · 0 failed** (2.9 min, chromium + s26-ultra) | 0 | 0 | ✅ |
| Tras el apply de la ronda 1 de revisión (fixer: 5 passed en el subconjunto E-4b + fila 12; 163 passed en el archivo), re-corrido por el orquestador | **163 passed · 0 failed** (2.7 min; 81 pruebas × 2 proyectos + setup; +E-4b) · `tsc` limpio | 0 | 0 | ✅ |
| `make tdd-check` | ✓ rojo `8e958fe`; las rutas de pruebas no cambiaron desde entonces | — | — | ✅ |
| `bunx tsc -p tsconfig.json --noEmit` · `bunx biome check src/components/Profile tests/profile-habits.spec.ts` | limpios (15 archivos) | 0 | — | ✅ |
| Suite Playwright COMPLETA como CI (`PLAYWRIGHT_BASE_URL=http://localhost:8000`, imagen reconstruida con `f1cf272`) | **339 passed · 2 failed**. Los 2 fallos son de `reset-password.spec.ts` (el archivo se identificó por el id de `.last-run.json`): el intermitente heredado de `memory/inbox/2026-10-20-fix-aparte-e2e-intermitentes-heredados-admin.md`. Con `--last-failed`, las 2 pruebas pasan (3 passed contando el setup). El diff no toca autenticación ni correo | 0 | 0 | 🟡 intermitencia heredada, ajena al cambio |
| Backend sin cambios: `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` | **560 passed** (igual que el cierre de la C2a) | 0 | 0 | ✅ |

## Criterio → prueba → anclaje → estado

| Criterio | Prueba (`frontend/tests/profile-habits.spec.ts`) | Estado |
|---|---|---|
| E-1 lista siempre a la vista | «E-1 (fila 1) la lista de actividades siempre a la vista…» (`:3486`) | ✅ chromium + s26-ultra |
| E-2 marcar abre debajo, desmarcar quita | «E-2 (fila 2) marcar abre sus preguntas debajo…» (`:3515`) | ✅ |
| E-3 excluyente | «E-3 (fila 3) 'No hago ejercicio' excluye…» (`:3611`) | ✅ |
| E-4 teclado y lector | «E-4 (fila 4) teclado y lector de pantalla…» (`:3638`) | ✅ |
| C-5 filas 1 a 4 (ahora con casillas) | «C-5 (fila 1)» `:2893` · «C-5 (fila 2)» `:2953` y U+200B `:2997` · «C-5, C-15 (fila 3)» `:3018` · «C-5 (fila 4)» `:3050` | ✅ |
| D20 en las casillas | «fila 12 (R7, C-13, D20)…» (`:3365`) | ✅ |
| Error de grupo que devuelve el servidor (contrato «Grupo»; ronda 1, A4) | «E-4b (fila 4b) el error de grupo que devuelve el servidor…» (`:3671`) | ✅ |
| Resto del requisito | filas 5 a 10 y 13 de la C2a, y la suite backend | ✅ |

## Exploración en Chrome (tarea 2.2), por el agente

La app corre en `http://localhost:8000` con la imagen reconstruida. Usé una cuenta de prueba nueva creada por la API
local; sus datos están solo en el scratchpad.

| Intento | Qué pasó |
|---|---|
| Abrir Hábitos | El grupo «¿Qué ejercicio haces?» trae 10 casillas: las 9 actividades y «No hago ejercicio». Ningún campo hasta marcar |
| Guardar sin nada en Ejercicio | Se guarda el bloque vacío (`exercise: null`), sin mensaje. Es lo que pide la spec (bloques opcionales, `openspec/specs/records/patient-profile/spec.md:612`) y lo prueba la fila 9 (`profile-habits.spec.ts:3319`). Lo reprodujo también el validador de la revisión el 2026-10-28 |
| Marcar Caminar, Correr y Otra | Cada una abre sus campos debajo de su casilla; Otra abre «¿Cuál?» primero |
| Guardar con Correr sin minutos y Otra vacía | No guarda. El foco va a «Minutos cada vez: Correr», que es lo primero que falta, con «Contesta esta pregunta.» y «Escribe cuál.». El total muestra 150 |
| Desmarcar Correr y Otra | Sus errores y campos se van y el total sigue en 150 |
| «No hago ejercicio» | Desmarca Caminar y el total desaparece |
| Volver a marcar Caminar | «No hago ejercicio» se desmarca y reaparecen 5 y 30 (Decision 3) |
| Doble clic en «Guardar» | Un solo guardado: `GET` devuelve walking 5×30, y running y other quedan `null` |
| Recargar | Caminar marcada con 5 y 30, total 150 |
| Teclado | Espacio en Bicicleta la marca y el foco se queda. Tab va a «Días por semana» de Bicicleta. Shift+Tab y Espacio la desmarcan y sus campos se van |
| Salir | Marcar y desmarcar no deja cambios, así que no hay aviso. Con Nadar marcada aparece «¿Salir sin guardar?», y «Salir sin guardar» lleva a /perfil |
| Consola | La app no dio errores. Hubo uno de una extensión de Chrome (`chrome-extension://…`), ajeno a la app |
| Tamaño | Cada casilla mide 16 × 16 px y su etiqueta, 55 × 14. Las filas sin marcar quedan a 28 px de distancia, lo que cumple WCAG 2.5.8 por espaciado. Es más chico que en el prototipo aprobado, que tenía filas de unos 40 px. Lo decide Saúl Pérez (`validation.md`, «Qué NO hace todavía») |
| 384 px | No se probó en Chrome, porque la ventana no se encoge. Lo cubren s26-ultra en todas las filas y el recorrido headless a 400 px del prototipo |

## Red before green

**Grupo 1: frontend, test→impl.** El tester escribió las pruebas a partir de la spec delta y del Interface contract.
El orquestador las commiteó como `8e958fe`.

| Run | Who | Result |
|---|---|---|
| Rojo final del tester: `cd frontend && bunx playwright test tests/profile-habits.spec.ts` (Vite :5173 + API :8000) | tester | 26 failed · 135 passed · 0 skipped (7.0 min). También hizo dos sondas solo en chromium, ya borradas: 1 falló por un error de la propia sonda y la otra pasó (2 passed) |
| El mismo comando, re-corrido por el orquestador | orquestador | **27 failed · 134 passed · 0 skipped** (8.0 min) |

- **Los 26 fallos esperados:** son 13 por proyecto (chromium y s26-ultra), y todos se deben a que falta la casilla
  (`getByRole('checkbox')` dentro del grupo «¿Qué ejercicio haces?»). Son E-1 a E-4 y las pruebas del ejercicio que
  pasaron de chips a casillas: C-5 filas 1 a 4 y U+200B, fila 9, C-14 fila 8, fila 12 y C-17 fila 13.
- **El fallo extra:** fila 31a en chromium (`profile-habits.spec.ts:1721`, atrás del navegador mientras guarda). El
  diff no la toca, porque los cambios empiezan en `:2745`. Corrida sola con `--repeat-each=4` pasa 4 de 4 (el setup
  aparte). Es intermitente y no tiene que ver con este cambio.
- **Sin roto:** no hay errores de sintaxis ni de tipos. `bunx tsc -p tsconfig.json --noEmit` y
  `bunx biome check tests/profile-habits.spec.ts` salen limpios. El diff no tiene caracteres invisibles literales
  (escaneado con `grep -P`).
- **Enmienda del plan a partir del rojo** (commit `be7a597`): el tester mostró que la cláusula de E-4 «Guardar sin
  nada → mensaje y foco en Caminar» no se puede alcanzar, porque los bloques son opcionales y «Guardar» guarda
  `exercise: null`. Se quitó de la spec y del plan. El tester agregó además `aria-disabled` en las casillas mientras
  guarda (D20) para no debilitar la fila 12.

## Revisión adversarial (ronda 1) y apply

- Dos finders, uno de código y otro de documentos, y dos validadores que reprodujeron cada hallazgo: 15 hallazgos (3 medios, 12 bajos). A5 quedó confirmado en el registro y falso positivo en el comportamiento. Detalle en los comentarios FINDER y VALIDATOR del PR #35.
- Saúl Pérez (author) aprobó «Todo lo recomendado», la enmienda de E-4 («Sí, guardar vacío») y «Línea y nombre en negritas» (B6), el 2026-10-28.
- El fixer aplicó todo sin rebotes. El orquestador corrigió el cuerpo del PR (A6, A7) y dejó imperativo el paso 5 del guion de E-2.
- **Guion de `validation.md` E-2 recorrido por el orquestador** (headless, Vite :5173, cuenta nueva por la API): (1) Correr abre sus campos; (2) Otra abre «¿Cuál?»; (3) 3×40 da un total de 120; (4) al desmarcar se van los campos y el total; (5) al volver a marcar reaparecen 3 y 40; (6) Guardar pasa sin errores a /perfil; (7) al reabrir, Caminar sigue marcada con 5×30 y Correr está sin marcar.
