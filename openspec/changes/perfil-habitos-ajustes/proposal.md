# Proposal

Origin: feedback de Saúl Pérez (author) al validar la Story C1 (PR #30, 2026-10-21), sobre product/prd.md § E2 —
US-18 (FR-028) · dominio: product/dominio.md § Hábitos · investigación: `memory/research/habitos.md#vapeo-inicio`,
`memory/research/humo-lena.md` (horas-año) · prototipo: `prototipo.html` en esta carpeta (se entrega con el plan)
Triage: change — toca `code` (backend, frontend y la generación del cliente) y modifica la spec
`records/patient-profile`. Sin migración: el cuestionario es un JSON cifrado (`patient_profile.habits`).

## Why

Saúl Pérez validó la Story C1 y encontró tres preguntas que no capturan lo que el médico necesita:
- **Alcohol:** "Lo dejé" pide la edad en que dejó de tomar, pero no desde cuándo tomaba. Tabaco sí pregunta las dos.
- **Vapeador:** solo dice Nunca/Antes/Actual, sin cuánto se usa. No hay una medida validada en vapeadores o pods; lo
  que miden los estudios es "todos los días / algunos días" y los días de los últimos 30.
- **Humo de leña:** "años aproximados" no basta. El estudio mexicano de referencia mide la exposición en horas-año (años
  × horas al día); por encima de 200 horas-año el riesgo de bronquitis con obstrucción sale 75 veces mayor.

Y dos problemas de uso: la pantalla valida solo al tocar "Guardar", con reglas copiadas a mano del backend (deuda R19);
y si la persona sale de la pantalla, cambia de cuenta en otra pestaña o se le cierra el navegador, pierde lo que
contestó (deuda "sin aviso de cambios sin guardar").

## User story

Como paciente, quiero contar desde cuándo y cuánto tomo, vapeo o me expongo al humo de leña, y que lo que contesto se
guarde solo, para que mi médico tenga mi historia completa sin que yo pierda lo que ya escribí.

## Acceptance criteria (los Given/When/Then con datos concretos van en la spec delta)

- **C-10 Alcohol, desde cuándo:** con "Lo dejé" o "Actual", "¿A qué edad empezaste a tomar? (sin contar probaditas)".
  No puede ser mayor que la edad en que lo dejó ni que la edad actual.
- **C-11 Vapeador como el tabaco:** Nunca / Antes / Actual. Con "Antes" o "Actual", a qué edad empezó; con "Antes", a
  qué edad lo dejó. Con "Actual", "Todos los días" o "Algunos días", y con "Algunos días", "¿Cuántos días de los
  últimos 30?" (1 a 30).
- **C-12 Humo de leña como rango:** con "Antes" o "Actual", a qué edad empezó y cuántas horas al día en promedio (1 a
  24); con "Antes", a qué edad terminó. Reemplaza los "años aproximados". La app NO calcula horas-año (C-6).
- **C-13 Se guarda solo:** cada respuesta válida se guarda sin botón; la pantalla dice si está guardando, si ya guardó
  o qué falta corregir. Salir de la pantalla no pierde lo ya guardado.
- **C-14 Errores al momento:** un número fuera de su escala, una edad imposible o una edad de inicio mayor que la de
  fin se marcan junto a su campo al salir de él, sin esperar al servidor. Los límites de cada número vienen del
  contrato del backend, no de una copia.
- Lo que ya se guardó en la forma anterior se sigue leyendo: el vapeador como Nunca/Antes/Actual, y la leña sin los
  años (no se pueden convertir a edades).
- Siguen vigentes C-1…C-4 y C-6 de la C1, y el cifrado, el aislamiento y el consentimiento.

## What Changes

- Los hábitos ganan campos: `alcohol.start_age`; `vaping` pasa de texto a objeto (`status`, `frequency`,
  `days_last_30`, `start_age`, `quit_age`); `wood_smoke` cambia `years` por `start_age`, `quit_age` y
  `hours_per_day`. El mismo `GET/PUT /profile/habits`.
- La pantalla de hábitos guarda sola (sin "Guardar"/"Cancelar") y valida al salir de cada campo.
- El cliente generado gana esquemas Zod del OpenAPI (`@hey-api/openapi-ts`, plugin `zod`), y el formulario toma de ahí
  los límites.

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
- `records/patient-profile`: "Hábitos: sustancias y humo" cambia alcohol, vapeador y leña, y el guardado pasa a ser
  automático.

## Impact

- **Backend:** `backend/app/models.py` (esquemas, normalización, validación de edades), sin migración.
- **Frontend:** `HabitsForm.tsx`, los textos es-MX, `openapi-ts.config.ts` y el cliente regenerado (`zod.gen.ts`).
- **Fuera:** guardado automático en las demás secciones (crónicas y eventos son listas con diálogo; se evalúa aparte);
  ejercicio, movimiento, sueño y trabajo (Story C2); calcular horas-año o cualquier puntaje.
