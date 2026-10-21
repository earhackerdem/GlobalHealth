# CHANGELOG

- 2026-10-20 · perfil-cronicas · PR #26 · Enfermedades crónicas (FR-028, Story B): la tarjeta ya se abre y se llena.
  Se elige la condición en chips (lista frecuente, "Salud mental y adicciones" u "Otra"), con la marca "Sensible"
  que decide el paciente (viene prendida en salud mental y adicciones), "Activa" o "Ya no la tengo" con desde y
  hasta, tratamiento, nota y el diagnóstico del expediente que la respalda. Al borrar ese diagnóstico, el aviso
  nombra las crónicas que respalda y estas se quedan, sin respaldo. Todo cifrado en reposo y aislado por cuenta.
  Endurecido por una revisión adversarial de tres rondas. Hábitos (Story C) sigue pendiente.

- 2026-10-20 · perfil-eventos · PR #20 · Historial por secciones (FR-028, Story A): enfermedades pasadas e
  infecciosas, cirugías y hospitalizaciones, fracturas y lesiones, y transfusiones con grupo sanguíneo ya se pueden
  llenar. "Cuándo" se contesta como lo pregunta el médico: la edad, la etapa escolar o el año, y la app calcula el año
  aproximado. Cada sección se puede marcar "No he tenido ninguna", y cada tarjeta de "Mi perfil médico" dice cómo va.
  Todo cifrado en reposo y aislado por cuenta; accesible con teclado y lector de pantalla, también en celular.
  Crónicas (Story B) y hábitos (Story C) siguen pendientes.

- 2026-10-19 · onboarding-perfil · PR #16 · Onboarding de perfil médico post-consentimiento: fecha de nacimiento, sexo, peso/estatura con historial, y antecedentes familiares (diabetes, cáncer, etc.) con parentesco distinguido (paterno/materno) y nota por condición. Wizard de 3 pasos con opción de omitir (lleva directo al expediente, no se repite). Perfil completo editable tras el onboarding con 6 secciones adicionales visibles sin captura (crónicas, hepatitis/pasadas, cirugías, fracturas, transfusiones, hábitos). Todo cifrado en reposo, aislado por cuenta, con validaciones es-MX (fechas futuras rechazadas, peso/estatura implausibles con mensaje). Tests: backend 94% cobertura (10 tests de API + 1 de migración), frontend suite completa en escritorio y móvil (384×832 viewport real). Hallazgo lateral: sr-only del SidebarTrigger usa estado de escritorio (anotado en inbox para quirk posterior).

- 2026-10-19 · receta-mexicana · PR #13 · La receta es a la mexicana: varias medicinas por receta (dosis,
  frecuencia y vía opcionales por medicina), sin vigencia obligatoria, diagnóstico opcional y diagnóstico suelto
  con estado "sin confirmar"; archivar/desarchivar cuando el tratamiento termina; detalle en solo lectura con
  edición deliberada (confirmación en ambos caminos) y adjunto opcional desde la creación; notas multilínea; el
  modal sobrevive al cambio de pestaña. Migración que pliega los datos existentes sin destruir nada (y aborta
  ante llave de cifrado equivocada — crítico del review adversarial, aplicado al 100% junto con el resto de
  hallazgos aprobados). E2e corriendo también en el viewport del dispositivo real de pruebas (384×832).

- 2026-10-18 · expediente-registros · PR #6 · El paciente registra su expediente real: diagnósticos (fecha,
  profesional, notas) y recetas (medicamento, dosis, vigencia), corrige y elimina lo propio (ARCO), y adjunta
  imágenes o PDF que se descargan íntegros; todo el texto clínico y los archivos quedan cifrados en reposo y
  aislados por cuenta (ADR D16: adjuntos en Postgres, sin servicios nuevos). Pantalla "Expediente" completa en
  es-MX con la suite Playwright como contrato. Endurecido por revisión adversarial aplicada al 100% (PR #6) y
  acompañado por: variables de Google al backend Docker (PR #7) y comandos make del proyecto (PR #8).

- 2026-10-12 · cuenta-consentimiento · PR #1 · El paciente puede crear su cuenta con Google o con
  correo/contraseña, otorgando consentimiento expreso (LFPDPPP) cuya evidencia se conserva; sus datos quedan
  aislados por cuenta y los campos sensibles cifrados en reposo. Incluye el esqueleto del producto (template
  full-stack FastAPI) con CI completo. Flujo OAuth endurecido por revisión adversarial (state anti-CSRF, PKCE
  estricto, claves de cifrado por propósito con rotación — ADR D13).

- 2026-10-12 · ui-es-mx-i18next · PR #4 · Toda la interfaz queda en español de México (NFR-012): pantallas,
  menús, validaciones, toasts (incluidos los errores del API), página 404, títulos de pestaña y los correos de
  alta y recuperación de contraseña. Los textos viven en recursos react-i18next (7 namespaces es-MX) y la suite
  Playwright los asierta como contrato del idioma (ADR D15). Infraestructura lista para un segundo idioma.

- 2026-10-12 · bd-pruebas-docker · PR #2 · Las pruebas automáticas del backend corren contra una base de datos
  de prueba efímera en Docker (db-test, tmpfs) y se niegan a ejecutar contra cualquier otra: los datos de
  desarrollo ya no pueden ser leídos ni borrados por la suite. La BD de prueba se automigra sola; CI corre
  contra ella y los workflows ahora disparan en main (ADR D14). Incluye el archivado de cuenta-consentimiento.
