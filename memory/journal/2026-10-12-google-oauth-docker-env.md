# 2026-10-12 · fix google-oauth-docker-env (PR #7)

- Saúl Pérez reportó 400 invalid_request de Google ("Missing required parameter: redirect_uri") al probar el
  login en local. Causa raíz: el environment del backend en compose.yml nunca incluyó las GOOGLE_* y Settings
  lee ../.env, inexistente en el contenedor — el login con Google nunca funcionó contra el backend dockerizado;
  antes pasaba porque el backend corría en el host. Hoy el :8000 lo ocupa Docker y afloró.
- Desbloqueo inmediato sin tocar el repo: override extra en el scratchpad con las 3 variables y reinicio del
  backend; verificado 307 a accounts.google.com con redirect_uri presente.
- Fix durable: compose.yml interpola GOOGLE_CLIENT_ID/SECRET/REDIRECT_URI desde el .env local con default
  vacío (CI no exige nada). Sin secretos en el repo. Rama fix/google-oauth-docker-env, PR #7, merge humano.
- Gate: typos rechazó "responde" en el comentario (el whitelist nuevo vive en la rama del PR #6) → reformulado
  a "devuelve" para no duplicar el whitelist en dos ramas.
