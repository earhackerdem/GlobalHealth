# records/clinical-records — delta: receta a la mexicana

## MODIFIED Requirements

### Requirement: El paciente registra diagnósticos y recetas en su expediente

El sistema SHALL permitir al paciente con consentimiento vigente registrar entradas clínicas de dos tipos:
**receta** — fecha de expedición, médico, diagnóstico opcional, notas opcionales y una lista de **1..N medicinas**
(cada una con nombre, dosis/indicación, y opcionalmente frecuencia de toma y vía de administración) — y
**diagnóstico** suelto (fecha, profesional, notas). La receta NO SHALL exigir vigencia ni diagnóstico. Todo el
contenido clínico (medicinas, médico, diagnóstico, notas) SHALL almacenarse cifrado en reposo.

#### Scenario: Registrar una receta con varias medicinas (AC-1)

- **GIVEN** una paciente autenticada con consentimiento otorgado
- **WHEN** registra una receta del 2026-10-12 del médico "Dra. Islas (endocrinología)" con las medicinas
  [{nombre: "Levotiroxina 50 µg", dosis: "1 tableta en ayunas", frecuencia: "cada 24 h"},
  {nombre: "Omeprazol 20 mg", dosis: "1 cápsula antes del desayuno por 14 días"}] y sin diagnóstico
- **THEN** responde 201 con el id; el registro aparece en su expediente con tipo "receta", las 2 medicinas en
  orden, la fecha y el médico, y sin campo alguno de vigencia

#### Scenario: El diagnóstico de la receta es opcional (AC-3) y la frecuencia por medicina también (AC-9)

- **GIVEN** la misma paciente
- **WHEN** registra una receta con una sola medicina sin frecuencia y sin diagnóstico, y otra igual pero con
  diagnóstico "faringitis" y frecuencia "cada 8 h"
- **THEN** ambas responden 201; la primera se consulta sin diagnóstico ni frecuencia (campos ausentes o nulos,
  nunca inventados) y la segunda devuelve exactamente los valores capturados

#### Scenario: Una receta sin medicinas se rechaza (AC-1)

- **GIVEN** la misma paciente
- **WHEN** intenta registrar una receta con la lista de medicinas vacía, o una medicina sin nombre
- **THEN** la API responde 422 con mensaje es-MX y nada queda persistido

#### Scenario: Registrar un diagnóstico

- **GIVEN** la misma paciente
- **WHEN** registra el diagnóstico "Hipotiroidismo subclínico" con fecha 2026-09-30, profesional "Dra. Islas
  (endocrinología)" y nota "TSH 6.8; repetir perfil en 3 meses", sin receta ni documento que lo respalde
- **THEN** el registro aparece en su expediente con tipo "diagnóstico" y responde 201 con el id

#### Scenario: Registrar una receta con dosis y vigencia

- **GIVEN** la misma paciente (escenario re-propuesto: documenta el retiro del modelo viejo, Q1-A)
- **WHEN** envía el payload de la versión anterior — receta con `dose` y vigencia `valid_from`/`valid_to` al
  nivel del registro y sin lista de medicinas
- **THEN** la API responde 422 con mensaje es-MX: la dosis vive ahora en cada medicina y la vigencia ya no existe

#### Scenario: El contenido clínico queda cifrado en reposo

- **GIVEN** la receta y el diagnóstico de los escenarios anteriores
- **WHEN** se lee la base de datos directamente, sin pasar por la aplicación
- **THEN** nombres y dosis de medicinas, médico, diagnóstico y notas son ciphertext (prefijo Fernet `gAAAA`) y
  ninguna columna contiene "Levotiroxina" ni "Hipotiroidismo" en claro

#### Scenario: Sin consentimiento no entra ni un dato

- **GIVEN** un usuario autenticado que NO ha otorgado el consentimiento
- **WHEN** intenta registrar o listar entradas del expediente
- **THEN** la API responde 403 con el código `CONSENT_REQUIRED` y nada queda persistido

### Requirement: El expediente es del dueño: aislado, corregible y eliminable

El sistema SHALL devolver a cada paciente únicamente sus propios registros, SHALL permitirle corregirlos —
incluyendo agregar, editar o quitar medicinas de una receta (dejando siempre al menos una) — y eliminarlos, y
SHALL responder de forma indistinguible ante un registro inexistente y uno ajeno.

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

## ADDED Requirements

### Requirement: La receta se archiva manualmente cuando el tratamiento termina

El sistema SHALL permitir al paciente marcar una receta propia como archivada y revertirlo; la lista del
expediente SHALL distinguir activas de archivadas (las archivadas no aparecen entre las activas, siguen
consultables y conservan sus adjuntos). Archivar NO SHALL ser automático: no existe vigencia (Q1-A; la vigencia
derivada queda diferida en memory/inbox.md).

#### Scenario: Archivar una receta activa (AC-8)

- **GIVEN** la paciente A con una receta activa
- **WHEN** la marca como archivada ("tratamiento terminado")
- **THEN** la receta deja de aparecer entre las activas, aparece como archivada, y sigue consultable por id con
  sus medicinas y adjuntos intactos

#### Scenario: Desarchivar devuelve la receta a activas

- **GIVEN** la receta archivada del escenario anterior
- **WHEN** la paciente revierte el archivado
- **THEN** la receta vuelve a aparecer entre las activas sin pérdida de datos

### Requirement: El diagnóstico suelto muestra su estado de confirmación

Todo diagnóstico suelto SHALL exponer un estado de confirmación, con valor inicial "sin confirmar"; en esta
versión NO existe operación para confirmarlo (el flujo de confirmación por un médico vía enlace llega con E3/E4,
según product/roles-permisos.md: el paciente no se autoconfirma).

#### Scenario: Un diagnóstico nuevo nace sin confirmar

- **GIVEN** la paciente A registra un diagnóstico suelto
- **WHEN** lo consulta en la lista y por id
- **THEN** el diagnóstico muestra estado "sin confirmar" y la API no ofrece operación alguna para cambiarlo
