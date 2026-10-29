# ux/visual-accessibility Specification

## Purpose
TBD - created by archiving change paleta-azul-clinico. Update Purpose after archive.
## Requirements
### Requirement: La paleta de la app pasa WCAG 2.2 AA en claro y en oscuro
La interfaz web SHALL usar la paleta B · Azul clínico de D22. El color de marca SHALL ser `#005eb8` en modo claro y
`#5aa9f0` en modo oscuro.

En los dos modos SHALL cumplirse:
- todo texto que se mide (normal, secundario, del botón principal, del chip elegido y mensajes de error) mide al
  menos 4.5:1 contra su fondo efectivo;
- el borde de los campos de texto, de las casillas sin marcar y de los chips sin elegir mide al menos 3:1 contra el
  fondo que los rodea.

El fondo efectivo es el primer fondo no transparente del elemento o de sus ancestros.

#### Scenario: Texto legible en claro (P-1)
- **GIVEN** un paciente con sesión, en modo claro, en «Mi perfil médico › Hábitos»
- **WHEN** marca «Caminar» en Ejercicio, elige «No» en un chip y pulsa «Guardar» sin contestar «Días por semana»
- **THEN** cada uno mide al menos 4.5:1 contra su fondo efectivo:
  - el título «Hábitos»;
  - el texto de introducción de la pantalla, que es texto secundario;
  - el texto de «Guardar» contra el fondo del botón;
  - el texto del chip elegido contra el suyo;
  - «Contesta esta pregunta.»

#### Scenario: Controles visibles en claro (P-2)
- **GIVEN** la misma pantalla en modo claro, con «Caminar» marcada
- **WHEN** se mide el borde de «Días por semana», el de la casilla «Correr» sin marcar y el de un chip sin elegir
- **THEN** cada borde mide al menos 3:1 contra el fondo efectivo de su contenedor

#### Scenario: Lo mismo en oscuro, con la marca de D22 (P-5)
- **GIVEN** el mismo paciente con el tema «oscuro» elegido
- **WHEN** repite los dos escenarios anteriores
- **THEN** se cumplen los mismos umbrales
- **AND** el fondo del botón «Guardar» es `#5aa9f0` en oscuro y `#005eb8` en claro

#### Scenario: El error no se dice solo con color (P-3)
- **GIVEN** «Caminar» marcada sin «Días por semana»
- **WHEN** el paciente pulsa «Guardar»
- **THEN** junto al campo aparece el texto «Contesta esta pregunta.»
- **AND** el campo lleva `aria-invalid="true"`

#### Scenario: Se distingue con daltonismo emulado (P-4)
- **GIVEN** la pantalla de hábitos con un chip elegido, una casilla marcada y un error a la vista
- **WHEN** quien valida emula deuteranopía, protanopía y tritanopía en Chrome (DevTools › Rendering › Emulate vision
  deficiencies)
- **THEN** en cada emulación se distingue el chip elegido de los demás, la casilla marcada de la no marcada, y el
  campo con error de los demás

### Requirement: Casillas de 20 px y la pregunta por encima de sus opciones
Las casillas de la app (`Checkbox`) SHALL medir 20 × 20 px. En una lista con casillas que abren preguntas, la pregunta
del grupo (`legend`) SHALL ir en negritas, con peso de al menos 600, y la etiqueta de cada opción SHALL ir en peso
normal (400), para que la pregunta pese más que sus opciones.

#### Scenario: Casillas y jerarquía en Ejercicio (P-6)
- **GIVEN** un paciente en «Mi perfil médico › Hábitos»
- **WHEN** mira el grupo «¿Qué ejercicio haces?»
- **THEN** la casilla «Caminar» mide 20 × 20 px
- **AND** la etiqueta «Caminar» tiene peso 400
- **AND** «¿Qué ejercicio haces?» tiene peso de al menos 600
