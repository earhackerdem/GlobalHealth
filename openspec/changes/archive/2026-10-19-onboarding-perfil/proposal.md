# Proposal

Origin: product/prd.md § E2 — US-17 (cubre FR-027 + FR-008) · dominio: product/dominio.md, rebanada "perfil del
paciente y antecedentes familiares (onboarding)", **agreed 2026-10-19** · prototipo validado:
product/prototipos/onboarding-perfil.html
Triage: change — toca `code` (backend + frontend) y los criterios salen del prototipo validado por Saúl Pérez
(2026-10-19); el discovery ya corrió (PR #15)

## Why

Hoy un paciente nuevo acepta el consentimiento y aterriza en un expediente vacío: la app no sabe su edad, peso,
estatura ni los antecedentes que todo médico pregunta primero (¿diabetes o cáncer en la familia? ¿alergias?). Ese
contexto mínimo es exactamente lo que la NOM-004 (6.1.1/6.1.2) obliga al médico a interrogar, y es insumo directo
de los avisos proactivos (FR-021: "AHF de diabetes sin tamizaje registrado"). El momento natural de pedirlo es una
sola vez, justo tras el consentimiento — sin bloquear nada (todo omitible, decisión de Saúl Pérez 2026-10-19).

## What Changes

- Nuevo **onboarding de perfil** post-aceptación del consentimiento, ofrecido una sola vez y omitible por paso y
  global ("Ahora no" → expediente).
- Nuevo **perfil del paciente**: fecha de nacimiento (edad derivada), sexo (con "prefiero no decir"), alergias a
  medicamentos, y **peso/estatura como mediciones con fecha** (el perfil muestra la última).
- Nuevos **antecedentes familiares (AHF)**: condición (lista frecuente + "otra") + parentescos con **línea
  materna/paterna** + detalle opcional (p. ej. edad al diagnóstico). Cubre FR-008.
- Nueva pantalla **"Mi perfil médico"**: muestra y edita lo anterior y lista las demás secciones de la anamnesis
  (crónicas, enfermedades pasadas, cirugías, fracturas, transfusiones, hábitos) **visibles pero vacías** — su
  llenado es la story siguiente (FR-028/US-18), aquí solo se sugieren sin estorbar.
- Todo el dato es sensible (LFPDPPP art. 3-VI; los AHF son datos de salud de terceros aportados por el titular):
  cifrado en reposo como el resto del contenido clínico, detrás del consentimiento.

## Capabilities

### New Capabilities

- `records/patient-profile`: el perfil médico del paciente — datos básicos (nacimiento, sexo, alergias),
  mediciones con fecha (peso, estatura), antecedentes familiares con línea, el onboarding post-consentimiento que
  lo captura una sola vez, y la pantalla de secciones con llenado progresivo.

### Modified Capabilities

(ninguna — `records/clinical-records` y `privacy/consent` no cambian de comportamiento; el onboarding se dispara
DESPUÉS de aceptar el consentimiento, que sigue igual)

## Impact

- **Backend**: modelos nuevos (perfil, medición, antecedente familiar) cifrados en reposo con la infraestructura
  existente (EncryptedString, D13/D16); rutas nuevas bajo `/api/v1/` con el patrón wrapper {data,count} y es-MX en
  errores; migración Alembic solo aditiva (sin tocar datos existentes).
- **Frontend**: pantalla de onboarding (wizard 3 pasos, calcada del prototipo), pantalla "Mi perfil médico",
  textos en recursos i18next es-MX; suite Playwright como contrato (proyectos chromium y s26-ultra).
- **No toca**: consentimiento (solo lee su estado/momento de aceptación), expediente de registros, compartir
  (E3/E4), IA (E5). Cuestionarios por especialidad: fuera (diferidos a E4/FR-022).
