# privacy/consent Specification

## Purpose
Consentimiento expreso para el tratamiento de datos personales sensibles (salud): se recaba antes de capturar el
primer dato, con evidencia conservada y consultable (LFPDPPP art. 9; NFR-004 del technical brief).
## Requirements
### Requirement: Ningún dato de salud sin consentimiento previo
El sistema SHALL rechazar la captura de cualquier dato de salud de una cuenta que no tenga consentimiento expreso
vigente registrado.

#### Scenario: Intento de captura sin consentimiento
- **GIVEN** una cuenta recién creada (por correo o por Google) que no ha otorgado consentimiento
- **WHEN** intenta guardar un dato de salud (p.ej. un diagnóstico)
- **THEN** la operación se rechaza indicando que primero debe otorgar el consentimiento

### Requirement: Otorgamiento con evidencia conservada
El sistema SHALL registrar, al otorgarse el consentimiento, la versión exacta del texto aceptado, la fecha y hora,
y el método de autenticación de la sesión, y SHALL conservar ese registro.

#### Scenario: Otorgamiento en el alta
- **GIVEN** una cuenta creada el 2026-10-11 que ve el texto de consentimiento versión `v1`
- **WHEN** acepta explícitamente el tratamiento de datos sensibles
- **THEN** queda registrado `{versión: v1, timestamp, método de sesión}` y la captura de datos de salud se habilita

#### Scenario: El consentimiento es consultable por el titular
- **GIVEN** una cuenta que otorgó el consentimiento `v1` el 2026-10-11
- **WHEN** el paciente consulta su estado de consentimiento
- **THEN** ve la versión aceptada y la fecha del otorgamiento

### Requirement: Mismo consentimiento en ambos flujos de alta
El sistema SHALL recabar el consentimiento expreso igual en el alta con correo/contraseña y en el alta con Google;
el inicio de sesión social no lo sustituye.

#### Scenario: Alta con Google no implica consentimiento
- **GIVEN** un paciente que completó el alta con Google
- **WHEN** llega al expediente sin haber aceptado el texto de consentimiento
- **THEN** la captura de datos de salud sigue bloqueada hasta que lo acepte

