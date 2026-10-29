# Evidence — paleta-azul-clinico

## Criterion → test → result

| Criterio | Prueba | Ancla | Resultado |
|---|---|---|---|
| P-1 texto legible (claro) | «P-1 texto legible en claro» | `frontend/tests/visual-accessibility.spec.ts:351` | ✅ chromium y s26-ultra |
| P-2 controles visibles (claro) | «P-2 controles visibles en claro» | `:358` | ✅ |
| P-5 oscuro y marca | «P-5 en oscuro se cumplen los mismos umbrales y «Guardar» es #5aa9f0 (en claro #005eb8)» | `:365` | ✅ |
| P-3 no solo color | «P-3 el error no es solo color» | `:383` | ✅ (ya pasaba: comportamiento existente) |
| P-6 casillas y jerarquía | «P-6 casillas y jerarquía» | `:395` | ✅ |
| P-4 daltonismo | manual, `validation.md § P-4` | — | el agente lo recorrió con las matrices de Machado (2009) en Chrome: deuteranopía y tritanopía, casilla marcada distinguible; falta Saúl Pérez con la emulación de DevTools |

## Red before green

Commit `6bb06a4`. Comando: `bunx playwright test tests/visual-accessibility.spec.ts --project=chromium --project=s26-ultra`.

Resultado: **8 failed, 3 passed** (setup y P-3 ×2). Cada falla venía de un valor medido; ninguna, de un selector o del
setup:
- «Guardar» y el chip elegido: 3.61:1 en claro y 2.95:1 en oscuro.
- Bordes: 1.26:1 en claro y 1.48:1 en oscuro.
- Fondo de «Guardar»: `rgb(0, 148, 133)` y `rgb(39, 164, 149)`.
- Casilla: 16 px.
- Pesos: etiqueta 600 y `legend` 500.

**Asimetría declarada:** el orquestador agregó `visual-accessibility` al `testMatch` de s26-ultra en
`frontend/playwright.config.ts:54`. Es infraestructura de pruebas fuera de `tests/` que el tester no podía escribir,
y fue en el mismo commit `test:`. Para esa línea, `make tdd-check` pasa de forma vacía.

## Green

Commit `2fbad7b`. Resultados:
- `visual-accessibility.spec.ts`: **11 passed, 0 failed, 0 skipped** (setup + 5 + 5), corrido por el implementer y
  de nuevo por el orquestador.
- `profile-habits.spec.ts` (implementer): 163 passed en los dos proyectos, 0 failed.
- `tsc -p tsconfig.json --noEmit`: limpio.
- `biome check src`: limpio.
- `make tdd-check`: ✓. El rojo es `6bb06a4` y las rutas de pruebas no cambiaron desde entonces.

## Full suite (como CI)

Backend reconstruido (`docker compose up -d --build --force-recreate --no-deps --wait backend`) y
`PLAYWRIGHT_BASE_URL=http://localhost:8000 bunx playwright test`: **351 passed, 2 failed, 0 skipped** (353 en total, 7.3 min).
- `profile-habits.spec.ts:2317` (C-15 fila 2, alcohol 'Actual'): `socket hang up` al crear la cuenta por API
  (`privateApi.ts:17`), antes de abrir la pantalla. Pasa con `--last-failed`. Es un fallo de la conexión, no del
  color: coincidió con el pase exploratorio del agente, que usaba el mismo backend.
- `reset-password.spec.ts:90` es el intermitente heredado del correo. Falló otra vez con `--last-failed` y pasa
  solo (`tests/reset-password.spec.ts:90`, chromium, 1 passed).

Por esos dos, «truly green» queda sin marcar en el PR, igual que en el PR #35.

## Exploratory pass (Chrome, Vite :5173, cuenta de prueba)

| Qué se intentó | Qué pasó |
|---|---|
| Hábitos en claro: chips, casillas, botón | Chips sin elegir con borde visible; «¿Qué ejercicio haces?» en negritas; actividades en peso normal; casillas de 20 px |
| Hábitos en oscuro, marcar «Caminar» | Casilla azul claro con ✓ oscuro; campos de días y minutos con borde visible |
| Expediente en oscuro | «Agregar diagnóstico» azul claro con texto oscuro; «Registrar receta» con borde |
| Mi perfil médico en claro y en oscuro | Tarjetas blancas sobre `#f0f4f5` en claro; botones con borde |
| Editar antecedentes familiares (claro) | Casillas de 20 px; el diálogo no se descuadra; «Guardar» azul y «Cancelar» con borde |
| Hábitos con deuteranopía y tritanopía simuladas (filtro SVG, Machado 2009) | La casilla marcada se distingue de las demás en las dos |
| Consola | Sin errores de la app; solo un 401 de una extensión del navegador |
