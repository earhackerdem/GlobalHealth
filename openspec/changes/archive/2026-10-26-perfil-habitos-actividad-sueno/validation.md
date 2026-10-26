# Validación — ejercicio, movimiento del día y sueño (para Saúl Pérez)

Guion no técnico. Necesitas la app corriendo con esta rama, en este orden: `docker compose build backend` y luego
`make up`. Entra con una cuenta de prueba (no la tuya real) y ve a **"Mi perfil médico" → "Hábitos"**. Los tres
bloques nuevos están debajo de "Humo de leña".

## Qué cambia, en una frase

El cuestionario de hábitos suma qué ejercicio haces (cada actividad con sus días y minutos, y el total de lo anotado),
cómo se mueve tu día y cómo duermes, con las mismas reglas de "Guardar" que el resto y sin ninguna calificación.

## C-5 · Ejercicio
- [ ] Bajo "¿Qué ejercicio haces?" veo los chips Caminar · Correr · Bicicleta · Nadar · Pesas o gimnasio · Fútbol u otro
  deporte · Yoga o pilates · Baile · Otra · No hago ejercicio. Puedo elegir varios.
- [ ] Elijo "Caminar" con 5 días por semana y 30 minutos cada vez, y "Pesas o gimnasio" con 2 y 45: mientras escribo,
  abajo dice "Total de lo anotado: 240 minutos por semana".
- [ ] Guardo y vuelvo a abrir: veo las dos actividades con sus números y el mismo total.
- [ ] Elijo "Otra" con 1 día y 90 minutos y toco "Guardar" sin escribir cuál: no se guarda, junto a "¿Cuál?" dice
  "Escribe cuál." y el cursor queda ahí. Escribo "Senderismo", guardo y al volver a abrir lo veo.
- [ ] Elijo "Correr" con 3 días y sin minutos, y "Guardar": junto a los minutos de correr dice "Contesta esta
  pregunta.". Ninguna pregunta del ejercicio tiene "No recuerdo".
- [ ] Con actividades guardadas, elijo "No hago ejercicio": se desmarcan los chips de actividades y se quitan sus
  números y el total.
  Guardo y al volver a abrir solo está "No hago ejercicio".

## C-7 · Movimiento del día, aparte del ejercicio
- [ ] Veo "En tu trabajo o actividad principal (casa, escuela…), ¿cómo pasas el día?" con 4 opciones, de "Casi todo
  sentado" a "Trabajo pesado o cargando cosas pesadas".
- [ ] Con "Caminar" 5×30 (total 150), contesto "Casi todo sentado", *Sí* a caminar o ir en bici al menos 10 minutos
  para ir a algún lado con 5 días, y 9 horas sentado: el total sigue en 150. Al guardar y volver a abrir veo las tres
  respuestas.
- [ ] Con *Sí* y sin días, "Guardar" no guarda y junto a "¿Cuántos días por semana?" dice "Contesta esta pregunta.".
  Si cambio a *No*, la pregunta y el mensaje se van y se guarda.
- [ ] Bajo las horas sentado dice "Sin contar el tiempo que duermes.".

## C-8 · Sueño
- [ ] Veo "En promedio, ¿cuántas horas duermes en un día?" con la ayuda "Cuenta las siestas. Si son 6 y media, escribe
  7.".
- [ ] Contesto 6 horas, "Algunos días" a que te costó dormirte y "Casi todos los días" a que te costó seguir durmiendo.
  Al guardar y volver a abrir, cada respuesta está en su pregunta.
- [ ] Contesto solo 7 horas de sueño en una cuenta sin hábitos: se guarda y la tarjeta "Hábitos" dice "Con datos".

## Fuera de escala, y el error que se va al corregir
- [ ] Al salir del campo: 8 días dice "Debe estar entre 1 y 7"; 601 minutos, "Debe estar entre 1 y 600"; 25 horas
  sentado, "Debe estar entre 0 y 24"; 0 horas de sueño, "Debe estar entre 1 y 24". Con eso, "Guardar" no guarda.
- Que las **dos** cajas marquen su error al dejarlas seguidas (25 horas sentado, clic en las horas de sueño, 0 y salir
  enseguida; esto fallaba y lo arreglé durante la exploración) no se ve a mano: a mano el clic termina antes de salir
  de la segunda caja, y el defecto no aparece. Lo revisa la prueba automática de C-14 de dos cajas (commit 641e976).
- [ ] Vuelvo a una caja con error y corrijo el número: el mensaje se va sin salir del campo.

## C-6 · Sin calificación
- [ ] Con "Caminar" 1×20, "Casi todo sentado", 12 horas sentado, 4 de sueño y "Todos los días" en las dos del sueño:
  dice "Total de lo anotado: 20 minutos por semana" y en ningún lado aparece una meta, "150", "OMS", "insuficiente",
  "sedentario", "insomnio", "riesgo" ni un puntaje.

## Lo de siempre, en los bloques nuevos
- [ ] Elegir una actividad cuenta como cambio: si salgo sin guardar, la app pregunta "¿Salir sin guardar?".
- [ ] Doble clic en "Guardar": se guarda una sola vez.
- Que los chips nuevos no respondan mientras dice "Guardando…" no se ve a mano: en tu computadora el guardado dura
  milisegundos. Lo revisa la prueba automática de la fila 12, que retiene el guardado.
- [ ] En el teléfono, los chips largos del día parten su texto y la pantalla no se mueve de lado.

## Lo que todavía NO hace
- **"Trabajo" en el Perfil básico** (C-9): es la C2b, el cambio siguiente.
- **No avisa de valores raros** (5 horas de sueño o menos, más de 4 horas de una actividad por vez, horas sentado más
  sueño que pasan de 24): se discutió y quedó fuera.
- **No separa el sueño de días laborales y libres**, ni distingue fuerza de aeróbico en el total.
- **No suma el desplazamiento al ejercicio** (a propósito: el médico lo lee aparte).
- **Una misma actividad dos veces al día** se anota como un solo día; los días por semana pueden quedarse cortos.
- **No hay vista para el médico** ni datos de relojes o apps de actividad.
