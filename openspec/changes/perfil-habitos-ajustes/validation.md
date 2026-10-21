# Validación — ajustes de hábitos (para Saúl Pérez)

Guion no técnico. Necesitas la app corriendo con esta rama, en este orden: `docker compose build backend` y luego
`make up`. Entra con una cuenta de prueba (no la tuya real) que ya tenga fecha de nacimiento, y ve a **"Mi perfil
médico" → "Hábitos"**. Los ejemplos suponen a alguien de 36 años; cambia las edades si tu cuenta tiene otra.

## Qué cambia, en una frase

Alcohol, vapeador y leña preguntan desde cuándo (y cuánto, en vapeador y leña); los errores aparecen al salir de cada
campo; se guarda con "Guardar", y si intentas salir con cambios sin guardar, la app te pregunta antes.

## C-10 · Alcohol, desde cuándo
- [ ] Con "Lo dejé" y con "Actual" aparece "¿A qué edad empezaste a tomar?" con la ayuda "Sin contar probaditas.".
- [ ] Con "Lo dejé", inicio 30 y fin 18: al salir del campo veo "No puede ser mayor que la edad en que lo dejaste"
  junto a la edad de inicio.
- [ ] Con 17 y 30 toco "Guardar"; al volver a abrir siguen 17 y 30.

## C-11 · Vapeador
- [ ] Con "Actual" aparecen la edad de inicio y "¿Con qué frecuencia vapeas?" (Todos los días · Algunos días).
- [ ] Con "Algunos días" aparece "¿Cuántos días de los últimos 30?"; con "Todos los días" desaparece.
- [ ] Con 31 días veo "Debe estar entre 1 y 30"; con 12 y "Guardar", al volver a abrir sigue 12.
- [ ] Con "Antes" veo la edad de inicio y la de fin, sin la frecuencia.

## C-12 · Humo de leña
- [ ] Con "Antes" veo "¿A qué edad empezaste a exponerte?", "¿A qué edad dejaste de exponerte?" y "¿Cuántas horas al
  día, en promedio?"; con "Actual", sin la edad de fin. Ya no aparece "Años con humo de leña".
- [ ] Con 25 horas veo "Debe estar entre 1 y 24"; con 3 y "Guardar", al volver a abrir sigue 3.
- [ ] En ningún lado aparece un cálculo con esos datos (ni "horas-año" ni un "riesgo").

## C-13 · Se guarda con "Guardar" y avisa antes de perderse
- [ ] Arriba de las preguntas dice "Tus respuestas se guardan cuando tocas «Guardar»."
- [ ] Elijo tabaco "Actual", escribo 12 cigarros y, sin salir del campo, toco "‹ Mi perfil médico": aparece "¿Salir sin
  guardar?". Con "Seguir editando" sigo en la pantalla con "Actual" y 12.
- [ ] Lo mismo con el botón de atrás del navegador y con el menú. Con "Salir sin guardar" vuelvo a "Mi perfil médico"
  y, al abrir, el tabaco está como antes.
- [ ] Con un cambio sin guardar recargo la página: el navegador me pregunta si quiero salir. Sin cambios, no pregunta.
- [ ] Abro la pantalla y salgo sin tocar nada (o elijo una opción y vuelvo a la de antes): no pregunta nada.
- [ ] Con un cambio sin guardar, cierro sesión en otra pestaña: esta va a "Iniciar sesión" sin preguntar.
- [ ] Toco "Guardar" varias veces seguidas: se guarda una sola vez y vuelvo a "Mi perfil médico" con "Hábitos
  guardados". Mientras dice "Guardando…", "Guardar", "Cancelar" y las preguntas no responden, y salir no pregunta.
- [ ] Cambio algo y toco "Cancelar": vuelvo con "Se descartaron los cambios", sin pregunta, y al abrir todo está como
  antes. Sin cambios, "Cancelar" solo me regresa.

## C-14 · Errores al momento
- [ ] Cada error aparece junto a su campo al salir de él, sin esperar a "Guardar"; con un error, "Guardar" no guarda
  y me lleva al campo marcado.
- [ ] Con 101 cigarros marcados, cambiar el tabaco a "Antes" no quita la marca de los cigarros.

## Lo que ya tenías
- [ ] Si guardaste hábitos antes de este cambio, se siguen viendo: el vapeador con su respuesta (sin frecuencia ni
  edades) y la leña sin los "años" (se piden ahora como edades).
- [ ] Cambiar de cuenta en otra pestaña sigue sacando a esta pestaña de tus hábitos.

## Lo que todavía NO hace
- No guarda solo: lo que no guardaste se pierde si el navegador cierra la pestaña sin preguntar (en el celular puede
  pasar con la app en segundo plano).
- El aviso de cambios sin guardar y el bloqueo del doble clic solo están en hábitos; revisarlos en el resto de la app
  está en la tarea de deudas (decisión D20).
- No calcula horas-año ni ningún puntaje: interpretarlo es del médico.
- Ejercicio, movimiento del día, sueño y trabajo (Story C2).
