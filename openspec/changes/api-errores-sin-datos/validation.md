# Validación — los errores de la API no repiten tus datos

Para: Saúl Pérez. Unos 3 minutos, en la terminal, con la app levantada (`make up`). No hay nada nuevo en pantalla:
el cambio es en lo que la API contesta cuando algo está mal.

## 1 · Un texto roto ya no tumba la API
1. Pega esto en la terminal:
   `curl -s -X POST localhost:8000/api/v1/users/signup -H 'content-type: application/json' --data-binary '{"email":"prueba@example.com","password":"contrasena-larga","full_name":"Texto-Prueba\ud800"}'`
- [ ] La respuesta empieza con `{"detail":[{"type":"string_unicode"` (antes era «Internal Server Error»).
- [ ] No aparece `Texto-Prueba` en la respuesta.
2. Pega `docker compose logs --since 2m backend | grep -c Texto-Prueba`.
- [ ] Dice `0`.

## 2 · Un error común se ve igual, pero sin repetir lo que mandaste
1. En http://localhost:8000, en «Crear cuenta», los mensajes de error se ven igual que antes.
2. En la terminal:
   `curl -s -X POST localhost:8000/api/v1/users/signup -H 'content-type: application/json' --data-binary '{"email":"sin-arroba","password":"x","full_name":"ok"}'`
- [ ] Hay dos errores, de `email` y de `password`, y en ninguno aparece `sin-arroba`.

## Lo que NO hace todavía
- Sentry sigue apagado: no hay `SENTRY_DSN`. El arreglo deja lista la configuración para cuando se encienda.
- Los mensajes de pydantic siguen en inglés (decisión congelada del 2026-10-19).

## Decisiones tomadas por delegación (corrígelas si no te late)
- El 422 deja de devolver `input` en **todas** las rutas, no solo en la que fallaba.
- `send_default_pii=False` se escribe explícito aunque es el valor por defecto.
