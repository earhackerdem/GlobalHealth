# Validación — ajustes de hábitos (para Saúl Pérez)

Guion no técnico. Necesitas la app corriendo con esta rama, en este orden: `docker compose build backend` y luego
`make up`. Entra con una cuenta de prueba (no la tuya real) que ya tenga fecha de nacimiento, y ve a **"Mi perfil
médico" → "Hábitos"**. Los ejemplos suponen a alguien de 36 años; cambia las edades si tu cuenta tiene otra.

## Qué cambia, en una frase

Alcohol, vapeador y leña preguntan desde cuándo (y cuánto, en vapeador y leña); todo se guarda solo mientras
contestas, y "Guardar" y "Cancelar" siguen ahí, desactivados mientras se guarda.

## C-10 · Alcohol, desde cuándo
- [ ] Con "Lo dejé" y con "Actual" aparece "¿A qué edad empezaste a tomar?" con la ayuda "Sin contar probaditas.".
- [ ] Con "Lo dejé", inicio 30 y fin 18: al salir del campo veo "No puede ser mayor que la edad en que lo dejaste"
  junto a la edad de inicio, y arriba "Sin guardar: corrige el campo marcado".
- [ ] Con 17 y 30, arriba dice "Guardado"; al recargar la página siguen 17 y 30.

## C-11 · Vapeador
- [ ] Con "Actual" aparecen la edad de inicio y "¿Con qué frecuencia vapeas?" (Todos los días · Algunos días).
- [ ] Con "Algunos días" aparece "¿Cuántos días de los últimos 30?"; con "Todos los días" desaparece.
- [ ] Con 31 días veo "Debe estar entre 1 y 30"; con 12 se guarda.
- [ ] Con "Antes" veo la edad de inicio y la de fin, sin la frecuencia.

## C-12 · Humo de leña
- [ ] Con "Antes" veo "¿A qué edad empezaste a exponerte?", "¿A qué edad dejaste de exponerte?" y "¿Cuántas horas al
  día, en promedio?"; con "Actual", sin la edad de fin. Ya no aparece "Años con humo de leña".
- [ ] Con 25 horas veo "Debe estar entre 1 y 24"; con 3 se guarda.
- [ ] En ningún lado aparece un cálculo con esos datos (ni "horas-año" ni un "riesgo").

## C-13 · Se guarda solo
- [ ] Elijo una opción y, sin tocar "Guardar", me voy a "Mi perfil médico" desde el menú: la tarjeta dice "Con datos"
  y al abrirla está lo que elegí.
- [ ] Escribo un número y, sin salir del campo, toco "‹ Mi perfil médico": al volver a abrir, el número está.
- [ ] Mientras dice "Guardando…", "Guardar" y "Cancelar" están desactivados. Si toco "Guardar" varias veces seguidas
  justo después de cambiar algo, se guarda una sola vez y vuelvo a "Mi perfil médico" con "Hábitos guardados".
- [ ] Cambio algo (se guarda solo) y toco "Cancelar": vuelvo con "Se descartaron los cambios" y, al abrir, todo está
  como antes de entrar.

## C-14 · Errores al momento
- [ ] Cada error aparece junto a su campo al salir de él, sin esperar a "Guardar", y mientras hay uno nada se guarda.

## Lo que ya tenías
- [ ] Si guardaste hábitos antes de este cambio, se siguen viendo: el vapeador con su respuesta (sin frecuencia ni
  edades) y la leña sin los "años" (se piden ahora como edades).
- [ ] Cambiar de cuenta en otra pestaña sigue sacando a esta pestaña de tus hábitos.

## Lo que todavía NO hace
- El guardado automático y el bloqueo del doble clic solo están en hábitos; revisarlos en el resto de la app está en
  la tarea de deudas (decisión D20).
- No calcula horas-año ni ningún puntaje: interpretarlo es del médico.
- Lo que tenga un error al salir de la pantalla no se guarda (la pantalla lo avisa antes).
- Ejercicio, movimiento del día, sueño y trabajo (Story C2).
