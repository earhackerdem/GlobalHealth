# Spec Delta

## ADDED Requirements

### Requirement: Registros de enfermedades crónicas
El sistema SHALL permitir al paciente con consentimiento vigente agregar, editar y eliminar registros en la sección
de enfermedades crónicas, con: condición (catálogo de once — diabetes tipo 2, hipertensión, asma, hipotiroidismo,
colesterol alto, EPOC, artritis, epilepsia, depresión, ansiedad, trastorno bipolar, consumo de alcohol u otras
sustancias — u "otra" con texto; **requerida**); marca **"Sensible"**; estado (*Activa* o *Ya no la tengo*); desde
cuándo y, solo si ya no la tiene, hasta cuándo, ambos con la mecánica de "cuándo"; tratamiento actual; diagnóstico
del expediente que la respalda; nota. La marca "Sensible" SHALL venir prendida por defecto en depresión, ansiedad,
trastorno bipolar y consumo de alcohol u otras sustancias, y apagada en las demás; el paciente SHALL poder prenderla
o apagarla en cualquier crónica. "Hasta" SHALL rechazarse cuando es claramente anterior a "desde". El diagnóstico
enlazado SHALL ser un diagnóstico (no una receta) del expediente del mismo paciente. Las mismas reglas de registro
vacío, aislamiento y confirmación al eliminar de las secciones de eventos SHALL aplicar.

#### Scenario: Crónica de la lista con tratamiento (B-1, B-3)
- **GIVEN** un paciente nacido el 15/03/1990, sin crónicas
- **WHEN** registra "Hipotiroidismo", activa, desde los 31 años, con tratamiento "Levotiroxina 50 mcg en ayunas"
- **THEN** la sección dice "1 registro" y la lista muestra "Hipotiroidismo · desde los 31 años (≈2021) · activa ·
  Levotiroxina 50 mcg en ayunas", sin la marca "sensible"

#### Scenario: Salud mental marcada como sensible por defecto (B-1b)
- **GIVEN** un paciente sin crónicas
- **WHEN** elige "Ansiedad" en la lista y guarda sin tocar el interruptor "Sensible"
- **THEN** la crónica se guarda con la marca "Sensible" prendida y la lista la muestra como "sensible"

#### Scenario: El paciente decide la marca sensible (B-1b)
- **GIVEN** un paciente con "Hipertensión" registrada sin la marca, y que registra "otra" con el texto "TOC"
- **WHEN** prende "Sensible" en "TOC" y también en "Hipertensión" al editarla
- **THEN** las dos se muestran como "sensible"; al apagarla de nuevo en "Hipertensión", deja de mostrarse así

#### Scenario: Ya no la tengo, con desde y hasta (B-2)
- **GIVEN** un paciente nacido el 15/03/1990
- **WHEN** registra "Asma", "Ya no la tengo", desde "En la primaria" y hasta los 16 años
- **THEN** la lista muestra "Asma · desde la primaria (≈1996–2001) · hasta los 16 años (≈2006)"

#### Scenario: "Hasta" antes de "desde" (B-2)
- **GIVEN** un paciente que registra "Epilepsia", "Ya no la tengo", desde los 20 años
- **WHEN** pone hasta los 12 años y guarda
- **THEN** el sistema lo rechaza con el mensaje es-MX "No puede ser antes de «desde cuándo»" junto al campo
  "¿Hasta cuándo?" y no guarda nada

#### Scenario: "Hasta" con estado activa no se guarda (B-2)
- **GIVEN** una crónica "Ya no la tengo" con hasta los 16 años
- **WHEN** el paciente la edita a "Activa" y guarda
- **THEN** la crónica queda activa y sin "hasta"

#### Scenario: Enlace a un diagnóstico del expediente (B-4)
- **GIVEN** un paciente con el diagnóstico "Hipotiroidismo subclínico" en su expediente
- **WHEN** registra "Hipotiroidismo" y elige ese diagnóstico como respaldo
- **THEN** la lista muestra "Respaldo: Hipotiroidismo subclínico"; el selector solo ofrece diagnósticos, no
  recetas

#### Scenario: Enlace a un diagnóstico que no es suyo (B-4)
- **GIVEN** dos pacientes A y B, B con un diagnóstico en su expediente
- **WHEN** A intenta guardar una crónica enlazada al diagnóstico de B, a una receta propia o a un id que no existe
- **THEN** las tres se rechazan con el mismo mensaje es-MX "Ese diagnóstico no está en tu expediente" y nada se
  guarda

#### Scenario: Falta la condición (B-1)
- **GIVEN** un paciente que llena "desde" y "tratamiento" de una crónica nueva
- **WHEN** guarda sin elegir condición, o eligiendo "otra" sin texto
- **THEN** el sistema lo rechaza con el mensaje es-MX "Elige la condición o escribe cuál es" junto al campo

## MODIFIED Requirements

### Requirement: Pantalla "Mi perfil médico" con secciones visibles
La pantalla "Mi perfil médico" SHALL mostrar el perfil básico, las mediciones y los antecedentes familiares con
su estado, y SHALL listar las demás secciones de la anamnesis: enfermedades crónicas; enfermedades pasadas e
infecciosas; cirugías y hospitalizaciones; fracturas y lesiones; transfusiones y grupo sanguíneo; hábitos. Las
secciones de enfermedades crónicas y de eventos (enfermedades pasadas, cirugías, fracturas, transfusiones) SHALL
mostrar en su tarjeta su estado (*Sin llenar*, *Ninguna* o el número de registros) y SHALL abrir su propia
pantalla de captura. Hábitos SHALL seguir visible y sin captura hasta su story de FR-028.

#### Scenario: Estado de cada sección en su tarjeta (A-1)
- **GIVEN** un paciente con dos enfermedades pasadas registradas, una crónica, "Nunca me han transfundido" marcado
  y nada en cirugías ni fracturas
- **WHEN** abre "Mi perfil médico"
- **THEN** la tarjeta de enfermedades pasadas dice "2 registros", la de crónicas "1 registro", la de transfusiones
  "Ninguna", las de cirugías y fracturas "Sin llenar", y la de hábitos "Sin llenar" sin formulario de captura

#### Scenario: Secciones listadas sin captura
- **GIVEN** un paciente con un antecedente familiar registrado y nada en el historial
- **WHEN** abre "Mi perfil médico"
- **THEN** ve su antecedente contabilizado y las seis secciones del historial listadas con "Sin llenar"; la de
  hábitos no ofrece formulario, enlace ni botón "Agregar"

#### Scenario: La tarjeta abre la pantalla de su sección
- **WHEN** el paciente toca la tarjeta "Cirugías y hospitalizaciones" o la de "Enfermedades crónicas"
- **THEN** llega a la pantalla de esa sección, con su lista de registros y la acción "Agregar"

### Requirement: Estado "ninguna" por sección
El paciente SHALL poder declarar que no ha tenido nada de una sección de eventos ("No he tenido ninguna"; en
transfusiones "Nunca me han transfundido") o que no tiene enfermedades crónicas ("No tengo ninguna"), solo cuando
la sección no tiene registros, y SHALL poder deshacerlo. Agregar un registro a una sección marcada como "ninguna"
SHALL quitar esa marca.

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

#### Scenario: "No tengo ninguna" en crónicas (B-0)
- **GIVEN** un paciente sin crónicas registradas
- **WHEN** elige "No tengo ninguna" y después registra "Hipertensión"
- **THEN** primero la tarjeta dice "Ninguna"; al registrar, la marca se quita, la tarjeta dice "1 registro" y la
  app lo avisa

### Requirement: Los registros del historial son solo del paciente y van cifrados
El sistema SHALL devolver a cada paciente únicamente sus propios registros del historial, SHALL responder de
forma indistinguible ante un registro inexistente y uno ajeno, y SHALL almacenar cifrados en reposo el contenido
de cada registro (incluidos su sección, la marca "Sensible" y el diagnóstico enlazado), la marca "ninguna" y el
grupo sanguíneo.

#### Scenario: Registro ajeno indistinguible de inexistente (A-8)
- **GIVEN** dos pacientes A y B, B con una cirugía registrada
- **WHEN** A intenta editar y eliminar por identificador la cirugía de B y un registro que no existe
- **THEN** ambas respuestas son indistinguibles entre sí (mismo status y mismo cuerpo) y la cirugía de B no
  cambia

#### Scenario: Cifrado en reposo (A-9)
- **GIVEN** un paciente con una cirugía "Apendicectomía", fracturas marcada como "ninguna" y grupo "O+"
- **WHEN** se lee el almacenamiento directamente, sin pasar por la app
- **THEN** ni "Apendicectomía", ni el nombre de la sección, ni la marca "ninguna", ni "O+" aparecen en claro

#### Scenario: Crónica cifrada en reposo (B-6)
- **GIVEN** un paciente con la crónica "Ansiedad", marcada "Sensible", con tratamiento "Sertralina 50 mg" y
  enlazada a un diagnóstico de su expediente
- **WHEN** se lee el almacenamiento directamente, sin pasar por la app
- **THEN** ni "anxiety" ni "Ansiedad", ni "Sertralina", ni la marca sensible, ni el id del diagnóstico aparecen en
  claro
