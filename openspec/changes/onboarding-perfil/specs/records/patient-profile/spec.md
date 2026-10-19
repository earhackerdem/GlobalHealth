# Spec Delta

## Purpose

El perfil médico del paciente: los datos que todo médico pregunta primero (nacimiento, sexo, alergias, peso y
estatura como mediciones fechadas, antecedentes familiares con línea materna/paterna), capturados una sola vez en
un onboarding omitible tras aceptar el consentimiento y editables después desde "Mi perfil médico".

## ADDED Requirements

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
reciente de cada tipo con su fecha. Valores fuera de rango plausible SHALL rechazarse. Las mediciones SHALL
almacenarse cifradas en reposo.

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
su estado, y SHALL listar las demás secciones de la anamnesis (enfermedades crónicas; enfermedades pasadas e
infecciosas; cirugías y hospitalizaciones; fracturas y lesiones; transfusiones y grupo sanguíneo; hábitos) como
secciones visibles pero aún sin captura — su llenado llega con FR-028 y esta versión NO SHALL inventarles
formularios.

#### Scenario: Secciones listadas sin captura
- **GIVEN** un paciente con un antecedente familiar registrado
- **WHEN** abre "Mi perfil médico"
- **THEN** ve su antecedente contabilizado y las seis secciones restantes listadas como vacías, sin formulario
  de captura disponible

### Requirement: El perfil es solo del paciente
El sistema SHALL devolver a cada paciente únicamente su propio perfil, mediciones y antecedentes, y SHALL
responder de forma indistinguible ante un recurso inexistente y uno ajeno.

#### Scenario: Perfil ajeno indistinguible de inexistente
- **GIVEN** dos pacientes A y B, cada uno con perfil propio
- **WHEN** A consulta por identificador una medición de B y una medición que no existe
- **THEN** ambas respuestas son indistinguibles entre sí y no revelan datos de B
