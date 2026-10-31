---
date: 2026-10-29
status: done
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

**Reafirmado (mismo día):** el agente objetó con chips (tres bases de código; Kotlin Multiplatform, React Native o
Flutter como alternativas). Saúl Pérez respondió que ahora le dedica la mayor parte de su tiempo al proyecto y que quiere
las apps nativas para aprovechar el hardware. Es su decisión: **Android nativo en Kotlin con Jetpack Compose**, y
**iPhone nativo en Swift después**. Queda abierto, para cuando llegue iPhone, si la lógica que no es pantalla se
comparte con Kotlin Multiplatform, que no limita el acceso al hardware. Antes de empezar va la mejora del hook
`lint.py` (harness primero, earhackerdem/harness#6).

**Status:** abierto · siguiente historia después de mergear el PR #40 y traer el harness 0.4.1: un ADR que revise D7 y
toque D17 y D23 (orden), y después `/triage` de la app de Android

**Closure:** decidido en D24 (PR #42, app nativa en Kotlin con Jetpack Compose; iPhone en Swift después) y empezado con su primera historia, android-base (PR #44: entrar, consentimiento y «Mi perfil médico» en solo lectura). Siguen android-camara y android-recordatorios.
