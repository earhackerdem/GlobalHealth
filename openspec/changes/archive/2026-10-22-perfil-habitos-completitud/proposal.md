# Proposal

Origin: feedback de Saúl Pérez (author) al validar perfil-habitos-ajustes (PR #32, 2026-10-22), sobre product/prd.md
§ E2 — US-18 (FR-028) · dominio: product/dominio.md § Hábitos · investigación: `memory/research/habitos.md#no-recuerdo`
· prototipo: `prototipo.html` en esta carpeta (se entrega con el plan)
Triage: change — toca `code` (backend y frontend) y modifica la spec `records/patient-profile` ("cada respuesta es
opcional"). Sin migración: el cuestionario es un JSON cifrado (`patient_profile.habits`).

## Why

Al validar, Saúl Pérez notó que con "Lo dejé" puede guardar la edad en que dejó de tomar sin la edad en que empezó, y
que con alcohol "Actual" no se le piden las preguntas de frecuencia ni la de fines de semana. Lo mismo pasa en los
demás rangos. Para el médico, un rango a medias o un consumo actual sin frecuencia vale poco. Saúl Pérez decidió
(2026-10-22): cuando una respuesta abre más preguntas, esas preguntas son obligatorias, con "No recuerdo" para no
obligar a inventar un dato.

También notó que "Escribe solo el número." se queda junto a un campo aunque ya lo haya corregido: el error solo se
revisa al salir del campo.

## User story

Como paciente, quiero que la app me pida completar lo que mi respuesta implica, y poder decir "No recuerdo" cuando no
sé un dato del pasado, para que mi médico reciba mis hábitos completos y sin datos inventados.

## Acceptance criteria (los Given/When/Then con datos concretos van en la spec delta)

- **C-15 Lo que abre una respuesta es obligatorio:** con alcohol "Lo dejé" o "Actual", tabaco, vapeador o leña
  "Antes" o "Actual", y humo ajeno con algún lugar, cada pregunta que aparece se contesta antes de guardar. Sin
  contestar, "Guardar" no guarda y marca junto a la pregunta "Contesta esta pregunta." (o "Contesta esta pregunta o
  marca «No recuerdo»." donde aplica). Cada hábito sigue siendo opcional: se puede no elegir nada en un bloque.
- **C-16 "No recuerdo" en lo que pasó:** las edades de inicio y de fin, y los cigarros al día y las horas de leña de
  "Antes", tienen "No recuerdo". Las preguntas de frecuencia del alcohol, "Sobre todo fines de semana", y lo que
  describe el presente (cigarros y horas de "Actual", frecuencia y días del vapeador, días de humo ajeno) no lo tienen.
  "No recuerdo" se guarda como tal y se ve al reabrir; no se compara con otras edades.
- **C-17 El error se va al corregirlo:** un error ya marcado en un número se quita en cuanto el valor es válido, sin
  esperar a salir del campo.
- Lo guardado antes con preguntas sin contestar se sigue leyendo; al tocar "Guardar", la pantalla marca lo que falta.
- Siguen vigentes C-1…C-4, C-6 y C-10…C-14, y el cifrado, el aislamiento y el consentimiento.

## What Changes

- El backend rechaza (422 por `loc`) una pregunta aplicable sin contestar, y acepta `"unknown"` solo en las preguntas
  con "No recuerdo".
- Las edades de inicio y fin, y los cigarros y las horas de "Antes", aceptan `"unknown"` además del número.
- La pantalla agrega "No recuerdo" junto a esas preguntas, marca lo que falta al tocar "Guardar", quita un error en
  cuanto se corrige, y cambia la introducción "Contesta solo lo que quieras".

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
- `records/patient-profile`: "Hábitos: sustancias y humo" deja de tener cada respuesta opcional; "Los errores se marcan
  al momento" agrega que el error se quita al corregir.

## Impact

- **Backend:** `backend/app/models.py` (tipos con `"unknown"`, reglas de obligatoriedad en `habits_errors`), sin
  migración ni cambio de ruta.
- **Frontend:** `HabitsForm.tsx`, textos es-MX, cliente regenerado (`types.gen.ts`, `zod.gen.ts`).
- **Fuera:** "Prefiero no responder" (`asked-declined`); una vista para el médico; la "mejor estimación" por rangos
  tras "No recuerdo"; la Story C2.
