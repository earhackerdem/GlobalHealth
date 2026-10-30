# Design

Status: APPROVED
Approved by: Saúl Pérez (author) on 2026-10-29, después de navegar el prototipo
Enmendado durante el andamio (2026-10-29, orquestador): `compileSdk` 37 en vez de 36. OkHttp 5.5.1 y otras librerías
actuales exigen compilar contra la API 37, que es la plataforma instalada. `targetSdk` sigue en 36 (Play) y minSdk en 29.
Versiones subidas a lo que lint marcó como estable: activity-compose 1.13.0, lifecycle 2.11.0, navigation-compose 2.10.2,
Robolectric 4.17 y coroutines-test 1.11.0.

**En una frase:** un proyecto Android nativo en `android/` (Kotlin, Jetpack Compose, AGP 9.5, minSdk 29, target 36) que
entra con correo y contraseña contra la misma API, pide el consentimiento si falta, guarda el token cifrado con el
Keystore y muestra «Mi perfil médico» en solo lectura, con su CI filtrado por `android/**`.

## Context

- D24: app nativa, v1 «hardware primero»; esta es su base. Saúl Pérez respondió las cuatro preguntas de la
  exploración el 2026-10-29: Google después, consentimiento en la app, básicos más el estado de las secciones, y
  minSdk 29.
- La API ya da todo lo necesario:
  - `POST /login/access-token` (`login.py:38`);
  - `GET`/`POST /consent/` y `GET /consent/text` (`consent.py:18`, `:68`, `:76`);
  - el 403 `CONSENT_REQUIRED` (`deps.py:83`);
  - `GET /profile`, `/profile/work`, `/profile/history`, `/profile/habits`, `/profile/family-history` (`profile.py`).

  El backend no cambia.
- Plataforma (`memory/research/android.md#android`): AGP 9.5 con Gradle 9.6, JDK 17 o más (en la Mac, JDK 25 de
  Android Studio) y Kotlin integrado al AGP; `security-crypto` quedó obsoleta (DataStore con Tink); Google Play pide
  target 36.

## Goals / Non-Goals

**Goals:** AB-1…AB-8 (spec delta y proposal).

**Non-Goals:**
- Google (FR-026), crear cuentas, recuperar la contraseña;
- editar el perfil, el detalle de cada sección;
- la cámara (FR-007) y los recordatorios (FR-025), que van en sus cambios;
- Play Console, iPhone;
- caché offline de datos de salud;
- inyección de dependencias con framework (Hilt).

## Qué se toca / qué NO

| Se toca | NO se toca |
|---|---|
| `android/` nuevo: `settings.gradle.kts`, `build.gradle.kts`, `gradle/libs.versions.toml`, wrapper de Gradle, módulo `app` (código, recursos, `src/debug/res/xml/network_security_config.xml`, pruebas en `app/src/test/`) | `backend/`, `frontend/` |
| `harness.json`: `code` + `android/`; `tests` + `android/app/src/test/`, `android/app/src/androidTest/` | Las decisiones (D24 ya lo cubre) |
| `.github/workflows/test-android.yml` nuevo (filtro `android/**` + `alls-green`) | Los otros workflows |
| `.gitignore` de `android/` (`.gradle/`, `build/`, `local.properties`) | `_typos.toml` salvo palabras en español que el gate frene |

**Decisiones afectadas:** se aplican D24 (plataforma), D20 (no disponible mientras envía), D22 (paleta en el tema de
Material 3), D15 (es-MX, aquí en `strings.xml`), D19 (cuentas `@example.com`) y D13/NFR-001 (nada en claro); ninguna
cambia.

**Citadores que vencen:** ninguno. Es una superficie nueva, y D24 y el brief ya la anuncian.

## Interface contract

**Proyecto.**
- `applicationId` y paquete `mx.globalhealth.paciente`. Es un supuesto: no se puede cambiar después de publicar en Play.
- minSdk 29, targetSdk 36, compileSdk 37 (enmienda del andamio).
- AGP 9.5.0, Gradle 9.6.0, Kotlin 2.4.21 (integrado al AGP), Compose BOM 2026.09.00 con Material 3.
- Retrofit 3 + OkHttp 5 + kotlinx.serialization 1.12; DataStore 1.3.0 + `datastore-tink`.
- Pruebas: JUnit 4, MockWebServer, Robolectric y `ui-test-junit4` de Compose, todo en `testDebugUnitTest`.

**Comandos** (desde `android/`):
- `./gradlew testDebugUnitTest` para las pruebas;
- `./gradlew lintDebug` y `./gradlew assembleDebug`;
- `adb install -r app/build/outputs/apk/debug/app-debug.apk`.

**URL base** (`BuildConfig.API_BASE_URL`): debug `http://10.0.2.2:8000/api/v1/` (emulador). Con el teléfono por USB
se compila con `-PapiBaseUrl=http://localhost:8000/api/v1/` y `adb reverse tcp:8000 tcp:8000`. Release: HTTPS (en
este cambio queda un marcador; no hay backend en línea).

**API usada** (Retrofit, `core/net/GlobalHealthApi.kt`):
```
POST login/access-token  form: username, password            -> Token { access_token, token_type }   400 { detail }
GET  consent/text                                             -> { version, text }
POST consent/            json: { version }                    -> { version, granted_at, auth_method }
GET  users/me                                                 -> { email, full_name, … }
GET  profile                                                  -> { birth_date, sex, allergies, latest_weight{value,measured_on}, latest_height{…}, sections_none[] , … }
GET  profile/work                                             -> Work { status, occupation, longest_job, exposures[], no_exposures, shift }
GET  profile/history                                          -> { data: [ { section, … } ], count }
GET  profile/habits                                           -> objeto; «Con datos» si algún valor de primer nivel no es null
GET  profile/family-history                                   -> { data: [ … ], count }
Cualquier 401 -> borrar el token y volver a la entrada · 403 detail "CONSENT_REQUIRED" -> pantalla de consentimiento
```
Los modelos de Kotlin ignoran los campos que no usan (`ignoreUnknownKeys = true`).

**Sesión** (`core/session/SessionStore`): `val token: Flow<String?>`, `suspend fun save(token: String)`,
`suspend fun clear()`. Un DataStore cifrado con Tink (AEAD), con el keyset bajo una llave maestra
`android-keystore://`. El archivo se excluye del respaldo (`data_extraction_rules.xml` y `full_backup_content`).

**Reglas de presentación** (`profile/ProfileFormat.kt`, funciones puras): las mismas de la web.
- Fecha `dd/MM/yyyy · N años`, con la edad calculada en America/Mexico_City.
- Sexo: «Mujer», «Hombre», «Prefiero no decir».
- Peso `72 kg · 12/10/2026` y estatura `165 cm · …`.
- Trabajo, el resumen de `perfil.tsx`: ocupación o etiqueta de la situación · turno en minúsculas · «antes: …» ·
  «expuesto a …».
- Estado de cada sección: «1 registro», «N registros», «Ninguna», «Sin llenar»; hábitos «Con datos» o «Sin llenar».
- Antecedentes familiares: «N registrados» o «Sin registros».

**Pantallas** (Compose; `testTag` entre paréntesis):
- **Entrada** (`login`): «Correo electrónico», «Contraseña» (oculta), «Entrar» y el error.
- **Consentimiento** (`consent`): texto con desplazamiento, la versión, «Acepto» y «Cerrar sesión».
- **Mi perfil médico** (`profile`):
  - las tarjetas «Datos básicos», «Antecedentes familiares» y «Tu historial» (seis filas con su estado);
  - «Cerrar sesión» en la barra superior;
  - el estado de error (`offline`) con «Reintentar».
- **Accesibilidad:** objetivos de al menos 48 dp; los íconos llevan `contentDescription`.

## Decisions

1. **Cliente Retrofit escrito a mano, no generado.** Son 9 endpoints, y el generador `kotlin` de openapi-generator no
   soporta el `anyOf` con que FastAPI escribe los opcionales (research). Se revisa cuando la app use muchos más.
2. **DataStore con Tink y llave del Keystore**, no EncryptedSharedPreferences (obsoleta desde 1.1.0, 2025-07-30).
3. **El consentimiento se detecta por el 403 `CONSENT_REQUIRED`** de la API, no comparando versiones en la app: el
   servidor es la autoridad, y una versión nueva del texto funciona sin actualizar la app.
4. **Un solo módulo `app`**, con paquetes por función (`auth`, `consent`, `profile`, `core/net`, `core/session`,
   `ui/theme`), e inyección manual (un `AppContainer`). Se modulariza o se suma Hilt cuando crezca.
5. **Las pruebas de Compose corren en la JVM con Robolectric**, sin emulador en CI por ahora. El emulador entra con
   la cámara o las notificaciones.
6. **Sin caché de datos de salud:** el perfil vive en memoria en el ViewModel. Offline solo muestra el error.
7. **CI aparte** (`test-android.yml`): `changes` filtra `android/**` y su propio workflow; corre
   `testDebugUnitTest lintDebug assembleDebug` con JDK 17; `alls-green-test-android`.
8. **Regla de cierre de la revisión**, decidida antes de la primera ronda: si una ronda después de la primera trae solo
   hallazgos bajos, quedan como deuda registrada y se archiva.
9. **Descargas** (la aprobación del plan las autoriza):
   - la distribución de Gradle 9.6.0 desde `services.gradle.org`, por el wrapper;
   - las librerías desde Google Maven y Maven Central.

   Son fuentes oficiales. El wrapper se genera con su checksum (`distributionSha256Sum`).

## Test plan (one row per scenario, mandatory)

| # | Spec · scenario | Test | Dónde |
|---|---|---|---|
| 1 | Abrir la app por primera vez (AB-1) | Compose/Robolectric: sin token, la primera pantalla tiene «Correo electrónico», «Contraseña» y «Entrar». Manual: `adb install` en el emulador y el S26, y abre | JVM + manual |
| 2 | Entrar con consentimiento (AB-2) | MockWebServer: 200 de login, luego 200 de perfil → la pantalla `profile`; el token se guardó; el pedido lleva `Authorization: Bearer …` | JVM |
| 3 | Contraseña equivocada (AB-2) | MockWebServer 400 `{"detail":"Correo o contraseña incorrectos"}` → se muestra ese texto; nada guardado; «Entrar» no disponible mientras envía (D20) | JVM |
| 4 | Cuenta sin consentimiento (AB-3) | 403 `CONSENT_REQUIRED` → la pantalla `consent` con el texto y «v1» de `consent/text`, sin datos del perfil; «Acepto» → `POST consent/` con `{"version":"v1"}` → el perfil | JVM |
| 5 | Perfil con datos (AB-4) | Funciones puras de `ProfileFormat` con los datos del escenario (edad con fecha fija 2026-10-29, resumen del trabajo, «2 registros», «Ninguna», «Sin llenar», «Con datos») + Compose: la pantalla muestra esas cadenas | JVM |
| 6 | Volver a abrir (AB-5) | Con un token guardado, el arranque va a `profile` sin pasar por `login` | JVM |
| 7 | Cerrar sesión y 401 (AB-5) | «Cerrar sesión» → token borrado y la pantalla `login`; cualquier 401 de MockWebServer → lo mismo | JVM |
| 8 | Nada en claro (AB-6) | Robolectric: tras guardar `eyJ…prueba`, ningún archivo de `filesDir`/`dataDir` contiene ese texto; ningún archivo contiene datos del perfil. Manual: `adb shell run-as … ls -R` en el emulador | JVM + manual |
| 9 | La API no responde (AB-7) | MockWebServer apagado o `SocketPolicy` de desconexión → el texto de error y «Reintentar»; con el servidor de vuelta, «Reintentar» muestra el perfil; el token sigue | JVM |
| 10 | CI (AB-8) | El workflow corre en este PR (toca `android/**`) y queda verde; un PR sin `android/**` lo salta | GitHub Actions |

Exploración del agente (no delegable): en el emulador y, si Saúl Pérez conecta el S26 con depuración USB, en el
teléfono, por `adb` (capturas con `screencap`, toques con `input`, árbol con `uiautomator dump`):
- contraseña equivocada, doble toque en «Entrar», girar la pantalla;
- sin red, cerrar y volver a abrir, cerrar sesión;
- modo oscuro, TalkBack en la pantalla de entrada.

## Non-functional constraints addressed

- **NFR-001:** fila 8; nada del perfil en disco.
- **NFR-004:** fila 4.
- **NFR-011:** filas 1 a 9.
- **NFR-012:** textos en `strings.xml`.
- **Seguridad de transporte:** HTTP solo en debug y solo hacia `10.0.2.2` y `localhost`, por `src/debug/res/xml/`;
  release solo HTTPS.

## Risks / Trade-offs

- **Curva:** Saúl Pérez no ha hecho Android. La estructura es simple a propósito (un módulo, sin Hilt) y lleva
  comentarios donde el patrón no es obvio.
- **Versiones recientes:** AGP 9.5 y DataStore con Tink 1.3.0 tienen semanas. Si algo falla al compilar, se baja a la
  versión anterior estable y queda anotado.
- **El token dura 8 días y no hay refresh:** al vencer, se vuelve a entrar. Un token más corto con refresh es un cambio
  de backend aparte.
- **Sin backend en línea, la release no sirve todavía:** se prueba en debug contra la Mac.

## Migration Plan

Ninguna: no hay datos ni esquema que migrar.

## Gate that closes the work

1. `./gradlew testDebugUnitTest lintDebug assembleDebug`: cero fallas y cero pruebas saltadas, con los números en
   `evidence.md`.
2. `test-android.yml` en verde en el PR; los demás workflows se saltan el PR o pasan.
3. `make tdd-check` verde.
4. `openspec validate android-base --strict` limpio.
5. La app instalada y recorrida por el agente en el emulador (y en el S26 si está conectado), sin defectos.
6. La revisión con la regla de la Decision 8, o el archivo sin revisión si Saúl Pérez lo elige, y el archivo como
   último commit del PR.
7. Después, la validación de Saúl Pérez con `validation.md` en su S26. El merge es humano.

## Open Questions

Ninguna bloqueante. Se aprueban con el prototipo:
- el `applicationId` `mx.globalhealth.paciente`;
- los textos;
- el orden de las tarjetas.
