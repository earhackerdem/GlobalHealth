# Validación — los errores de la API no repiten tus datos

Para: Saúl Pérez. Unos 3 minutos en la terminal, con la app levantada (`make up`). En pantalla no cambia nada: el
cambio está en lo que la API contesta cuando le llega algo mal escrito.

## 1 · Un texto roto ya no tumba la API ni queda en el registro
1. Copia y pega:
   `curl -s -X POST localhost:8000/api/v1/users/signup -H 'content-type: application/json' --data-binary '{"email":"prueba@example.com","password":"contrasena-larga","full_name":"Texto-Prueba\ud800"}'`
- [ ] La respuesta empieza con `{"detail":[` (antes decía «Internal Server Error»).
- [ ] En la respuesta no aparece `Texto-Prueba`.
2. Copia y pega: `docker compose logs --since 2m backend | grep -c Texto-Prueba`
- [ ] Sale `0`: el texto no quedó en el registro del servidor.

## 2 · Un error común ya no repite lo que mandaste
1. Copia y pega:
   `curl -s -X POST localhost:8000/api/v1/users/signup -H 'content-type: application/json' --data-binary '{"email":"sin-arroba","password":"x","full_name":"ok"}'`
- [ ] La respuesta habla de `email` y de `password`.
- [ ] En ninguna parte aparece `sin-arroba` (antes la API lo repetía).

## Lo que NO hace todavía
- El servicio de reporte de errores (Sentry) sigue apagado. Este cambio deja lista su configuración para que, el día
  que se encienda, no reciba lo que la persona escribió.
- Un carácter nulo en el nombre o el correo todavía hace fallar a la API, y en ese caso el registro del servidor
  muestra los datos de esa cuenta. Quedó anotado para el cambio de base de datos.
- Los mensajes técnicos de la API siguen en inglés (decisión del 2026-10-19).

## Decisiones tomadas por delegación (corrígelas si no te late)
- La API deja de repetir el dato recibido en **todos** sus errores de validación, no solo en el que fallaba.
- La configuración del reporte de errores dice explícitamente «sin datos personales», aunque ya era así por defecto.
