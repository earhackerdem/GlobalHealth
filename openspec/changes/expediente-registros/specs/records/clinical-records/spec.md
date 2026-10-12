# records/clinical-records — delta

## Purpose

El expediente clínico del paciente: registrar diagnósticos y recetas, adjuntar documentos, y corregir o eliminar
lo propio, con el contenido clínico cifrado en reposo, aislado por cuenta y detrás del consentimiento.

## ADDED Requirements

### Requirement: El paciente registra diagnósticos y recetas en su expediente
El sistema SHALL permitir al paciente con consentimiento vigente registrar entradas clínicas de tipo diagnóstico
(fecha, profesional, notas) y de tipo receta/medicación (medicamento, dosis, vigencia), listarlas y consultarlas;
todo el contenido clínico SHALL almacenarse cifrado en reposo.

#### Scenario: Registrar un diagnóstico
- **GIVEN** una paciente autenticada con consentimiento otorgado
- **WHEN** registra el diagnóstico "Hipotiroidismo subclínico" con fecha 2026-09-30, profesional "Dra. Islas
  (endocrinología)" y nota "TSH 6.8; repetir perfil en 3 meses"
- **THEN** el registro aparece en su expediente con esos datos y tipo "diagnóstico", y responde 201 con el id

#### Scenario: Registrar una receta con dosis y vigencia
- **GIVEN** la misma paciente
- **WHEN** registra la receta "Levotiroxina 50 µg" con dosis "1 tableta en ayunas cada 24 h" y vigencia del
  2026-10-01 al 2026-12-30
- **THEN** el registro aparece con tipo "receta", medicamento, dosis y ambas fechas de vigencia

#### Scenario: El contenido clínico queda cifrado en reposo
- **GIVEN** un diagnóstico y una receta registrados con los datos de los escenarios anteriores
- **WHEN** se lee la tabla de registros directamente en la base de datos, sin pasar por la aplicación
- **THEN** notas, profesional, medicamento y dosis son ciphertext (prefijo Fernet `gAAAA`), y ninguna columna
  contiene "Hipotiroidismo" ni "Levotiroxina" en claro

#### Scenario: Sin consentimiento no entra ni un dato
- **GIVEN** un usuario autenticado que NO ha otorgado el consentimiento
- **WHEN** intenta registrar o listar entradas del expediente
- **THEN** la API responde 403 con el código `CONSENT_REQUIRED` y nada queda persistido

### Requirement: El expediente es del dueño: aislado, corregible y eliminable
El sistema SHALL devolver a cada paciente únicamente sus propios registros, SHALL permitirle corregirlos y
eliminarlos (rectificación y cancelación sobre su propio dato), y SHALL responder de forma indistinguible ante un
registro inexistente y uno ajeno.

#### Scenario: Un registro ajeno no existe para mí
- **GIVEN** la paciente A con un diagnóstico registrado y el paciente B autenticado y con consentimiento
- **WHEN** B lista su expediente y consulta, edita o elimina el registro de A por su id
- **THEN** la lista de B no contiene el registro de A y cada intento directo responde el MISMO 404 que un id
  inexistente, sin revelar que el registro de A existe

#### Scenario: Corregir y eliminar un registro propio
- **GIVEN** la paciente A con la receta de "Levotiroxina 50 µg"
- **WHEN** corrige la dosis a "1 tableta en ayunas cada 24 h, lunes a sábado" y después elimina el registro
- **THEN** la corrección se refleja al reconsultar y, tras eliminar, el registro ya no aparece en la lista ni por
  id (404), junto con sus adjuntos

### Requirement: Un registro admite documentos adjuntos (imagen o PDF)
El sistema SHALL permitir adjuntar a un registro propio documentos de tipo imagen (JPEG/PNG) o PDF dentro del
límite de tamaño fijado en el design, listarlos y descargarlos íntegros; los adjuntos SHALL almacenarse cifrados
en reposo y eliminarse junto con su registro.

#### Scenario: Adjuntar y descargar un resultado en PDF
- **GIVEN** la paciente A con su diagnóstico registrado y un archivo `perfil-tiroideo.pdf` válido
- **WHEN** lo adjunta al diagnóstico y después lo descarga
- **THEN** el adjunto aparece listado en el registro con nombre y tipo, y la descarga devuelve bytes idénticos a
  los subidos con el content-type `application/pdf`

#### Scenario: Tipo o tamaño fuera de contrato se rechaza
- **GIVEN** la paciente A con un registro propio
- **WHEN** intenta adjuntar un `.exe` renombrado o un archivo que excede el límite de tamaño
- **THEN** la API responde 4xx con mensaje es-MX, el adjunto no queda persistido y el listado del registro no
  cambia

#### Scenario: Los adjuntos quedan cifrados en reposo
- **GIVEN** el PDF adjuntado en el primer escenario
- **WHEN** se lee la tabla de adjuntos directamente en la base de datos
- **THEN** el contenido y el nombre del archivo son ciphertext, sin el magic number `%PDF` en claro
