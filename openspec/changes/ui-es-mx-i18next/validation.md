# Validación (no técnica) — ui-es-mx-i18next

**Qué cambió, en una frase:** toda la aplicación —pantallas, mensajes de error y éxito, y los correos que envía—
está ahora en español de México.

## Cómo comprobarlo tú mismo (5 minutos)

1. Abre la app y recorre sin sesión: login, "Regístrate", "¿Olvidaste tu contraseña?" — todo en español,
   incluidos los mensajes de validación (deja un campo vacío y envía).
2. Equivócate de contraseña a propósito: el aviso dice "Correo o contraseña incorrectos".
3. Entra con tu cuenta y recorre: panel ("¡Qué gusto verte de nuevo!"), Elementos, Administración, Configuración,
   menú lateral y el menú de tu usuario.
4. Pide recuperar contraseña con un correo registrado y revisa la bandeja (Mailpit en dev,
   http://localhost:8025): asunto y correo en español, botón "Restablecer contraseña" funcional.
5. El texto del acuerdo de consentimiento es EXACTAMENTE el mismo que aceptaste (solo cambió de lugar en el
   código, no de redacción).

## Qué NO cambió

- Ningún comportamiento: mismos flujos, mismos permisos, mismos códigos de error para integraciones.
- El inglés no desapareció del código interno (logs del servidor, documentación técnica): solo lo que ve el
  usuario.
