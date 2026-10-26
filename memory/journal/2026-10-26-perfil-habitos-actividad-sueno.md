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
