# Spec Delta

## MODIFIED Requirements

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
