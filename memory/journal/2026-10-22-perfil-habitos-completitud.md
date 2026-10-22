# 2026-10-22 · perfil-habitos-completitud (C-15…C-17)

**Quién:** Saúl Pérez (author) con el agente (orquestador), con tester e implementer por grupo.

## Intención
Al validar perfil-habitos-ajustes, Saúl Pérez notó que "Lo dejé" se podía guardar con solo la edad de fin, y que con
alcohol "Actual" no se pedían la frecuencia ni los fines de semana: lo que una respuesta abre debería ser obligatorio.
También, que "Escribe solo el número." seguía visible mientras corregía.

## Decisiones de Saúl Pérez
- "Obligatorias + «No recuerdo»" (AskUserQuestion, la recomendada).
- "plan approved" tras navegar el prototipo, que ya traía el ajuste de la investigación: "No recuerdo" solo en lo que
  pasó (edades; cigarros y horas de "Antes"), no en el AUDIT-C ni en lo actual (`memory/research/habitos.md#no-recuerdo`).

## Qué se hizo
- Backend: `"unknown"` en el mismo campo (FHIR `asked-unknown`), distinto de `null`; la tabla de obligatoriedad como
  datos (`HABITS_REQUIRED`), revisada después de normalizar; "unknown" nunca se compara.
- Frontend: chip "No recuerdo" con nombre accesible por pregunta, obligatorias al tocar "Guardar", el error que se va
  al corregir (C-17), intro nueva.
- Producto: `product/dominio.md` § Hábitos y la pantalla de hábitos de `product/prototipos/perfil-secciones.html`.

## Verificación
Backend 444 passed (96 %); e2e de perfil 181 passed (chromium + s26-ultra); suite Playwright completa 283 passed tras el
arreglo de la carrera (en otra corrida, 282 + el heredado `reset-password.spec.ts:90`). Exploración en Chrome sin
defectos (14 intentos). Números en `openspec/changes/perfil-habitos-completitud/evidence.md`.

## Sorpresas
- La imagen del backend compila el frontend: con `tsc` rojo entre el cliente regenerado y el verde del grupo 2 no se
  puede reconstruir. El rojo del frontend corrió con `models.py` copiado al contenedor (`fastapi dev` recarga), igual
  que haría el `sync` de `docker compose watch`; al verde, imagen reconstruida.
- La suite completa, con carga, destapó una carrera en C-17: una salida de campo diferida por un toque marcaba un error
  en el campo que se escribía. Arreglada en `leave()` (4ba7717); el estrés en Vite no la detecta.
- `places` faltante conserva "Elige dónde, o «No me expongo»" en vez de "Contesta esta pregunta." (más específico).

## Deuda
- La tabla de obligatoriedad vive dos veces (servidor y pantalla), como las demás reglas de hábitos; el servidor manda.

## Revisión ronda 1
Cinco lentes (F-Security sin hallazgos), cuatro validadores por reproducción: 2 medios (A: los casos fuera de escala ya
no protegían los límites tras C-15; B: la prueba de C-17 no detectaba revertir el arreglo, bajado a bajo) y bajos de
cobertura (D: 7/10 filas de la tabla de la pantalla sin prueba), esquema (E), documentos e investigación (C, G–J: Krosnick
estudió preguntas de opinión, se aplica por analogía; el umbral del ~1 % de NHIS no es comparable), PR (K), exploración
(L), comentarios (M, N) y prototipo (O). F (obligatorias sin marcar) ya triado como R8: deuda
(`memory/closed/2026-10-22-f-obligatorias-sin-marcar-habitos.md`). Saúl Pérez: "procede" con la recomendación (aplicar
todo, F a deuda, ronda 2 con la misma regla de cierre). Aplicado por dos fixers con archivos disjuntos; ninguno rebotó.
El fixer de pruebas quitó dos casos fuera de escala que repetían `UNKNOWN_IN_CURRENT_AMOUNT_CASES` (su 422 correcto es de
dominio). Verde: backend 442, e2e de perfil 203; los mutantes de cada hallazgo mueren.

*Corrección (ronda 2, R2-6):* de los dos medios de la ronda 1 se validó uno (A); B bajó a bajo. Los mutantes mueren
todos salvo `places` sin requerir, inalcanzable en pantalla.

## Revisión ronda 2 y cierre
Dos finders sobre el diff de la ronda 1: las correcciones de pruebas cerradas y deterministas (C-17 con el clic sostenido
30/30, 10/10 contra la guarda revertida; 16/16 mutantes de la tabla de obligatorias mueren, el `expectNoPut` es el único
que atrapa un cliente que manda el `PUT` igual). Seis hallazgos bajos, todos de documentos (Krosnick p. 384 fue
telefónica; el disparador de "Re-check if" no ve a quien marca todo; `[INFERENCE]` no es etiqueta de la casa;
`CIGNOW_A` sin su universo; inventario de pruebas citado sin actualizar; estos números del journal). Por la regla de
cierre aprobada por Saúl Pérez, deuda registrada (`memory/closed/2026-10-22-ronda-2-de-perfil-habitos-completitud.md`) y
archivo. El cuerpo del PR se puso al día (442 backend, 203 e2e de perfil).

**Convergencia:** ronda 1 medio → ronda 2 bajo (documentos). Lección: la regla de cierre decidida antes de la primera
ronda ahorró una tercera.
