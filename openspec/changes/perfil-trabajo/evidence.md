# Evidence — perfil-trabajo

## Criterion → test → result

| Criterio | Prueba | Ancla | Resultado |
|---|---|---|---|
| T-1 guardar y ver en la tarjeta | `test_t1_employed_driver_round_trip` · «T-1 guardar el trabajo y verlo en la tarjeta…» | `backend/tests/api/routes/test_profile_work.py:142` · `frontend/tests/profile-work.spec.ts:272` | ✅ pytest · ✅ chromium y s26-ultra |
| T-2 todo opcional | `test_t2_*` (3) · «T-2 todo es opcional…» | `test_profile_work.py:157`, `:175`, `:192` · `profile-work.spec.ts:308` | ✅ · ✅ |
| T-3 «Nada de esto» excluye | `test_t3_no_exposures_drops_exposures` · «T-3 «Nada de esto» excluye…» | `:207` · `:325` | ✅ · ✅ |
| T-4 jubilado con el de más años | `test_t4_retired_keeps_longest_job_drops_occupation_and_shift` y `test_t4_non_employed_with_no_exposures_stores_false` (ronda 1, V8) · «T-4 el detalle solo aplica con «Trabajo»…» | `:226`, `:249` · `:348` | ✅ · ✅ |
| T-5 cifrado, solo del paciente, consentimiento | `test_t5_*` (4: otro usuario, cifrado, y consentimiento en GET y PUT) | `:400`, `:415`, `:434` | ✅ |
| T-6 cambiar de situación borra lo del trabajo | `test_t6_switch_to_looking_clears_job_fields_keeps_longest_job` · «T-6 cambiar de situación…» | `:270` · `:370` | ✅ · ✅ |
| Fuera de opciones o de largo | `test_out_of_options_or_length_is_422_and_leaves_work_unchanged` (7 casos) y 4 de recorte y repetidos · «largo: … 200 caracteres» | `:317`-`:386` · `:412` | ✅ · ✅ |
| Sin veredicto (C-6), accesibilidad, D20, foco, 384 px | `test_response_has_exactly_the_six_keys_no_verdict` · «accesibilidad, D20 y sin veredicto…» (desde la ronda 1 también: foco dentro del diálogo al abrir `:439`, sin la X mientras guarda `:509`, una ocupación de 200 sin espacios no desborda a 384 px `:530`) | `:452` · `:431` | ✅ · ✅ |
| Fila ilegible en la base (ronda 1, V9) | `test_unreadable_work_*` (1 + 3 casos): responde vacío y el log lleva solo el id | `:483`, `:519` | ✅ |

## Red before green

| Grupo | Rojo (corrido por el orquestador) | Commit |
|---|---|---|
| 1 · backend | `cd backend && FASTAPI_ENV=development uv run pytest tests/ -q` → **23 failed, 560 passed, 0 errors**. Las 23 son `404` de `/profile/work` (21 esperaban 200 y 2 esperaban 403); ningún error de importación, fixture o SQL | `25be476` |
| 2 · frontend | `bunx playwright test tests/profile-work.spec.ts --project=chromium --project=s26-ultra` → **14 failed, 1 passed** (el setup). 10 no encuentran «Editar trabajo» en la tarjeta; 4 leen la fila «Trabajo», que no existe («Sin registrar» y el resumen de T-6 esperados, `<0 etiquetas>` recibido) | `5505fd0` |

**Rojo inválido corregido:** la primera corrida del tester del frontend falló entera en el setup. `GET /profile` daba
500 porque la base de desarrollo no tenía la columna `work`: reconstruir el contenedor no aplica las migraciones. El
orquestador corrió `alembic upgrade head` y repitió el rojo, que entonces falló por lo que faltaba. La receta quedó en
el bloque de contexto de `AGENTS.md` (`prestart.sh`, como el CI).

**Asimetría declarada:** el orquestador agregó `profile-work` al `testMatch` de `s26-ultra`
(`frontend/playwright.config.ts:54`) en el commit `test:` `5505fd0`. Es infraestructura de pruebas fuera de `tests/`;
para esa línea `make tdd-check` pasa de forma vacía.

## Green

| Grupo | Verde (re-corrido por el orquestador) | Commit |
|---|---|---|
| 1 · backend | `uv run coverage run -m pytest tests/ -q` → **583 passed, 0 failed, 0 skipped**; cobertura **96 %**; `mypy app` sin problemas; `ruff check app` limpio. Migración: sube y baja (corrida del implementer contra la base de pruebas: `7d3e9a1c5b42` ↔ `3b8e5f2a9c61`) | `d0ac777` (+ cliente `0b71f68`) |
| 2 · frontend | `profile-work.spec.ts` + `profile.spec.ts` en chromium y s26-ultra → **27 passed, 0 failed, 0 skipped**; `tsc -p tsconfig.json --noEmit` limpio; `biome check src` limpio (88 archivos) | `dd1bffb` |

`make tdd-check`: ✓ en los dos grupos (rojo `25be476`, después `5505fd0`; las rutas de pruebas no cambiaron desde
entonces). Sin caracteres invisibles en el diff.

## Full suite (como CI)

Backend reconstruido, migraciones con `docker compose run --rm backend bash scripts/prestart.sh` (como
`.github/workflows/playwright.yml:84`) y `PLAYWRIGHT_BASE_URL=http://localhost:8000 bunx playwright test`: **366 passed,
1 failed, 0 skipped** (367, 3.7 min). La que falló es `reset-password.spec.ts:90`, el intermitente heredado del correo
(`memory/inbox/2026-10-20-fix-aparte-e2e-intermitentes-heredados-admin.md`); sola pasa (chromium, 2 passed con el
setup). Por ella, «truly green» queda sin marcar en el PR, como en los PR #35 y #37.

## Exploratory pass (Chrome, :8000 con la imagen reconstruida, cuenta de prueba creada por API; primero en oscuro, la ronda 1 completó el claro)

| Qué se intentó | Qué pasó |
|---|---|
| Cuenta nueva, «Mi perfil médico» | Fila «Trabajo: Sin registrar»; botón «Editar trabajo» junto a los otros dos |
| Abrir el diálogo sin situación | Solo «Hoy…» y «El trabajo que más años has tenido»; título y descripción del plan |
| «Trabajo», ocupación «  Enfermera 👩‍⚕️ de urgencias  » (emoji y espacios), Polvo → Nada de esto, De noche, **doble clic** en «Guardar» | Un solo aviso «Trabajo guardado»; fila «Enfermera 👩‍⚕️ de urgencias · de noche»; la API guardó el texto recortado con el emoji, `exposures: []`, `no_exposures: true` |
| Reabrir | «Nada de esto», «De noche» y la ocupación como se guardaron |
| Elegir «Hogar» y salir con Escape | Desaparecen los campos del trabajo; al cerrar, la fila no cambia; al reabrir vuelve a estar «Trabajo» (el borrador se descarta) |
| Tocar «Trabajo» elegido | Se desmarca: ninguna situación y solo el campo del de más años |
| «Estudio» y guardar | Fila «Estudio» |
| Escribir más de 200 caracteres en el trabajo de más años, guardar y recargar | El campo se queda en 200; tras recargar la fila muestra el texto con «antes: » |
| Ventana angosta (el mínimo de Chrome: 500 px de ancho útil) con el diálogo abierto en «Trabajo» | Sin desborde lateral (`scrollWidth` 500 = ancho); los chips se acomodan en renglones; «Guardar» a todo el ancho. Los 384 px los cubre `s26-ultra` |
| Consola | Sin errores de la página (solo uno de la extensión de Chrome) |

| **Ronda 1 (V4), modo claro:** «Busco trabajo», «Jubilado o pensionado» y «No puedo trabajar por mi salud», cada una con «Albañil» en el de más años | Solo se ven «Hoy…» y el campo del de más años; filas «Busco trabajo · antes: Albañil», «Jubilado o pensionado · antes: Albañil», «No puedo trabajar por mi salud · antes: Albañil» |
| **Ronda 1:** «Nada de esto» contra cada exposición (Polvo, Químicos o solventes, Ruido fuerte) | En los tres: «Nada de esto» apaga la exposición y la exposición apaga «Nada de esto»; las tres juntas se pueden elegir |
| **Ronda 1 (V5):** ocupación de 200 caracteres sin espacios, «Nada de esto», «Rotativo», guardar | La fila se parte en renglones, sin desborde (`scrollWidth` = ancho); la X del diálogo está presente en reposo. Que desaparezca mientras guarda (V1) y los 384 px los fija el e2e |

Sin defectos. Se le pasa `validation.md` a Saúl Pérez.

**Cambio de formato tras el verde (declarado):** al empujar, el gate prek (`ruff format`) unió en una línea una aserción
de `test_profile_work.py:258`. No cambia lo que prueba; va en su propio commit con prefijo `test:` (la regla de la casa para todo cambio en rutas de
pruebas) y el archivo sigue con 23 passed. `make tdd-check` mide desde ese commit, así que para esa línea pasa de forma
vacía; la implementación ya estaba verde contra la versión sin formatear.

## Revisión adversaria, ronda 1 (aplicada)

Dos finders (backend, seguridad y criterios; frontend, convenciones y documentos) y un validador distinto, que
reprodujo los 9 hallazgos: 9 confirmados, todos bajos (V1 bajó de medio). Saúl Pérez aprobó aplicarlos todos (V2 y V7
solo en la instancia nueva). Comentarios `finder` y `validator` en el PR #40.

| Hallazgo | Cambio | Commit |
|---|---|---|
| V1 la X parecía disponible mientras guarda | `showCloseButton={!busy}` (`EditWork.tsx:142-146`); e2e `:509` | `ad3376f` (rojo verificado) · `68e0e82` |
| V2 el prototipo de producto no normalizaba | `normalizarTrabajo` al guardar (`perfil-secciones.html:266-273`, `:687`) | `e9ad78f` |
| V3 anclas corridas y «pytest (11)» | esta tabla y el cuerpo del PR (12) | este commit |
| V4 tarea 3.2 marcada de más | pase completado arriba (claro, tres situaciones, exclusiones); 3.3 marcada | este commit |
| V5 desborde con una palabra larga | `[overflow-wrap:anywhere]` en `Row` (`perfil.tsx:50`); e2e `:530` | `ad3376f` · `68e0e82` |
| V6 foco sin prueba y dos citas | e2e `:439`; `exploration.md:53`, `:84`; `design.md` fila 8 | `ad3376f` · `e9ad78f` |
| V7 `research.md` inexistente y URL de HL7 | `dominio.md:431`, `memory/research/ocupacion.md` | `e9ad78f` |
| V8 `no_exposures` con otra situación | `test_t4_non_employed_with_no_exposures_stores_false` (el mutante ahora muere: 1 failed) | `ad3376f` |
| V9 fila ilegible sin prueba | dos pruebas portadas de hábitos (el mutante `raise` ahora muere: 4 failed) | `ad3376f` |

Re-corrido por el orquestador tras aplicar: backend **588 passed, 0 failed, 0 skipped**; `profile-work` + `profile`
en chromium y s26-ultra **27 passed**; `tsc` y `biome` limpios; `make tdd-check` ✓ (rojo `ad3376f`).
