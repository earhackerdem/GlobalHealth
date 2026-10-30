# Exploration — android-base

Fecha: 2026-10-29 · Entrada: `proposal.md` (AB-1…AB-8), D24 y `memory/research/android.md#android`.

## 1. Input validation

| Check | Result |
|---|---|
| As/I want/so that story with a concrete role | ✅ «Como paciente, quiero entrar a GlobalHealth desde una app en mi teléfono Android y ver mi perfil médico…» |
| Every AC in Given/When/Then with concrete data | 🟡 AB-1…AB-8 son observables; los datos concretos de AB-3 y AB-4 dependen de las preguntas 2 y 3 (§5) y van a la spec delta |
| No imposed technical solution | ⚠️ AB-6 nombra el Android Keystore. Se acepta: es la recomendación primaria de Google, no una preferencia |

## 2. Coverage matrix per criterion

**Greenfield de Android:** no existe `android/` ni nada de Kotlin en el repo. Las filas dicen qué da la plataforma y
qué da la API que ya existe.

| AC | Coverage | Where (file:line / URL + date) | Missing |
|---|---|---|---|
| AB-1 instalar y abrir | ❌ New | Toolchain de la Mac verificado hoy: Android Studio 2026.2, JDK 25 (jbr; AGP 9.5 pide 17+), plataforma android-37, build-tools 36.0.0, `adb` 1.0.41. Sin teléfono conectado aún | El proyecto Gradle (AGP 9.5, Gradle 9.6, Kotlin integrado), la pantalla de entrada, textos es-MX |
| AB-2 entrar | 🟡 Partial | La API existe: `POST /login/access-token` (form OAuth2, `backend/app/api/routes/login.py:38`); el error «Correo o contraseña incorrectos» (`:49`); el token dura 8 días (`backend/app/core/config.py:25`), sin refresh | Cliente HTTP y pantalla |
| AB-3 consentimiento | 🟡 Partial | `GET /consent/text` da la versión vigente y su texto (`consent.py:68`); `POST /consent/` registra versión, hash del texto y método de entrada (`:18`); `GET /consent/` da el estado (`:76`). Las rutas de perfil piden consentimiento (403 `CONSENT_REQUIRED`, `backend/app/api/deps.py:83`) | Pantalla de consentimiento en la app (pregunta 2) |
| AB-4 ver mi perfil | 🟡 Partial | `GET /profile`, `/profile/work`, `/profile/history`, `/profile/habits`, `/profile/family-history` (`profile.py:271`, `:659` y siguientes). La web arma la tarjeta y los estados en `frontend/src/routes/_layout/perfil.tsx` | Las pantallas de solo lectura; el alcance, en la pregunta 3 |
| AB-5 sesión | ❌ New | El 401 de la API ya existe (corrección de la revisión, 2026-10-29: la API da 401 solo sin cabecera; a un token vencido o inválido le responde 403 «No se pudieron validar las credenciales», `backend/app/api/deps.py:38-42`) | Guardar el token, cerrar sesión y volver a la entrada con 401 o con ese 403 |
| AB-6 nada en claro | ❌ New | `security-crypto` quedó obsoleta (1.1.0, 2025-07-30); DataStore 1.3.0 con `datastore-tink` y una llave del Keystore (`memory/research/android.md#android`) | El almacenamiento del token; sin caché de datos de salud; excluir el archivo del respaldo automático |
| AB-7 sin red | ❌ New | — | Estados de error y reintentar |
| AB-8 CI | 🟡 Partial | Patrón `changes` + `alls-green` (PR #43, `.github/workflows/test-backend.yml`); AGP 9.5 pide JDK 17; pruebas de Compose con Robolectric en la JVM | `test-android.yml` filtrado por `android/**` |

## 3. What looked useful and was discarded (and why)

- **EncryptedSharedPreferences (`security-crypto`):** obsoleta y sin más versiones.
- **Cliente generado del OpenAPI con openapi-generator:** su generador `kotlin` no soporta `anyOf`, y FastAPI escribe
  así los opcionales (esto último sin verificar). Para los ~8 endpoints de la v1, un cliente Retrofit escrito a mano,
  con kotlinx.serialization, cuesta menos. Se revisa cuando crezca.
- **Google desde la v1 (FR-026):** el flujo de hoy es web, con PKCE y una cookie (`login.py:72-109`). En una app
  nativa pide Credential Manager y un endpoint nuevo que verifique el ID token. Es un cambio de backend; ver la
  pregunta 1.
- **`usesCleartextTraffic="true"` en toda la app:** se descarta. El HTTP de desarrollo va solo en
  `src/debug/res/xml/network_security_config.xml`, para `10.0.2.2` y `localhost` con `adb reverse`.
- **Pruebas instrumentadas en el emulador de CI desde el día 1:** con Robolectric las de Compose corren en la JVM, más
  rápido. El emulador (android-emulator-runner) entra cuando haya cámara o notificaciones que probar.

## 4. Non-functional constraints

- **NFR-001 (cifrado):**
  - el token cifrado con Tink y una llave del Keystore;
  - los datos de salud solo en memoria;
  - `android:allowBackup` sin el archivo del token (la llave no sobrevive a una restauración).
- **NFR-004 (consentimiento):** nada del perfil se muestra sin consentimiento vigente. La API ya lo hace cumplir y la
  app lo respeta.
- **NFR-011:** esta es la superficie del paciente en Android que pide el PRD.
- **NFR-012 (es-MX):** textos en `res/values/strings.xml` en español; los mensajes de la API se muestran tal cual.
- **Accesibilidad:** TalkBack, con descripciones en botones e íconos, y objetivos táctiles de al menos 48 dp (la guía
  de Android; la web usa 24 px por WCAG). La paleta es D22, con el mismo azul y modo oscuro.
- **Seguridad de transporte:** HTTPS en release y HTTP solo en debug, hacia la Mac.
- **Datos de prueba:** solo cuentas `@example.com` (D19).

## 5. Classification and questions

**New:** una superficie nueva contra una API existente. No hay cambios de backend si la pregunta 1 queda en la
recomendación.

Saúl Pérez respondió las cuatro con AskUserQuestion el 2026-10-29 y eligió las recomendadas: Google después (la v1
entra con correo), el consentimiento en la app, datos básicos y estado de las secciones, y minSdk 29.

Preguntas, con la recomendación primero:
1. **Google en la v1.** (a) Solo correo y contraseña; Google entra después, con su endpoint. (b) Google desde la v1,
   con un endpoint nuevo de verificación del ID token y Credential Manager.
2. **Cuenta sin consentimiento.** (a) La app muestra el mismo texto y la misma versión, y lo registra. (b) La app
   manda a la web a aceptarlo.
3. **Qué se ve del perfil.** (a) Datos básicos (con trabajo) y el estado de cada sección, como la tarjeta de la web,
   en solo lectura. (b) Además, el detalle de cada sección en solo lectura. (c) Solo los datos básicos.
4. **Versión mínima de Android.**
   - (a) **minSdk 29 (Android 10):** al menos el 93.1 % en México (la cifra de México no baja de Android 11) y 96.2 %
     mundial. Queda arriba de todos los mínimos de las librerías.
   - (b) **minSdk 31 (Android 12):** 88.64 % en México.
   - (c) **minSdk 26:** más alcance, sin cifra exacta para México.

   En los tres casos, targetSdk y compileSdk 36.

**Pistas para el plan:**
- **Proyecto:** un solo módulo `app`, con paquetes por función (`auth`, `consent`, `profile`, `core/net`,
  `core/session`); se modulariza cuando crezca.
- **Arquitectura:** Retrofit 3, OkHttp, kotlinx.serialization y ViewModel con StateFlow. Inyección manual al inicio, en
  vez de Hilt, para no sumar curva.
- **Probar en el S26:** URL base por tipo de compilación, y `adb reverse tcp:8000 tcp:8000`.
- **Pruebas:** con MockWebServer (sin servicios reales) y Compose con Robolectric en `testDebugUnitTest`.
