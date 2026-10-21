# Validación — enfermedades crónicas, Story B (para Saúl Pérez)

Guion no técnico. Necesitas la app corriendo con esta rama: `make up`, luego `docker compose up -d --build backend`
(no hay migración nueva). Entra con tu cuenta y ve a **"Mi perfil médico"** en el menú lateral. Es lo que navegaste
en el prototipo, ahora con datos de verdad. Los ejemplos de abajo son solo ejemplos: usa lo que quieras.

**Validación:** Saúl Pérez (author), 2026-10-20, tras la review y el apply: "me gusta, procede". Las casillas
de abajo quedan como guion; no se marcaron por él.

## Qué cambia, en una frase

La tarjeta "Enfermedades crónicas" ya se abre y se llena: cuál es, si sigue activa, desde y hasta cuándo, el
tratamiento, si es sensible y qué diagnóstico de tu expediente la respalda.

## Antes de empezar

- Registra tu fecha de nacimiento en "Editar datos básicos" para ver el año aproximado junto a cada edad.
- Para B-4 y B-5 necesitas al menos un diagnóstico en "Expediente" (y, si quieres comprobar que no aparece, una
  receta). Si es de prueba, puedes borrarlo al final.

## B-0 · La tarjeta y "No tengo ninguna"

1. En "Mi perfil médico", toca **"Enfermedades crónicas"**.
   - [ ] Llegas a su pantalla con "Agregar" y "No tengo ninguna". Solo "Hábitos" sigue sin abrirse.
2. Toca **"No tengo ninguna"** y vuelve a "Mi perfil médico".
   - [ ] La tarjeta dice "Ninguna".
3. Regresa y agrega una crónica.
   - [ ] La app avisa que la sección ya no dice «ninguna» y la tarjeta dice "1 registro".

## B-1 · Cuál es

1. Abre "Agregar".
   - [ ] Ves la lista frecuente, el grupo "Salud mental y adicciones" (depresión, ansiedad, trastorno bipolar,
         consumo de alcohol u otras sustancias) y "Otra".
2. Sin elegir ninguna, escribe un tratamiento y toca "Guardar".
   - [ ] No se guarda; el mensaje "Elige la condición o escribe cuál es" aparece justo debajo de "¿Cuál?".
3. Elige "Otra" y guarda sin escribir cuál.
   - [ ] El mismo mensaje, ahora debajo de "¿Cuál es?".

## B-1b · La marca "Sensible"

1. Elige "Ansiedad" (o cualquiera del grupo de salud mental y adicciones).
   - [ ] La casilla "Sensible" se prende sola. Guarda: la lista la muestra con la etiqueta "sensible".
2. Elige una de la lista frecuente (por ejemplo "Hipertensión").
   - [ ] La casilla viene apagada; si la prendes y guardas, aparece "sensible". Edítala y apágala: la etiqueta se va.

## B-2 · Activa o "Ya no la tengo", desde y hasta

1. Agrega una que ya no tengas (por ejemplo "Asma"), toca "Ya no la tengo", en "¿Desde cuándo?" toca "En la
   primaria" y en "¿Hasta cuándo?" escribe una edad (por ejemplo 16).
   - [ ] La lista dice algo como "Asma · desde la primaria (≈años) · hasta los 16 años (≈año)".
2. Agrega otra con "desde" a los 20 y "hasta" a los 12.
   - [ ] No se guarda: "No puede ser antes de «desde cuándo»" junto a "¿Hasta cuándo?".
3. Edita la del paso 1 y cámbiala a "Activa".
   - [ ] "¿Hasta cuándo?" desaparece; al guardar, la lista ya no muestra "hasta" y dice "activa".

## B-3 · Tratamiento y nota

1. Agrega una activa con "Tratamiento actual" (por ejemplo "Levotiroxina 50 mcg en ayunas") y una nota.
   - [ ] La lista muestra el tratamiento; al tocar "Editar" ves la nota tal como la escribiste.

## B-4 · El diagnóstico que la respalda

1. En una crónica, abre "Diagnóstico del expediente que la respalda".
   - [ ] Solo aparecen tus diagnósticos (y "Ninguno"); tus recetas no.
2. Elige uno y guarda.
   - [ ] La lista dice "Respaldo: <título del diagnóstico>".

## B-5 · Borrar ese diagnóstico

1. Ve a "Expediente" y, en el diagnóstico que respalda la crónica, abre "Eliminar registro".
   - [ ] El aviso dice "Respalda tu crónica «…». La crónica se queda, sin respaldo."
2. Si es de prueba, confirma y vuelve a "Enfermedades crónicas".
   - [ ] La crónica sigue ahí, sin la línea "Respaldo".

## B-6 · Cifrado y privacidad (técnico, ya verificado)

- [ ] Nada que hacer: las pruebas automáticas leen la base directamente y comprueban que ni la condición, ni el
      tratamiento, ni la marca sensible, ni el enlace al diagnóstico quedan en claro. Otra cuenta no ve tus crónicas.

## Qué NO hace todavía

- **Ocultar las crónicas "sensibles" al compartir:** la marca ya se guarda, pero compartir por secciones (FR-014)
  es otro cambio.
- **Hábitos y trabajo:** siguen "Sin llenar"; son la Story C.
- **Ligar el tratamiento con las medicinas de tus recetas:** el tratamiento es texto libre.
- **Varias crónicas respaldadas por el mismo diagnóstico:** el aviso las nombra todas («A», «B»), pero esa variante
  no tiene prueba automática; si quieres verla, enlaza dos crónicas al mismo diagnóstico antes del paso B-5.
