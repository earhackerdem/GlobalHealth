# Spec Delta

## MODIFIED Requirements

### Requirement: Pantalla "Mi perfil médico" con secciones visibles
La pantalla "Mi perfil médico" SHALL mostrar el perfil básico, las mediciones y los antecedentes familiares con
su estado, y SHALL listar las demás secciones de la anamnesis: enfermedades crónicas; enfermedades pasadas e
infecciosas; cirugías y hospitalizaciones; fracturas y lesiones; transfusiones y grupo sanguíneo; hábitos. Las
cuatro secciones de eventos (enfermedades pasadas, cirugías, fracturas, transfusiones) SHALL mostrar en su tarjeta
su estado (*Sin llenar*, *Ninguna* o el número de registros) y SHALL abrir su propia pantalla de captura.
Enfermedades crónicas y hábitos SHALL seguir visibles y sin captura hasta sus stories de FR-028.

#### Scenario: Estado de cada sección en su tarjeta (A-1)
- **GIVEN** un paciente con dos enfermedades pasadas registradas, "Nunca me han transfundido" marcado y nada en
  cirugías ni fracturas
- **WHEN** abre "Mi perfil médico"
- **THEN** la tarjeta de enfermedades pasadas dice "2 registros", la de transfusiones "Ninguna", las de cirugías
  y fracturas "Sin llenar", y las de crónicas y hábitos "Sin llenar" sin formulario de captura

#### Scenario: La tarjeta abre la pantalla de su sección
- **WHEN** el paciente toca la tarjeta "Cirugías y hospitalizaciones"
- **THEN** llega a la pantalla de esa sección, con su lista de registros y la acción "Agregar"

## ADDED Requirements

### Requirement: Registros de las secciones de eventos
El sistema SHALL permitir al paciente con consentimiento vigente agregar, editar y eliminar registros en las
secciones de enfermedades pasadas, cirugías y hospitalizaciones, fracturas y lesiones, y transfusiones, con los
campos de cada una: enfermedad pasada (condición de un catálogo de diez — varicela, sarampión, paperas, rubéola,
hepatitis A, hepatitis B, hepatitis C, COVID-19 grave, dengue, tuberculosis — u "otra" con texto; cuándo;
¿requirió hospitalización?; secuelas; nota); cirugía u hospitalización (tipo; nombre; cuándo; motivo; hospital o
lugar; médico; complicaciones; ¿reacción a la anestesia? con detalle; material implantado); fractura o lesión
(qué hueso o lesión; lado; cuándo; ¿requirió cirugía?; material implantado; secuelas); transfusión (cuándo;
motivo; qué se transfundió; hospital o lugar; ¿hubo reacción? con detalle). Las preguntas sí/no SHALL admitir
"No sé". Son requeridos solo la condición, el nombre de la cirugía y el hueso o lesión; un registro sin ningún
dato SHALL rechazarse. Eliminar SHALL pedir confirmación en la misma pantalla.

#### Scenario: Enfermedad pasada del catálogo (A-4)
- **WHEN** el paciente registra la condición "Varicela", cuándo "En la primaria" y hospitalización "No"
- **THEN** la sección de enfermedades pasadas muestra "Varicela" con "en la primaria" en su resumen

#### Scenario: Enfermedad pasada fuera del catálogo (A-4)
- **WHEN** el paciente elige "Otra" y escribe "Chikungunya"
- **THEN** el registro se guarda y se muestra como "Chikungunya"

#### Scenario: Cirugía con todos sus datos (A-5)
- **WHEN** el paciente registra tipo "Cirugía", nombre "Apendicectomía", a los 24 años, motivo "Apendicitis",
  hospital "Hospital General de Zona", médico "Dra. Ruiz", reacción a la anestesia "Sí" con detalle "Náusea
  fuerte" y material implantado vacío
- **THEN** el registro se guarda con esos valores y al editarlo los muestra tal cual

#### Scenario: Fractura con lado e implante (A-6)
- **WHEN** el paciente registra "Radio", lado "Izquierdo", a los 10 años, ¿requirió cirugía? "Sí" y material
  implantado "Placa y tornillos"
- **THEN** la sección de fracturas muestra "Radio" con "izquierdo" y el implante en su resumen

#### Scenario: Transfusión (A-7)
- **WHEN** el paciente registra una transfusión en 2015, motivo "Parto", qué se transfundió "Sangre" y reacción
  "No"
- **THEN** la sección de transfusiones muestra la transfusión con "en 2015" y "Parto"

#### Scenario: Falta el dato requerido
- **WHEN** el paciente intenta guardar una cirugía sin nombre
- **THEN** el sistema la rechaza con un mensaje en es-MX y no crea el registro

#### Scenario: Registro vacío no se guarda (A-8)
- **WHEN** el paciente intenta guardar una transfusión sin ningún dato
- **THEN** el sistema la rechaza con el mensaje "Llena al menos un dato" y no crea el registro

#### Scenario: Editar y eliminar con confirmación (A-8)
- **GIVEN** una fractura "Radio" registrada
- **WHEN** el paciente cambia el lado a "Derecho" y guarda, y luego elige "Eliminar" y confirma en la misma
  pantalla
- **THEN** primero se muestra "derecho" y después el registro desaparece de la sección y del almacenamiento; si
  en lugar de confirmar elige "Cancelar", el registro sigue ahí

### Requirement: "Cuándo" como lo pregunta el médico
El "cuándo" de un registro SHALL contestarse con la edad que tenía el paciente, una etapa escolar (antes de la
primaria, primaria, secundaria, prepa), un año o "No recuerdo", y SHALL guardarse tal como se contestó. Donde se
muestre, el sistema SHALL añadir el año aproximado calculado con la fecha de nacimiento del perfil (edad: año de
nacimiento + edad; etapa: rango con primaria 6–11, secundaria 12–14, prepa 15–17 y antes de la primaria 0–5
años); sin fecha de nacimiento SHALL mostrar solo la edad o la etapa. El sistema SHALL rechazar una edad mayor que
la edad actual del paciente, un año futuro y, si conoce la fecha de nacimiento, un año anterior a ella.

#### Scenario: Edad con fecha de nacimiento (A-3)
- **GIVEN** un paciente nacido el 1990-03-15
- **WHEN** registra una cirugía "a los 7 años"
- **THEN** el registro guarda la edad 7 y se muestra "a los 7 años (≈1997)"

#### Scenario: Etapa escolar (A-3)
- **GIVEN** un paciente nacido el 1990-03-15
- **WHEN** registra la varicela "En la primaria"
- **THEN** se muestra "en la primaria (≈1996–2001)"

#### Scenario: Sin fecha de nacimiento (A-3)
- **GIVEN** un paciente que omitió su fecha de nacimiento
- **WHEN** registra una fractura "a los 10 años"
- **THEN** se muestra "a los 10 años" sin año aproximado

#### Scenario: El año se recalcula al corregir la fecha de nacimiento (A-3)
- **GIVEN** un paciente nacido el 1990-03-15 con una cirugía "a los 7 años"
- **WHEN** corrige su fecha de nacimiento a 1992-01-01
- **THEN** la cirugía se muestra "a los 7 años (≈1999)"

#### Scenario: Edad o año imposibles (A-3)
- **GIVEN** un paciente nacido el 1990-03-15 y fecha actual 2026-10-20
- **WHEN** intenta registrar "a los 40 años", el año 1985 o el año 2030
- **THEN** el sistema rechaza cada uno con un mensaje en es-MX y no crea el registro

### Requirement: Estado "ninguna" por sección
El paciente SHALL poder declarar que no ha tenido nada de una sección de eventos ("No he tenido ninguna"; en
transfusiones "Nunca me han transfundido") solo cuando la sección no tiene registros, y SHALL poder deshacerlo.
Agregar un registro a una sección marcada como "ninguna" SHALL quitar esa marca.

#### Scenario: Marcar "ninguna" (A-2)
- **GIVEN** un paciente sin cirugías registradas
- **WHEN** elige "No he tenido ninguna" en cirugías
- **THEN** la sección y su tarjeta dicen "Ninguna"

#### Scenario: No se marca con registros (A-2)
- **GIVEN** un paciente con una fractura registrada
- **WHEN** intenta marcar fracturas como "ninguna"
- **THEN** el sistema lo rechaza con un mensaje en es-MX y la sección sigue con su registro

#### Scenario: Agregar quita la marca (A-2)
- **GIVEN** transfusiones marcada como "Nunca me han transfundido"
- **WHEN** el paciente registra una transfusión
- **THEN** la sección deja de estar en "ninguna", su tarjeta dice "1 registro" y la app lo avisa

#### Scenario: Deshacer (A-2)
- **GIVEN** cirugías marcada como "ninguna"
- **WHEN** el paciente elige "Deshacer"
- **THEN** la sección vuelve a "Sin llenar"

### Requirement: Grupo sanguíneo
El perfil SHALL guardar el grupo sanguíneo como un solo dato del paciente: A+, A−, B+, B−, AB+, AB−, O+, O− o
"No lo sé". Se SHALL poder corregir y borrar, y SHALL almacenarse cifrado en reposo.

#### Scenario: Elegir y corregir el grupo sanguíneo (A-7)
- **WHEN** el paciente elige "O+" en la sección de transfusiones y después lo cambia a "No lo sé"
- **THEN** el perfil guarda "No lo sé" y la sección lo muestra seleccionado

#### Scenario: Grupo sanguíneo fuera del catálogo
- **WHEN** se intenta guardar el grupo "C+"
- **THEN** el sistema lo rechaza y el grupo guardado no cambia

### Requirement: Los registros del historial son solo del paciente y van cifrados
El sistema SHALL devolver a cada paciente únicamente sus propios registros del historial, SHALL responder de
forma indistinguible ante un registro inexistente y uno ajeno, y SHALL almacenar cifrados en reposo el contenido
de cada registro (incluida su sección), la marca "ninguna" y el grupo sanguíneo.

#### Scenario: Registro ajeno indistinguible de inexistente (A-8)
- **GIVEN** dos pacientes A y B, B con una cirugía registrada
- **WHEN** A intenta editar y eliminar por identificador la cirugía de B y un registro que no existe
- **THEN** ambas respuestas son indistinguibles entre sí (mismo status y mismo cuerpo) y la cirugía de B no
  cambia

#### Scenario: Cifrado en reposo (A-9)
- **GIVEN** un paciente con una cirugía "Apendicectomía", fracturas marcada como "ninguna" y grupo "O+"
- **WHEN** se lee el almacenamiento directamente, sin pasar por la app
- **THEN** ni "Apendicectomía", ni el nombre de la sección, ni la marca "ninguna", ni "O+" aparecen en claro
