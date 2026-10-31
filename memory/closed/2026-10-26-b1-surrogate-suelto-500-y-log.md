---
date: 2026-10-26
state: frozen
anchor: journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)
---
B1 de perfil-habitos-actividad-sueno (PR #34, ronda 1): un surrogate UTF-16 suelto en cualquier texto del cuerpo (`"…\ud800"`) hace que el 422 de pydantic (`string_unicode`) no se pueda serializar: la API responde 500 y el traceback en stdout lleva el `input` en claro (`docker logs`), datos de salud incluidos

**Verdict and why:** Confirmado por reproducción (validador de backend, 2026-10-26) en el nombre de "Otra", en `alcohol.status`, en `other_text` de `POST /profile/history` y en `full_name` de `POST /users/signup` (sin sesión). La causa está en `backend/app/main.py`, que no tiene un handler de `RequestValidationError`; no es de este cambio. Saúl Pérez aprobó la recomendación (2026-10-26): historia propia dentro de la tarea de deudas (`memory/inbox/2026-10-21-atender-todas-las-deudas-antes-de-la-investigacion-ux.md`). Arreglo probable: un handler de toda la app que quite `input` de los errores (o codifique con `errors="replace"`), con una prueba por ruta representativa. Es distinto de ⏸️ S2 (Sentry) y de 🔒 "422 en inglés"

**State:** 🔒 frozen (pagado)

**Anchor (journal: date · title):** journal: 2026-10-26 · perfil-habitos-actividad-sueno (C2a: C-5, C-7, C-8)

**Pagado (2026-10-31):** api-errores-sin-datos, PR #46. `backend/app/main.py`: el 422 sin `input` y `SENTRY_OPTIONS` (`max_request_body_size="never"`, `include_local_variables=False`), probado en `backend/tests/api/routes/test_error_reports.py`. No se vuelve a reportar; lo que quedó (NUL, discriminador, `query_string`) tiene veredicto propio del 2026-10-31.
