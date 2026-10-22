# Validación — hábitos completos (para Saúl Pérez)

Guion no técnico. Necesitas la app corriendo con esta rama, en este orden: `docker compose build backend` y luego
`make up`. Entra con una cuenta de prueba (no la tuya real) que ya tenga fecha de nacimiento, y ve a **"Mi perfil
médico" → "Hábitos"**. Los ejemplos suponen a alguien de 36 años; cambia las edades si tu cuenta tiene otra.

## Qué cambia, en una frase

Cuando eliges una respuesta que abre más preguntas, "Guardar" te pide contestarlas; en lo que ya pasó (edades, y
cigarros u horas de leña de "Antes") puedes marcar "No recuerdo"; y un error se va en cuanto corriges el dato.

## La introducción
- [ ] Arriba dice: "Contesta los hábitos que quieras. Si eliges una respuesta, completa sus preguntas; si no recuerdas
  un dato del pasado, marca «No recuerdo». «Nunca» también le sirve a tu médico. La app no califica tus respuestas."

## C-15 · Lo que abre una respuesta se contesta
- [ ] Alcohol "Lo dejé", solo 30 en "¿A qué edad dejaste de tomar?" y "Guardar": no se guarda; junto a la edad de inicio
  dice "Contesta esta pregunta o marca «No recuerdo»." y el cursor queda ahí.
- [ ] Alcohol "Actual" con 18 de inicio y "Guardar": bajo "¿Con qué frecuencia tomas?", "Sobre todo fines de semana",
  "¿cuántas bebidas?" y "6 o más" dice "Contesta esta pregunta.". Ninguna de esas cuatro tiene "No recuerdo".
- [ ] Al contestar una de ellas, su mensaje se va. Si cambio a "Nunca", se van todos y se guarda.
- [ ] Tabaco "Actual" sin cigarros y "Guardar": junto a "Cigarros al día" dice "Contesta esta pregunta.".
- [ ] Si "Nunca" o no contesto un hábito, "Guardar" no me pide nada de ese hábito.

## C-16 · "No recuerdo" solo en lo que pasó
- [ ] Con tabaco "Actual", "Cigarros al día" no tiene "No recuerdo" y la edad de inicio sí. Con "Antes", los cigarros,
  la edad de inicio y la de fin lo tienen. Igual con las horas de leña.
- [ ] Alcohol "Lo dejé": marco "No recuerdo" en la edad de inicio (si había un número, se borra), 18 en la de fin y
  "Guardar": se guarda sin error. Al volver a abrir, "No recuerdo" sigue marcado y el 18 sigue ahí.
- [ ] Con "No recuerdo" marcado, escribo 16 en ese campo: "No recuerdo" se desmarca. Al guardar y volver a abrir veo 16.
- [ ] Marcar "No recuerdo" cuenta como cambio: si salgo sin guardar, la app pregunta "¿Salir sin guardar?".
- [ ] Mientras dice "Guardando…", "No recuerdo" tampoco responde.

## C-17 · El error se va al corregirlo (lo de tu captura)
- [ ] Escribo "12a" en una edad y salgo del campo: "Escribe solo el número.". Vuelvo al campo y borro la "a": el mensaje
  se va sin tener que salir.
- [ ] Escribo 101 en "Cigarros al día" y salgo: "Debe estar entre 1 y 100". Vuelvo y borro todo: el mensaje se va.
- [ ] Mientras escribo en un campo limpio no aparece ningún error; aparece solo al salir del campo.

## Lo guardado antes, a medias
- [ ] Si una cuenta de prueba tenía un hábito guardado a medias (de antes de este cambio), la pantalla abre sin errores
  y "Guardar" marca lo que falta.

## Lo que NO hace todavía
- No hay "Prefiero no responder"; para no contestar un hábito, déjalo sin elegir.
- Después de "No recuerdo" no pregunta una "mejor estimación" (por ejemplo, "antes de los 18").
- Tu médico todavía no tiene una vista propia de estas respuestas.
- La Story C2 (ejercicio, movimiento del día, sueño, trabajo) sigue pendiente.
