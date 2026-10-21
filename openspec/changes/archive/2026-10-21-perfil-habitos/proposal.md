# Proposal

Origin: product/prd.md § E2 — US-18 (cubre FR-028, **Story C1 de C**: la Story C se partió en dos por decisión de
Saúl Pérez, 2026-10-20) · dominio: product/dominio.md § Hábitos (APNP + tabaquismo) · prototipo:
product/prototipos/perfil-secciones.html (v4, criterios C-1…C-4 y C-6)
Triage: change — toca `code` (backend + frontend, con una migración) y modifica la spec `records/patient-profile`.
Reutiliza el patrón de dato 1:1 cifrado del perfil (`blood_type`, Story A) y los chips (D18).

## Why

"Hábitos" es la única tarjeta de "Mi perfil médico" que sigue sin captura. Lo que el médico pregunta siempre
(alcohol, tabaco, humo) es justo lo que los campos estructurados de los expedientes capturan mal: frecuencia,
cantidad, si ya lo dejó y la exposición al humo de otros (`memory/research/habitos.md`, `humo-lena.md`).

## User story

Como paciente, quiero contar cuánto tomo, si fumo o fumé, y a qué humo me expongo, para que mi médico lo sepa sin
preguntármelo en cada consulta.

## Acceptance criteria (del prototipo v4 y del dominio; los Given/When/Then con datos concretos van en las specs)

- **C-1 Alcohol:** nunca / lo dejé (a qué edad) / actual. Si es actual, las 3 preguntas del AUDIT-C con su escala
  (frecuencia, bebidas en un día típico, 6 o más en una ocasión) y "sobre todo fines de semana".
- **C-2 Tabaco y vapeador:** tabaco nunca / antes / actual, cigarros al día, a qué edad empezó y, si lo dejó, a qué
  edad. Vapeador nunca / antes / actual.
- **C-3 Humo de tabaco ajeno:** dónde (casa · trabajo o escuela · otro lugar, varios) y cuántos días por semana, o
  "No me expongo".
- **C-4 Humo de leña:** nunca / antes / actual y años aproximados.
- **C-6 Sin interpretación:** la app no calcula puntajes (AUDIT-C), riesgos ni veredictos con estas respuestas
  (NFR-008).
- Todo es opcional: se guarda lo que haya contestado. La tarjeta pasa de "Sin llenar" a "Con datos" y abre su
  pantalla.
- Lo que no aplica se descarta al guardar, y las edades imposibles se rechazan junto a su campo (respuestas del
  gate, exploration.md §8).
- Cifrado en reposo, solo del paciente, tras el consentimiento (NFR-001, D13).

## What Changes

- Un dato nuevo, **hábitos**, 1:1 con el perfil y cifrado (columna `patient_profile.habits`), con `GET` y `PUT
  /profile/habits`.
- La tarjeta "Hábitos" abre `/perfil/habitos`: un cuestionario de cuatro bloques con un solo "Guardar".
- `ChipGroup` gana una variante de **selección múltiple** con opción excluyente ("No me expongo"), que la C2 reusará
  para las exposiciones del trabajo.

## Capabilities

### New Capabilities
Ninguna.

### Modified Capabilities
- `records/patient-profile`: se agregan los hábitos (sustancias y humo) y la regla sin interpretación; la tarjeta de
  hábitos deja de ser "sin captura"; el cifrado cubre los hábitos.

## Impact

- **Backend:** `backend/app/models.py`, `backend/app/api/routes/profile.py`, una migración Alembic (columna nueva,
  nullable, sin datos que mover).
- **Frontend:** `perfil.tsx`, una ruta nueva `perfil_.habitos.tsx`, `HabitsForm.tsx`, `ChipGroup.tsx`, `history.ts`,
  los textos es-MX y el cliente regenerado.
- **Fuera:** ejercicio, movimiento del día, sueño y trabajo (Story C2); vacunación; otras sustancias; puntajes.
