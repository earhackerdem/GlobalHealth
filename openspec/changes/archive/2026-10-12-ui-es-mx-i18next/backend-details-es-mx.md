# Contrato grupo 3 — `detail` del API y correos en es-MX

Fuente única para tester (aserciones) e implementer (traducción). Los textos se copian EXACTOS.
`CONSENT_REQUIRED` NO se traduce: es un código de máquina que el frontend intercepta (ConsentGate), no un texto
visible. Los details de consent.py y health_records.py ya están en es-MX y no cambian.

## detail= (login.py, users.py, items.py, deps.py, private.py)

| Inglés actual | es-MX |
|---|---|
| Could not validate credentials | No se pudieron validar las credenciales |
| Inactive user | Usuario inactivo |
| Incorrect email or password | Correo o contraseña incorrectos |
| Incorrect password | Contraseña incorrecta |
| Invalid token | Token inválido o expirado |
| Item not found | Elemento no encontrado |
| New password cannot be the same as the current one | La nueva contraseña no puede ser igual a la actual |
| Not enough permissions | No tienes permisos suficientes |
| Super users are not allowed to delete themselves | Un superusuario no puede eliminarse a sí mismo |
| The user doesn't have enough privileges | El usuario no tiene privilegios suficientes |
| The user with this email already exists in the system. | Ya existe una cuenta con este correo. |
| The user with this email already exists in the system | Ya existe una cuenta con este correo |
| The user with this id does not exist in the system | No existe un usuario con este id |
| The user with this username does not exist in the system. | No existe una cuenta con este correo. |
| User not found | Usuario no encontrado |
| User with this email already exists | Ya existe una cuenta con este correo |

Nota: se respeta el punto final (o su ausencia) del original por string, para que cada aserción siga siendo copia
exacta.

## message= de éxito (login.py, users.py, items.py) — añadidos tras el hueco que encontró el tester

| Inglés actual | es-MX |
|---|---|
| If that email is registered, we sent a password recovery link | Si ese correo está registrado, enviamos un enlace de recuperación de contraseña |
| Password updated successfully | Contraseña actualizada correctamente |
| Item deleted successfully | Elemento eliminado correctamente |
| User deleted successfully | Usuario eliminado correctamente |

## Asuntos de correo (app/utils.py)

| Inglés actual | es-MX |
|---|---|
| {project_name} - Test email | {project_name} - Correo de prueba |
| {project_name} - Password recovery for user {email} | {project_name} - Recuperación de contraseña para {email} |
| {project_name} - New account for user {username} | {project_name} - Nueva cuenta para {username} |

## Plantillas React Email (packages/react-email/emails/*.tsx → backend/app/email-templates/*.html)

- `reset_password.tsx`: saludo, cuerpo ("Recibimos una solicitud para restablecer tu contraseña…"), botón
  "Restablecer contraseña", nota de expiración con las horas interpoladas, despedida.
- `new_account.tsx`: bienvenida a {project_name}, cuenta creada para {username}, botón "Entrar a mi cuenta".
- `test_email.tsx`: "Correo de prueba de {project_name}".
El implementer redacta el cuerpo completo en es-MX natural (tuteo, consistente con la UI); el tester SOLO asierte
asunto (exacto, tabla de arriba) y, en el flujo Playwright de reset, que el enlace de restablecer funciona y el
botón/cuerpo contiene "Restablecer contraseña".
