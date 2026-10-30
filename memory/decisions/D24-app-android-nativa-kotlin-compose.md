---
id: D24
date: 2026-10-29
status: accepted
---

## D24 — App de Android nativa (Kotlin + Jetpack Compose); iPhone nativo después

- **Status:** Accepted · 2026-10-29 · decided by: Saúl Pérez (autor).
  - Revisa D7, que planteaba un shell de Capacitor.
  - Matiza D17: el spike deja de ser la puerta de entrada.
  - Cambia el orden de D23: la mascota va después de la v1 de Android.
- **Decision:**
  1. **Plataforma.** El paciente tiene una app de Android nativa, en Kotlin con Jetpack Compose. La de iPhone será
     nativa en Swift y vendrá después. Cuando llegue iPhone se decide si la lógica que no es pantalla (cliente de la
     API, modelos, cifrado local) se comparte con Kotlin Multiplatform; eso no limita el acceso al hardware.
  2. **Mismo backend.** La app habla con la misma API (`/api/v1`, FastAPI) que la web y no tiene servidor propio. La
     web se queda como está para el paciente y el profesional (D11).
  3. **Alcance de la v1: hardware primero.**
     - entrar con la cuenta existente, con el consentimiento de siempre;
     - fotografiar una receta o un documento con la cámara y adjuntarlo (FR-007);
     - recordatorios de las tomas con notificaciones locales (FR-025);
     - ver el perfil médico.

     Lo demás sigue en la web y se suma por historias.
  4. **Código** en este repo, en la carpeta `android/`: la misma memoria, las mismas decisiones, el mismo harness y
     el mismo CI. El cliente de la API puede generarse del mismo OpenAPI.
  5. **Distribución.** Al principio, APK instalado por cable o `adb` en el S26 Ultra de Saúl Pérez. La prueba interna
     de Play Console llega cuando haya algo que compartir.
  6. **Versión mínima de Android:** la decide la exploración del primer cambio, con cifras de uso en México y lo que
     piden Compose, CameraX y Health Connect.
- **Why:** Saúl Pérez quiere aprovechar el hardware del teléfono:
  - la cámara;
  - notificaciones locales fiables;
  - IA en el dispositivo (ML Kit GenAI, la vía de D17);
  - Health Connect cuando entren los wearables (D4).

  Desde el 2026-10-29 le dedica la mayor parte de su tiempo al proyecto, así que el argumento de D7 (meses de curva
  para una persona a tiempo parcial) pesa menos.
- **Discarded alternatives:**
  - **Shell de Capacitor (D7):** reusa la web, pero el hardware queda detrás de plugins.
  - **Kotlin Multiplatform, React Native o Flutter desde ya:** era la objeción del agente (tres bases de código para
    una persona). Saúl Pérez reafirmó lo nativo. KMP queda como opción para la lógica compartida cuando llegue iPhone.
  - **Paridad con la web en la v1:** demasiado trabajo antes de tener algo en el teléfono.
  - **Spike de IA primero (D17):** pasa a ser una historia posible dentro de la app nativa, no una condición para
    hacerla.
  - **Repo aparte:** la memoria y las decisiones quedarían en dos lugares.
  - **Play Console desde el inicio:** pide la cuenta y la ficha de la app antes de tiempo.
- **Risks the agent noted, accepted by Saúl Pérez:**
  - Tres bases de código (web, Android y, después, iPhone). Cada cambio del modelo de dominio se paga en cada una.
  - Saúl Pérez no tiene experiencia en Android (`product/technical-brief.md` §1). Primero viene la curva.
  - **Datos de salud en el teléfono.** Sigue valiendo NFR-001: nada sensible en claro en el dispositivo. El token de
    la sesión va en almacenamiento respaldado por el Android Keystore, y lo que se guarde en caché va cifrado o no se
    guarda. El cómo lo decide la exploración, con fuentes de la versión vigente.
  - **FR-025.** Necesita saber los horarios de las tomas. Si la receta de hoy no los guarda, hay que ampliar el
    modelo antes de los recordatorios. Lo verifica la exploración.
- **Applies to:**
  - `product/technical-brief.md`: §3 cliente móvil y §5 tabla de decisiones;
  - NFR-011, que deja de leerse como «Android por Capacitor»;
  - `harness.json → code` y `tests`: el primer cambio de Android suma `android/` y sus rutas de pruebas;
  - el orden de D23.
