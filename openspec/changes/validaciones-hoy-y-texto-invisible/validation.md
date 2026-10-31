# Validación — fecha de nacimiento y textos invisibles

Para: Saúl Pérez. Unos 5 minutos en http://localhost:8000 con una cuenta de prueba (no la tuya), después de
`make up`.

## 1 · Un «¿Cuál fue?» que no se ve no se guarda
1. Entra a «Mi perfil médico» → «Enfermedades pasadas e infecciosas» → «Agregar». Elige «Otra».
2. En «¿Cuál fue?» pega este texto, que parece vacío pero no lo está: copia lo que hay entre los corchetes [​] (sin los
   corchetes): es un espacio de ancho cero.
3. Toca «Guardar».
- [ ] La caja «¿Cuál fue?» se pone en rojo y dice «Elige la condición o escribe cuál fue».
- [ ] No aparece ningún registro nuevo.
4. Escribe «Zika» en la misma caja y guarda.
- [ ] Aparece «Zika» en la lista.

## 2 · La fecha de nacimiento usa el día de México
Esto solo se nota de noche: entre las 18:00 y las 24:00 de Ciudad de México.
1. En ese horario, en «Datos básicos», pon como fecha de nacimiento la de **mañana**.
- [ ] Sale «La fecha de nacimiento no puede estar en el futuro» (antes, a esa hora, se aceptaba).
2. Pon la de **hoy**.
- [ ] Se guarda.

## Lo que NO hace todavía
- Otros formularios del perfil (datos básicos, antecedentes familiares, trabajo, la bienvenida) todavía aceptan un
  texto invisible como si fuera algo. Quedó anotado.
- La edad que muestra la web se calcula con la fecha de tu aparato, no con la de México (otra deuda de la web).

## Decisiones tomadas por delegación (corrígelas si no te late)
- Un texto invisible en un campo requerido del historial se **rechaza** con el mensaje de siempre; no se borra en
  silencio.
- La regla de «qué cuenta como vacío» es la misma que ya usaba la pantalla de hábitos, ahora compartida.
