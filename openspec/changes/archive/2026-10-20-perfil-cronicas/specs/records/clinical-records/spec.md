# Spec Delta

## MODIFIED Requirements

### Requirement: El expediente es del dueño: aislado, corregible y eliminable

El sistema SHALL devolver a cada paciente únicamente sus propios registros, SHALL permitirle corregirlos —
incluyendo agregar, editar o quitar medicinas de una receta (dejando siempre al menos una) — y eliminarlos, y
SHALL responder de forma indistinguible ante un registro inexistente y uno ajeno. Antes de eliminar un diagnóstico
que respalda enfermedades crónicas del perfil, la confirmación SHALL nombrarlas; al eliminarlo, esas crónicas SHALL
conservarse y solo perder el enlace.

#### Scenario: Un registro ajeno no existe para mí

- **GIVEN** la paciente A con una receta registrada y el paciente B autenticado y con consentimiento
- **WHEN** B lista su expediente y consulta, edita, archiva o elimina la receta de A por su id
- **THEN** la lista de B no contiene la receta de A y cada intento directo responde el MISMO 404 que un id
  inexistente, sin revelar que el registro de A existe

#### Scenario: Corregir las medicinas de una receta propia (AC-6)

- **GIVEN** la paciente A con la receta de 2 medicinas del escenario de registro
- **WHEN** corrige la frecuencia de la Levotiroxina a "cada 24 h, lunes a sábado", quita el Omeprazol y agrega
  {nombre: "Ibuprofeno 400 mg", dosis: "1 tableta por 5 días", frecuencia: "cada 8 h"}
- **THEN** al reconsultar, la receta tiene exactamente esas 2 medicinas; intentar dejar la receta sin medicinas
  responde 422 con mensaje es-MX

#### Scenario: Corregir y eliminar un registro propio

- **GIVEN** la paciente A con el diagnóstico suelto "Hipotiroidismo subclínico"
- **WHEN** corrige la nota a "TSH 6.8; repetir perfil en 3 meses, ayunas" y después lo elimina
- **THEN** la corrección se refleja al reconsultar y, tras eliminar, el registro ya no aparece en la lista ni por
  id (404)

#### Scenario: Eliminar una receta arrastra medicinas y adjuntos

- **GIVEN** la paciente A con una receta con 2 medicinas y una foto adjunta (AC-4)
- **WHEN** elimina la receta
- **THEN** la receta ya no aparece en la lista ni por id (404) y sus medicinas y adjuntos no sobreviven en la
  base de datos

#### Scenario: Eliminar un diagnóstico que respalda crónicas avisa y conserva las crónicas (B-5)

- **GIVEN** la paciente A con el diagnóstico "Hipotiroidismo subclínico", que respalda su crónica "Hipotiroidismo"
- **WHEN** abre "Eliminar registro" sobre ese diagnóstico
- **THEN** la confirmación dice que respalda su crónica "Hipotiroidismo" y que la crónica se queda sin respaldo; al
  confirmar, el diagnóstico desaparece, la crónica "Hipotiroidismo" sigue en su perfil sin "Respaldo", y el id del
  diagnóstico ya no está guardado en la crónica
