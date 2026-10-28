# Delta — records/patient-profile (perfil-habitos-actividad-sueno)

## ADDED Requirements

### Requirement: Hábitos: ejercicio, movimiento del día y sueño
El cuestionario de hábitos SHALL sumar tres bloques, cada uno opcional, con las mismas reglas de guardado que los demás
hábitos (se guardan con "Guardar", lo que no aplica se descarta, lo que una respuesta abre se contesta antes de guardar,
y ninguna de estas preguntas admite "No recuerdo"):
- **ejercicio:** qué ejercicio hace, eligiendo una o varias actividades (caminar · correr · bicicleta · nadar · pesas o
  gimnasio · fútbol u otro deporte · yoga o pilates · baile · otra), o "No hago ejercicio". Cada actividad elegida pide
  sus días por semana (1 a 7) y sus minutos cada vez (1 a 600); "Otra" pide además cuál es (texto de 1 a 60
  caracteres). La pantalla SHALL mostrar el total de lo anotado en minutos por semana (la suma de días por minutos de
  cada actividad);
- **movimiento del día:** cómo pasa el día en su trabajo o actividad principal (casi todo sentado · de pie o caminando,
  sin cargar cosas · cargando cosas ligeras o subiendo escaleras seguido · trabajo pesado o cargando cosas pesadas); si
  camina o va en bici al menos 10 minutos seguidos para ir a algún lado (No · Sí) y, con *Sí*, cuántos días por semana
  (1 a 7); y cuántas horas pasa sentado o reclinado en un día normal, sin contar el tiempo que duerme (0 a 24). El
  movimiento del día NO SHALL sumarse al total del ejercicio;
- **sueño:** cuántas horas duerme en promedio en un día de 24 horas (1 a 24, horas enteras), y en los últimos 30 días
  con qué frecuencia le costó dormirse y con qué frecuencia le costó seguir durmiendo o despertó demasiado temprano
  (nunca · algunos días · casi todos los días · todos los días), cada una por separado.

Al guardar, el sistema SHALL descartar las actividades si elige "No hago ejercicio", el nombre de "Otra" si no la
eligió, y los días del desplazamiento si contesta *No*. Después SHALL rechazar, con el mensaje junto a su campo, los días
o los minutos de una actividad elegida sin contestar ("Contesta esta pregunta."), el nombre de "Otra" vacío ("Escribe
cuál."), "hago ejercicio" sin ninguna actividad ("Elige al menos una actividad, o «No hago ejercicio»"), los días del
desplazamiento con *Sí* sin contestar ("Contesta esta pregunta."), un valor fuera de su escala, y un "No recuerdo" en
cualquiera de estas preguntas.

#### Scenario: Dos actividades con su total (C-5)
- **GIVEN** un paciente en la pantalla de hábitos
- **WHEN** elige "Caminar" con 5 días por semana y 30 minutos cada vez, y "Pesas o gimnasio" con 2 días y 45 minutos,
  y toca "Guardar"
- **THEN** antes de guardar ve "Total de lo anotado: 240 minutos por semana", y al volver a abrir la pantalla ve las
  dos actividades con sus días y minutos

#### Scenario: Otra actividad con su nombre (C-5)
- **GIVEN** un paciente que elige "Otra" con 1 día por semana y 90 minutos
- **WHEN** toca "Guardar" sin escribir cuál
- **THEN** no se guarda y junto a "¿Cuál?" ve "Escribe cuál."; con "Senderismo" se guarda y al volver a abrir ve
  "Otra" elegida con "Senderismo" en "¿Cuál?"

#### Scenario: Falta un dato de una actividad (C-5, C-15)
- **GIVEN** un paciente que elige "Correr" con 3 días por semana y sin los minutos
- **WHEN** toca "Guardar"
- **THEN** no se guarda; junto a "Minutos cada vez" de correr ve "Contesta esta pregunta." y el foco va ahí; sin
  "No recuerdo" en ninguna pregunta del ejercicio

#### Scenario: No hago ejercicio (C-5)
- **GIVEN** un paciente con "Caminar" 5 días y 30 minutos guardado
- **WHEN** elige "No hago ejercicio" y toca "Guardar"
- **THEN** al volver a abrir ve "No hago ejercicio" elegido, ninguna actividad y ningún total

#### Scenario: Movimiento del día aparte del ejercicio (C-7)
- **GIVEN** un paciente con "Caminar" 5 días y 30 minutos
- **WHEN** contesta "Casi todo sentado", *Sí* a caminar o ir en bici para ir a algún lado con 5 días por semana, y 9
  horas sentado, y toca "Guardar"
- **THEN** el total sigue en 150 minutos por semana, y al volver a abrir ve sus tres respuestas del movimiento del día

#### Scenario: Desplazamiento sin días (C-7, C-15)
- **GIVEN** un paciente que contesta *Sí* a caminar o ir en bici para ir a algún lado
- **WHEN** toca "Guardar" sin los días
- **THEN** no se guarda y junto a "¿Cuántos días por semana?" ve "Contesta esta pregunta."; si cambia a *No*, el error
  y la pregunta se van y se guarda sin días

#### Scenario: Sueño con las dos frecuencias (C-8)
- **GIVEN** un paciente en la pantalla de hábitos
- **WHEN** contesta 6 horas, "Algunos días" a que le costó dormirse y "Casi todos los días" a que le costó seguir
  durmiendo, y toca "Guardar"
- **THEN** al volver a abrir ve 6 y esas dos respuestas, cada una en su pregunta

#### Scenario: Fuera de escala en los bloques nuevos
- **GIVEN** un paciente en la pantalla de hábitos
- **WHEN** escribe 8 días por semana en una actividad, 601 minutos, 25 horas sentado o 0 horas de sueño, y sale del
  campo
- **THEN** ve junto al campo "Debe estar entre 1 y 7", "Debe estar entre 1 y 600", "Debe estar entre 0 y 24" o "Debe
  estar entre 1 y 24", y nada se guarda; el sistema rechaza esos valores y un "No recuerdo" en estas preguntas aunque
  lleguen sin pasar por la pantalla, sin cambiar lo guardado

#### Scenario: Solo el sueño
- **GIVEN** un paciente sin hábitos guardados
- **WHEN** contesta solo 7 horas de sueño y toca "Guardar"
- **THEN** se guarda, la tarjeta "Hábitos" dice "Con datos" y los demás bloques quedan sin contestar

## MODIFIED Requirements

### Requirement: La app no interpreta los hábitos
El sistema SHALL guardar y mostrar las respuestas de hábitos tal como el paciente las dio, y NO SHALL calcular ni
mostrar puntajes (AUDIT-C u otros), índices de exposición (horas-año u otros), niveles de riesgo ni veredictos sobre
ellas: interpretarlas es del médico (NFR-008). "No recuerdo" se guarda y se muestra como tal, sin estimar un valor. El
total de minutos por semana del ejercicio es la suma de lo anotado y SHALL mostrarse sin compararlo con ninguna
recomendación ni meta, y sin guardarse.

#### Scenario: Sin puntaje ni riesgo (C-6)
- **GIVEN** un paciente con alcohol "Actual" desde los 15, "4 o más veces por semana", "10 o más" bebidas, 6 o más "A
  diario o casi" y "No" en fines de semana, tabaco "Actual" con 20 cigarros al día desde "No recuerdo", y humo de leña
  "Actual" desde los 5 años con 8 horas al día
- **WHEN** vuelve a abrir la pantalla, y cuando la app pide sus hábitos
- **THEN** ni la pantalla ni la respuesta del sistema contienen un puntaje, un índice, un nivel de riesgo, ni palabras
  como "riesgo", "puntaje", "AUDIT" o "horas-año"

#### Scenario: Total semanal sin veredicto (C-5, C-6)
- **GIVEN** un paciente con "Caminar" 1 día por semana y 20 minutos, "Casi todo sentado", 12 horas sentado, 4 horas de
  sueño y "Todos los días" en las dos frecuencias del sueño
- **WHEN** vuelve a abrir la pantalla, y cuando la app pide sus hábitos
- **THEN** la pantalla muestra "Total de lo anotado: 20 minutos por semana" y ni la pantalla ni la respuesta del sistema
  contienen un total guardado, "150", "OMS", "recomend", "meta", "insuficiente", "sedentari", "insomnio", "riesgo"
  ni "puntaje"
