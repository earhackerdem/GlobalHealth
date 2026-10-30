# clients/android-app Specification

## Purpose
TBD - created by archiving change android-base. Update Purpose after archive.
## Requirements
### Requirement: App de Android del paciente
El sistema SHALL ofrecer al paciente una app de Android nativa (D24), en español de México, para Android 10 (API 29) o
más reciente. La app SHALL hablar con la misma API que la web (`/api/v1`) y no SHALL tener servidor propio. En las
compilaciones de prueba SHALL poder apuntar a la API de la computadora de desarrollo: `10.0.2.2:8000` desde el
emulador, `localhost:8000` desde un teléfono con `adb reverse`. Solo esas compilaciones SHALL permitir HTTP sin
cifrar, y solo hacia esas dos direcciones.

#### Scenario: Abrir la app por primera vez (AB-1)
- **GIVEN** la app recién instalada en un teléfono con Android 10 o más reciente
- **WHEN** el paciente la abre
- **THEN** ve la pantalla de entrada con «Correo electrónico», «Contraseña» y «Entrar», en español

### Requirement: Entrar con correo y contraseña
La app SHALL permitir entrar con el correo y la contraseña de una cuenta existente (`POST /login/access-token`). Ante
un rechazo SHALL mostrar el mensaje de la API («Correo o contraseña incorrectos»). Mientras envía, o mientras el correo
o la contraseña estén vacíos, «Entrar» SHALL no estar disponible (D20). No SHALL ofrecer entrar con Google ni crear cuentas: eso queda para cambios propios.

#### Scenario: Entrar con una cuenta con consentimiento (AB-2)
- **GIVEN** la cuenta `paciente.android@example.com` con consentimiento vigente
- **WHEN** escribe su correo y su contraseña y toca «Entrar»
- **THEN** llega a «Mi perfil médico»

#### Scenario: Contraseña equivocada (AB-2)
- **WHEN** escribe una contraseña equivocada y toca «Entrar»
- **THEN** ve «Correo o contraseña incorrectos» y sigue en la pantalla de entrada, sin sesión guardada

### Requirement: Consentimiento antes de cualquier dato
Si la API responde que falta el consentimiento (403 `CONSENT_REQUIRED`), la app SHALL mostrar el texto vigente del
consentimiento (`GET /consent/text`), con su versión, y los botones «Acepto» y «Cerrar sesión». Al aceptar SHALL
registrarlo (`POST /consent/` con esa versión) y seguir al perfil. Mientras no lo acepte, la app NO SHALL mostrar
ningún dato del perfil.

#### Scenario: Cuenta sin consentimiento (AB-3)
- **GIVEN** la cuenta `sin.consentimiento@example.com` sin consentimiento
- **WHEN** entra
- **THEN** ve el texto del consentimiento versión «v1» y ningún dato del perfil; al tocar «Acepto» queda registrado y
  llega a «Mi perfil médico»

### Requirement: Mi perfil médico en solo lectura
La app SHALL mostrar en solo lectura:
- **Datos básicos:** fecha de nacimiento con la edad, sexo, alergias a medicamentos, el último peso y la última
  estatura con su fecha, y el trabajo con el mismo resumen que la web; cada dato sin registrar dice «Sin registrar».
- **Antecedentes familiares:** cuántos hay registrados, o «Sin registros».
- **Las seis secciones del historial**, cada una con su estado como en la web:
  - enfermedades crónicas; enfermedades pasadas e infecciosas; cirugías y hospitalizaciones; fracturas y lesiones;
    transfusiones y grupo sanguíneo: «1 registro», «N registros», «Ninguna» o «Sin llenar»;
  - hábitos: «Con datos» o «Sin llenar».

La app NO SHALL permitir editar nada en este cambio y NO SHALL calcular ningún riesgo ni veredicto.

#### Scenario: Perfil con datos (AB-4)
- **GIVEN** una cuenta con fecha de nacimiento 1990-03-15 y fecha actual 2026-10-29, sexo «Mujer», alergias
  «Penicilina», trabajo «Chofer de transporte» rotativo con ruido fuerte, dos enfermedades pasadas, «Ninguna» en
  transfusiones y sin hábitos
- **WHEN** abre «Mi perfil médico»
- **THEN** ve «15/03/1990 · 36 años», «Mujer», «Penicilina», «Chofer de transporte · rotativo · expuesto a ruido
  fuerte», «2 registros» en enfermedades pasadas, «Ninguna» en transfusiones y «Sin llenar» en hábitos y en las
  demás secciones

### Requirement: Sesión guardada sin datos de salud en el teléfono
La app SHALL guardar el token de la sesión cifrado con una llave del Android Keystore (DataStore con Tink), fuera del
respaldo automático. Si el Keystore del teléfono no se puede usar, NO SHALL guardar el token en disco: la sesión dura
mientras la app esté abierta. Si la llave guardada ya no se puede leer, SHALL descartar la sesión guardada y pedir
entrar de nuevo, sin cerrarse. NO SHALL guardar datos del perfil en el teléfono: los pide a la API cada vez. Al
volver a abrir la app con un token guardado SHALL ir directo al perfil. «Cerrar sesión» SHALL borrar el token. Un 401
de la API, o un 403 que no sea `CONSENT_REQUIRED` (así responde la API a un token vencido o inválido:
`backend/app/api/deps.py:38-42`), SHALL borrar el token y volver a la pantalla de entrada.

#### Scenario: Volver a abrir la app (AB-5)
- **GIVEN** el paciente entró y cerró la app
- **WHEN** la vuelve a abrir
- **THEN** llega a «Mi perfil médico» sin volver a escribir su contraseña

#### Scenario: Cerrar sesión y token vencido (AB-5)
- **WHEN** toca «Cerrar sesión», o la API responde a cualquier pedido con 401 o con 403 «No se pudieron validar las
  credenciales»
- **THEN** el token se borra y ve la pantalla de entrada

#### Scenario: Nada en claro en el teléfono (AB-6)
- **GIVEN** el paciente entró y vio su perfil
- **WHEN** se leen los archivos de la app en el teléfono
- **THEN** el token no aparece en claro en ninguno y ningún dato del perfil está guardado

### Requirement: Sin conexión
Si no hay red, la API no responde o responde 502, 503 o 504, la app SHALL mostrar «No pudimos conectar. Revisa tu conexión e intenta de
nuevo.» con un botón «Reintentar», sin perder la sesión.

#### Scenario: La API no responde (AB-7)
- **GIVEN** el paciente con sesión y la API apagada
- **WHEN** abre «Mi perfil médico»
- **THEN** ve el mensaje y «Reintentar»; con la API de vuelta, «Reintentar» muestra el perfil
