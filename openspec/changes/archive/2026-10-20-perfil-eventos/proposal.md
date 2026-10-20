# Proposal

Origin: product/prd.md § E2 — US-18 (cubre FR-028, **Story A de 3**) · dominio: product/dominio.md, rebanada
"perfil médico por secciones (llenado, FR-028)", **agreed para la Story A el 2026-10-20** (PR #18) · prototipo
validado: product/prototipos/perfil-secciones.html (v4, https://claude.ai/artifact/TRBywm3SEhDA5ey2duMV8n)
Triage: change — toca `code` (backend + frontend) y modifica la spec `records/patient-profile`; los criterios salen
del prototipo que Saúl Pérez navegó en 4 versiones ("procede con la story a", 2026-10-20). No hace falta brief ni
PRD nuevos: FR-028 ya existe y el discovery ya corrió (PR #18).

## Why

El PR #16 dejó en "Mi perfil médico" seis secciones del historial visibles pero vacías, con la promesa "se podrán
capturar próximamente". Son los antecedentes personales que todo médico pregunta (NOM-004 6.1.1). Hoy el paciente
no puede contestarlos, ni siquiera para decir que no ha tenido ninguno. Esta story llena las cuatro secciones de
**eventos pasados**, que comparten forma: enfermedades pasadas e infecciosas, cirugías y hospitalizaciones,
fracturas y lesiones, y transfusiones con el grupo sanguíneo. Crónicas (Story B) y hábitos (Story C) siguen
"Sin llenar".

## User story

Como paciente, quiero registrar mis enfermedades pasadas, cirugías, fracturas y transfusiones (o decir que no he
tenido ninguna), para que el médico no tenga que preguntármelo cada vez y sepa distinguir "no ha pasado" de "no
lo ha contado".

## Acceptance criteria (del prototipo v4; los Given/When/Then con datos concretos van en las specs)

- **A-1** Cada sección muestra su estado en su tarjeta: *Sin llenar*, *Ninguna* o "N registros".
- **A-2** "No he tenido ninguna" (en transfusiones: "Nunca me han transfundido") se marca solo en una sección sin
  registros y se puede deshacer; agregar un registro después la quita, con aviso.
- **A-3** "Cuándo" se contesta como lo pregunta el médico: la **edad** que tenía, la **etapa escolar** (antes de
  la primaria · primaria · secundaria · prepa), el **año** si lo sabe, o "No recuerdo". Se guarda lo dicho (tipo
  + valor) y el año aproximado se calcula al mostrarlo con la fecha de nacimiento del perfil; sin fecha de
  nacimiento se muestra solo la edad o la etapa. Se rechazan una edad mayor que la actual y un año antes del
  nacimiento o futuro.
- **A-4** Enfermedad pasada: condición (lista frecuente: varicela, sarampión, paperas, rubéola, hepatitis A/B/C,
  COVID-19 grave, dengue, tuberculosis + "otra"; **requerida**), cuándo, ¿requirió hospitalización? (sí/no/no
  sé), secuelas, nota.
- **A-5** Cirugía u hospitalización: tipo (cirugía / hospitalización sin cirugía), nombre (**requerido**), cuándo,
  motivo, hospital o lugar, médico que operó o atendió, complicaciones, ¿reacción a la anestesia? (sí/no/no sé,
  con detalle si sí), material implantado.
- **A-6** Fractura o lesión: qué hueso o lesión (**requerido**), lado (izquierdo/derecho/ambos/no aplica),
  cuándo, ¿requirió cirugía? (sí/no/no sé), material implantado, secuelas.
- **A-7** Transfusión: cuándo, motivo, qué se transfundió (sangre/plaquetas/plasma/no sé), hospital, ¿hubo
  reacción? (con detalle). **Grupo sanguíneo** como un solo dato del paciente: A/B/AB/O con Rh ±, o "No lo sé".
- **A-8** Solo el paciente agrega, corrige o elimina lo suyo; eliminar pide confirmación en la misma pantalla; un
  registro sin ningún dato no se guarda.
- **A-9** Todo se guarda cifrado en reposo, aislado por cuenta y detrás del consentimiento, como el resto del
  perfil (criterio técnico).

<!-- MISSING: ¿el grupo sanguíneo vive en el perfil básico (1→1) o en la sección de transfusiones? El dominio dice "un solo dato del paciente"; el prototipo lo pinta dentro de la sección. Decide /epe-1-explore con el modelo actual. -->
<!-- MISSING: ¿"ninguna" en una sección se muestra al médico/IA igual que en la historia clínica ("negados")? Solo aplica al compartir (E3/E4); confirmar que aquí basta con guardarlo. -->

## What Changes

- Las cuatro secciones de eventos dejan de ser solo visibles y se pueden **llenar**: lista de registros por
  sección con agregar, editar y eliminar, y el estado "ninguna".
- Nuevo dato **grupo sanguíneo**.
- La tarjeta de cada sección en "Mi perfil médico" muestra su estado (A-1) y abre su pantalla. Crónicas y hábitos
  siguen visibles y sin captura.
- Todo el dato es sensible (LFPDPPP art. 3-VI; médico y hospital son datos de terceros aportados por el titular):
  cifrado en reposo y detrás del consentimiento.

## Capabilities

### New Capabilities

(ninguna)

### Modified Capabilities

- `records/patient-profile`: la lista de secciones (hoy "visibles pero aún sin captura", spec:86-88) pasa a tener
  cuatro secciones llenables con estado y el grupo sanguíneo; crónicas y hábitos conservan el comportamiento
  actual.

## Impact

- **Backend**: modelo(s) nuevos para los registros de sección y su estado "ninguna", cifrados con la
  infraestructura existente (EncryptedString, D13/D16); rutas bajo `/api/v1/` con el patrón {data,count} y
  errores es-MX; migración Alembic solo aditiva.
- **Frontend**: pantalla por sección y formulario por tipo, calcados del prototipo; el widget "cuándo"
  (edad/etapa/año) reutilizable por las stories B y C; textos en i18next es-MX; Playwright como contrato
  (proyectos chromium y s26-ultra).
- **No toca**: crónicas y hábitos (Stories B y C), onboarding, AHF, mediciones, expediente de registros,
  compartir (E3/E4), IA (E5).
