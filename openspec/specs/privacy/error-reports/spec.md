# privacy/error-reports Specification

## Purpose
Lo que un error de la API (de validación o inesperado) puede devolver, escribir en el log o mandar al servicio de
reportes: nunca el dato recibido ni datos de salud (NFR-001; deudas B1 y S2, api-errores-sin-datos, 2026-10-31).
## Requirements
### Requirement: Un dato rechazado no se devuelve ni se escribe en el log
El sistema SHALL responder 422 a un cuerpo JSON con datos inválidos, incluido un texto con un surrogate UTF-16 suelto
(escape `\ud800`), con
`detail` como lista de errores (`loc`, `msg`, `type`). La respuesta SHALL ser UTF-8 válido y SHALL NOT incluir el
campo `input` con el valor recibido, y el sistema SHALL NOT escribir ese valor en sus logs. (Un cuerpo que ni
siquiera se puede leer como JSON, con bytes inválidos, recibe el 400 de FastAPI sin eco.)

#### Scenario: Texto con un surrogate suelto en el alta
- **GIVEN** una persona sin sesión
- **WHEN** envía `POST /api/v1/users/signup` con `full_name` igual a `"Dato-Prueba-B1"` seguido de `\ud800`
- **THEN** recibe 422 con un error cuyo `loc` es `["body", "full_name"]`, sin `input`, y ningún log del proceso
  contiene `Dato-Prueba-B1`

#### Scenario: Un 422 ordinario conserva su forma y pierde el eco
- **GIVEN** una persona sin sesión
- **WHEN** envía el alta con `email` igual a `"sin-arroba"` y `password` igual a `"x"`
- **THEN** recibe 422 con dos errores, `loc` `["body", "email"]` y `["body", "password"]`, cada uno con `msg` y
  `type`, y ninguno con `input`

#### Scenario: Una clave desconocida con un surrogate suelto
- **GIVEN** una persona con sesión y consentimiento vigente
- **WHEN** guarda sus hábitos (`PUT /api/v1/profile/habits`) con una clave extra cuyo nombre es `"x\ud800"`
- **THEN** recibe 422 y el cuerpo de la respuesta se decodifica como UTF-8 sin error

### Requirement: Los reportes de errores no llevan datos de salud
Cuando el reporte de errores a Sentry está activo, el evento de un error inesperado SHALL incluir el tipo de la
excepción y la ruta, y SHALL NOT incluir el cuerpo de la petición, las variables locales de los frames ni el token
de la sesión.

#### Scenario: Falla inesperada al guardar un antecedente
- **GIVEN** el reporte a Sentry activo y una persona con consentimiento vigente
- **WHEN** guarda un antecedente personal (`POST /api/v1/profile/history`) con `other_text` igual a un texto único
  de prueba y el guardado falla con `RuntimeError`
- **THEN** la API responde 500, se genera un evento con la excepción `RuntimeError`, y ni el texto de prueba ni el
  token aparecen en ninguna parte del evento
