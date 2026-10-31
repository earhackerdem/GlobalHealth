# platform/database Specification

## Purpose
Lo que la base de datos garantiza al resto del sistema: los valores no salen en los errores, los textos en claro se
pueden guardar, toda llave foránea tiene índice y un enlace entre registros nunca queda colgando
(bd-candados-indices-y-log, 2026-10-31).
## Requirements
### Requirement: Los valores de una consulta no salen en los errores
El sistema SHALL ocultar los parámetros de las consultas en los errores de base de datos, de modo que ni el log ni el
mensaje de la excepción (lo que recibiría el reporte de errores) lleven los valores.

#### Scenario: Error de base de datos con un valor de prueba
- **GIVEN** una consulta con el parámetro `"Valor-Prueba-M1"` que la base rechaza
- **WHEN** falla
- **THEN** el mensaje de la excepción no contiene `Valor-Prueba-M1`

### Requirement: Un carácter nulo en un texto en claro se rechaza
El sistema SHALL rechazar con 422 un texto con el carácter NUL (U+0000) en los campos que se guardan sin cifrar (nombre
y correo de la cuenta, título y descripción de un elemento), y SHALL responder al login con un `username` que lo
contenga igual que a unas credenciales incorrectas.

#### Scenario: Nombre con NUL en el alta
- **WHEN** una persona se da de alta con `full_name` igual a `"Nombre"` seguido de `\u0000`
- **THEN** recibe 422 y no se crea la cuenta

#### Scenario: Nombre con NUL al editar la cuenta
- **GIVEN** una persona con sesión
- **WHEN** cambia su `full_name` a uno que contiene `\u0000`
- **THEN** recibe 422 y su nombre no cambia

#### Scenario: NUL en el login
- **WHEN** alguien inicia sesión con `username` igual a `"correo"` seguido de `\u0000`
- **THEN** recibe 400 «Correo o contraseña incorrectos», como con cualquier credencial incorrecta

#### Scenario: NUL en un elemento
- **GIVEN** una persona con sesión
- **WHEN** crea un elemento con `title` que contiene `\u0000`
- **THEN** recibe 422 y no se crea

### Requirement: Cada llave foránea tiene índice
Toda llave foránea de la base SHALL tener un índice cuya primera columna sea la de la llave.

#### Scenario: Catálogo de la base migrada
- **GIVEN** la base migrada a la última versión
- **WHEN** se buscan llaves foráneas sin índice en `pg_constraint` y `pg_index`
- **THEN** no hay ninguna

### Requirement: Un enlace a un diagnóstico nunca queda colgando
Guardar una enfermedad crónica enlazada a un diagnóstico y borrar ese diagnóstico, a la vez, SHALL terminar en uno de
dos estados: la crónica se guarda y queda sin enlace, o se rechaza con «Ese diagnóstico no está en tu expediente».
Nunca SHALL quedar una crónica que apunte a un diagnóstico borrado.

#### Scenario: Primer guardado sin perfil contra el borrado del diagnóstico
- **GIVEN** una persona con consentimiento, un diagnóstico en su expediente y todavía sin perfil
- **WHEN** el DELETE del diagnóstico ya desenlazó las crónicas pero no ha confirmado, y en ese momento llega el POST
  de una crónica enlazada a ese diagnóstico
- **THEN** al terminar los dos, ninguna crónica apunta al diagnóstico borrado
