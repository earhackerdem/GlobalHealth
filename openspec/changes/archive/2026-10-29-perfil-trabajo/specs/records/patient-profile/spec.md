# Delta — records/patient-profile (perfil-trabajo)

## ADDED Requirements

### Requirement: Trabajo en el perfil básico
El sistema SHALL permitir al paciente con consentimiento vigente guardar y editar, como parte de su perfil básico y
desde la tarjeta "Datos básicos" de "Mi perfil médico", un bloque "Trabajo" con:
- **situación laboral**, una sola: trabajo · busco trabajo · jubilado o pensionado · hogar · estudio · no puedo
  trabajar por mi salud;
- **el trabajo de más años, si es otro**: texto libre de hasta 200 caracteres;
- solo con *Trabajo*: **a qué se dedica** (texto libre de hasta 200 caracteres), **a qué se expone en su trabajo** (polvo ·
  químicos o solventes · ruido fuerte, una o varias, o "Nada de esto") y **turno** (de día · de noche · rotativo).

Todo el bloque SHALL ser opcional y SHALL almacenarse cifrado en reposo. Al guardar, el sistema SHALL recortar los
espacios de los textos (un texto vacío queda sin registrar), SHALL descartar lo que solo aplica al trabajo cuando la
situación no es *Trabajo*, y SHALL descartar las exposiciones si se eligió "Nada de esto". SHALL rechazar un valor
fuera de sus opciones, un texto de más de 200 caracteres y cualquier dato que no sea de este bloque. La tarjeta
"Datos básicos" SHALL mostrar el trabajo en una línea: a qué se dedica (o la situación, si no lo escribió), el turno,
"antes: " y el trabajo de más años, y "expuesto a " con las exposiciones, separados por " · "; sin datos, SHALL decir
"Sin registrar". La app NO SHALL calcular ni mostrar ningún riesgo, puntaje o veredicto a partir del trabajo.

#### Scenario: Guardar el trabajo y verlo en la tarjeta (T-1)
- **GIVEN** un paciente con consentimiento vigente y sin trabajo guardado
- **WHEN** abre "Editar trabajo", elige "Trabajo", escribe "Chofer de transporte", elige "Ruido fuerte" y "Rotativo",
  y guarda
- **THEN** la tarjeta "Datos básicos" muestra en "Trabajo" "Chofer de transporte · rotativo · expuesto a ruido fuerte",
  y al reabrir el diálogo ve las mismas respuestas

#### Scenario: Todo es opcional (T-2)
- **GIVEN** un paciente sin trabajo guardado
- **WHEN** abre "Editar trabajo" y guarda sin contestar nada
- **THEN** el sistema lo acepta y la tarjeta dice "Sin registrar" en "Trabajo"

#### Scenario: "Nada de esto" y una exposición se excluyen (T-3)
- **GIVEN** un paciente que eligió "Trabajo" y "Polvo"
- **WHEN** elige "Nada de esto"
- **THEN** "Polvo" deja de estar elegido; y si después elige "Químicos o solventes", "Nada de esto" deja de estarlo

#### Scenario: Jubilado con el trabajo de más años (T-4)
- **GIVEN** un paciente sin trabajo guardado
- **WHEN** elige "Jubilado o pensionado", escribe "Minero" en el trabajo de más años y guarda
- **THEN** el diálogo no le preguntó a qué se dedica, exposiciones ni turno, y la tarjeta muestra
  "Jubilado o pensionado · antes: Minero"

#### Scenario: Cambiar de situación borra lo que solo aplica al trabajo (T-6)
- **GIVEN** un paciente con "Trabajo", "Chofer de transporte", "Ruido fuerte", "Rotativo" y "Taxista" como el trabajo
  de más años, guardados
- **WHEN** cambia a "Busco trabajo" y guarda
- **THEN** el sistema guarda "Busco trabajo" y "Taxista", sin a qué se dedica, exposiciones ni turno, y la tarjeta
  muestra "Busco trabajo · antes: Taxista"

#### Scenario: Valores fuera de las opciones o de su largo
- **WHEN** el paciente (o un cliente) envía una situación, exposición o turno que no está en las opciones, un texto de
  201 caracteres o una propiedad que no es del bloque
- **THEN** el sistema lo rechaza, indicando el campo, y lo guardado no cambia

#### Scenario: El trabajo es solo del paciente y va cifrado (T-5)
- **GIVEN** dos pacientes, uno con "Chofer de transporte" guardado
- **WHEN** el otro paciente consulta su trabajo, o alguien lee la base de datos sin las llaves de la app
- **THEN** el otro paciente recibe solo su propio trabajo (vacío) y "Chofer de transporte" no aparece en claro en la
  base de datos; sin consentimiento vigente, consultar o guardar el trabajo se rechaza
