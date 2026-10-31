# Validación — fecha de nacimiento y textos invisibles

Para: Saúl Pérez. Unos 5 minutos en http://localhost:8000 con una cuenta de prueba (no la tuya), después de
`make up`.

## 1 · Un «¿Cuál fue?» que no se ve no se guarda
1. Entra a «Mi perfil médico» → «Enfermedades pasadas e infecciosas» → «Agregar». Elige «Otra».
2. Copia el hueco que hay entre las dos flechas, sin las flechas: →ㅤ←. Parece un espacio, pero es un «relleno»
   invisible. Pégalo en «¿Cuál fue?».
3. Toca «Guardar».
- [ ] La caja «¿Cuál fue?» se pone en rojo y dice «Elige la condición o escribe cuál fue».
- [ ] No aparece ningún registro nuevo.
4. Escribe «Zika» en la misma caja, sin borrar lo que pegaste, y guarda.
- [ ] Aparece «Zika» en la lista.

## 2 · Un «cuándo» invisible no cuenta como dato
1. En «Transfusiones» → «Agregar», pega el mismo hueco en «Edad que tenías» y guarda sin llenar nada más.
- [ ] Dice «Llena al menos un dato» (antes decía que escribieras solo el número).

## 3 · La fecha de nacimiento usa el día de México (opcional; necesitas cambiar la zona horaria de la Mac)
Solo se nota cuando tu aparato y Ciudad de México están en días distintos.
1. En Ajustes del Sistema → General → Fecha y hora, pon la zona de Tokio. Recarga la página.
2. Entre las 09:00 y las 24:00 de Ciudad de México (ya es «mañana» en Tokio), abre «Editar datos básicos» y escribe
   como fecha de nacimiento la de **mañana en México**.
- [ ] Sale «La fecha de nacimiento no puede ser futura».
3. Escribe la de **hoy en México**.
- [ ] No sale el mensaje. Al terminar, regresa la zona horaria a Ciudad de México.

## Lo que NO hace todavía
- Otros formularios del perfil (datos básicos, antecedentes familiares, trabajo, la bienvenida) todavía guardan un
  texto invisible como si fuera algo. Quedó anotado.
- La edad que muestra la web se calcula con la fecha de tu aparato (otra deuda de la web).

## Decisiones tomadas por delegación (corrígelas si no te late)
- Un texto invisible en el historial se **rechaza** con el mensaje de siempre; no se borra en silencio.
- «Invisible» es una sola regla para la API y para todas las pantallas: la de hábitos de antes, más las marcas que
  Unicode declara ignorables (la deuda C1, que se pagó aquí junto con B2).
