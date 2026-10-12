# identity/user-auth Specification

## Purpose
Registro e inicio de sesión del paciente (correo/contraseña y Google OIDC), con los datos de cada cuenta aislados
de cualquier otra.
## Requirements
### Requirement: Registro con correo y contraseña
El sistema SHALL permitir crear una cuenta de paciente con correo y contraseña e iniciar sesión con esas credenciales.

#### Scenario: Alta exitosa con correo
- **GIVEN** no existe cuenta para `saul@example.com`
- **WHEN** se registra con `saul@example.com` y una contraseña válida
- **THEN** la cuenta queda creada y puede iniciar sesión con esas credenciales

#### Scenario: Correo ya registrado
- **GIVEN** ya existe una cuenta para `saul@example.com`
- **WHEN** alguien intenta registrarse con `saul@example.com`
- **THEN** el alta se rechaza sin revelar datos de la cuenta existente

### Requirement: Registro e inicio de sesión con Google
El sistema SHALL permitir crear la cuenta e iniciar sesión mediante la cuenta de Google del paciente (OIDC),
usando a Google únicamente como proveedor de identidad.

#### Scenario: Alta con Google
- **GIVEN** no existe cuenta para `saul@gmail.com` y el paciente tiene esa cuenta de Google
- **WHEN** elige "Continuar con Google" y autoriza
- **THEN** la cuenta queda creada sin contraseña local y la sesión iniciada

#### Scenario: Google con correo ya registrado por contraseña
- **GIVEN** existe una cuenta creada con correo/contraseña para `saul@gmail.com`
- **WHEN** inicia con Google y Google reporta ese correo como verificado
- **THEN** accede a la misma cuenta (no se crea una cuenta duplicada)

### Requirement: Aislamiento de datos por cuenta
El sistema SHALL garantizar que ninguna operación de una cuenta lea o modifique recursos de otra cuenta.

#### Scenario: Acceso a recurso ajeno por identificador
- **GIVEN** la cuenta A y la cuenta B existen y B posee el recurso con id `r-123`
- **WHEN** la cuenta A solicita `r-123`
- **THEN** la respuesta es un error de no-encontrado/no-autorizado y el recurso no se expone

#### Scenario: Listados solo propios
- **GIVEN** la cuenta A tiene 2 registros y la cuenta B tiene 3
- **WHEN** la cuenta A lista sus registros
- **THEN** recibe exactamente sus 2 registros y ninguno de B
