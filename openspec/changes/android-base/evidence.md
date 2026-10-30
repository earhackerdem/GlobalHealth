# Evidence — android-base

Rutas cortas: `T/` = `android/app/src/test/java/mx/globalhealth/paciente/`.

## Criterion → test → result

| Criterio | Prueba | Ancla | Resultado |
|---|---|---|---|
| AB-1 instalar y abrir | `ab1_sinToken_laPrimeraPantallaEsLaEntrada…` + instalación por `adb` en el emulador | `T/SessionLoginConsentTest.kt:81` | ✅ JVM · ✅ emulador |
| AB-2 entrar | `ab2_loginCorrecto_guardaElTokenYLlegaAlPerfilConBearer`, `ab2_contrasenaEquivocada_…` (con D20 reforzado) | `:94`, `:122` | ✅ |
| AB-3 consentimiento | `ab3_sinConsentimiento_muestraElTextoV1SinDatos…` | `:158` | ✅ JVM · ✅ emulador contra la API real |
| AB-4 ver mi perfil | `ProfileFormatTest` (21) + `ab4_perfilConDatos_…` (2), `ab4_perfil_esSoloLectura…`, `ab4_perfilSinDatos_…` | `T/profile/ProfileFormatTest.kt` · `T/profile/ProfileScreenTest.kt:83`, `:115`, `:130`, `:158` | ✅ |
| AB-5 sesión | `ab5_conTokenGuardado_…`, `ab5_cerrarSesion_…`, `ab5_un401DelPerfil_…`, `ab5_un401EnCualquierPedido_…`, `ab5_clear_borraElTokenGuardado` | `:192`, `:210`, `:223`, `:234` · `T/core/session/SessionStoreEncryptionTest.kt:48` | ✅ |
| AB-6 nada en claro | `ab6_trasGuardarElToken_…`, `ab6_trasEntrarYVerElPerfil_…` + revisión a mano de los archivos en el emulador | `T/core/session/SessionStoreEncryptionTest.kt:30` · `:248` | ✅ |
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

`make tdd-check` ✓. Sin caracteres invisibles en el diff.

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
| «Cerrar sesión» | La entrada; `files/datastore/session.pb` ya no existe |
| Cuenta nueva sin consentimiento | La pantalla de consentimiento con «Versión v1» y el texto de la API, sin datos del perfil. «Acepto» → `POST /consent/` 201 y el perfil; `GET /consent/` por API confirma la versión `v1` |
| Consola (logcat) | Sin `FATAL` ni `AndroidRuntime` de la app |

**No cubierto en el pase:**
- **El S26 Ultra de Saúl Pérez:** la Mac no lo ve por USB (no aparece en `adb` ni en el sistema); su recorrido va en
  `validation.md`.
- **TalkBack:** no se activó. El árbol de accesibilidad muestra las etiquetas de los campos y los textos de los
  botones, y los botones miden 48 dp.
- **El 401 de un token vencido:** cubierto por dos pruebas, no se forzó a mano.

El emulador, con GPU por software, mostró varias veces «System isn't responding» del propio sistema, no de la app. Se
cerró con «Wait».
