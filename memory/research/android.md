## App de Android nativa: plataforma, librerías y seguridad (verificado 2026-10-29) <a id="android"></a>
Para D24 y el cambio `android-base`. Todas las fuentes se consultaron el 2026-10-29.

- **Fact (versiones en México):** StatCounter, móvil, septiembre de 2026: Android 16 38.32 %, 15 16.9 %, 14 13.23 %, 13
  12.82 %, 12 7.37 %, 11 4.46 %. La página no desglosa versiones anteriores a Android 11; el resto, ~6.9 %, queda
  sin desglose. Acumulado: API 31 o más, 88.64 %; API 30 o más, 93.10 %. Para minSdk 24 a 29 solo hay cota inferior:
  al menos 93.1 %. Mundial (apilevels.com, datos de StatCounter): minSdk 28 97.9 %, 29 96.2 %, 31 86.6 %. Google ya
  no publica su tabla de distribución en la web (está en Play Console, «Reach and devices»).
- **Source:** https://gs.statcounter.com/android-version-market-share/mobile/mexico · https://apilevels.com/
- **Confidence:** [VERIFIED]. Es tráfico web, no dispositivos instalados.
- **Re-check if:** se sube minSdk o hay cuenta de Play Console.

- **Fact (mínimos de las librerías):**
  - AndroidX usa minSdk 24 por defecto en las versiones nuevas (desde julio de 2026).
  - Compose: BOM 2026.09.00; compose-ui subió su mínimo por defecto a 23 en la 1.10.
  - CameraX: 1.6.2, mínimo 23.
  - Health Connect: integrado al sistema desde Android 14; el SDK dice API 26 y el cliente 1.2.0-alpha05 dice 24.
  - ML Kit GenAI (Gemini Nano): API 26 o más, con AICore, en beta; el S26 Ultra está en la lista de dispositivos.
  - Google Play pide **target API 36** desde el 2026-08-31 y no fija mínimo.
- **Source:** https://developer.android.com/jetpack/androidx/versions ·
  https://developer.android.com/develop/ui/compose/bom/bom-mapping ·
  https://developer.android.com/jetpack/androidx/releases/camera ·
  https://developer.android.com/health-and-fitness/guides/health-connect/develop/get-started ·
  https://developers.google.com/ml-kit/genai/prompt/android/get-started ·
  https://developer.android.com/google/play/requirements/target-sdk
- **Confidence:** [VERIFIED]. La documentación de Health Connect se contradice (24 o 26).
- **Re-check if:** se agrega una librería con mínimo propio.

- **Fact (token seguro):** `androidx.security:security-crypto` (EncryptedSharedPreferences, MasterKey) quedó obsoleta
  en 1.1.0 (2025-07-30): «Deprecated all APIs in favour of existing platform APIs and direct use of Android Keystore»,
  y no habrá más versiones. DataStore 1.3.0 (2026-10-21) trae `datastore-tink` (`AeadSerializer`), con el keyset de
  Tink protegido por una llave maestra del Android Keystore. La guía de seguridad pide Keystore más Tink y tokens de
  vida corta. Que «DataStore con Tink» sea el reemplazo es una lectura de esas páginas juntas: ninguna lo nombra así.
- **Source:** https://developer.android.com/jetpack/androidx/releases/security ·
  https://developer.android.com/privacy-and-security/cryptography ·
  https://developer.android.com/jetpack/androidx/releases/datastore · https://developer.android.com/topic/security/data
- **Confidence:** [VERIFIED] la obsolescencia y DataStore con Tink; el reemplazo es [OPINION].
- **Re-check if:** Google publica un reemplazo oficial.

- **Fact (backend local en desarrollo):**
  - El emulador ve la Mac en `10.0.2.2`.
  - Un teléfono por USB la ve con `adb reverse tcp:8000 tcp:8000` (en el manual de adb).
  - Desde API 28 el texto en claro (HTTP) está apagado; se permite por dominio con `network_security_config`
    (`cleartextTrafficPermitted`), y `<debug-overrides>` no sirve para esto. Para limitarlo a debug se pone el XML en
    `src/debug/res/`.
- **Source:** https://developer.android.com/studio/run/emulator-networking-address ·
  https://android.googlesource.com/platform/packages/modules/adb/+/refs/heads/master/docs/user/adb.1.md ·
  https://developer.android.com/privacy-and-security/security-config
- **Confidence:** [VERIFIED]. `adb reverse` con el S26 no se ha probado todavía.
- **Re-check if:** se publica la app contra un backend en línea.

- **Fact (cliente generado de OpenAPI 3.1):** openapi-generator v7.26.0 tiene 3.1 en beta, y su generador `kotlin`
  marca oneOf, anyOf y allOf como no soportados. Fabrikt 28.3.0 genera `Any` o `JsonElement` para los tipos múltiples.
  FastAPI escribe los opcionales como `anyOf: [X, null]`; esto último NOT VERIFIED.
- **Source:** https://github.com/OpenAPITools/openapi-generator · https://openapi-generator.tech/docs/generators/kotlin/
  · https://github.com/fabrikt-io/fabrikt
- **Confidence:** [VERIFIED] las limitaciones; su efecto en nuestro spec, sin probar.
- **Re-check if:** se genera el cliente con el `openapi.json` real.

- **Fact (versiones de compilación y CI):**
  - AGP 9.5.0 (octubre de 2026): pide Gradle 9.6.0, JDK 17 y Build Tools 36.0.0, y soporta hasta API 37. Desde AGP 9
    el soporte de Kotlin viene integrado y se quita el plugin `org.jetbrains.kotlin.android`. Kotlin estable: 2.4.21.
  - Las pruebas de Compose corren en la JVM con Robolectric.
  - Para el emulador en GitHub Actions: android-emulator-runner v2.38.0 en ubuntu-latest con KVM.
- **Source:** https://developer.android.com/build/releases/agp-9-5-0-release-notes ·
  https://developer.android.com/build/migrate-to-built-in-kotlin ·
  https://developer.android.com/training/testing/local-tests/robolectric ·
  https://github.com/ReactiveCircus/android-emulator-runner
- **Confidence:** [VERIFIED]
- **Re-check if:** sale AGP 10.

- **Fact (versiones fijadas en `android/gradle/libs.versions.toml`, verificadas el 2026-10-30 ~04:30 UTC):** cada una
  es la última estable publicada en ese momento; lo que hay después es solo alpha o beta.
  - AGP 9.5.0 (después, 9.6.0-alpha02);
  - Kotlin 2.4.21 (después, 2.5.0-Beta2);
  - Compose BOM 2026.09.00;
  - activity-compose 1.13.0 (después, 1.14.0-alpha03);
  - lifecycle 2.11.0 (después, 2.12.0-alpha05);
  - navigation-compose 2.10.2;
  - datastore-tink 1.3.0;
  - Retrofit 3.0.0;
  - OkHttp 5.5.1;
  - kotlinx-serialization-json 1.12.0;
  - kotlinx-coroutines-test 1.11.0;
  - Robolectric 4.17;
  - JUnit 4.13.2.
- **Source:** el `maven-metadata.xml` de cada artefacto, en https://dl.google.com/android/maven2/ (AndroidX, AGP) y
  https://repo1.maven.org/maven2/ (los demás), por ejemplo
  https://repo1.maven.org/maven2/com/squareup/okhttp3/okhttp/maven-metadata.xml. Se leyeron los campos `<versions>`,
  `<release>` y `<lastUpdated>`.
- **Confidence:** [VERIFIED]
- **Re-check if:** se sube cualquier versión del catálogo.
