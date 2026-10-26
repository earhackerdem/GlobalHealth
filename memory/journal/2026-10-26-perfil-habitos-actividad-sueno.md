# 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)

**Quién:** Saúl Pérez (author) partió la C2 en C2a (este cambio) y C2b ("Trabajo"), eligió las cuatro respuestas
recomendadas de la exploración (insomnio con los dos ítems de NHIS, los 4 niveles de NHANES `PAQ180`, el chip "No hago
ejercicio", horas de sueño enteras en 24 h) y aprobó el plan ("plan approved") después de que el agente recorriera el
prototipo en su Chrome.

**Intención:** sumar al cuestionario de hábitos el ejercicio por actividad con su total a la vista, el movimiento del
día aparte y el sueño, con las mismas reglas de guardado y sin veredicto (C-6).

**Qué se hizo:**
- **Backend (test→impl):** bloques cerrados `exercise`, `daily_movement`, `sleep` en `models.py`, con escalas en el
  esquema, normalización, filas de obligatoriedad y el `loc` de cuatro niveles. Rojo be8ae0f (285 fallos), verde
  4556d92; cliente regenerado 6971634.
- **Corrección del plan:** `design.md` decía "NO se toca" `routes/profile.py`, pero el contrato pedía un `loc` que la
  ruta no podía armar. El implementer se detuvo y lo señaló; el orquestador corrigió el plan y autorizó una línea (el
  campo partido por puntos). Queda anotado en `design.md` y `evidence.md`.
- **Pantalla (test→impl):** los tres bloques en `HabitsForm.tsx` y `profile.json`. Rojo d630f04 (24 fallos), una
  prueba devuelta al tester por el `<main>` anidado del layout (7d5d76a), verde 0d49477.
- **Producto:** `product/dominio.md` (filas de ejercicio, movimiento y sueño; se arregló de paso una línea en blanco que
  partía la tabla) y el prototipo `product/prototipos/perfil-secciones.html`.
- **Exploración en Chrome:** un defecto. Salir de dos cajas seguidas mientras dura un clic perdía la revisión de la
  primera (la salida diferida tenía una sola casilla). Venía de perfil-habitos-completitud, no de los bloques nuevos.
  Prueba roja 641e976 (6/6), arreglo 090e257.

**Verificación:** backend 551 passed, cobertura 96 %, mypy y ruff limpios. Suites de perfil 229 passed (chromium y
s26-ultra). `tsc` y `biome` limpios, `make tdd-check` ✓. Suite completa como CI: antes del arreglo, 328 passed y 1 failed en dos corridas (el heredado
`reset-password.spec.ts:90` de Mailpit, más frecuente que antes, anotado en el inbox); después del arreglo, 331 passed. Números en `evidence.md`.

**Deuda:**
- `<main>` anidado en el layout (`memory/inbox/2026-10-26-main-anidado-en-el-layout.md`).
- El falso positivo de `lint.py` con PEP 758 volvió a bloquear a un agente: recurrencia anotada en
  `memory/meta-improvements/2026-10-20-el-hook-lint-py-posttooluse-compila.md`, para decidir antes de la C2b (harness
  first).
- `zod.gen.ts` lleva `max(60)` sin `min(1)` en el nombre de "Otra": el vacío es "sin contestar" a propósito.

**Siguiente:** revisión adversarial con la regla de cierre de la Decision 7, archivo como último commit del PR, y
después la validación de Saúl Pérez con `validation.md`.

## Revisión, ronda 1 (2026-10-26)

**Quién:** cinco finders y tres validadores automáticos (`/epe-4-review`); Saúl Pérez (author) aprobó "Todo lo
recomendado".

**Qué salió:** 13 hallazgos tras deduplicar, todos bajos. 12 confirmados; D4 (el plan enmendado) quedó casi todo como
falso positivo, porque el commit, la evidencia y el journal sí lo registraban.

**Aplicado:**
- **Código (b083b89, pruebas 2c99c8f):** el nombre invisible de "Otra" cuenta como sin contestar (B2, en API y
  pantalla); un bloque de sueño o de movimiento sin respuestas se guarda `null` (B3); la región viva del total queda en
  el árbol de accesibilidad (P1).
- **Pruebas:** casos en los extremos (B4), `does_exercise` obligatorio (B5) y "meta" como palabra prohibida (D3).
- **Documentos (36da16d):** la spec dice lo que se ve ("Otra" con "Senderismo" en "¿Cuál?"); citadores de la propuesta
  y el dominio al día; `validation.md` sin pasos imposibles a mano; nota de la enmienda en `design.md`; el prototipo del
  producto con los exclusivos por grupo.
- **Investigación:** la regla de "menos de 1 hora" es solo de NHIS. ENSANUT 2022 mide el sueño en 5 categorías, así
  que la Decision 5 ya no dice "sin convertir". La introducción omitida del GPAQ queda como decisión [OPINION].

**Deuda (memory/closed):**
- B1: un surrogate suelto da 500 y deja el texto en el log, en toda la API; queda como historia propia en la tarea de
  deudas.
- B2 del historial: el mismo texto invisible en "¿Cuál fue?".

**Verificación:** backend 560 passed (cobertura 96 %), perfil 231 passed, `tsc`, `biome`, mypy y ruff limpios,
`tdd-check` ✓ (2c99c8f). El fixer vio dos intermitencias en las suites de perfil, en pruebas que no tocó
(`profile-history.spec.ts:415` y un "socket hang up" en la fila 4); las dos pasaron solas 6/6, y la corrida del
orquestador salió limpia.

**Siguiente:** ronda 2 con la regla de cierre de la Decision 7.

## Revisión, ronda 2 y cierre (2026-10-26)

**Qué salió:** dos finders sobre lo que tocó la ronda 1 (`a95570c..d3f114b`), validados por otros dos agentes por
reproducción. Once hallazgos bajos (C1–C4, M1, M2, M4–M6, M8, M10) y dos falsos positivos (M3, M7). El único que llegó
como medio (M1) bajó a bajo: el "socket hang up" de la fila 4 ocurre en `createUser` del helper compartido
`privateApi.ts`, antes de cualquier código de hábitos. Se reprodujo sobre la pila estable, así que la hipótesis de la
recarga quedó descartada.

**Decisión:** se aplicó la regla de cierre de la Decision 7, aprobada con el plan. Los bajos quedan como deuda en
`memory/closed/2026-10-26-ronda-2-de-perfil-habitos-actividad-sueno.md`, los falsos positivos de las dos rondas
congelados en `memory/closed/2026-10-26-falsos-positivos-revision-perfil-habitos-actividad-sueno.md`, y se archiva. Al
cerrar solo se tocó el registro de M1 (fila en `evidence.md` y línea en el inbox de e2e intermitentes), porque la
evidencia debe decir los números reales.

**Corrección en línea:** la sección de la ronda 1 dice que la Decision 5 "ya no dice 'sin convertir'"; lo dice, acotado a
NHIS, BRFSS y NHANES `PAQ180`.
