---
date: 2026-10-29
status: open
---

**Prioridad: la app de Android, después del PR #40** (Saúl Pérez, 2026-10-29, durante la revisión de perfil-trabajo:
«despues de esto prioriza hacer la app de android»). Pasa por delante de la mascota (D23 decía «después de la C2b») y
de la tarea de deudas.

**Why it matters:** toca dos decisiones vigentes que hay que reconciliar antes de planear:
- **D7:** la app de Android de v1 es un shell de Capacitor sobre la misma web (notificaciones locales para FR-025,
  cámara para FR-007);
- **D17:** Android entra por un spike acotado (ML Kit GenAI en el S26 Ultra leyendo el corpus de recetas), no en
  paralelo (`memory/inbox/2026-10-18-spike-android-ia-en-dispositivo-pedido.md`).

Hay que preguntarle a Saúl Pérez, con chips, cuál de las dos cosas quiere (o ambas, y en qué orden), y si D17 se
revisa.

**Actualización (mismo día):** Saúl Pérez cambió de opinión: «prefiero una app nativa para android, despues tendremos
que hacer la app nativa de iphone». Esto revisa **D7** (Capacitor) y matiza **D17** (spike primero), y suma iOS como
plataforma futura. Antes de planear, una objeción con alternativa (AGENTS.md): dos apps nativas más la web son tres
bases de código para una persona a tiempo parcial sin experiencia en Android; la alternativa es una base nativa
multiplataforma (por ejemplo Kotlin Multiplatform con Compose Multiplatform, React Native o Flutter). Se decide con
chips y queda como ADR que revisa D7 (y toca D17) en el mismo cambio.

**Status:** abierto · triage pendiente (va después del PR #40)
