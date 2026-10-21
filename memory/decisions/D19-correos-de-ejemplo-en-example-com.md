---
id: D19
date: 2026-10-21
status: accepted
---

## D19 — Correos de ejemplo en example.com
- **Status:** Accepted · 2026-10-21 · decided by: Saúl Pérez (author/owner)
- **Decision:** en specs, escenarios, tests fijos y documentos, un caso con un solo correo usa `email@example.com`;
  un caso con dos correos usa `email@example.com` y `test@example.com`. Nada de correos reales, nombres propios ni
  dominios registrados (gmail.com, listo.com…). Los tests que crean cuentas al vuelo siguen con sus helpers
  aleatorios en example.com.
- **Why:** el repo es público desde 2026-10-21 (Saúl Pérez lo abrió para que el CI no consuma minutos de pago), y un
  correo de ejemplo con dominio real puede ser de alguien.
- **Consequence:** fuera de alcance: la identidad de git del repo (`harness.json`, D1) y el placeholder es-MX del
  formulario de inicio de sesión. La historia de git conserva los correos anteriores (journal 2026-10-21 · correos
  de ejemplo).
