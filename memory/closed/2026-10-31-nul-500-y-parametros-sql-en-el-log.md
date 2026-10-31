---
date: 2026-10-31
state: frozen
anchor: journal: 2026-10-31 · api-errores-sin-datos: los errores de la API no repiten datos de salud (B1 y S2)
---
M1 de api-errores-sin-datos (PR #46, ronda 1): un carácter NUL (`\u0000`) en un texto en claro da 500, y el log y el evento de Sentry llevan los parámetros SQL en claro (correo, nombre, hash argon2)

**Verdict and why:** Confirmado por reproducción (validador, 2026-10-31):
- `POST /users/signup` con `full_name` que termina en `\u0000` da 500;
- `docker compose logs backend` muestra `[parameters: {'email': …, 'full_name': …, 'hashed_password': '$argon2id$…'}]`;
- lo mismo con `PATCH /users/me` y con el `username` de `/login/access-token`, sin sesión;
- con `SENTRY_OPTIONS`, el texto viaja en `exception.values[].value`.

Los campos de salud van cifrados, así que su NUL se guarda bien. Solo filtran las columnas en claro de la cuenta, y
son datos de la misma persona que hizo la petición. Queda fuera de api-errores-sin-datos porque cambiar los 500 que no
vienen de validación es un Non-Goal de su `design.md`. Se decidió por delegación de Saúl Pérez (author).

**Arreglo medido:** `create_engine(…, hide_parameters=True)` en `backend/app/core/db.py:7` quita los valores del log
y del mensaje de la excepción. Lo probó el validador con SQLAlchemy 2.0.51. Rechazar `\x00` en la validación lo
vuelve 422. Va en el cambio de base de datos de las deudas de FastAPI.

**State:** 🔒 frozen (pagado)

**Anchor (journal: date · title):** journal: 2026-10-31 · api-errores-sin-datos: los errores de la API no repiten datos de salud (B1 y S2)

**Pagado (2026-10-31):** bd-candados-indices-y-log, PR #48. `hide_parameters=True` en el engine; el NUL se rechaza con 422 en los textos en claro, y `get_user_by_email` lo ataja para el login y la recuperación de contraseña. Queda F2 (el `DETAIL` de unicidad), con veredicto propio.
