# Spec Delta

## MODIFIED Requirements

### Requirement: Hábitos: sustancias y humo
El perfil SHALL guardar los hábitos del paciente como un solo cuestionario, en el que cada respuesta es opcional y
se guarda lo que haya contestado:
- **alcohol:** *Nunca*, *Lo dejé* o *Actual*. Con *Lo dejé* o *Actual*, a qué edad empezó a tomar (sin contar
  probaditas); con *Lo dejé*, además, a qué edad lo dejó. Si es *Actual*, las tres preguntas del AUDIT-C con su
  escala: con qué frecuencia toma (una vez al mes o menos · 2 a 4 veces al mes · 2 a 3 veces por semana · 4 o más
  veces por semana), cuántas bebidas en un día que toma (1 o 2 · 3 o 4 · 5 o 6 · 7 a 9 · 10 o más), cada cuándo toma
  6 o más en una sola ocasión (nunca · menos de una vez al mes · cada mes · cada semana · a diario o casi), y si toma
  sobre todo en fines de semana (Sí · No);
- **tabaco:** *Nunca*, *Antes* o *Actual*, con cigarros al día (1 a 100), a qué edad empezó y, si es *Antes*, a qué
  edad lo dejó;
- **vapeador o cigarro electrónico:** *Nunca*, *Antes* o *Actual*. Con *Antes* o *Actual*, a qué edad empezó; con
  *Antes*, a qué edad lo dejó. Con *Actual*, si lo usa todos los días o algunos días, y con *Algunos días*, cuántos
  días de los últimos 30 (1 a 30);
- **humo de tabaco de otras personas:** dónde (casa · trabajo o escuela · otro lugar, uno o varios) con los días por
  semana (1 a 7), o "No me expongo";
- **humo de leña o carbón:** *Nunca*, *Antes* o *Actual*. Con *Antes* o *Actual*, a qué edad empezó la exposición y
  cuántas horas al día en promedio (1 a 24); con *Antes*, a qué edad terminó.

Al guardar, el sistema SHALL descartar lo que no aplica a la respuesta elegida: las preguntas del AUDIT-C y la marca
de fines de semana si el alcohol no es *Actual*; las edades si el alcohol, el tabaco, el vapeador o la leña son
*Nunca*; la edad en que lo dejó o terminó si no es *Lo dejé* o *Antes*; los cigarros si el tabaco es *Nunca*; la
frecuencia del vapeador si no es *Actual*, y los días de los últimos 30 si no es *Algunos días*; las horas si la leña
es *Nunca*; los lugares y los días si no se expone. El sistema SHALL rechazar, con el mensaje junto a su campo, una
edad mayor que la edad actual del paciente, una edad fuera de 0 a 130, y una edad de inicio mayor que la edad en que
lo dejó o terminó, en el alcohol, el tabaco, el vapeador y la leña. Sin fecha de nacimiento SHALL aceptar cualquier
edad entre 0 y 130.

Los hábitos guardados antes de este cambio SHALL seguir leyéndose: el vapeador conserva su *Nunca*, *Antes* o
*Actual*, y los años aproximados de la leña se descartan (no se pueden convertir a edades).

#### Scenario: Alcohol actual con las preguntas del AUDIT-C (C-1)
- **GIVEN** un paciente nacido el 15/03/1990, sin hábitos guardados
- **WHEN** elige alcohol "Actual", "2 a 3 veces por semana", "3 o 4" bebidas, 6 o más "Cada mes", "Sí" en "Sobre
  todo fines de semana"
- **THEN** la tarjeta "Hábitos" dice "Con datos" y, al volver a abrir la pantalla, esas cinco respuestas siguen
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
- **GIVEN** un paciente que eligió alcohol "Actual", con edad de inicio, y contestó las tres preguntas del AUDIT-C
- **WHEN** cambia a "Nunca"
- **THEN** al volver a abrir la pantalla ve "Nunca" sin edad ni preguntas del AUDIT-C, y el perfil guardado no
  conserva esas respuestas

#### Scenario: Tabaco que dejó, y vapeador actual (C-2)
- **GIVEN** un paciente nacido el 15/03/1990
- **WHEN** elige tabaco "Antes" con 10 cigarros al día, empezó a los 18 y lo dejó a los 30, y vapeador "Actual" con
  "Todos los días"
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
- **GIVEN** un paciente con vapeador "Actual", "Algunos días" y 12 días
- **WHEN** elige "Todos los días"; después cambia a "Antes" y escribe que empezó a los 25 y lo dejó a los 28
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
  de vapeador, 0 o 25 horas al día de leña, una edad de 131, o una opción que no está en la escala
- **THEN** el sistema lo rechaza y los hábitos guardados no cambian

#### Scenario: Lo guardado antes de este cambio se sigue leyendo
- **GIVEN** un paciente que guardó con la versión anterior vapeador "Actual" y humo de leña "Antes" con 12 años, más
  tabaco "Antes"
- **WHEN** abre su pantalla de hábitos
- **THEN** ve vapeador "Actual" sin frecuencia ni edades, leña "Antes" sin edades ni horas, y su tabaco igual que
  antes; ninguna respuesta se pierde salvo los años de leña

### Requirement: La app no interpreta los hábitos
El sistema SHALL guardar y mostrar las respuestas de hábitos tal como el paciente las dio, y NO SHALL calcular ni
mostrar puntajes (AUDIT-C u otros), índices de exposición (horas-año u otros), niveles de riesgo ni veredictos sobre
ellas: interpretarlas es del médico (NFR-008).

#### Scenario: Sin puntaje ni riesgo (C-6)
- **GIVEN** un paciente con alcohol "Actual", "4 o más veces por semana", "10 o más" bebidas y 6 o más "A diario o
  casi", tabaco "Actual" con 20 cigarros al día, y humo de leña "Actual" desde los 5 años con 8 horas al día
- **WHEN** vuelve a abrir la pantalla, y cuando la app pide sus hábitos
- **THEN** ni la pantalla ni la respuesta del sistema contienen un puntaje, un índice, un nivel de riesgo, ni palabras
  como "riesgo", "puntaje", "AUDIT" o "horas-año"

## ADDED Requirements

### Requirement: Los hábitos se guardan solos
La pantalla de hábitos SHALL guardar cada respuesta sin esperar a un botón: una opción al elegirla y un número al
salir de su campo, siempre que todo el cuestionario sea válido. Mientras haya un campo con error SHALL no guardar nada
y decirlo. La pantalla SHALL mostrar en un mensaje de estado, sin mover el foco, si está guardando, si ya guardó o qué
falta corregir. "Guardar" SHALL mandar lo pendiente y volver a "Mi perfil médico"; "Cancelar" SHALL dejar los hábitos
como estaban al abrir la pantalla y volver. Los dos botones SHALL estar desactivados mientras se guarda, para que un
doble clic no mande dos veces lo mismo.

#### Scenario: Una respuesta se guarda al elegirla (C-13)
- **GIVEN** un paciente con la pantalla de hábitos abierta y nada guardado
- **WHEN** elige tabaco "Nunca" y, sin tocar "Guardar", vuelve a "Mi perfil médico" desde el menú
- **THEN** la tarjeta "Hábitos" dice "Con datos" y, al abrirla, ve tabaco "Nunca"

#### Scenario: Un número se guarda al salir de su campo (C-13)
- **GIVEN** un paciente con tabaco "Actual"
- **WHEN** escribe 12 en "Cigarros al día" y pasa al siguiente campo
- **THEN** el mensaje de estado dice "Guardado" y, al recargar la página, ve 12

#### Scenario: Con un error no se guarda nada (C-13, C-14)
- **GIVEN** un paciente nacido el 15/03/1990, con vapeador "Nunca" guardado
- **WHEN** escribe 101 en "Cigarros al día", sale del campo, y después elige vapeador "Actual"
- **THEN** ve "Debe estar entre 1 y 100" junto a los cigarros y "Sin guardar: corrige el campo marcado" en el estado,
  sin que el sistema reciba nada; al recargar, el vapeador sigue en "Nunca"

#### Scenario: Botones desactivados mientras guarda (C-13)
- **GIVEN** un paciente que acaba de elegir una respuesta y la pantalla dice "Guardando…"
- **WHEN** intenta tocar "Guardar" o "Cancelar"
- **THEN** los dos están desactivados hasta que el estado dice "Guardado", y el sistema recibe un solo guardado

#### Scenario: Cancelar deja todo como al abrir (C-13)
- **GIVEN** un paciente con tabaco "Nunca" guardado, que abre la pantalla y cambia a tabaco "Actual" con 5 cigarros
  (ya guardado solo)
- **WHEN** toca "Cancelar"
- **THEN** vuelve a "Mi perfil médico" y, al abrir la pantalla, ve tabaco "Nunca"

### Requirement: Los errores se marcan al momento
Al salir de un campo numérico, la pantalla de hábitos SHALL marcar junto a él, sin preguntar al servidor, un valor que
no es un número entero, uno fuera de su escala, una edad mayor que la actual o una edad de inicio mayor que la de fin.
Los límites de cada número SHALL ser los mismos que publica el contrato del sistema.

#### Scenario: Fuera de escala al salir del campo (C-14)
- **GIVEN** un paciente con humo de leña "Actual"
- **WHEN** escribe 25 en "¿Cuántas horas al día, en promedio?" y sale del campo
- **THEN** ve "Debe estar entre 1 y 24" junto a ese campo, con el campo marcado como inválido, y el sistema no recibe
  ningún guardado
