# Validación — la app de Android: entrar y ver tu perfil

Para: Saúl Pérez, en tu S26 Ultra. Unos 15 minutos. Usa una cuenta de prueba, no la tuya.

## Antes de empezar (una vez)
1. Conecta el teléfono a la Mac con un cable de datos y acepta «¿Permitir la depuración por USB?».
2. En la Mac, con la API corriendo (http://localhost:8000):
   - `adb reverse tcp:8000 tcp:8000`
   - `cd android && ./gradlew assembleDebug -PapiBaseUrl=http://localhost:8000/api/v1/`
   - `adb install -r app/build/outputs/apk/debug/app-debug.apk`
3. Abre «GlobalHealth» en el teléfono.

## AB-1 · Abre en la entrada
- [ ] Ves «Correo electrónico», «Contraseña» y «Entrar», en español.

## AB-2 · Entrar
1. Escribe tu correo de prueba con una contraseña equivocada y toca «Entrar» dos veces seguidas.
- [ ] Ves «Correo o contraseña incorrectos» y sigues en la entrada.
2. Escribe la contraseña correcta y toca «Entrar».
- [ ] Llegas a «Mi perfil médico».

## AB-3 · Consentimiento
1. Crea en la web una cuenta nueva y **no** aceptes el consentimiento. Entra con ella en la app.
- [ ] La app te muestra el consentimiento («Versión v1») y ningún dato.
- [ ] «Acepto» te lleva al perfil.

## AB-4 · Tu perfil
- [ ] Ves tus datos básicos tal como en la web: fecha y edad, sexo, alergias, peso, estatura y trabajo.
- [ ] Ves cuántos antecedentes familiares hay y el estado de las seis secciones («Sin llenar», «Ninguna» o «N registros»).
- [ ] No hay nada que se pueda editar; abajo dice «Para editar, entra a la web».

## AB-5 · La sesión
- [ ] Cierra la app desde recientes y vuélvela a abrir: entras directo al perfil.
- [ ] «Cerrar sesión» te regresa a la entrada.

## AB-7 · Sin conexión
1. Con la sesión abierta, detén la API en la Mac (`docker compose stop backend`). El modo avión no sirve aquí: el
   cable de `adb reverse` sigue conectado. Cierra la app desde recientes y vuélvela a abrir.
- [ ] Ves «No pudimos conectar. Revisa tu conexión e intenta de nuevo.» y «Reintentar».
2. Vuelve a encender la API (`docker compose start backend`) y toca «Reintentar».
- [ ] Vuelve tu perfil.

## En el teléfono (opcional)
- [ ] En modo oscuro se lee bien.
- [ ] Al girar el teléfono no pierdes nada.

## Lo que todavía NO hace
- Entrar con Google ni crear cuentas (van después).
- Editar el perfil o abrir el detalle de una sección (sigue en la web).
- La cámara y los recordatorios de tomas (sus propios cambios, D24).
- Funcionar sin la Mac: no hay backend en línea; la versión «release» apunta a una dirección provisional.
- El ícono es provisional (una cruz blanca sobre el azul de D22).
