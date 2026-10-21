# Spec Delta

## ADDED Requirements

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

## MODIFIED Requirements

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
