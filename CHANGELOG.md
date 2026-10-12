# CHANGELOG

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
