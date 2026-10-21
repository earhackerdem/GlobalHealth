# records/patient-profile Specification

## Purpose
El perfil médico del paciente: los datos que todo médico pregunta primero (nacimiento, sexo, alergias, peso y
estatura como mediciones fechadas, antecedentes familiares con línea materna/paterna), capturados una sola vez en
un onboarding omitible tras aceptar el consentimiento y editables después desde "Mi perfil médico".
## Requirements
### Requirement: Perfil básico del paciente
El sistema SHALL permitir al paciente con consentimiento vigente guardar y editar su perfil básico: fecha de
nacimiento (nunca futura), sexo (mujer / hombre / prefiero no decir) y alergias a medicamentos (texto libre).
Todos los campos SHALL ser opcionales (el perfil parcial o vacío es válido) y SHALL almacenarse cifrados en
reposo. Donde el perfil se muestre, la edad SHALL derivarse de la fecha de nacimiento a la fecha actual.

#### Scenario: Guardar el perfil básico y ver la edad
- **GIVEN** una paciente con consentimiento vigente y fecha actual 2026-10-19
- **WHEN** guarda fecha de nacimiento 1990-03-15, sexo "Mujer" y alergias "penicilina"
- **THEN** su perfil muestra esos datos y la edad "36 años", y los valores quedan cifrados en reposo

#### Scenario: Fecha de nacimiento futura rechazada
- **WHEN** el paciente intenta guardar fecha de nacimiento 2030-01-01
- **THEN** el sistema la rechaza con un mensaje en es-MX y el perfil no cambia

#### Scenario: Perfil vacío es válido
- **WHEN** el paciente guarda el perfil sin llenar ningún campo
- **THEN** el sistema lo acepta y el perfil se muestra como vacío y editable

### Requirement: Peso y estatura como mediciones con fecha
El sistema SHALL registrar peso (kg) y estatura (cm) como mediciones con fecha, nunca como un valor que se
sobreescribe: registrar un valor nuevo SHALL conservar los anteriores, y el perfil SHALL mostrar la medición más
reciente de cada tipo con su fecha. Valores fuera de rango plausible SHALL rechazarse. El VALOR de la medición
SHALL almacenarse cifrado en reposo; el tipo y la fecha quedan en claro porque el sistema consulta por ellos
(frontera ratificada en el review 2026-10-19, G19).

#### Scenario: La medición nueva no borra la anterior
- **GIVEN** un paciente con peso 72 kg registrado el 2026-10-19
- **WHEN** registra 74 kg el 2026-11-02
- **THEN** el perfil muestra "74 kg (02/11/2026)" y la medición de 72 kg del 19/10/2026 sigue existiendo

#### Scenario: Valor implausible rechazado
- **WHEN** el paciente intenta registrar peso 0 kg o estatura 500 cm
- **THEN** el sistema rechaza el valor con un mensaje en es-MX y no crea la medición

### Requirement: Antecedentes familiares con línea materna y paterna
El sistema SHALL permitir registrar antecedentes familiares: una condición (catálogo: diabetes, cáncer,
hipertensión, enfermedad del corazón; u "otra" con texto) con 0..N parentescos que distinguen línea (madre, padre,
abuela/abuelo materno, abuela/abuelo paterno, hermana/o, otro) y un detalle opcional (p. ej. edad al diagnóstico).
Varios antecedentes por paciente SHALL ser posibles; el contenido SHALL almacenarse cifrado en reposo.

#### Scenario: Antecedente con línea y detalle
- **WHEN** el paciente registra la condición "Diabetes" con parentescos [abuelo paterno, madre] y detalle
  "abuelo diagnosticado a los 50"
- **THEN** su perfil muestra "Diabetes: abuelo paterno, madre · abuelo diagnosticado a los 50"

#### Scenario: Quitar una condición elimina sus parentescos
- **GIVEN** un antecedente "Cáncer" con parentesco [abuela materna]
- **WHEN** el paciente elimina ese antecedente
- **THEN** la condición y sus parentescos desaparecen del perfil y del almacenamiento

### Requirement: Onboarding una sola vez tras el consentimiento
El sistema SHALL ofrecer el onboarding de perfil inmediatamente después de que el paciente acepte el
consentimiento, una sola vez por cuenta: tanto completarlo como omitirlo ("Ahora no") SHALL registrarse y el
onboarding NO SHALL volver a ofrecerse en sesiones posteriores; omitirlo SHALL llevar directo al expediente.

#### Scenario: Omitir lleva al expediente y no se repite
- **GIVEN** una cuenta recién creada que acaba de aceptar el consentimiento
- **WHEN** el paciente elige "Ahora no, llévame a mi expediente" y después cierra sesión y vuelve a entrar
- **THEN** la primera vez aterriza en el expediente sin llenar nada y en el siguiente inicio de sesión el
  onboarding no se le vuelve a ofrecer

#### Scenario: Completarlo tampoco se repite
- **GIVEN** un paciente que completó el onboarding con sus datos
- **WHEN** vuelve a iniciar sesión
- **THEN** entra directo al expediente y sus datos siguen en "Mi perfil médico"

### Requirement: Nada del onboarding es obligatorio
Cada paso del onboarding SHALL poder omitirse por separado y ningún campo SHALL ser obligatorio; lo capturado u
omitido SHALL poder completarse y corregirse después desde la pantalla "Mi perfil médico".

#### Scenario: Omitir por pasos y completar después
- **WHEN** el paciente omite el paso de datos básicos, llena solo "Diabetes: madre" en antecedentes y guarda
- **THEN** el perfil queda con ese único dato, y desde "Mi perfil médico" puede agregar su fecha de nacimiento
  más tarde

### Requirement: Pantalla "Mi perfil médico" con secciones visibles
La pantalla "Mi perfil médico" SHALL mostrar el perfil básico, las mediciones y los antecedentes familiares con
su estado, y SHALL listar las demás secciones de la anamnesis: enfermedades crónicas; enfermedades pasadas e
infecciosas; cirugías y hospitalizaciones; fracturas y lesiones; transfusiones y grupo sanguíneo; hábitos. Las
secciones de enfermedades crónicas y de eventos (enfermedades pasadas, cirugías, fracturas, transfusiones) SHALL
mostrar en su tarjeta su estado (*Sin llenar*, *Ninguna* o el número de registros) y SHALL abrir su propia
pantalla de captura. La tarjeta de hábitos SHALL mostrar *Sin llenar* o *Con datos* (no tiene "ninguna": cada
hábito tiene su "Nunca") y SHALL abrir la pantalla del cuestionario de hábitos.

#### Scenario: Estado de cada sección en su tarjeta (A-1)
- **GIVEN** un paciente con dos enfermedades pasadas registradas, una crónica, "Nunca me han transfundido" marcado,
  nada en cirugías ni fracturas, y sin hábitos guardados
- **WHEN** abre "Mi perfil médico"
- **THEN** la tarjeta de enfermedades pasadas dice "2 registros", la de crónicas "1 registro", la de transfusiones
  "Ninguna", y las de cirugías, fracturas y hábitos "Sin llenar"

#### Scenario: Secciones listadas sin captura
- **GIVEN** un paciente con un antecedente familiar registrado y nada en el historial ni en hábitos
- **WHEN** abre "Mi perfil médico"
- **THEN** ve su antecedente contabilizado y las seis secciones del historial listadas con "Sin llenar", cada una
  con su enlace

#### Scenario: La tarjeta abre la pantalla de su sección
- **WHEN** el paciente toca la tarjeta "Cirugías y hospitalizaciones", la de "Enfermedades crónicas" o la de
  "Hábitos"
- **THEN** llega a la pantalla de esa sección: con su lista de registros y la acción "Agregar" en las dos primeras,
  y con el cuestionario y "Guardar" en la de hábitos

### Requirement: El perfil es solo del paciente
El sistema SHALL devolver a cada paciente únicamente su propio perfil, mediciones y antecedentes, y SHALL
responder de forma indistinguible ante un recurso inexistente y uno ajeno.

#### Scenario: Perfil ajeno indistinguible de inexistente
- **GIVEN** dos pacientes A y B, cada uno con perfil propio
- **WHEN** A consulta, modifica o elimina por identificador un antecedente familiar de B y uno que no existe
  (las mediciones no exponen operaciones por identificador; su no-fuga se verifica por el listado aislado)
- **THEN** ambas respuestas son indistinguibles entre sí (mismo status y mismo cuerpo) y no revelan datos de B

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
El sistema SHALL devolver a cada paciente únicamente sus propios registros del historial y sus propios hábitos,
SHALL responder de forma indistinguible ante un registro inexistente y uno ajeno, y SHALL almacenar cifrados en
reposo el contenido de cada registro (incluidos su sección, la marca "Sensible" y el diagnóstico enlazado), la marca
"ninguna", el grupo sanguíneo y los hábitos.

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

#### Scenario: Hábitos solo del paciente y cifrados
- **GIVEN** dos pacientes A y B; A con alcohol "Actual" y humo ajeno en "Casa"
- **WHEN** B pide sus hábitos, y cuando se lee el almacenamiento directamente
- **THEN** B no recibe nada de A, y ni las respuestas de A ni los nombres de sus campos aparecen en claro

### Requirement: Registros de enfermedades crónicas
El sistema SHALL permitir al paciente con consentimiento vigente agregar, editar y eliminar registros en la sección
de enfermedades crónicas, con: condición (catálogo de doce — diabetes tipo 2, hipertensión, asma, hipotiroidismo,
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

### Requirement: Hábitos: sustancias y humo
El perfil SHALL guardar los hábitos del paciente como un solo cuestionario, en el que cada respuesta es opcional y
se guarda lo que haya contestado:
- **alcohol:** *Nunca*, *Lo dejé* (con la edad a la que lo dejó) o *Actual*. Si es *Actual*, las tres preguntas del
  AUDIT-C con su escala: con qué frecuencia toma (una vez al mes o menos · 2 a 4 veces al mes · 2 a 3 veces por
  semana · 4 o más veces por semana), cuántas bebidas en un día que toma (1 o 2 · 3 o 4 · 5 o 6 · 7 a 9 · 10 o más),
  cada cuándo toma 6 o más en una sola ocasión (nunca · menos de una vez al mes · cada mes · cada semana · a diario o
  casi), y si toma sobre todo en fines de semana (Sí · No);
- **tabaco:** *Nunca*, *Antes* o *Actual*, con cigarros al día (1 a 100), a qué edad empezó y, si es *Antes*, a qué
  edad lo dejó;
- **vapeador o cigarro electrónico:** *Nunca*, *Antes* o *Actual*;
- **humo de tabaco de otras personas:** dónde (casa · trabajo o escuela · otro lugar, uno o varios) con los días por
  semana (1 a 7), o "No me expongo";
- **humo de leña o carbón:** *Nunca*, *Antes* o *Actual*, con los años aproximados.

Al guardar, el sistema SHALL descartar lo que no aplica a la respuesta elegida: las preguntas del AUDIT-C y la marca
de fines de semana si el alcohol no es *Actual*; la edad en que lo dejó si no es *Lo dejé* o *Antes*; los cigarros y
las edades si el tabaco es *Nunca*; los años si la leña es *Nunca*; los lugares y los días si no se expone. El sistema
SHALL rechazar, con el mensaje junto a su campo, una edad mayor que la edad actual del paciente, una edad fuera de 0 a
130, y una edad de inicio del tabaco mayor que la edad en que lo dejó. Sin fecha de nacimiento SHALL aceptar
cualquier edad entre 0 y 130.

#### Scenario: Alcohol actual con las preguntas del AUDIT-C (C-1)
- **GIVEN** un paciente nacido el 15/03/1990, sin hábitos guardados
- **WHEN** elige alcohol "Actual", "2 a 3 veces por semana", "3 o 4" bebidas, 6 o más "Cada mes", "Sí" en "Sobre
  todo fines de semana" y guarda
- **THEN** la tarjeta "Hábitos" dice "Con datos" y, al volver a abrir la pantalla, esas cinco respuestas siguen
  elegidas

#### Scenario: Lo dejó, con la edad (C-1)
- **GIVEN** un paciente nacido el 15/03/1990
- **WHEN** elige alcohol "Lo dejé", escribe 30 en "¿A qué edad dejaste de tomar?" y guarda
- **THEN** al volver a abrir la pantalla ve "Lo dejé" con 30, y ninguna pregunta del AUDIT-C

#### Scenario: Una edad mayor que la actual (C-1, C-2)
- **GIVEN** un paciente nacido el 15/03/1990, que hoy tiene 36 años
- **WHEN** elige alcohol "Lo dejé" con 40 años y guarda
- **THEN** ve "La edad no puede ser mayor que tu edad actual" junto a ese campo, y nada se guarda

#### Scenario: Lo que no aplica se descarta (C-1)
- **GIVEN** un paciente que eligió alcohol "Actual" y contestó las tres preguntas del AUDIT-C
- **WHEN** cambia a "Nunca" y guarda
- **THEN** al volver a abrir la pantalla ve "Nunca" sin preguntas del AUDIT-C, y el perfil guardado no conserva esas
  respuestas

#### Scenario: Tabaco que dejó, y vapeador actual (C-2)
- **GIVEN** un paciente nacido el 15/03/1990
- **WHEN** elige tabaco "Antes" con 10 cigarros al día, empezó a los 18 y lo dejó a los 30, vapeador "Actual", y
  guarda
- **THEN** al volver a abrir la pantalla ve esas respuestas

#### Scenario: Empezó después de dejarlo (C-2)
- **GIVEN** un paciente que elige tabaco "Antes"
- **WHEN** escribe que empezó a los 30 y lo dejó a los 18, y guarda
- **THEN** ve "No puede ser mayor que la edad en que lo dejaste" junto a la edad de inicio, y nada se guarda

#### Scenario: Humo ajeno en varios lugares, y después "No me expongo" (C-3)
- **GIVEN** un paciente sin hábitos guardados
- **WHEN** elige "Casa" y "Trabajo o escuela" con 2 días por semana y guarda; después elige "No me expongo" y guarda
- **THEN** primero ve los dos lugares con 2 días; al final ve "No me expongo" sin lugares ni días

#### Scenario: Humo de leña de antes (C-4)
- **WHEN** el paciente elige humo de leña "Antes" con 12 años aproximados y guarda
- **THEN** al volver a abrir la pantalla ve "Antes" con 12 años

#### Scenario: Contesta solo una cosa
- **GIVEN** un paciente sin hábitos guardados
- **WHEN** solo elige vapeador "Nunca" y guarda
- **THEN** la tarjeta dice "Con datos" y las demás preguntas siguen sin contestar

#### Scenario: Respuestas fuera de su escala
- **WHEN** se intenta guardar 0 o 101 cigarros al día, 8 días por semana de humo ajeno, una edad de 131, o una
  opción que no está en la escala
- **THEN** el sistema lo rechaza y los hábitos guardados no cambian

### Requirement: La app no interpreta los hábitos
El sistema SHALL guardar y mostrar las respuestas de hábitos tal como el paciente las dio, y NO SHALL calcular ni
mostrar puntajes (AUDIT-C u otros), niveles de riesgo ni veredictos sobre ellas: interpretarlas es del médico
(NFR-008).

#### Scenario: Sin puntaje ni riesgo (C-6)
- **GIVEN** un paciente con alcohol "Actual", "4 o más veces por semana", "10 o más" bebidas y 6 o más "A diario o
  casi", y tabaco "Actual" con 20 cigarros al día
- **WHEN** guarda y vuelve a abrir la pantalla, y cuando la app pide sus hábitos
- **THEN** ni la pantalla ni la respuesta del sistema contienen un puntaje, un nivel de riesgo, ni palabras como
  "riesgo", "puntaje" o "AUDIT"
