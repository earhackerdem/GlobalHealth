# Evidence — android-base

Rutas cortas: `T/` = `android/app/src/test/java/mx/globalhealth/paciente/`. Un ancla suelta (`:192`) es una línea
de `T/SessionLoginConsentTest.kt`.

## Criterion → test → result

| Criterio | Prueba | Ancla | Resultado |
|---|---|---|---|
| AB-1 instalar y abrir | `ab1_sinToken_laPrimeraPantallaEsLaEntrada…` + instalación por `adb` en el emulador | `T/SessionLoginConsentTest.kt:81` | ✅ JVM · ✅ emulador |
| AB-2 entrar | `ab2_loginCorrecto_guardaElTokenYLlegaAlPerfilConBearer`, `ab2_contrasenaEquivocada_…` (con D20 reforzado) | `:94`, `:122` | ✅ |
| AB-3 consentimiento | `ab3_sinConsentimiento_muestraElTextoV1SinDatos…` | `:158` | ✅ JVM · ✅ emulador contra la API real |
| AB-4 ver mi perfil | `ProfileFormatTest` (21) + `ab4_perfilConDatos_…` (2), `ab4_perfil_esSoloLectura…`, `ab4_perfilSinDatos_…` | `T/profile/ProfileFormatTest.kt` · `T/profile/ProfileScreenTest.kt:83`, `:115`, `:130`, `:158` | ✅ |
| AB-5 sesión | `ab5_conTokenGuardado_…`, `ab5_cerrarSesion_…`, `ab5_un401DelPerfil_…`, `ab5_un401EnCualquierPedido_…`, `ab5_clear_borraElTokenGuardado` | `:192`, `:210`, `:223`, `:234` · `T/core/session/SessionStoreEncryptionTest.kt:48` | ✅ |
| AB-6 nada en claro | `ab6_trasGuardarElToken_…`, `ab6_trasEntrarYVerElPerfil_…` + revisión a mano de los archivos en el emulador | `T/core/session/SessionStoreEncryptionTest.kt:30` · `T/SessionLoginConsentTest.kt:248` | ✅ |
| AB-7 sin conexión | `ab7_laApiSeDesconecta_…`, `ab7_laApiApagada_…`, `ab7_unaParteDelPerfilNoResponde_…` | `:268`, `:287` · `T/profile/ProfileScreenTest.kt:173` | ✅ |
| AB-8 CI | `.github/workflows/test-android.yml`: corre en el PR porque toca `android/**` | PR #44 | ✅ `test-android` y `alls-green-test-android` en verde (Linux, JDK 17); backend, docker-compose y playwright saltados por el filtro de rutas |

## Red before green

| Grupo | Rojo (re-corrido por el orquestador) | Commit |
|---|---|---|
| 1 · sesión, entrada, consentimiento | `./gradlew testDebugUnitTest` → la compilación de las pruebas falla con 12 errores, todos `Unresolved reference` a nombres del contrato (`AppContainer`, `GlobalHealthApp`, `SessionStore`, `sessionStore`). Ningún error en el código de prueba | `aac7b2a` |
| 2 · perfil | 30 errores, todos `Unresolved reference 'ProfileFormat'`. El tester comprobó por separado que, sin `ProfileFormatTest`, las 13 pruebas del grupo 1 pasaban y las 5 de pantalla fallaban por comportamiento faltante (se agotaba el tiempo esperando los textos) | `6d12f4a` |

**Prueba corregida durante el verde (una, por el tester).** `ab4_perfil_esSoloLecturaSinNingunControlDeEdicion`
prohibía la palabra «Editar» en cualquier texto, y la nota aprobada del prototipo («Para editar, entra a la web. Aquí
todo es de solo lectura.») la contiene. La spec habla de controles, así que el tester limitó la búsqueda a nodos que se
pueden tocar o escribir. Va en su propio `test:` (`f1118e7`) y `make tdd-check` mide desde ahí.

**Asimetrías declaradas** (infraestructura de pruebas y de compilación escrita por el orquestador; para ellas `make
tdd-check` pasa de forma vacía):
- el andamio (`c5d1705`): las dependencias de prueba en `app/build.gradle.kts` y `libs.versions.toml`;
- `android/app/src/test/resources/robolectric.properties` (`sdk=35`), en el commit del rojo `aac7b2a`. Robolectric
  4.17 con su SDK 36 por defecto no arranca sobre el JDK 25: `java.base` no exporta `jdk.internal.access`. Lo encontró
  el tester.

## Green

| Grupo | Verde (re-corrido por el orquestador) | Commit |
|---|---|---|
| 1 | 13 pruebas: `SessionLoginConsentTest` 11, `SessionStoreEncryptionTest` 2 · 0 fallas, 0 errores, 0 saltadas | `e141544` |
| 2 | 39 pruebas: `SessionLoginConsentTest` 11, `SessionStoreEncryptionTest` 2, `ProfileFormatTest` 21, `ProfileScreenTest` 5 · 0 fallas, 0 errores, 0 saltadas | `2e621ae` |

`./gradlew testDebugUnitTest lintDebug assembleDebug` termina en BUILD SUCCESSFUL. Lint no da errores y deja 2 avisos
esperados:
- `OldTargetApi`: el target es 36, que es lo que pide Play;
- `AndroidGradlePluginVersion`: hay Gradle 9.8.2; el plan fija 9.6.0, que es lo que pide AGP 9.5.

`make tdd-check` ✓. `openspec validate android-base --strict` → «Change 'android-base' is valid» (compuerta 4,
registrada en la revisión, D5). Sin caracteres invisibles en el diff.

**Desviaciones del plan:**
- `compileSdk` 37 (enmienda en `design.md`): OkHttp 5.5.1 y otras librerías lo exigen; el target sigue en 36.
- Los textos que devuelve `ProfileFormat` son constantes en es-MX dentro de ese objeto, para que sean funciones puras
  que se prueban sin Android. Las etiquetas de las pantallas sí están en `strings.xml`.
- El contenedor (`AppContainer`) vive en una `GlobalHealthApplication`. Si se creara en la actividad, al girar la
  pantalla habría dos DataStore sobre el mismo archivo, y DataStore lo rechaza.
- `SessionStore.clearIfCurrent(token)`: un 401 tardío de un token viejo no cierra una sesión nueva.

## Full suite

El backend y la web no cambiaron. Su CI se lo salta si el PR no toca sus rutas (PR #43): este PR toca `harness.json` y
`.github/workflows/test-android.yml`, que no están en esos filtros.

## Exploratory pass (emulador `Medium_Phone_API_37.0`, debug contra la API local en `10.0.2.2:8000`, cuentas `@example.com`)

| Qué se intentó | Qué pasó |
|---|---|
| Instalar con datos borrados y abrir | La entrada: «GlobalHealth», «Tu expediente, a la mano», «Correo electrónico», «Contraseña», «Entrar», «¿Aún no tienes cuenta? Créala en la web.» |
| Contraseña equivocada con **doble toque** en «Entrar» | «Correo o contraseña incorrectos»; el backend registró **un** solo `POST /login/access-token` |
| Contraseña correcta (la cuenta del pase de perfil-trabajo) | «Mi perfil médico» con datos reales: el trabajo «Ingeniera…» de 200 caracteres se parte en renglones, «· rotativo · antes: Albañil», «Sin registros», las seis secciones «Sin llenar» y, al final, la nota de solo lectura |
| Archivos de la app (`run-as … find`) | Solo `shared_prefs/…session_keyset.xml` (el keyset de Tink protegido por el Keystore), `files/datastore/session.pb` y `files/profileInstalled`. Ningún archivo contiene `eyJhbGci` (inicio del JWT) ni «Ingeniera» o «Albañil»: **0 coincidencias** |
| Forzar el cierre y volver a abrir | Va directo al perfil, sin pedir la contraseña |
| Girar a horizontal; modo oscuro | El perfil sigue con sus datos, sin volver a la entrada; en oscuro los colores de D22, legibles |
| API detenida (`docker compose stop backend`) y abrir | «No pudimos conectar. Revisa tu conexión e intenta de nuevo.», «Reintentar» y «Cerrar sesión». Con la API de vuelta, «Reintentar» trae el perfil |
| «Cerrar sesión» | La entrada. `files/datastore/session.pb` sigue existiendo, con 33 bytes: la cadena vacía cifrada, sin el token (corrección de la revisión, A8; la versión anterior de esta fila decía «ya no existe») |
| Cuenta nueva sin consentimiento | La pantalla de consentimiento con «Versión v1» y el texto de la API, sin datos del perfil. «Acepto» → `POST /consent/` 201 y el perfil; `GET /consent/` por API confirma la versión `v1` |
| Consola (logcat) | Sin `FATAL` ni `AndroidRuntime` de la app |

## Exploratory pass en el S26 Ultra (SM-S948B, Android 17 / API 37, 2026-10-29, durante la revisión)

Debug compilada con `-PapiBaseUrl=http://localhost:8000/api/v1/` y `adb reverse tcp:8000 tcp:8000`, contra la API
local, con cuentas `@example.com`. Es el código de antes de los arreglos de la revisión.

| Qué se intentó | Qué pasó |
|---|---|
| Borrar datos y abrir (el teléfono ya estaba en modo oscuro) | La entrada en español, con los colores oscuros de D22 |
| Contraseña equivocada con **doble toque** en «Entrar» | «Correo o contraseña incorrectos»; el backend registró **un** `POST /login/access-token` |
| Contraseña correcta | Samsung Pass ofreció guardar el usuario y la contraseña (se tocó «Cancelar»). Después, «Mi perfil médico» con las seis secciones y la nota «Para editar, entra a la web» |
| Archivos de la app (`run-as`) | `shared_prefs/…session_keyset.xml`, `files/datastore/session.pb` y `files/profileInstalled`. El keyset empieza con el byte `0x12`: es un `EncryptedKeyset`, cifrado por la llave del Keystore. Ningún archivo contiene `eyJhbGci`, «Ingeniera» ni «Albañil» |
| Forzar el cierre y volver a abrir | Directo al perfil |
| API detenida (`docker compose stop backend`) y abrir | «No pudimos conectar…» con «Reintentar». Con la API de vuelta, «Reintentar» trae el perfil |
| «Cerrar sesión» | La entrada. `session.pb` queda con 33 bytes (ver A8) |
| Cuenta nueva sin consentimiento | «Versión v1» y el texto, sin datos. «Acepto» → `GET /consent/text` 200, `POST /consent/` 201 y el perfil |
| logcat | Sin `FATAL` de la app; solo avisos del sistema de Samsung (Adreno, libpenguin) |

No se giró la pantalla ni se activó TalkBack, porque los dos cambian ajustes del teléfono de Saúl Pérez. Están en la
parte opcional de `validation.md`.

**No cubierto en el pase del emulador:**
- **El S26 Ultra de Saúl Pérez:** al principio la Mac no lo veía por USB. Se recorrió después, en la sección de
  arriba.
- **TalkBack:** no se activó. El árbol de accesibilidad muestra las etiquetas de los campos y los textos de los
  botones, y los botones miden 48 dp.
- **El 401 de un token vencido:** decía «cubierto por dos pruebas». Era falso: la API responde **403** a un token
  vencido, y las pruebas usaban un 401 que la API no da (B1 de la revisión; la corrección está en § Revisión).

El emulador, con GPU por software, mostró varias veces «System isn't responding» del propio sistema, no de la app. Se
cerró con «Wait».

## Revisión, ronda 1 (PR #44)

Revisión adversaria con cinco revisores, uno por lente, y cuatro validadores que reprodujeron cada hallazgo. El
detalle está en los comentarios `review-agent` del PR. Resultado: **26 hallazgos confirmados** (1 alto, 3 medios, 22
bajos), 2 falsos positivos, 1 dudoso y 6 fuera de alcance. Saúl Pérez aprobó aplicar los 26 el 2026-10-29. Los
veredictos están en `memory/closed/2026-10-29-falsos-positivos-de-android-base.md` y
`memory/closed/2026-10-29-fuera-de-alcance-de-android-base.md`.

**Qué se aplicó:** un fixer, con el código y las pruebas de `android/`. El orquestador hizo los documentos, la
enmienda de la spec y del diseño (B1, A1, A2, B2, B3 y las firmas `Aead?`), `validation.md` (D1) y el research (D6).

**Rojo** (re-corrido por el orquestador, con las pruebas nuevas contra el código anterior, `git stash` de `src/main`):
69 pruebas, **18 fallas**, 0 errores, 0 saltadas. Todas son por comportamiento:

| Pruebas que fallan | Cuántas | Hallazgos |
|---|---|---|
| `SessionLoginConsentTest` | 7 | B1 ×2, B2, B3, C1, A3 ×2 |
| `ApiResultTest` | 3 | B1, B3 |
| `KeystoreAeadTest` | 3 | A1, A2 |
| `ThemeTest` | 3 | C6 |
| `ConsentLayoutTest` | 1 | C4 |
| `ProfileFormatTest` | 1 | C2 |

Commit `c3c46cf`.

A4, A5, A6, B4, B5, B7, B8 y C7 eran huecos de prueba, no defectos, así que sus pruebas pasan desde el rojo. El fixer
comprobó que matan a su mutante:
- B8: la prueba vieja deja pasar un destello de 4 cuadros de la entrada; la nueva falla.
- B5: sin la guarda salen 2 pedidos.
- A6: sin la exclusión de `sharedpref`.

**Verde** (re-corrido por el orquestador desde cero, `testDebugUnitTest lintDebug assembleDebug --rerun-tasks`):
**69 pruebas, 0 fallas, 0 errores, 0 saltadas**. Por clase:

| Clase | Pruebas |
|---|---|
| `SessionLoginConsentTest` | 20 (incluye AB-1 en API 29 y 35) |
| `ProfileFormatTest` | 22 |
| `ApiResultTest` | 6 |
| `ProfileScreenTest` | 5 |
| `SessionStoreEncryptionTest` | 5 |
| `ThemeTest` | 3 |
| `KeystoreAeadTest` | 3 |
| `BackupRulesTest` | 3 |
| `ConsentLayoutTest` | 1 |
| `LoginViewModelTest` | 1 |

`lintDebug`: 0 errores, con los mismos 2 avisos de antes. `assembleDebug`: BUILD SUCCESSFUL. Commit `369af78`. `make
tdd-check` ✓ desde `c3c46cf`. Sin caracteres invisibles en el diff.

**Lo que corrige B1, ahora con prueba:** con un token vencido, la API responde 403 «No se pudieron validar las
credenciales», y la app borra el token y vuelve a la entrada. El escenario lo reprodujo un validador contra la API
real, con un JWT firmado con `exp` en el pasado. Las pruebas usan esa misma respuesta.

**Asimetrías y notas del fixer:**
- A5 cancela por reflexión el `CoroutineScope` del primer DataStore para abrir otro sobre el mismo archivo. Puede
  romperse al actualizar DataStore; la alternativa limpia es un parámetro `scope` en `SessionStore`.
- `ConsentLayoutTest` usa los gráficos nativos de Robolectric (`@GraphicsMode(NATIVE)`). El CI de Linux lo confirma
  o lo desmiente en este PR.
- El tema de ventana es `Theme.DeviceDefault.DayNight`: `Theme.Material.DayNight.NoActionBar` no existe en
  `android.jar` API 37.
- Fuera de los hallazgos, sin arreglar: con un token válido, la API también responde 404 «Usuario no encontrado» o
  400 «Usuario inactivo» (`deps.py:50-53`), y la app muestra «Algo salió mal». Va con la deuda de la ronda.

**Pase exploratorio de los arreglos** (emulador `Medium_Phone_API_37.0`, debug de `369af78` contra la API local,
cuentas `@example.com` creadas por API):

| Qué se intentó | Qué pasó |
|---|---|
| «Entrar» con los campos vacíos, y con solo el correo (tres toques) | El backend no registró **ningún** `POST /login/access-token`. Con el correo vacío y la contraseña escrita, «Entrar» se ve gris |
| Cuenta con un antecedente familiar | «Antecedentes familiares: 1 registrado» (C2) |
| Consentimiento en horizontal con letra al 200 % | El texto del consentimiento se lee y la pantalla se desplaza (C4). Antes de los arreglos, a ese tamaño el texto no aparecía |
| CI en Linux, JDK 17 (run 41009713195) | 69 pruebas, 0 fallas, 0 errores, 0 saltadas, con `ConsentLayoutTest` (gráficos nativos) incluida |

**No cubierto a mano tras los arreglos:**
- «Enviando…» con «Cerrar sesión» no disponible (C1) y el arranque en oscuro sin destello blanco (C6). El emulador
  se colgó: primero «Process system isn't responding», luego, al reiniciarlo, «invalid color buffer» de la GPU por
  software, con poca memoria libre en la Mac.
- Un deslizamiento rápido sobre el consentimiento, con el emulador tardando 2.6 s por evento, terminó en «Cerrar
  sesión». La API no recibió nada, así que fue un toque, no una respuesta del servidor. No se reprodujo con gestos
  lentos antes de que el emulador cayera, así que queda como **observación por confirmar**, no como defecto.

Lo que no se cubrió a mano lo cubren `ab3_mientrasSeRegistra_aceptoMuestraEnviando…` y `ThemeTest`, y queda en los
pasos de AB-3 y en la parte opcional de `validation.md` para el S26. El S26 no estaba conectado al terminar los
arreglos.
