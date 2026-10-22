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
