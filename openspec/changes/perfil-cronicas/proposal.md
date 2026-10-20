# Proposal

Origin: product/prd.md § E2 — US-18 (cubre FR-028, **Story B de 3**) · dominio: product/dominio.md § Enfermedad
crónica (Story B), rebanada "perfil médico por secciones (llenado, FR-028)" · prototipo:
product/prototipos/perfil-secciones.html (v4, criterios B-1…B-4)
Triage: change — toca `code` (backend + frontend) y modifica la spec `records/patient-profile`. Reutiliza la
infraestructura de la Story A (perfil-eventos, PR #20). El discovery ya corrió (PR #18) y la pregunta abierta que
bloqueaba esta story la respondió Saúl Pérez el 2026-10-20.

## Why

"Enfermedades crónicas" es la única sección de eventos y antecedentes que sigue "Sin llenar" en "Mi perfil
médico" (la de hábitos es la Story C). Es la que más pesa en consulta: el médico y, a futuro, la IA necesitan saber
qué condición tiene hoy el paciente aunque no traiga el papel del diagnóstico.

## User story

Como paciente, quiero registrar mis enfermedades crónicas, para que el médico y la IA conozcan mi condición actual
aunque no tenga el papel del diagnóstico.

## Acceptance criteria (del prototipo v4 y del dominio; los Given/When/Then con datos concretos van en las specs)

- **B-0** La sección se comporta como las de la Story A: su tarjeta muestra *Sin llenar*, *Ninguna* o
  "N registros"; "No tengo ninguna" se marca solo sin registros, se deshace, y agregar un registro la quita con
  aviso; eliminar pide confirmación en la misma pantalla; un registro vacío no se guarda.
- **B-1** Condición desde una lista frecuente (diabetes tipo 2, hipertensión, asma, hipotiroidismo, colesterol alto,
  EPOC, artritis, epilepsia) + **salud mental y adicciones** (depresión, ansiedad, trastorno bipolar, consumo de
  alcohol u otras sustancias) + "otra"; **requerida**.
- **B-1b** (Saúl Pérez, 2026-10-20: "Interruptor por crónica") Cada crónica lleva un interruptor **"Sensible"** que el
  paciente prende o apaga al registrarla o editarla. Viene prendido en las de salud mental y adicciones, apagado en
  las demás, y en "otra" lo decide el paciente. La lista muestra "sensible" en las que lo tienen; FR-014 usará la
  marca para ocultarlas al compartir. Sin catálogo propio de enfermedades.
- **B-2** Estado **Activa** o **Ya no la tengo**. "Desde cuándo" y, si ya no la tiene, "hasta cuándo" se contestan
  con la mecánica "cuándo" de la Story A (edad, etapa escolar, año o "No recuerdo"). Se rechazan "hasta" antes de
  "desde" y las mismas edades y años imposibles que en A-3.
- **B-3** Tratamiento actual como texto libre opcional, y una nota opcional.
- **B-4** Enlace opcional a un **diagnóstico** de su expediente (no a una receta) que la respalda; la lista muestra
  el respaldo. El diagnóstico no depende de la crónica.
- **B-5** (pregunta 2, respondida por Saúl Pérez el 2026-10-20: "Se queda y se avisa") Al borrar un diagnóstico que
  respalda una o más crónicas, la confirmación de borrado lo dice y nombra cuáles; al confirmar, las crónicas se
  conservan y solo pierden el respaldo.
- **B-6** Todo se guarda cifrado en reposo, aislado por cuenta y detrás del consentimiento, como la Story A
  (criterio técnico).

<!-- MISSING: ¿el enlace a un diagnóstico de otra cuenta, o a uno ya borrado, se rechaza al guardar o se ignora? Lo decide /epe-1-explore con el modelo actual (el contenido va cifrado, sin llave foránea posible). -->

## What Changes

- La tarjeta "Enfermedades crónicas" deja de ser solo visible: se abre y se llena con la misma pantalla por sección
  de la Story A.
- Formulario de crónica con estado, "desde" y "hasta", tratamiento, nota y el selector de diagnóstico del
  expediente.
- La confirmación de borrado de un diagnóstico en el expediente avisa si respalda crónicas.

## Capabilities

### New Capabilities

(ninguna)

### Modified Capabilities

- `records/patient-profile`: la sección de crónicas pasa de "visible sin captura" a llenable, con el
  comportamiento de las secciones de la Story A; hábitos conserva el comportamiento actual.
- `records/health-records` (si existe la spec del expediente): la confirmación de borrado de un diagnóstico gana el
  aviso de B-5. Lo confirma /epe-1-explore.

## Impact

- **Backend**: una sección nueva (`chronic`) sobre la tabla `medical_history_entry` de la Story A, con su esquema
  validado y cifrado; validación de "desde"/"hasta" y del diagnóstico enlazado.
- **Frontend**: formulario de crónica, chip "sensible", selector de diagnóstico, y el aviso en el diálogo de
  borrado del expediente; textos es-MX; Playwright (chromium y s26-ultra).
- **No toca**: hábitos y trabajo (Story C), las secciones de la Story A salvo lo común, compartir (E3/E4, FR-014
  solo recibe la marca), IA (E5).
