## MODIFIED Requirements

### Requirement: Perfil básico del paciente
El sistema SHALL permitir al paciente con consentimiento vigente guardar y editar su perfil básico: fecha de
nacimiento (nunca futura según la fecha de hoy en Ciudad de México, America/Mexico_City), sexo (mujer / hombre / prefiero no decir) y alergias a medicamentos (texto libre).
Todos los campos SHALL ser opcionales (el perfil parcial o vacío es válido) y SHALL almacenarse cifrados en
reposo. Donde el perfil se muestre, la edad SHALL derivarse de la fecha de nacimiento a la fecha actual.

#### Scenario: Guardar el perfil básico y ver la edad
- **GIVEN** una paciente con consentimiento vigente y fecha actual 2026-10-19
- **WHEN** guarda fecha de nacimiento 1990-03-15, sexo "Mujer" y alergias "penicilina"
- **THEN** su perfil muestra esos datos y la edad "36 años", y los valores quedan cifrados en reposo

#### Scenario: Fecha de nacimiento futura rechazada
- **WHEN** el paciente intenta guardar como fecha de nacimiento la de pasado mañana
- **THEN** el sistema la rechaza con un mensaje en es-MX y el perfil no cambia

#### Scenario: «Hoy» es el de Ciudad de México
- **GIVEN** son las 20:00 del 2026-03-10 en Ciudad de México (02:00 del 2026-03-11 en UTC)
- **WHEN** el paciente guarda fecha de nacimiento 2026-03-11
- **THEN** el sistema la rechaza con «La fecha de nacimiento no puede estar en el futuro»; y si guarda
  2026-03-10, la acepta

#### Scenario: La pantalla usa el mismo «hoy», no el del aparato
- **GIVEN** el aparato está en la zona de Tokio y son las 20:00 del 2026-03-10 en Ciudad de México (ya 2026-03-11
  en Tokio)
- **WHEN** el paciente escribe como fecha de nacimiento 2026-03-11
- **THEN** la pantalla le dice «La fecha de nacimiento no puede ser futura» sin enviar nada; con 2026-03-10 no hay
  mensaje

#### Scenario: Perfil vacío es válido
- **WHEN** el paciente guarda el perfil sin llenar ningún campo
- **THEN** el sistema lo acepta y el perfil se muestra como vacío y editable

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
dato SHALL rechazarse. Un texto sin nada visible (solo espacios, controles, caracteres de formato como U+200B, marcas que Unicode
declara ignorables como U+034F, U+FE0F o el relleno U+3164, y el braille en blanco U+2800) SHALL contar como vacío,
en la pantalla y en la API, también en la caja de «cuándo». Eliminar SHALL pedir confirmación en la misma pantalla.

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

#### Scenario: «¿Cuál fue?» con un texto invisible
- **WHEN** el paciente elige «Otra» en una enfermedad pasada y en «¿Cuál fue?» solo hay un espacio de ancho cero
  (U+200B)
- **THEN** la pantalla le pide «Elige la condición o escribe cuál fue» junto a esa caja y no se guarda nada; y si
  la petición llega igual a la API, responde 422 con ese mensaje y no crea el registro

#### Scenario: Un «cuándo» invisible no es un dato
- **WHEN** el paciente intenta guardar una transfusión cuyo único contenido es un U+200B en «Edad que tenías»
- **THEN** la pantalla le dice «Llena al menos un dato» y no se guarda nada

#### Scenario: Un texto visible con un carácter invisible dentro sí cuenta
- **WHEN** el paciente elige «Otra» y escribe «Zika» seguido de un U+200B
- **THEN** el registro se guarda
