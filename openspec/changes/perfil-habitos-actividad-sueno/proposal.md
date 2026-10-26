# Proposal

Origin: product/prd.md § E2 — US-18 (FR-028) · dominio: product/dominio.md § Hábitos (filas ejercicio, movimiento del
día, sueño) y § Rebanada (Story C: C2 — cuerpo, descanso y trabajo) · prototipo de producto:
`product/prototipos/perfil-secciones.html` (C-5, C-7, C-8) · investigación: `memory/research/habitos.md#habitos`,
`memory/research/ocupacion.md#ocupacion` y la sección nueva de actividad y sueño · prototipo del cambio:
`prototipo.html` en esta carpeta (se entrega con el plan)
Triage: change — toca `code` (backend y frontend) y agrega un requisito a la spec `records/patient-profile`. Saúl Pérez
partió la C2 en dos cambios el 2026-10-26: este (C2a: ejercicio, movimiento del día y sueño, en Hábitos) y después
C2b ("Trabajo" en el Perfil básico, C-9). Sin migración: el cuestionario es el mismo JSON cifrado
(`patient_profile.habits`), que la C1 cerró para que la C2 lo extienda a propósito (`backend/app/models.py:843`).

## Why

La C1 y sus ajustes cubrieron sustancias y humo. Al médico le falta el resto de lo que pregunta en los antecedentes
no patológicos: cuánto ejercicio hace el paciente y de qué tipo, cuánto se mueve o está sentado en su día, y cómo
duerme. En la ronda 6 del dominio Saúl Pérez pidió "varios ejercicios con su propia frecuencia", y en la ronda 7 el
movimiento del día (aparte del ejercicio, porque la actividad del trabajo no da los beneficios de la del tiempo libre)
y el sueño.

## User story

Como paciente, quiero contar mi ejercicio, cómo se mueve mi día y cómo duermo, con el detalle que el médico pregunta,
para que no quede en un "sí hago ejercicio" o "duermo bien".

## Acceptance criteria (los Given/When/Then con datos concretos van en la spec delta)

- **C-5 Ejercicio como lista de actividades:** cada actividad con su tipo, días por semana y minutos por vez; la
  pantalla muestra el total de minutos por semana, sin compararlo con ninguna recomendación.
- **C-7 Movimiento del día, aparte del ejercicio:** cómo pasa el día en su trabajo o actividad principal, si camina o va
  en bici para ir a algún lado (con los días por semana) y las horas sentado al día; no se suma al ejercicio.
- **C-8 Sueño:** horas por noche y si le cuesta dormir o se despierta en la noche, con su frecuencia.
- Lo que una respuesta abre se contesta antes de guardar (C-15), sin "No recuerdo" (todo describe el presente, C-16);
  los errores se marcan al salir del campo y se van al corregir (C-14, C-17).
- La app no califica nada de esto (C-6, NFR-008).
- Siguen vigentes C-1…C-4, C-6, C-10…C-17, el guardado con "Guardar" y el aviso de cambios sin guardar, el cifrado, el
  aislamiento y el consentimiento.

## What Changes

- El cuestionario de hábitos suma tres bloques: ejercicio (lista), movimiento del día y sueño, con sus límites,
  obligatoriedad y normalización en el servidor.
- La pantalla de hábitos suma esos bloques después del humo de leña, con el total semanal del ejercicio.

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
- `records/patient-profile`: requisito nuevo "Hábitos: ejercicio, movimiento del día y sueño"; "La app no interpreta
  los hábitos" aclara que el total semanal es una suma a la vista, no un veredicto.

## Impact

- **Backend:** `backend/app/models.py` (bloques nuevos del esquema cerrado, normalización, obligatoriedad), sin
  migración ni cambio de ruta.
- **Frontend:** `HabitsForm.tsx`, textos es-MX, cliente regenerado (`types.gen.ts`, `zod.gen.ts`).
- **Fuera:** "Trabajo" en el Perfil básico (C2b, siguiente cambio); cualquier veredicto contra la OMS; datos de
  wearables; la vista del médico.
