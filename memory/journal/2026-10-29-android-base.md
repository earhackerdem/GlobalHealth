---
date: 2026-10-29
---

# android-base: la app de Android entra y muestra el perfil

**Quién e intención.** Saúl Pérez (autor) instaló Android Studio y pidió arrancar la app nativa (D24). Es la primera
historia de la v1 «hardware primero».

**Exploración y plan.**
- Investigación con fuentes primarias (`memory/research/android.md`): minSdk 29 cubre al menos el 93.1 % en México;
  `security-crypto` quedó obsoleta (se usa DataStore con Tink); AGP 9.5; Play pide target 36.
- Saúl Pérez eligió las cuatro recomendaciones: Google después, el consentimiento en la app, básicos más el estado de
  las secciones, y minSdk 29. Navegó el prototipo y escribió «plan approved».

**Ejecución.**
- **Andamio:** Gradle 9.6.0 descargado de la fuente oficial con su checksum verificado, Compose con la paleta D22, CI
  `test-android` filtrado por `android/**` y `android/` agregado a `harness.json`.
- **Dos grupos test→impl:**
  - Grupo 1 (sesión, entrada, consentimiento): rojo de 12 referencias sin resolver; verde con 13 pruebas.
  - Grupo 2 (perfil): rojo de 30 referencias a `ProfileFormat`; verde con 39 pruebas.
  - Ninguna falla, error ni prueba saltada; lint sin errores; `tdd-check` ✓.
- **Lo que aparecieron en el camino:**
  - Robolectric con el SDK 36 no arranca sobre el JDK 25: se fijó el SDK 35 de pruebas.
  - Las librerías actuales exigen `compileSdk` 37.
  - Una prueba prohibía la palabra «editar» y chocaba con la nota aprobada: volvió al tester y ahora busca solo
    controles.
  - El tester también reforzó la prueba de D20 de «Entrar», que pasaba aunque el botón siguiera disponible.

**Verificación.** Pase en el emulador contra la API real:
- un solo pedido con doble toque;
- el perfil con datos reales;
- **cero coincidencias** del JWT o de datos del perfil en los archivos de la app;
- reabrir, girar, modo oscuro, sin API con «Reintentar», cerrar sesión, y el consentimiento registrado (201).

**No hecho.** El S26 Ultra no aparece por USB en la Mac (ni en `adb` ni en el sistema). Su recorrido queda en
`validation.md`. TalkBack no se activó.

**Deuda.**
- El texto del consentimiento es el provisional del backend («pendiente de revisión legal»).
- No hay backend en línea para la versión release.
- El ícono es provisional.
- Gradle 9.8.2 está disponible y el plan fijó 9.6.0.
