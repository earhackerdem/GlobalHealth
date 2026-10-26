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
El perfil SHALL guardar los hábitos del paciente como un solo cuestionario. Cada hábito es opcional: el paciente puede
no contestar un bloque. Cuando elige una respuesta que abre más preguntas, esas preguntas SHALL contestarse antes de
guardar; en las que tratan del pasado SHALL poder contestar "No recuerdo":
- **alcohol:** *Nunca*, *Lo dejé* o *Actual*. Con *Lo dejé* o *Actual*, a qué edad empezó a tomar (sin contar
  probaditas; admite "No recuerdo"); con *Lo dejé*, además, a qué edad lo dejó (admite "No recuerdo"). Si es *Actual*,
  las tres preguntas del AUDIT-C con su escala: con qué frecuencia toma (una vez al mes o menos · 2 a 4 veces al mes ·
  2 a 3 veces por semana · 4 o más veces por semana), cuántas bebidas en un día que toma (1 o 2 · 3 o 4 · 5 o 6 · 7 a
  9 · 10 o más), cada cuándo toma 6 o más en una sola ocasión (nunca · menos de una vez al mes · cada mes · cada semana
  · a diario o casi), y si toma sobre todo en fines de semana (Sí · No); ninguna de estas cuatro admite "No recuerdo";
- **tabaco:** *Nunca*, *Antes* o *Actual*, con cigarros al día (1 a 100), a qué edad empezó y, si es *Antes*, a qué
  edad lo dejó; las edades admiten "No recuerdo", y los cigarros solo si es *Antes*;
- **vapeador o cigarro electrónico:** *Nunca*, *Antes* o *Actual*. Con *Antes* o *Actual*, a qué edad empezó; con
  *Antes*, a qué edad lo dejó (las dos admiten "No recuerdo"). Con *Actual*, si lo usa todos los días o algunos días,
  y con *Algunos días*, cuántos días de los últimos 30 (1 a 30), sin "No recuerdo";
- **humo de tabaco de otras personas:** dónde (casa · trabajo o escuela · otro lugar, uno o varios) con los días por
  semana (1 a 7, sin "No recuerdo"), o "No me expongo";
- **humo de leña o carbón:** *Nunca*, *Antes* o *Actual*. Con *Antes* o *Actual*, a qué edad empezó la exposición y
  cuántas horas al día en promedio (1 a 24); con *Antes*, a qué edad terminó. Las edades admiten "No recuerdo", y las
  horas solo si es *Antes*.

Al guardar, el sistema SHALL descartar lo que no aplica a la respuesta elegida: las preguntas del AUDIT-C y la marca
de fines de semana si el alcohol no es *Actual*; las edades si el alcohol, el tabaco, el vapeador o la leña son
*Nunca*; la edad en que lo dejó o terminó si no es *Lo dejé* o *Antes*; los cigarros si el tabaco es *Nunca*; la
frecuencia del vapeador si no es *Actual*, y los días de los últimos 30 si no es *Algunos días*; las horas si la leña
es *Nunca*; los lugares y los días si no se expone. Después SHALL rechazar, con el mensaje junto a su campo, una
pregunta que aplica y no se contestó ("Contesta esta pregunta." o, donde admite "No recuerdo", "Contesta esta pregunta
o marca «No recuerdo»."; si faltan los lugares del humo ajeno, "Elige dónde, o «No me expongo»"), un "No recuerdo" en
una pregunta que no lo admite, una edad mayor que la edad actual del
paciente, una edad fuera de 0 a 130, y una edad de inicio mayor que la edad en que lo dejó o terminó, en el alcohol,
el tabaco, el vapeador y la leña. "No recuerdo" no se compara con otras edades. Sin fecha de nacimiento SHALL aceptar
cualquier edad entre 0 y 130.

Los hábitos guardados antes de este cambio SHALL seguir leyéndose: el vapeador conserva su *Nunca*, *Antes* o
*Actual*, los años aproximados de la leña se descartan (no se pueden convertir a edades), y una pregunta que se dejó
sin contestar se muestra sin contestar (nunca como "No recuerdo") hasta que el paciente la contesta al guardar.

#### Scenario: Alcohol actual con las preguntas del AUDIT-C (C-1)
- **GIVEN** un paciente nacido el 15/03/1990, sin hábitos guardados
- **WHEN** elige alcohol "Actual", escribe 18 en "¿A qué edad empezaste a tomar?", elige "2 a 3 veces por semana",
  "3 o 4" bebidas, 6 o más "Cada mes", y "Sí" en "Sobre todo fines de semana"
- **THEN** la tarjeta "Hábitos" dice "Con datos" y, al volver a abrir la pantalla, ve 18 y esas cinco respuestas
  elegidas

#### Scenario: Lo dejó, con la edad (C-1)
- **GIVEN** un paciente nacido el 15/03/1990
- **WHEN** elige alcohol "Lo dejé", escribe 17 en "¿A qué edad empezaste a tomar?" y 30 en "¿A qué edad dejaste de
  tomar?"
- **THEN** al volver a abrir la pantalla ve "Lo dejé" con 17 y 30, y ninguna pregunta del AUDIT-C

#### Scenario: Alcohol: empezó después de dejarlo (C-10)
- **GIVEN** un paciente que elige alcohol "Lo dejé"
- **WHEN** escribe que empezó a los 30 y lo dejó a los 18
- **THEN** ve "No puede ser mayor que la edad en que lo dejaste" junto a la edad de inicio, y nada se guarda

#### Scenario: Una edad mayor que la actual (C-1, C-2)
- **GIVEN** un paciente nacido el 15/03/1990, que hoy tiene 36 años
- **WHEN** elige alcohol "Lo dejé" y escribe 40 en la edad en que lo dejó
- **THEN** ve "La edad no puede ser mayor que tu edad actual" junto a ese campo, y nada se guarda

#### Scenario: Lo que no aplica se descarta (C-1)
- **GIVEN** un paciente que eligió alcohol "Actual", con edad de inicio, y contestó las tres preguntas del AUDIT-C y la
  de fines de semana
- **WHEN** cambia a "Nunca"
- **THEN** al volver a abrir la pantalla ve "Nunca" sin edad ni preguntas del AUDIT-C, y el perfil guardado no
  conserva esas respuestas

#### Scenario: Tabaco que dejó, y vapeador actual (C-2)
- **GIVEN** un paciente nacido el 15/03/1990
- **WHEN** elige tabaco "Antes" con 10 cigarros al día, empezó a los 18 y lo dejó a los 30, y vapeador "Actual",
  empezó a los 30, con "Todos los días"
- **THEN** al volver a abrir la pantalla ve esas respuestas

#### Scenario: Empezó después de dejarlo (C-2)
- **GIVEN** un paciente que elige tabaco "Antes"
- **WHEN** escribe que empezó a los 30 y lo dejó a los 18
- **THEN** ve "No puede ser mayor que la edad en que lo dejaste" junto a la edad de inicio, y nada se guarda

#### Scenario: Vapeador actual algunos días (C-11)
- **GIVEN** un paciente nacido el 15/03/1990
- **WHEN** elige vapeador "Actual", escribe 25 en "¿A qué edad empezaste a vapear?", elige "Algunos días" y escribe 12
  en "¿Cuántos días de los últimos 30?"
- **THEN** al volver a abrir la pantalla ve "Actual", 25, "Algunos días" y 12

#### Scenario: Vapeador de antes, y luego todos los días (C-11)
- **GIVEN** un paciente con vapeador "Actual" desde los 25, "Algunos días" y 12 días
- **WHEN** elige "Todos los días"; después cambia a "Antes" y escribe que dejó de vapear a los 28
- **THEN** primero ya no ve la pregunta de los días; al final, al volver a abrir la pantalla, ve "Antes" con 25 y 28,
  sin frecuencia ni días

#### Scenario: Humo ajeno en varios lugares, y después "No me expongo" (C-3)
- **GIVEN** un paciente sin hábitos guardados
- **WHEN** elige "Casa" y "Trabajo o escuela" con 2 días por semana; después elige "No me expongo"
- **THEN** primero ve los dos lugares con 2 días; al final ve "No me expongo" sin lugares ni días

#### Scenario: Humo de leña de antes (C-4)
- **GIVEN** un paciente nacido el 15/03/1990
- **WHEN** elige humo de leña "Antes", escribe que empezó a los 5 y terminó a los 20, y 3 horas al día
- **THEN** al volver a abrir la pantalla ve "Antes" con 5, 20 y 3 horas, y en ningún lado ve un cálculo con esos
  datos

#### Scenario: Contesta solo una cosa
- **GIVEN** un paciente sin hábitos guardados
- **WHEN** solo elige vapeador "Nunca"
- **THEN** la tarjeta dice "Con datos" y las demás preguntas siguen sin contestar

#### Scenario: Respuestas fuera de su escala
- **WHEN** se intenta guardar 0 o 101 cigarros al día, 8 días por semana de humo ajeno, 0 o 31 días de los últimos 30
  de vapeador, 0 o 25 horas al día de leña, una edad de 131, una opción que no está en la escala, o "No recuerdo" en
  una pregunta que no lo admite
- **THEN** el sistema lo rechaza y los hábitos guardados no cambian

#### Scenario: Lo guardado antes de este cambio se sigue leyendo
- **GIVEN** un paciente que guardó con la versión anterior vapeador "Actual" y humo de leña "Antes" con 12 años, más
  tabaco "Antes"
- **WHEN** abre su pantalla de hábitos
- **THEN** ve vapeador "Actual" sin frecuencia ni edades, leña "Antes" sin edades ni horas, y su tabaco igual que
  antes; ninguna respuesta se pierde salvo los años de leña, y ninguna pregunta aparece como "No recuerdo"

#### Scenario: Falta una pregunta de lo que eligió (C-15)
- **GIVEN** un paciente nacido el 15/03/1990, sin hábitos guardados
- **WHEN** elige alcohol "Lo dejé", escribe 30 en "¿A qué edad dejaste de tomar?", deja vacía la edad de inicio y toca
  "Guardar"
- **THEN** ve "Contesta esta pregunta o marca «No recuerdo»." junto a "¿A qué edad empezaste a tomar?", con el foco en
  ese campo, y nada se guarda

#### Scenario: Alcohol actual sin las preguntas de frecuencia (C-15)
- **GIVEN** un paciente nacido el 15/03/1990, sin hábitos guardados
- **WHEN** elige alcohol "Actual", escribe 18 en la edad de inicio y toca "Guardar" sin contestar las preguntas de
  frecuencia ni la de fines de semana
- **THEN** ve "Contesta esta pregunta." bajo cada una de esas cuatro preguntas, ninguna de ellas ofrece "No recuerdo",
  y nada se guarda

#### Scenario: No recuerda cuándo empezó (C-16)
- **GIVEN** un paciente nacido el 15/03/1990
- **WHEN** elige alcohol "Lo dejé", marca "No recuerdo" en "¿A qué edad empezaste a tomar?", escribe 18 en "¿A qué
  edad dejaste de tomar?" y toca "Guardar"
- **THEN** se guarda sin error (la edad de inicio no se compara), y al volver a abrir la pantalla ve "No recuerdo"
  marcado en la edad de inicio y 18 en la de fin

#### Scenario: "No recuerdo" solo en lo que pasó (C-16)
- **GIVEN** un paciente que elige tabaco "Actual"
- **WHEN** mira "Cigarros al día" y la edad de inicio; después cambia a "Antes"
- **THEN** con "Actual" los cigarros no ofrecen "No recuerdo" y la edad de inicio sí; con "Antes", los cigarros, la
  edad de inicio y la de fin lo ofrecen

#### Scenario: Escribir un número quita "No recuerdo" (C-16)
- **GIVEN** un paciente con "No recuerdo" marcado en la edad de inicio del tabaco
- **WHEN** escribe 16 en ese campo
- **THEN** "No recuerdo" deja de estar marcado y, al guardar y volver a abrir, ve 16

#### Scenario: Lo guardado a medias pide completar al guardar (C-15)
- **GIVEN** un paciente que guardó antes de este cambio alcohol "Lo dejé" con solo la edad en que lo dejó
- **WHEN** abre la pantalla y toca "Guardar" sin cambiar nada
- **THEN** ve "Contesta esta pregunta o marca «No recuerdo»." junto a la edad de inicio, y lo guardado no cambia

### Requirement: La app no interpreta los hábitos
El sistema SHALL guardar y mostrar las respuestas de hábitos tal como el paciente las dio, y NO SHALL calcular ni
mostrar puntajes (AUDIT-C u otros), índices de exposición (horas-año u otros), niveles de riesgo ni veredictos sobre
ellas: interpretarlas es del médico (NFR-008). "No recuerdo" se guarda y se muestra como tal, sin estimar un valor.

#### Scenario: Sin puntaje ni riesgo (C-6)
- **GIVEN** un paciente con alcohol "Actual" desde los 15, "4 o más veces por semana", "10 o más" bebidas, 6 o más "A
  diario o casi" y "No" en fines de semana, tabaco "Actual" con 20 cigarros al día desde "No recuerdo", y humo de leña
  "Actual" desde los 5 años con 8 horas al día
- **WHEN** vuelve a abrir la pantalla, y cuando la app pide sus hábitos
- **THEN** ni la pantalla ni la respuesta del sistema contienen un puntaje, un índice, un nivel de riesgo, ni palabras
  como "riesgo", "puntaje", "AUDIT" o "horas-año"

### Requirement: Los hábitos se guardan con "Guardar" y avisan antes de perderse
La pantalla de hábitos SHALL decir desde que se abre que las respuestas se guardan al tocar "Guardar", y SHALL guardar
solo entonces, si todo el cuestionario es válido. Si el paciente sale de la pantalla con cambios sin guardar (por el
menú, por "‹ Mi perfil médico", con atrás del navegador, al recargar o al cerrar la pestaña), la pantalla SHALL
preguntarle antes, salvo que la sesión haya terminado o cambiado de cuenta, o que se esté guardando. Mientras se
guarda, salir dentro de la app SHALL esperar a que el guardado termine: si sale bien, seguir a donde iba; si falla,
quedarse con el error a la vista; recargar o cerrar la pestaña no pregunta. "Cancelar" SHALL descartar los cambios sin
preguntar y sin guardar nada. "Guardar", "Cancelar" y las preguntas SHALL quedar no disponibles mientras se guarda,
sin perder el foco, para que un doble clic no mande dos veces lo mismo.

#### Scenario: Se guarda al tocar "Guardar" (C-13)
- **GIVEN** un paciente con la pantalla de hábitos abierta y nada guardado
- **WHEN** lee "Tus respuestas se guardan cuando tocas «Guardar».", elige tabaco "Nunca" y toca "Guardar"
- **THEN** el sistema no recibe nada hasta que toca "Guardar"; después vuelve a "Mi perfil médico" con "Hábitos
  guardados", la tarjeta dice "Con datos" y, al abrirla, ve tabaco "Nunca"

#### Scenario: Aviso al salir con cambios sin guardar (C-13)
- **GIVEN** un paciente con tabaco "Nunca" guardado, que abre la pantalla, elige "Actual" y escribe 12 en "Cigarros al
  día" sin salir del campo
- **WHEN** toca "‹ Mi perfil médico"
- **THEN** ve "¿Salir sin guardar?"; con "Seguir editando" sigue en la pantalla con "Actual" y 12; con "Salir sin
  guardar" vuelve a "Mi perfil médico", el sistema no recibió nada y, al abrir, ve tabaco "Nunca"

#### Scenario: Sin cambios no hay aviso (C-13)
- **GIVEN** un paciente con tabaco "Nunca" guardado
- **WHEN** abre la pantalla, elige "Actual", vuelve a elegir "Nunca" y toca "‹ Mi perfil médico"
- **THEN** vuelve a "Mi perfil médico" sin ninguna pregunta

#### Scenario: Aviso del navegador al recargar (C-13)
- **GIVEN** un paciente con un cambio sin guardar
- **WHEN** recarga la página
- **THEN** el navegador le pregunta si quiere salir; sin cambios, no le pregunta

#### Scenario: Sin aviso cuando la sesión cambió (C-13)
- **GIVEN** un paciente con un cambio sin guardar en la pantalla de hábitos
- **WHEN** cierra sesión en otra pestaña
- **THEN** esta pestaña va a la pantalla de inicio de sesión sin preguntar, y el sistema no recibió nada

#### Scenario: Botones no disponibles mientras guarda (C-13)
- **GIVEN** un paciente que eligió una respuesta y tocó "Guardar", y el guardado sigue en curso
- **WHEN** vuelve a tocar "Guardar" o toca "Cancelar"
- **THEN** los dos están marcados como no disponibles, el foco sigue en "Guardar", el sistema recibe un solo guardado y
  al terminar vuelve a "Mi perfil médico"

#### Scenario: Un guardado en camino no llega a otra cuenta (C-13)
- **GIVEN** un paciente A que eligió tabaco "Actual" con 20 cigarros y tocó "Guardar", y el guardado sigue en curso
- **WHEN** cierra sesión y, en la misma pestaña, entra otro paciente B antes de que el guardado termine
- **THEN** B no ve "Hábitos guardados" ni es llevado a "Mi perfil médico" por ese guardado, y al abrir sus hábitos no
  ve las respuestas de A

#### Scenario: Mientras guarda no se cambia nada ni se pregunta al salir (C-13)
- **GIVEN** un paciente que tocó "Guardar", y el guardado sigue en curso
- **WHEN** intenta elegir otra opción, y después va al "Expediente" desde el menú
- **THEN** la opción no cambia, no ve ninguna pregunta, y en cuanto el guardado termina llega al "Expediente"; al
  volver a abrir sus hábitos ve lo que guardó

#### Scenario: Un rechazo al salir se queda a la vista (C-13)
- **GIVEN** un paciente que tocó "Guardar" y, mientras guarda, intenta volver a "Mi perfil médico"
- **WHEN** el sistema rechaza el guardado (por ejemplo, una edad mayor que la actual tras corregir su fecha de
  nacimiento en otra pestaña)
- **THEN** se queda en la pantalla de hábitos con el error junto a su campo, y nada se guarda

#### Scenario: Cancelar descarta (C-13)
- **GIVEN** un paciente con tabaco "Nunca" guardado, que abre la pantalla y cambia a tabaco "Actual" con 5 cigarros
- **WHEN** toca "Cancelar"
- **THEN** vuelve a "Mi perfil médico" con "Se descartaron los cambios", sin ninguna pregunta, el sistema no recibió
  nada y, al abrir la pantalla, ve tabaco "Nunca"; si toca "Cancelar" sin haber cambiado nada, vuelve sin ese aviso

### Requirement: Los errores se marcan al momento
Al salir de un campo numérico, la pantalla de hábitos SHALL marcar junto a él, sin preguntar al servidor, un valor que
no es un número entero, uno fuera de su escala, una edad mayor que la actual o una edad de inicio mayor que la de fin.
Los límites de cada número SHALL ser los mismos que publica el contrato del sistema. Un error ya marcado SHALL
quitarse en cuanto el valor del campo sea válido, sin esperar a salir de él; mientras se escribe no aparecen errores
nuevos.

#### Scenario: Fuera de escala al salir del campo (C-14)
- **GIVEN** un paciente con humo de leña "Actual"
- **WHEN** escribe 25 en "¿Cuántas horas al día, en promedio?" y sale del campo
- **THEN** ve "Debe estar entre 1 y 24" junto a ese campo, con el campo marcado como inválido, y el sistema no recibe
  ningún guardado

#### Scenario: La marca sigue mientras el campo está a la vista (C-14)
- **GIVEN** un paciente con tabaco "Actual" y 101 en "Cigarros al día", marcado con "Debe estar entre 1 y 100"
- **WHEN** cambia el tabaco a "Antes"
- **THEN** los cigarros siguen a la vista con su marca y su mensaje

#### Scenario: El error se va al corregirlo (C-17)
- **GIVEN** un paciente con "12a" en "¿A qué edad empezaste a tomar?", marcado con "Escribe solo el número."
- **WHEN** vuelve al campo, borra la "a" y, sin salir del campo, deja 12
- **THEN** el mensaje y la marca de inválido desaparecen en ese momento; si en cambio borra todo, el mensaje también
  desaparece y el campo queda vacío sin error hasta que toque "Guardar"
