# Validación — la base de datos: candados, índices y registro

Para: Saúl Pérez. Unos 3 minutos en la terminal, con la app levantada (`make up`, que aplica la migración nueva). En
pantalla no cambia nada.

## 1 · Un carácter nulo ya no tumba la API ni deja datos en el registro
1. Copia y pega:
   `curl -s -X POST localhost:8000/api/v1/users/signup -H 'content-type: application/json' --data-binary '{"email":"prueba-nul@example.com","password":"contrasena-larga","full_name":"Prueba-Nulo\u0000x"}'`
- [ ] Dice «El texto no puede contener el carácter nulo» (antes: «Internal Server Error»).
2. Copia y pega: `docker compose logs --since 2m backend | grep -c Prueba-Nulo`
- [ ] Sale `0`.

## 2 · Las búsquedas por paciente usan índice
1. Copia y pega:
   `docker compose exec -T db psql -U postgres -d app -At -c "SELECT count(*) FROM pg_constraint c WHERE c.contype='f' AND NOT EXISTS (SELECT 1 FROM pg_index i WHERE i.indrelid=c.conrelid AND i.indkey[0]=c.conkey[1]);"`
- [ ] Sale `0` (antes eran 9 llaves sin índice).

## 3 · Lo de siempre sigue igual
1. Entra con tu cuenta de prueba, agrega una enfermedad crónica enlazada a un diagnóstico de tu expediente y después
   borra ese diagnóstico.
- [ ] La crónica sigue ahí, sin enlace, como antes.

## Lo que NO hace todavía
- La carrera entre guardar una crónica y borrar su diagnóstico al mismo tiempo no se puede provocar a mano. La cubre
  una prueba automática que pausa el borrado a la mitad.
- Si alguna vez se borra una cuenta mientras se borra uno de sus diagnósticos, la base elige cuál de las dos
  operaciones cancela (deuda registrada; solo pasaría si el borrado de cuentas se vuelve masivo).

## Decisiones tomadas por delegación (corrígelas si no te late)
- El inicio de sesión con un carácter nulo responde «Correo o contraseña incorrectos», sin decir nada más.
- También se indexaron las tablas de «Elementos» (del template) y de la cuenta de Google, porque la regla es «toda
  llave con índice».
