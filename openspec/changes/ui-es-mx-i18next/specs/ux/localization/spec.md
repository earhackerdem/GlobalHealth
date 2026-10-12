# ux/localization — delta

## ADDED Requirements

### Requirement: Toda pantalla visible se entrega en es-MX desde recursos de traducción
La interfaz web SHALL mostrar todo texto visible al usuario en español de México, servido desde recursos de
react-i18next (`es-MX`), sin strings de interfaz hardcodeados en los componentes.

#### Scenario: Las pantallas del template quedan en es-MX
- **GIVEN** un usuario sin sesión y otro con sesión iniciada
- **WHEN** recorren login, registro, recuperación y cambio de contraseña, panel inicial, items, administración,
  configuración y la barra lateral
- **THEN** todo texto visible (títulos, botones, etiquetas, placeholders, menús, toasts de éxito) está en es-MX,
  verificado por la suite Playwright completa asertando los textos es-MX

#### Scenario: Cero strings de interfaz hardcodeados
- **GIVEN** el código del frontend tras el cambio
- **WHEN** se inspeccionan los componentes con texto de cara al usuario
- **THEN** los textos provienen de `useTranslation`/recursos `es-MX` (se admite texto fijo solo en atributos no
  visibles como ids o rutas), verificado por revisión del diff y una búsqueda documentada en evidence.md

### Requirement: Los errores del API que ve el usuario llegan en es-MX
Los mensajes `detail` del backend que la interfaz muestra al usuario SHALL estar en español de México.

#### Scenario: Credenciales incorrectas en es-MX
- **GIVEN** un usuario que intenta iniciar sesión con contraseña equivocada
- **WHEN** el backend rechaza las credenciales
- **THEN** el toast visible muestra el mensaje en es-MX (ya no "Incorrect email or password"), verificado por
  Playwright end-to-end y por pytest sobre el `detail` de la respuesta

### Requirement: Los correos transaccionales se envían en es-MX
Los correos de alta de cuenta y de recuperación de contraseña SHALL enviarse con asunto y contenido en español de
México.

#### Scenario: Recuperación de contraseña en es-MX
- **GIVEN** un usuario registrado que solicita recuperar su contraseña
- **WHEN** llega el correo a su bandeja (Mailpit en los tests)
- **THEN** el asunto y el cuerpo están en es-MX y el enlace de restablecimiento funciona, verificado por el flujo
  Playwright de reset-password leyendo el correo desde Mailpit
