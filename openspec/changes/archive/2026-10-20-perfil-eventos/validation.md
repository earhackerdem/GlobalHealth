# Validación — historial por secciones, Story A (para Saúl Pérez)

Guion no técnico. Necesitas la app corriendo (`make up`; si cambiaste de rama, `docker compose up -d --build
backend` y luego `make migrate`) y entrar con tu cuenta. Todo se hace desde **"Mi perfil médico"** en el menú
lateral. Es lo mismo que navegaste en el prototipo v4, ahora con datos de verdad.

## Qué cambia, en una frase

Las secciones de enfermedades pasadas, cirugías, fracturas y transfusiones ya se pueden llenar; cada tarjeta dice
cómo va, y "cuándo" se contesta con la edad que tenías.

## Antes de empezar

- Si ya tienes fecha de nacimiento en tu perfil, verás el año aproximado junto a cada edad; si no, solo la edad.
- Crónicas y hábitos siguen diciendo "Sin llenar" y no se abren: llegan con las Stories B y C.

## A-1 · Cada tarjeta dice cómo va

1. Abre "Mi perfil médico" y baja a **"Tu historial"**.
   - [x] Las seis tarjetas dicen "Sin llenar", y el texto de arriba dice "Crónicas y hábitos llegan pronto".
2. Toca **"Cirugías y hospitalizaciones"**.
   - [x] Llegas a la pantalla de cirugías con el botón "Agregar". Crónicas y hábitos no se dejan tocar.

## A-2 · "No he tenido ninguna"

1. En cirugías, toca **"No he tenido ninguna"**.
   - [x] La sección y su tarjeta en "Mi perfil médico" dicen "Ninguna".
2. Toca **"Deshacer"**.
   - [x] Vuelve a "Sin llenar".
3. En transfusiones, toca "Nunca me han transfundido" y luego agrega una transfusión.
   - [x] Aparece el aviso "Guardado. La sección ya no dice «ninguna»." y la tarjeta dice "1 registro".

## A-3 · "Cuándo" como lo pregunta el médico

1. Agrega una cirugía y en "¿Cuándo?" escribe tu edad de entonces (p. ej. 7).
   - [x] Debajo aparece "Año aproximado: …"; al guardar, la lista dice "a los 7 años (≈año)".
2. Agrega una enfermedad pasada y toca **"En la primaria"** en vez de escribir.
   - [x] La lista dice "en la primaria (≈año–año)".
3. En otra, toca **"o el año, si lo sabes"** y escribe un año.
   - [x] La lista dice "en <año>".
4. Con tu fecha de nacimiento ya registrada en "Editar datos básicos", prueba una edad mayor que la tuya, o un año
   antes de que nacieras. (Sin fecha de nacimiento la app no sabe tu edad: solo rechaza edades fuera de 0–130 y
   años antes de 1900 o futuros.)
   - [x] No se guarda y te dice por qué, en español.
5. Cambia tu fecha de nacimiento en "Editar datos básicos" y vuelve a la sección.
   - [x] El año aproximado cambió solo; la edad que contestaste sigue igual.

## A-4 · Enfermedades pasadas e infecciosas

1. Agrega "Varicela" (o elige "Otra" y escribe una que no esté en la lista).
   - [x] Puedes decir si requirió hospitalización (Sí / No / No sé), secuelas y una nota; solo la condición es
         obligatoria.

## A-5 · Cirugías y hospitalizaciones

1. Agrega una con todos sus datos: tipo, nombre, cuándo, motivo, hospital, médico, complicaciones, reacción a la
   anestesia (con detalle si fue "Sí") y material implantado.
   - [x] Al tocar "Editar" ves exactamente lo que escribiste.

## A-6 · Fracturas y lesiones

1. Agrega una fractura con lado "Izquierdo", "¿Requirió cirugía?" y material implantado.
   - [x] La lista muestra el lado y el implante.

## A-7 · Transfusiones y grupo sanguíneo

1. En transfusiones, toca tu grupo sanguíneo (o "No lo sé").
   - [x] Queda marcado; tocar otro lo corrige y tocar el mismo lo borra; sigue ahí al recargar.
2. Agrega una transfusión con motivo, qué te transfundieron y si hubo reacción.
   - [x] La lista la muestra con su año y motivo.

## A-8 · Es tuyo y se borra con confirmación

1. Toca "Eliminar" en un registro.
   - [x] Pide confirmar ahí mismo: "Cancelar" lo deja, "Sí, eliminar" lo quita.
2. Toca "Agregar" y "Guardar" sin llenar nada.
   - [x] No se guarda: "Llena al menos un dato".

## A-9 · Cifrado (técnico, no se clickea)

- [ ] Lo verificó una prueba automática que lee la base de datos directamente: ni el contenido, ni la sección,
      ni "ninguna", ni el grupo sanguíneo están en claro.

## Lo que NO hace todavía

- **Crónicas y hábitos** (con trabajo, movimiento del día y sueño): Stories B y C.
- **Compartir el historial con tu médico** (E3/E4): por ahora solo tú lo ves. La pantalla dice "El médico verá
  que lo respondiste", pero eso llegará con el compartir (lo marqué para el review).
- Fechas exactas: "cuándo" es edad, etapa o año, a propósito.
- Enlazar una fractura con su cirugía: se marca "¿Requirió cirugía?" y, si quieres, registras la cirugía aparte.

## Cómo reportar un problema

Comenta en el PR con el número del criterio (A-1…A-9) y una captura.
