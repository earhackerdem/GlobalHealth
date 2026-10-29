# Proposal

Origin: pedido de Saúl Pérez del 2026-10-28, al usar la pantalla de hábitos después de mergear el PR #34 · investigación:
`memory/research/formularios-ux.md` · prototipo de decisión: `product/prototipos/ejercicio-variantes.html`, variante E,
elegida por Saúl Pérez («ok procede con la E») · decisión: D18 revisada el 2026-10-28
(`memory/decisions/D18-opciones-en-la-ui-chips-como.md`)
Triage: change — toca `code` (solo la pantalla de hábitos) y modifica un requisito de `records/patient-profile`. Es el
primer resultado del hilo 1 (formularios) de la investigación de UX completa
(`memory/inbox/2026-10-28-investigacion-ux-completa.md`). Los hilos 2 (identidad) y 3 (captura) van aparte.

## Why

Con los chips, cada actividad elegida agrega dos campos debajo del grupo, en el orden del catálogo. Con varias
actividades, la pantalla se llena de campos y no se ve a qué actividad pertenece cada uno. Si se eligen todas, son 18
campos seguidos. Saúl Pérez propuso pestañas. En el prototipo, las pestañas se salen de la pantalla a 400 px y esconden
los errores; él eligió entonces su otra propuesta: una lista con casillas siempre a la vista, en la que cada casilla
marcada muestra y exige sus campos justo debajo.

## User story

Como paciente, quiero ver todas las actividades como una lista y marcar las que hago, con sus días y minutos justo
debajo de cada una, para saber siempre qué estoy contestando y de qué actividad.

## Acceptance criteria (los Given/When/Then con datos concretos van en la spec delta)

- **E-1 Lista siempre a la vista:** nueve casillas en el orden del catálogo y, separada con «o», «No hago ejercicio»;
  ningún campo hasta marcar.
- **E-2 Marcar abre y desmarcar quita:** los campos de una actividad aparecen justo debajo de su casilla y se van al
  desmarcarla; lo desmarcado no cuenta en el total ni se guarda.
- **E-3 Excluyente:** «No hago ejercicio» desmarca las actividades, y marcar una actividad desmarca «No hago ejercicio».
- **E-4 Teclado, lector de pantalla y foco:** casilla con su nombre dentro del grupo «¿Qué ejercicio haces?»; Espacio
  marca sin mover el foco y Tab entra a sus campos; el error «Elige al menos una actividad…» lleva el foco a la primera
  casilla.
- Siguen vigentes C-5 (total, «Otra» con su nombre, falta un dato, «No hago ejercicio») y las reglas de guardado,
  errores (C-14, C-15, C-17), aviso de salida (C-13) y D20.

## What Changes

- El bloque Ejercicio de la pantalla de hábitos cambia los chips por una lista con casillas, con los campos de cada
  actividad debajo de su casilla.
- El resto de la pantalla, el esquema, el servidor y lo guardado no cambian.

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
- `records/patient-profile`: el requisito «Hábitos: ejercicio, movimiento del día y sueño» dice cómo se marcan las
  actividades y dónde aparecen sus preguntas; suma los escenarios E-1 a E-4.

## Impact

- **Frontend:** `HabitsForm.tsx` (bloque Ejercicio y el foco del error de grupo), posiblemente un componente de lista
  con casillas en `frontend/src/components/Profile/`, textos es-MX (`profile.json`).
- **Pruebas:** `frontend/tests/profile-habits.spec.ts`: las pruebas del ejercicio eligen con casillas en vez de chips.
- **Producto:** `product/prototipos/perfil-secciones.html` (pantalla de hábitos), `product/dominio.md` (ya actualizado
  con D18).
- **Fuera:** backend, esquema y datos guardados (sin migración); los demás chips de la app, incluido «¿Dónde?» del humo
  de tabaco ajeno (D18 revisada); los hilos 2 y 3 de la investigación.
