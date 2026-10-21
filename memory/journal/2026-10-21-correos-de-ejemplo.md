# 2026-10-21 · correos de ejemplo en example.com

**Quién:** Saúl Pérez (author) hizo público el repo para que el CI no consuma minutos de pago, y pidió que los
ejemplos usen `email@example.com` (un correo) y `test@example.com` (dos). El agente aplicó.

**Qué se hizo:** los escenarios de `identity/user-auth` (spec canónica y copia archivada) y `test_private.py` pasan a
`email@example.com`. Antes usaban un Gmail real, un nombre propio en example.com y un dominio real (`listo.com`).
Ninguno usaba dos correos con dominio real.

**Verificación:** `openspec validate --specs` 6/6. El test se verifica en CI: la BD de prueba local ya tiene la
migración de hábitos (`7d3e9a1c5b42`, PR #30), que `main` todavía no conoce, y alembic no la resuelve.

**Riesgo declarado a Saúl Pérez:** la identidad de git del repo (`harness.json`, D1, journal fundacional) sigue a la
vista, y la historia de git conserva la evidencia vieja del inicio de sesión con su cuenta real de Google. Limpiar la
historia exige `--force` o un repo nuevo; se queda así por decisión suya.
