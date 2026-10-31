# Proposal

Origin: `memory/decisions/D24-app-android-nativa-kotlin-compose.md` (v1 «hardware primero», primera historia) ·
`product/prd.md` NFR-011 (paciente en Android) · FR-001..004 (cuenta, consentimiento, aislamiento) y la pantalla «Mi
perfil médico» de FR-027/FR-028, de solo lectura
Triage: change. Es la primera historia de la app de Android. Toca `code` nuevo (`android/`), suma esa ruta a
`harness.json` y agrega un workflow de CI. Las historias que siguen (cámara, recordatorios) van en sus propios
cambios (D24).

## Why

Saúl Pérez decidió una app de Android nativa para aprovechar el hardware del teléfono (D24). Antes de la cámara y
los recordatorios, la app necesita su base:
- el proyecto en `android/` que compila y se instala en el S26 Ultra;
- entrar con la cuenta de siempre contra la misma API;
- el consentimiento (NFR-004);
- guardar la sesión sin dejar datos de salud en claro en el teléfono (NFR-001);
- una primera pantalla con datos reales: el perfil médico, en solo lectura.

## User story

Como paciente, quiero entrar a GlobalHealth desde una app en mi teléfono Android y ver mi perfil médico, para tener
mis datos a la mano y que la app quede lista para usar la cámara y los recordatorios.

## Acceptance criteria (borrador; los Given/When/Then con datos van en la spec delta tras las preguntas de la exploración)

- **AB-1 Instalar y abrir:** la app se instala por `adb` en el S26 Ultra (y en el emulador) y abre en la pantalla
  de entrada, en español de México.
- **AB-2 Entrar:** con el correo y la contraseña de una cuenta existente entro y llego a mi perfil. Si me equivoco,
  veo «Correo o contraseña incorrectos», el mismo texto de la API.
- **AB-3 Consentimiento:** si mi cuenta no tiene consentimiento vigente, la app me lo pide antes de mostrar cualquier
  dato, con el mismo texto y la misma versión que la web (`GET /consent/text`). Al aceptarlo queda registrado.
- **AB-4 Ver mi perfil:** veo mis datos básicos (fecha de nacimiento y edad, sexo, alergias, peso, estatura,
  trabajo) y el estado de cada sección del historial, igual que en la web y en solo lectura.
- **AB-5 Sesión:** si cierro y vuelvo a abrir la app sigo dentro. «Cerrar sesión» borra el token. Con el token
  vencido o rechazado (401, o el 403 «No se pudieron validar las credenciales» con que la API responde a un token
  vencido) vuelvo a la pantalla de entrada.
- **AB-6 Nada en claro:** el token se guarda cifrado con una llave del Android Keystore, y los datos de salud no se
  guardan en el teléfono (o se guardan cifrados).
- **AB-7 Sin red:** si no hay conexión o la API no responde, veo un mensaje en español y puedo reintentar.
- **AB-8 CI:** un workflow compila la app y corre sus pruebas solo cuando cambia `android/**`, con el mismo patrón que
  los demás (PR #43).

## What Changes

- Nuevo `android/`: proyecto Gradle (Kotlin y Jetpack Compose) con la app, sus pruebas unitarias y de UI, y un
  cliente de la API.
- `harness.json`: `code` suma `android/` y `tests` suma las rutas de pruebas de Android.
- Nuevo `.github/workflows/test-android.yml`.

## Capabilities

### New Capabilities
- `clients/android-app`: la app de Android del paciente (entrada, consentimiento, sesión, perfil en solo lectura).

### Modified Capabilities
Ninguna. La API no cambia.

## Impact

- **Backend:** ninguno (usa `/login/access-token`, `/consent`, `/consent/text`, `/profile`, `/profile/work`,
  `/profile/history`, `/profile/habits`, `/profile/family-history`).
- **Fuera:**
  - la cámara (FR-007) y los recordatorios (FR-025), que van en cambios propios;
  - editar el perfil;
  - Google (FR-026, sujeto a la pregunta de la exploración);
  - el registro de cuentas nuevas desde la app;
  - Play Console;
  - iPhone.
