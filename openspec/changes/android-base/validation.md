# Validación — la app de Android: entrar y ver tu perfil

Para: Saúl Pérez, en tu S26 Ultra. Unos 15 minutos. Usa una cuenta de prueba, no la tuya.

## Antes de empezar (una vez)
1. **En el teléfono**, activa la depuración USB. Si ya lo hiciste, salta este paso.
   - Ajustes → Acerca del teléfono → Información de software → toca 7 veces «Número de compilación».
   - Luego Ajustes → Opciones de desarrollador → «Depuración por USB».
2. Conecta el teléfono a la Mac con un cable que transfiera datos. Acepta «¿Permitir la depuración por USB?»
   marcando «Permitir siempre desde esta computadora».
3. **En la Mac**, en una terminal, desde la carpeta del proyecto:
   - `docker compose up -d` (levanta la API y la web en http://localhost:8000).
   - `export ANDROID_HOME="$HOME/Library/Android/sdk"` y
     `export JAVA_HOME="/Applications/Android Studio.app/Contents/jbr/Contents/Home"`. La Mac no trae Java
     propio: se usa el de Android Studio.
   - `"$ANDROID_HOME/platform-tools/adb" devices` debe mostrar tu teléfono como `device`. Si dice `unauthorized`,
     acepta el aviso en el teléfono. Si no aparece, cambia el cable.
   - `"$ANDROID_HOME/platform-tools/adb" reverse tcp:8000 tcp:8000`
   - `cd android && ./gradlew assembleDebug -PapiBaseUrl=http://localhost:8000/api/v1/`
   - `"$ANDROID_HOME/platform-tools/adb" install -r app/build/outputs/apk/debug/app-debug.apk`
4. **Dos cuentas de prueba**, creadas en la web (http://localhost:8000, «Crear cuenta»), con correos que terminen en
   `@example.com`:
   - **A:** acepta el consentimiento al crearla. Es la de AB-2, AB-4, AB-5 y AB-7.
   - **B:** no aceptes el consentimiento (cierra la sesión en la web en cuanto te lo pida). Es la de AB-3.
5. Abre «GlobalHealth» en el teléfono.

## AB-1 · Abre en la entrada
- [ ] Ves «Correo electrónico», «Contraseña» y «Entrar», en español.
- [ ] Con los campos vacíos, «Entrar» no se puede tocar.

## AB-2 · Entrar
1. Escribe el correo de la cuenta A con una contraseña equivocada y toca «Entrar» dos veces seguidas.
- [ ] Ves «Correo o contraseña incorrectos» y sigues en la entrada.
2. Escribe la contraseña correcta y toca «Entrar».
- [ ] Llegas a «Mi perfil médico».

## AB-3 · Consentimiento
1. Cierra la sesión de la app y entra con la cuenta B.
- [ ] La app te muestra el consentimiento («Versión v1») y ningún dato.
- [ ] Al tocar «Acepto», el botón dice «Enviando…» un instante, y llegas al perfil.

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
